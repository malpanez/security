import os
import testinfra.utils.ansible_runner


testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    ".molecule/ansible_inventory.yml"
).get_hosts("all")


def test_pam_packages_installed(host):
    """Test that required PAM packages are installed."""
    os_family = host.system_info.distribution.lower()

    if os_family in ["debian", "ubuntu"]:
        packages = ["libpam-u2f", "libpam-google-authenticator"]
        for pkg in packages:
            assert host.package(pkg).is_installed, f"Package {pkg} should be installed"
    elif os_family in ["centos", "rocky", "almalinux", "oraclelinux"]:
        packages = ["pam_u2f", "google-authenticator"]
        for pkg in packages:
            assert host.package(pkg).is_installed, f"Package {pkg} should be installed"


def test_pam_sshd_contains_u2f_or_fido2(host):
    """Test that PAM SSH configuration includes U2F or FIDO2."""
    pam_sshd = host.file("/etc/pam.d/sshd")
    assert pam_sshd.exists, "/etc/pam.d/sshd should exist"
    content = pam_sshd.content_string
    assert "pam_u2f" in content or "pam_fido2" in content, \
        "PAM sshd should contain pam_u2f or pam_fido2 configuration"


def test_pam_sshd_contains_totp(host):
    """Test that PAM SSH configuration includes TOTP backup."""
    pam_sshd = host.file("/etc/pam.d/sshd")
    content = pam_sshd.content_string
    assert "pam_google_authenticator" in content, \
        "PAM sshd should contain google-authenticator for TOTP backup"
    # CRITICAL: Verify nullok option to prevent lockout
    if "pam_google_authenticator" in content:
        assert "nullok" in content, \
            "CRITICAL: PAM google-authenticator MUST have 'nullok' to prevent lockout"


def test_pam_sudo_contains_u2f_or_fido2(host):
    """Test that PAM sudo configuration includes MFA."""
    pam_sudo = host.file("/etc/pam.d/sudo")
    assert pam_sudo.exists, "/etc/pam.d/sudo should exist"
    content = pam_sudo.content_string
    assert "pam_u2f" in content or "pam_fido2" in content, \
        "PAM sudo should contain pam_u2f or pam_fido2 configuration"


def test_u2f_keys_directory_exists(host):
    """Test that U2F keys directory exists with correct permissions."""
    keys_dir = host.file("/etc/Yubico")
    assert keys_dir.exists, "/etc/Yubico directory should exist"
    assert keys_dir.is_directory, "/etc/Yubico should be a directory"
    assert keys_dir.mode == 0o755, "/etc/Yubico should have 755 permissions"


def test_mfa_breakglass_group_exists(host):
    """Test that MFA breakglass group exists."""
    group = host.group("mfa-breakglass")
    assert group.exists, "mfa-breakglass group should exist for TOTP fallback"


def test_service_accounts_exempt(host):
    """Test that service accounts bypass MFA (CRITICAL for automation)."""
    pam_sshd = host.file("/etc/pam.d/sshd")
    content = pam_sshd.content_string

    # CRITICAL: Verify service account bypass exists
    assert "pam_succeed_if" in content and "mfa-bypass" in content, \
        "CRITICAL: Service accounts MUST have MFA bypass to prevent automation lockout"

    service_accounts = ["ansible", "ci", "sftp", "rsync"]
    for account in service_accounts:
        # Check if user exists before testing
        user = host.user(account)
        if user.exists:
            # Service accounts should have /usr/sbin/nologin or similar
            assert user.shell in ["/usr/sbin/nologin", "/sbin/nologin", "/bin/false"], \
                f"Service account {account} should have restricted shell"


def test_pam_configuration_syntax(host):
    """Test that PAM configurations have valid syntax."""
    pam_files = ["/etc/pam.d/sshd", "/etc/pam.d/sudo", "/etc/pam.d/common-auth"]
    for pam_file in pam_files:
        f = host.file(pam_file)
        if f.exists:
            # Check that file is not empty
            assert f.size > 0, f"{pam_file} should not be empty"
            # Check that file contains basic PAM directives
            content = f.content_string
            assert any(directive in content for directive in ["auth", "account", "session", "password"]), \
                f"{pam_file} should contain PAM directives"


def test_authselect_on_rhel(host):
    """Test authselect configuration on RHEL-based systems."""
    os_family = host.system_info.distribution.lower()

    if os_family in ["centos", "rocky", "almalinux", "oraclelinux"]:
        # Check if authselect is installed
        if host.package("authselect").is_installed:
            # Verify authselect current profile
            cmd = host.run("authselect current")
            assert cmd.rc == 0, "authselect should have a current profile configured"


def test_totp_directory_exists(host):
    """Test that TOTP directory exists if TOTP is enabled."""
    totp_dir = host.file("/etc/google-authenticator.d")
    # Directory might not exist if no users configured yet, but it should be creatable
    if totp_dir.exists:
        assert totp_dir.is_directory, "/etc/google-authenticator.d should be a directory"
        assert totp_dir.mode == 0o755, "/etc/google-authenticator.d should have 755 permissions"


def test_pam_order_prevents_lockout(host):
    """CRITICAL: Test that PAM order allows bypass before MFA enforcement."""
    pam_sshd = host.file("/etc/pam.d/sshd")
    content = pam_sshd.content_string
    lines = content.split("\n")

    # Find the line numbers of bypass and MFA modules
    bypass_line = None
    mfa_line = None

    for i, line in enumerate(lines):
        if "pam_succeed_if" in line and "mfa-bypass" in line:
            bypass_line = i
        if ("pam_u2f" in line or "pam_fido2" in line) and "auth" in line:
            if mfa_line is None:  # Get the first MFA line
                mfa_line = i

    # CRITICAL: Service account bypass MUST come before MFA enforcement
    if bypass_line is not None and mfa_line is not None:
        assert bypass_line < mfa_line, \
            "CRITICAL: Service account bypass MUST appear before MFA enforcement in PAM stack"


def test_pam_control_keywords_safe(host):
    """CRITICAL: Verify PAM control keywords won't cause lockout."""
    pam_sshd = host.file("/etc/pam.d/sshd")
    content = pam_sshd.content_string

    # Check that google-authenticator has sufficient or nullok to allow fallback
    if "pam_google_authenticator" in content:
        # Extract the google-authenticator line
        for line in content.split("\n"):
            if "pam_google_authenticator" in line:
                # Should have 'sufficient' control OR 'nullok' argument
                assert "sufficient" in line or "nullok" in line, \
                    "CRITICAL: google-authenticator must have 'sufficient' control or 'nullok' argument"


def test_ssh_allows_keyboard_interactive(host):
    """CRITICAL: Verify SSH is configured to allow keyboard-interactive auth for MFA."""
    sshd_config = host.file("/etc/ssh/sshd_config")

    if sshd_config.exists:
        content = sshd_config.content_string.lower()
        # Check that keyboard-interactive is not explicitly disabled
        assert "challengeresponseauthentication no" not in content and \
               "kbdinteractiveauthentication no" not in content, \
            "CRITICAL: SSH must allow keyboard-interactive authentication for MFA"
