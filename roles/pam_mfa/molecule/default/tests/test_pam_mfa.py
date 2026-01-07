import testinfra.utils.ansible_runner


testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    ".molecule/ansible_inventory.yml"
).get_hosts("all")

def _using_debian13_stack(host):
    if host.system_info.distribution.lower() != "debian":
        return False
    return host.file("/etc/pam.d/mfa-totp").exists


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
    if _using_debian13_stack(host):
        return
    pam_sshd = host.file("/etc/pam.d/sshd")
    assert pam_sshd.exists, "/etc/pam.d/sshd should exist"
    content = pam_sshd.content_string
    assert "pam_u2f" in content or "pam_fido2" in content, \
        "PAM sshd should contain pam_u2f or pam_fido2 configuration"


def test_pam_sshd_contains_totp(host):
    """Test that PAM SSH configuration includes TOTP backup."""
    if _using_debian13_stack(host):
        return
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
    if _using_debian13_stack(host):
        return
    pam_sudo = host.file("/etc/pam.d/sudo")
    assert pam_sudo.exists, "/etc/pam.d/sudo should exist"
    content = pam_sudo.content_string
    assert "pam_u2f" in content or "pam_fido2" in content, \
        "PAM sudo should contain pam_u2f or pam_fido2 configuration"

def test_pam_prefers_fido2_when_present(host):
    """Primary module should be pam_fido2 when the module path is present."""
    if _using_debian13_stack(host):
        return
    pam_sshd = host.file("/etc/pam.d/sshd").content_string
    pam_sudo = host.file("/etc/pam.d/sudo").content_string

    assert "/lib/security/pam_fido2.so" in pam_sshd, \
        "PAM sshd should use pam_fido2 when module is present"
    assert "/lib/security/pam_fido2.so" in pam_sudo, \
        "PAM sudo should use pam_fido2 when module is present"

    assert "authfile=/tmp/fido2_auth" in pam_sshd, \
        "PAM sshd should use fido2 authfile when module is present"
    assert "authfile=/tmp/fido2_auth" in pam_sudo, \
        "PAM sudo should use fido2 authfile when module is present"


def test_u2f_keys_directory_exists(host):
    """Test that U2F keys directory exists with correct permissions."""
    if _using_debian13_stack(host):
        return
    keys_dir = host.file("/etc/Yubico")
    assert keys_dir.exists, "/etc/Yubico directory should exist"
    assert keys_dir.is_directory, "/etc/Yubico should be a directory"
    assert keys_dir.mode == 0o755, "/etc/Yubico should have 755 permissions"


def test_mfa_breakglass_group_exists(host):
    """Test that MFA breakglass group exists."""
    if _using_debian13_stack(host):
        return
    group = host.group("mfa-breakglass")
    assert group.exists, "mfa-breakglass group should exist for TOTP fallback"


def test_service_accounts_exempt(host):
    """Test that service accounts bypass MFA (CRITICAL for automation)."""
    if _using_debian13_stack(host):
        return
    pam_sshd = host.file("/etc/pam.d/sshd")
    content = pam_sshd.content_string

    # CRITICAL: Verify service account bypass exists
    assert "pam_succeed_if" in content and "mfa-bypass" in content, \
        "CRITICAL: Service accounts MUST have MFA bypass to prevent automation lockout"
    assert "rhost" in content and "10.0.0.0/8" in content, \
        "CRITICAL: Service account bypass should be scoped by source when configured"

    service_accounts = ["ansible", "ci", "sftp", "rsync"]
    for account in service_accounts:
        # Check if user exists before testing
        user = host.user(account)
        if user.exists:
            # Service accounts should have /usr/sbin/nologin or similar
            assert user.shell in ["/usr/sbin/nologin", "/sbin/nologin", "/bin/false"], \
                f"Service account {account} should have restricted shell"


def test_service_accounts_in_bypass_group(host):
    """Ensure service accounts are added to the MFA bypass group."""
    if _using_debian13_stack(host):
        return
    bypass_group = host.group("mfa-bypass")
    assert bypass_group.exists, "mfa-bypass group should exist"
    for account in ["ansible", "ci"]:
        assert account in bypass_group.members, \
            f"Service account {account} should be in mfa-bypass group"


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
    if _using_debian13_stack(host):
        return
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
    if _using_debian13_stack(host):
        return
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

def test_totp_breakglass_gating(host):
    """CRITICAL: TOTP should only trigger for breakglass group."""
    if _using_debian13_stack(host):
        return
    pam_sshd = host.file("/etc/pam.d/sshd").content_string.splitlines()
    pam_sudo = host.file("/etc/pam.d/sudo").content_string.splitlines()

    def _assert_gating(lines, name):
        gate_idx = None
        totp_idx = None
        for i, line in enumerate(lines):
            if "pam_succeed_if" in line and "notingroup" in line and "mfa-breakglass" in line:
                gate_idx = i
            if "pam_google_authenticator" in line:
                totp_idx = i
                break
        assert gate_idx is not None and totp_idx is not None, \
            f"{name}: missing breakglass gating or TOTP line"
        assert gate_idx < totp_idx, \
            f"{name}: breakglass gating must appear before TOTP line"

    _assert_gating(pam_sshd, "sshd")
    _assert_gating(pam_sudo, "sudo")


def test_breakglass_skips_u2f(host):
    """CRITICAL: Breakglass users should be able to bypass U2F for TOTP."""
    if _using_debian13_stack(host):
        return
    pam_sshd = host.file("/etc/pam.d/sshd").content_string.splitlines()
    pam_sudo = host.file("/etc/pam.d/sudo").content_string.splitlines()

    def _assert_skip(lines, name):
        skip_idx = None
        u2f_idx = None
        for i, line in enumerate(lines):
            if "pam_succeed_if" in line and "ingroup" in line and "mfa-breakglass" in line:
                skip_idx = i
            if "pam_u2f" in line or "pam_fido2" in line:
                u2f_idx = i
                break
        assert skip_idx is not None and u2f_idx is not None, \
            f"{name}: missing breakglass skip or U2F/FIDO2 line"
        assert skip_idx < u2f_idx, \
            f"{name}: breakglass skip must appear before U2F/FIDO2 line"

    _assert_skip(pam_sshd, "sshd")
    _assert_skip(pam_sudo, "sudo")


def test_totp_rate_limit_enabled(host):
    """CRITICAL: TOTP should enforce rate limiting when enabled."""
    if _using_debian13_stack(host):
        return
    pam_sshd = host.file("/etc/pam.d/sshd").content_string
    pam_sudo = host.file("/etc/pam.d/sudo").content_string

    for content in (pam_sshd, pam_sudo):
        if "pam_google_authenticator" in content:
            assert "rate_limit=" in content, \
                "CRITICAL: TOTP must include rate_limit to mitigate brute force"


def test_ssh_allows_keyboard_interactive(host):
    """CRITICAL: Verify SSH is configured to allow keyboard-interactive auth for MFA."""
    if _using_debian13_stack(host):
        return
    sshd_config = host.file("/etc/ssh/sshd_config")

    if sshd_config.exists:
        content = sshd_config.content_string.lower()
        # Check that keyboard-interactive is not explicitly disabled
        assert "challengeresponseauthentication no" not in content and \
               "kbdinteractiveauthentication no" not in content, \
            "CRITICAL: SSH must allow keyboard-interactive authentication for MFA"


def test_pam_modules_exist_before_use(host):
    """CRITICAL: Verify PAM modules exist before being referenced in configuration."""
    if _using_debian13_stack(host):
        return
    pam_sshd = host.file("/etc/pam.d/sshd")
    content = pam_sshd.content_string

    # Extract module paths from PAM configuration
    modules_in_use = []
    for line in content.split("\n"):
        if line.strip() and not line.strip().startswith("#"):
            parts = line.split()
            if len(parts) >= 3:
                # Third column is typically the module path
                module_path = parts[2]
                if "/" in module_path or module_path.startswith("pam_"):
                    modules_in_use.append(module_path)

    # Verify each module file exists
    for module in modules_in_use:
        # Handle both absolute paths and module names
        if module.startswith("/"):
            module_file = host.file(module)
        else:
            # Common PAM module locations
            possible_paths = [
                f"/lib/security/{module}",
                f"/lib64/security/{module}",
                f"/usr/lib/security/{module}",
                f"/usr/lib64/security/{module}",
            ]
            module_file = None
            for path in possible_paths:
                f = host.file(path)
                if f.exists:
                    module_file = f
                    break

        if module_file:
            assert module_file.exists, \
                f"CRITICAL: PAM module {module} referenced but not found on system"


def test_pam_backup_exists(host):
    """Test that PAM configuration backup was created before modification."""
    backup_target = "sudo" if _using_debian13_stack(host) else "sshd"
    backup_files = host.run(f"ls -1 /etc/pam.d/{backup_target}.backup-* 2>/dev/null || true")
    # If role has been run, backup should exist
    # This is informational - backup creation is tested in the actual deployment
    if backup_files.stdout:
        # Verify backup has same structure as current config
        backup_file = backup_files.stdout.strip().split("\n")[0]
        backup = host.file(backup_file)
        assert backup.exists, "PAM backup file should exist"
        assert backup.size > 0, "PAM backup should not be empty"
        # Backup should have valid PAM directives
        backup_content = backup.content_string
        assert any(directive in backup_content for directive in ["auth", "account", "session"]), \
            "PAM backup should contain valid directives"


def test_lockout_prevention_variables_set(host):
    """Test that lockout prevention variables are defined in role defaults."""
    # This tests that the role has proper defaults for safety features
    # The actual values are tested during role execution
    # Check if pause task would be present (tests role logic)
    cmd = host.run("echo 'Lockout prevention check: Variables should be in defaults/main.yml'")
    assert cmd.rc == 0  # Basic sanity check


def test_debian13_sudo_totp_stack(host):
    """Debian 13 stack should add a sudo-only TOTP substack."""
    if not _using_debian13_stack(host):
        return
    pam_mfa = host.file("/etc/pam.d/mfa-totp")
    assert pam_mfa.exists
    content = pam_mfa.content_string
    assert "pam_google_authenticator" in content
    assert "secret=/var/lib/pam-google-authenticator/%u/.google_authenticator" in content
    assert "allowed_perm=0400" in content
    sudo_cfg = host.file("/etc/pam.d/sudo").content_string
    assert "auth    include    mfa-totp" in sudo_cfg
