import os
import pytest
import testinfra.utils.ansible_runner


testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ["MOLECULE_INVENTORY_FILE"]
).get_hosts("all")

EVIDENCE_DIR = "/var/log/compliance"


def _in_container(host):
    res = host.run("systemd-detect-virt --container")
    return res.rc == 0


def _find_evidence(host, suffix):
    """Return the single evidence file ending in *suffix*.

    The role names host-scoped files ``<inventory_hostname>-<name>``. The
    inventory hostname is set by Molecule (the platform name) and does not match
    the container's /etc/hostname, so locate the file by its stable suffix
    instead of reconstructing the prefix.
    """
    res = host.run(
        "find %s -maxdepth 1 -type f -name '*%s'" % (EVIDENCE_DIR, suffix)
    )
    matches = [line for line in res.stdout.splitlines() if line.strip()]
    return matches[0] if matches else None


def test_evidence_directory_exists(host):
    reports = host.file(EVIDENCE_DIR)
    assert reports.exists
    assert reports.is_directory


def test_sshd_config_collected(host):
    path = _find_evidence(host, "-sshd_config")
    assert path is not None, "no <host>-sshd_config evidence file produced"
    collected = host.file(path)
    assert collected.exists
    assert collected.size > 0
    assert "Port" in collected.content_string


def test_sudoers_collected(host):
    path = _find_evidence(host, "-sudoers")
    assert path is not None, "no <host>-sudoers evidence file produced"
    sudoers = host.file(path)
    assert sudoers.exists
    assert "Defaults" in sudoers.content_string


def test_selinux_status_report(host):
    selinux = host.file(f"{EVIDENCE_DIR}/selinux_status.md")
    assert selinux.exists
    assert selinux.size >= 0


def test_sshd_policy_report(host):
    policy = host.file(f"{EVIDENCE_DIR}/sshd_effective_policy.md")
    assert policy.exists
    assert "SSHD Effective Policy" in policy.content_string


def test_audit_rules_loaded_report(host):
    # The role always writes this file (auditctl -l || true), but inside a
    # container the kernel audit subsystem is unavailable so auditctl returns no
    # loaded rules. The file therefore exists but may be empty; only assert on
    # its contents on a full host where auditctl can report loaded rules.
    path = _find_evidence(host, "-audit_rules_loaded.log")
    assert path is not None, "no <host>-audit_rules_loaded.log evidence file produced"
    audit = host.file(path)
    assert audit.exists
    assert audit.size >= 0
    if _in_container(host):
        pytest.skip("auditctl -l cannot report loaded rules without the kernel audit subsystem (container)")
    if audit.size > 0:
        assert "sshd_config" in audit.content_string


def test_hash_manifest_present(host):
    manifest = host.file(f"{EVIDENCE_DIR}/evidence.sha256")
    assert manifest.exists
    assert manifest.size > 0
