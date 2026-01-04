"""
Service Account MFA Bypass Tests

CRITICAL: These tests validate that service accounts can bypass MFA
to prevent automation lockout.
"""
import pytest


def test_mfa_bypass_group_exists(host):
    """
    CRITICAL: mfa-bypass group must exist before PAM configuration.
    If PAM references a non-existent group, authentication fails.
    """
    group = host.group("mfa-bypass")
    assert group.exists, \
        "CRITICAL: mfa-bypass group must exist for service account bypass"


def test_service_accounts_in_bypass_group(host):
    """
    CRITICAL: Service accounts must be in mfa-bypass group.
    This prevents automation lockout when MFA is enforced.
    """
    # Common service account names
    service_accounts = ["ansible", "ci", "backup", "monitoring", "deploy"]

    # Get all users in mfa-bypass group
    result = host.run("getent group mfa-bypass")

    if result.rc == 0:
        bypass_members = result.stdout.strip().split(":")[-1].split(",")
        bypass_members = [m.strip() for m in bypass_members if m.strip()]

        # Check if any service accounts exist and are in bypass group
        found_service_accounts = []
        for account in service_accounts:
            user = host.user(account)
            if user.exists:
                found_service_accounts.append(account)
                # Verify this service account is in mfa-bypass group
                user_groups = host.run(f"id -Gn {account}").stdout
                assert "mfa-bypass" in user_groups, \
                    f"CRITICAL: Service account {account} exists but NOT in mfa-bypass group. " \
                    f"This will cause automation lockout when MFA is enforced!"

        # If service accounts exist, at least one should be in bypass group
        if found_service_accounts:
            assert len(bypass_members) > 0, \
                f"CRITICAL: Service accounts found ({found_service_accounts}) but mfa-bypass group is empty"


def test_pam_bypass_rule_exists(host):
    """
    Verify PAM configuration includes bypass rule for mfa-bypass group.
    """
    pam_sshd = host.file("/etc/pam.d/sshd")

    if pam_sshd.exists:
        content = pam_sshd.content_string

        # Check for pam_succeed_if bypass rule
        assert "pam_succeed_if" in content and "mfa-bypass" in content, \
            "PAM configuration must include bypass rule for mfa-bypass group"

        # Verify it's in the auth section (required for SSH)
        lines = content.split("\n")
        found_bypass = False
        for line in lines:
            if "auth" in line and "pam_succeed_if" in line and "mfa-bypass" in line:
                found_bypass = True
                # Verify it uses success=1 to skip next rule
                assert "[success=1" in line or "success=1" in line, \
                    "Bypass rule should use [success=1 default=ignore] control"
                break

        assert found_bypass, \
            "PAM auth section must include pam_succeed_if bypass for mfa-bypass group"


def test_bypass_comes_before_mfa_enforcement(host):
    """
    CRITICAL: Bypass rule must come BEFORE MFA enforcement in PAM stack.
    If MFA enforcement comes first, bypass won't work.
    """
    pam_sshd = host.file("/etc/pam.d/sshd")

    if pam_sshd.exists:
        content = pam_sshd.content_string
        lines = content.split("\n")

        bypass_line = None
        mfa_line = None

        for i, line in enumerate(lines):
            # Skip comments and empty lines
            if not line.strip() or line.strip().startswith("#"):
                continue

            # Find bypass rule
            if "auth" in line and "pam_succeed_if" in line and "mfa-bypass" in line:
                if bypass_line is None:
                    bypass_line = i

            # Find MFA enforcement (pam_u2f or pam_fido2 with required)
            if "auth" in line and ("pam_u2f" in line or "pam_fido2" in line):
                if "required" in line and mfa_line is None:
                    mfa_line = i

        if bypass_line is not None and mfa_line is not None:
            assert bypass_line < mfa_line, \
                f"CRITICAL: PAM bypass rule (line {bypass_line}) must come BEFORE " \
                f"MFA enforcement (line {mfa_line}). Current order will cause lockout!"


def test_breakglass_group_exists(host):
    """
    Verify breakglass group exists for emergency MFA bypass.
    """
    group = host.group("mfa-breakglass")
    assert group.exists, \
        "mfa-breakglass group should exist for emergency access"


def test_service_accounts_have_restricted_shell(host):
    """
    Service accounts should have /usr/sbin/nologin or similar restricted shell.
    This prevents interactive login while allowing automated processes.
    """
    service_accounts = ["ansible", "ci", "backup", "monitoring", "deploy"]

    for account in service_accounts:
        user = host.user(account)
        if user.exists:
            # Service accounts should have restricted shell
            assert user.shell in ["/usr/sbin/nologin", "/sbin/nologin", "/bin/false"], \
                f"Service account {account} should have restricted shell, got {user.shell}"


def test_pam_bypass_does_not_affect_human_users(host):
    """
    Verify that regular users are NOT in mfa-bypass group.
    Only service accounts should bypass MFA.
    """
    # Get all users in mfa-bypass group
    result = host.run("getent group mfa-bypass")

    if result.rc == 0:
        bypass_members = result.stdout.strip().split(":")[-1].split(",")
        bypass_members = [m.strip() for m in bypass_members if m.strip()]

        # Check if any bypass members have interactive shells
        for member in bypass_members:
            if not member:  # Skip empty strings
                continue

            user = host.user(member)
            if user.exists:
                # If user has interactive shell, warn (they shouldn't be in bypass)
                if user.shell not in ["/usr/sbin/nologin", "/sbin/nologin", "/bin/false"]:
                    pytest.fail(
                        f"WARNING: User {member} has interactive shell ({user.shell}) "
                        f"but is in mfa-bypass group. Only service accounts should bypass MFA."
                    )


def test_mfa_bypass_group_is_not_primary_group(host):
    """
    mfa-bypass should be a supplementary group, not primary.
    This ensures users aren't accidentally added via primary GID.
    """
    result = host.run("getent group mfa-bypass")

    if result.rc == 0:
        # Get GID of mfa-bypass group
        group_info = result.stdout.strip().split(":")
        mfa_bypass_gid = group_info[2]

        # Verify no user has this as primary group
        users_with_bypass_primary = host.run(
            f"getent passwd | awk -F: '$4 == {mfa_bypass_gid} {{print $1}}'"
        )

        if users_with_bypass_primary.stdout.strip():
            pytest.fail(
                f"CRITICAL: Users have mfa-bypass as primary group: "
                f"{users_with_bypass_primary.stdout.strip()}. "
                f"mfa-bypass should only be supplementary group."
            )


def test_pam_modules_required_for_bypass_exist(host):
    """
    Verify pam_succeed_if.so exists before PAM references it.
    Missing modules cause authentication failures.
    """
    # Common locations for PAM modules
    pam_module_paths = [
        "/lib/security/pam_succeed_if.so",
        "/lib64/security/pam_succeed_if.so",
        "/usr/lib/security/pam_succeed_if.so",
        "/usr/lib64/security/pam_succeed_if.so",
    ]

    module_exists = False
    for path in pam_module_paths:
        if host.file(path).exists:
            module_exists = True
            break

    assert module_exists, \
        "CRITICAL: pam_succeed_if.so not found. Required for service account bypass."


def test_no_wildcard_bypass_in_pam(host):
    """
    Verify PAM bypass rule doesn't use wildcards or overly permissive patterns.
    Bypass should be explicit (group membership only).
    """
    pam_sshd = host.file("/etc/pam.d/sshd")

    if pam_sshd.exists:
        content = pam_sshd.content_string

        # Check for dangerous patterns
        dangerous_patterns = [
            "user in *",
            "user eq *",
            "uid >= 0",  # Matches all users
        ]

        for pattern in dangerous_patterns:
            assert pattern not in content, \
                f"CRITICAL: Dangerous bypass pattern '{pattern}' found in PAM config"
