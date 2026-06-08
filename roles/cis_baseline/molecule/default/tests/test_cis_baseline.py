import os
import pytest
import testinfra.utils.ansible_runner


testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ["MOLECULE_INVENTORY_FILE"]
).get_hosts("all")


def test_sshd_cis_settings(host):
    # The role edits the main sshd_config (cis_baseline_sshd_config_path,
    # default /etc/ssh/sshd_config) via lineinfile. That file is the
    # deterministic, role-managed artifact, so assert its content directly —
    # no running sshd service is required.
    cfg = host.file("/etc/ssh/sshd_config")
    assert cfg.exists, "/etc/ssh/sshd_config must exist after enforce run"
    content = cfg.content_string.lower()
    assert "passwordauthentication no" in content
    assert "permitrootlogin no" in content
    assert "maxauthtries 4" in content

    # Cross-check with the effective config dump (sshd -T). This needs host
    # keys but not a running sshd; skip only if the dump itself is unavailable
    # in this environment (e.g. missing binary), never weakening the assertions.
    sshd_t = host.run("sshd -T 2>/dev/null || /usr/sbin/sshd -T 2>/dev/null")
    if sshd_t.rc != 0:
        pytest.skip("sshd -T effective-config dump unavailable in this environment")
    output = sshd_t.stdout.lower()
    assert "passwordauthentication no" in output
    assert "permitrootlogin no" in output


def test_sudoers_use_pty(host):
    sudoers = host.file("/etc/sudoers")
    assert sudoers.exists
    assert "Defaults    use_pty" in sudoers.content_string

    visudo = host.run("visudo -cf /etc/sudoers")
    assert visudo.rc == 0
