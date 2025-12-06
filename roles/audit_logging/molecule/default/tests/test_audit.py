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
    assert "-w /etc/ssh/sshd_config -p wa -k sshd-config" in content
    assert "-w /etc/sudoers -p wa -k sudoers" in content
