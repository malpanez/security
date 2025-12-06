import testinfra.utils.ansible_runner


testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    ".molecule/ansible_inventory.yml"
).get_hosts("all")


def test_evidence_directory_exists(host):
    reports = host.file("reports")
    assert reports.exists
    assert reports.is_directory


def test_sshd_config_collected(host):
    hostname = host.check_output("cat /etc/hostname")
    collected = host.file(f"reports/{hostname}-sshd_config")
    assert collected.exists
    assert collected.size > 0
    assert "Port" in collected.content_string


def test_sudoers_collected(host):
    hostname = host.check_output("cat /etc/hostname")
    sudoers = host.file(f"reports/{hostname}-sudoers")
    assert sudoers.exists
    assert "Defaults" in sudoers.content_string


def test_selinux_status_report(host):
    selinux = host.file("reports/selinux_status.md")
    assert selinux.exists
    assert selinux.size >= 0


def test_sshd_policy_report(host):
    policy = host.file("reports/sshd_effective_policy.md")
    assert policy.exists
    assert "SSHD Effective Policy" in policy.content_string
