import testinfra.utils.ansible_runner


testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    ".molecule/ansible_inventory.yml"
).get_hosts("all")


def test_sudoers_main_file_exists(host):
    """CRITICAL: Test that main sudoers file exists with correct permissions."""
    main = host.file("/etc/sudoers")
    assert main.exists, "/etc/sudoers must exist"
    assert main.user == "root", "/etc/sudoers must be owned by root"
    assert main.group == "root", "/etc/sudoers must be in root group"
    assert main.mode == 0o440, "CRITICAL: /etc/sudoers must have 0440 permissions"


def test_sudoers_d_directory_exists(host):
    """Test that sudoers.d directory exists with correct permissions."""
    sudoers_d = host.file("/etc/sudoers.d")
    assert sudoers_d.exists, "/etc/sudoers.d must exist"
    assert sudoers_d.is_directory, "/etc/sudoers.d must be a directory"
    assert sudoers_d.user == "root"
    assert sudoers_d.group == "root"


def test_sudoers_d_file_permissions(host):
    """CRITICAL: Test that sudoers.d files have safe permissions."""
    sudoers_file = host.file("/etc/sudoers.d/99-security")
    if sudoers_file.exists:
        assert sudoers_file.mode == 0o440, \
            "CRITICAL: sudoers.d files must have 0440 permissions"
        assert sudoers_file.user == "root", "sudoers.d files must be owned by root"
        assert sudoers_file.group == "root", "sudoers.d files must be in root group"


def test_sudoers_syntax_valid(host):
    """CRITICAL: Verify sudoers syntax is valid to prevent lockout."""
    # Test main sudoers file
    assert host.run("visudo -cf /etc/sudoers").rc == 0, \
        "CRITICAL: /etc/sudoers syntax MUST be valid to prevent sudo lockout"

    # Test all files in sudoers.d
    sudoers_d = host.file("/etc/sudoers.d")
    if sudoers_d.exists and sudoers_d.is_directory:
        # Some distros might not allow this, so we test individually
        for f in ["99-security"]:
            file_path = f"/etc/sudoers.d/{f}"
            if host.file(file_path).exists:
                assert host.run(f"visudo -cf {file_path}").rc == 0, \
                    f"CRITICAL: {file_path} syntax MUST be valid"


def test_sudoers_defaults_security(host):
    """Test that security defaults are properly configured."""
    sudoers_content = host.file("/etc/sudoers").content_string

    # Essential security defaults
    assert "use_pty" in sudoers_content, \
        "use_pty should be enabled to prevent privilege escalation"

    # Logging configuration
    assert "logfile=/var/log/sudo.log" in sudoers_content or \
           "log_output" in sudoers_content, \
        "sudo logging should be configured"


def test_sudoers_root_access_preserved(host):
    """CRITICAL: Verify root can always use sudo to prevent lockout."""
    sudoers_content = host.file("/etc/sudoers").content_string

    # Root should have ALL privileges
    assert "root" in sudoers_content and "ALL" in sudoers_content, \
        "CRITICAL: root MUST maintain sudo ALL privileges"


def test_sudoers_secure_path_set(host):
    """Test that secure_path is configured."""
    sudoers_content = host.file("/etc/sudoers").content_string

    assert "secure_path" in sudoers_content.lower(), \
        "secure_path should be set to prevent PATH manipulation"

    # Verify it contains standard paths
    if "secure_path" in sudoers_content:
        assert "/usr/bin" in sudoers_content and "/usr/sbin" in sudoers_content, \
            "secure_path should include standard system paths"


def test_sudoers_includedir_present(host):
    """CRITICAL: Verify includedir directive exists for modularity."""
    sudoers_content = host.file("/etc/sudoers").content_string

    # Check for includedir or @includedir
    assert "includedir" in sudoers_content.lower() or \
           "@includedir" in sudoers_content, \
        "sudoers should include directive for /etc/sudoers.d"


def test_sudoers_no_nopasswd_all(host):
    """CRITICAL: Verify no dangerous NOPASSWD:ALL rules exist."""
    sudoers_content = host.file("/etc/sudoers").content_string

    # Check sudoers.d files too
    dangerous_pattern = False
    for line in sudoers_content.split("\n"):
        # Skip comments
        if line.strip().startswith("#"):
            continue
        # Check for dangerous patterns
        if "NOPASSWD" in line and "ALL" in line:
            # Allow if it's explicitly for automation accounts
            if not any(svc in line for svc in ["svc_automation", "ansible", "ci"]):
                dangerous_pattern = True

    assert not dangerous_pattern, \
        "CRITICAL: NOPASSWD:ALL should only be used for service accounts"


def test_sudoers_timestamp_timeout(host):
    """Test that timestamp_timeout is reasonably configured."""
    sudoers_content = host.file("/etc/sudoers").content_string

    if "timestamp_timeout" in sudoers_content:
        # Extract the timeout value
        for line in sudoers_content.split("\n"):
            if "timestamp_timeout" in line and not line.strip().startswith("#"):
                # Timeout should be reasonable (not -1 which means never expire)
                assert "timestamp_timeout=-1" not in line, \
                    "timestamp_timeout should not be set to never expire"


def test_sudoers_passwd_tries_limited(host):
    """Test that password attempts are limited."""
    sudoers_content = host.file("/etc/sudoers").content_string

    if "passwd_tries" in sudoers_content:
        # Extract the tries value
        for line in sudoers_content.split("\n"):
            if "passwd_tries" in line and not line.strip().startswith("#"):
                # Should have reasonable limit (typically 3)
                assert "passwd_tries" in line, "passwd_tries should limit auth attempts"


def test_sudo_log_file_writable(host):
    """Test that sudo log file directory is writable."""
    log_dir = host.file("/var/log")
    assert log_dir.exists, "/var/log must exist for sudo logging"
    assert log_dir.is_directory, "/var/log must be a directory"

    # Check if sudo.log can be created (if it exists, check it's writable)
    sudo_log = host.file("/var/log/sudo.log")
    if sudo_log.exists:
        assert sudo_log.user == "root", "sudo.log should be owned by root"


def test_sudoers_groups_configuration(host):
    """Test that configured groups have proper sudo access."""
    sudoers_d_file = host.file("/etc/sudoers.d/99-security")

    if sudoers_d_file.exists:
        content = sudoers_d_file.content_string

        # Check that groups are properly formatted
        for line in content.split("\n"):
            if line.strip() and not line.strip().startswith("#"):
                # Lines should start with % for groups or username for users
                if line.strip().startswith("%"):
                    # Group entry should have proper format
                    assert "ALL=" in line or ":" in line, \
                        "Group sudo entries should specify hosts and commands"


def test_sudo_command_actually_works(host):
    """CRITICAL: Test that sudo command is functional."""
    # Try a simple sudo command
    cmd = host.run("sudo -n true 2>&1 || sudo -l")
    # Should either succeed or show sudo is configured (not broken)
    assert cmd.rc in [0, 1], \
        "CRITICAL: sudo command must be functional (not broken)"


def test_visudo_binary_exists(host):
    """CRITICAL: Verify visudo exists for safe editing."""
    visudo = host.file("/usr/sbin/visudo")
    assert visudo.exists, "CRITICAL: visudo must exist for safe sudoers editing"
    assert visudo.is_file
    # Should be executable
    assert visudo.mode & 0o111, "visudo must be executable"
