import os
import pytest
import testinfra.utils.ansible_runner


testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ["MOLECULE_INVENTORY_FILE"]
).get_hosts("all")


def _in_container(host):
    res = host.run("systemd-detect-virt --container")
    return res.rc == 0


def test_auditd_service_running(host):
    # The kernel audit subsystem is unavailable inside a container, so auditd
    # cannot run there. Assert the real service state only on full hosts.
    if _in_container(host):
        pytest.skip("auditd cannot run without the kernel audit subsystem (container)")
    service = host.service("auditd")
    assert service.is_running
    assert service.is_enabled


def test_audit_rules_file(host):
    rules = host.file("/etc/audit/rules.d/99-security.rules")
    assert rules.exists
    assert rules.user == "root"
    assert rules.group == "root"
    assert rules.mode == 0o640
    assert rules.size > 0

    content = rules.content_string
    # Header proving this is the role-managed file.
    assert "Managed by malpanez.security.audit_logging" in content

    # Syscall rules are written unconditionally (the role never filters them),
    # so they are always present regardless of which watch paths exist.
    assert "-a always,exit -F arch=b64 -S execve -k exec" in content

    # The role builds audit_logging_effective_rules by stat-ing each watch
    # target and dropping the `-w` rule when the path is absent (see
    # tasks/common.yml). Minimal container images may lack /etc/ssh/sshd_config
    # or /etc/pam.d/sshd, so those watches are legitimately filtered out. Assert
    # only watch rules whose targets are guaranteed to exist on every image,
    # and assert the optional ones only when their target is actually present.
    # /etc/sudoers ships on every image (ubuntu/debian/rocky) and is in the
    # converge rule set, so its watch is always written.
    assert "-w /etc/sudoers -p wa -k sudoers" in content

    watch_rules = {
        "/etc/ssh/sshd_config": "-w /etc/ssh/sshd_config -p wa -k sshd_config",
        "/etc/pam.d/sshd": "-w /etc/pam.d/sshd -p wa -k pam_sshd",
        "/etc/pam.d/sudo": "-w /etc/pam.d/sudo -p wa -k pam_sudo",
        "/etc/pam.d/mfa-totp": "-w /etc/pam.d/mfa-totp -p wa -k pam_mfa_substack",
    }
    for target, rule in watch_rules.items():
        if host.file(target).exists:
            assert rule in content, f"watch rule for existing path missing: {rule}"


def test_audit_rules_loaded(host):
    """Ensure audit rules are loaded by the kernel."""
    if _in_container(host):
        pytest.skip("augenrules --load cannot load rules without the kernel audit subsystem (container)")
    cmd = host.run("auditctl -l")
    assert cmd.rc == 0
    output = cmd.stdout
    assert "-w /etc/ssh/sshd_config -p wa -k sshd_config" in output
    assert "-w /etc/sudoers -p wa -k sudoers" in output
    assert "-w /etc/pam.d/sshd -p wa -k pam_sshd" in output
    assert "-w /etc/pam.d/sudo -p wa -k pam_sudo" in output
    mfa_substack = host.file("/etc/pam.d/mfa-totp")
    if mfa_substack.exists:
        assert "-w /etc/pam.d/mfa-totp -p wa -k pam_mfa_substack" in output
    assert "-a always,exit -F arch=b64 -S execve -k exec" in output
