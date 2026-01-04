import testinfra.utils.ansible_runner


testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    ".molecule/ansible_inventory.yml"
).get_hosts("all")


def test_auditd_service_running(host):
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
    assert "-w /etc/ssh/sshd_config -p wa -k sshd_config" in content
    assert "-w /etc/sudoers -p wa -k sudoers" in content
    assert "-w /etc/pam.d/sshd -p wa -k pam_sshd" in content
    assert "-w /etc/pam.d/sudo -p wa -k pam_sudo" in content


def test_audit_rules_loaded(host):
    """Ensure audit rules are loaded by the kernel."""
    cmd = host.run("auditctl -l")
    assert cmd.rc == 0
    output = cmd.stdout
    assert "-w /etc/ssh/sshd_config -p wa -k sshd_config" in output
    assert "-w /etc/sudoers -p wa -k sudoers" in output
    assert "-w /etc/pam.d/sshd -p wa -k pam_sshd" in output
    assert "-w /etc/pam.d/sudo -p wa -k pam_sudo" in output
