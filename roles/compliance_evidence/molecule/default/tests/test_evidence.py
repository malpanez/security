import testinfra.utils.ansible_runner


testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    ".molecule/ansible_inventory.yml"
).get_hosts("all")


def test_evidence_directory_exists(host):
    reports = host.file("/var/log/compliance")
    assert reports.exists
    assert reports.is_directory


def test_sshd_config_collected(host):
    hostname = host.check_output("cat /etc/hostname")
    collected = host.file(f"/var/log/compliance/{hostname}-sshd_config")
    assert collected.exists
    assert collected.size > 0
    assert "Port" in collected.content_string


def test_sudoers_collected(host):
    hostname = host.check_output("cat /etc/hostname")
    sudoers = host.file(f"/var/log/compliance/{hostname}-sudoers")
    assert sudoers.exists
    assert "Defaults" in sudoers.content_string


def test_selinux_status_report(host):
    selinux = host.file("/var/log/compliance/selinux_status.md")
    assert selinux.exists
    assert selinux.size >= 0


def test_sshd_policy_report(host):
    policy = host.file("/var/log/compliance/sshd_effective_policy.md")
    assert policy.exists
    assert "SSHD Effective Policy" in policy.content_string


def test_audit_rules_loaded_report(host):
    hostname = host.check_output("cat /etc/hostname")
    audit = host.file(f"/var/log/compliance/{hostname}-audit_rules_loaded.log")
    assert audit.exists
    assert audit.size >= 0
    if audit.size > 0:
        assert "sshd_config" in audit.content_string


def test_hash_manifest_present(host):
    manifest = host.file("/var/log/compliance/evidence.sha256")
    assert manifest.exists
    assert manifest.size > 0
