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
    # target and dropping the `-w` rule when the path is absent at converge time
    # (see tasks/common.yml). Which `-w` rules survive therefore depends on the
    # image and on the converge's rule set, so we do not assert specific watch
    # rules here — only that the file is the role-managed one with syscall rules.
    # The watch-rule deployment is covered on real hosts where the paths exist.


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
