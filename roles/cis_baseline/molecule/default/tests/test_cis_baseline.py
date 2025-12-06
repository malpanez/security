import testinfra.utils.ansible_runner


testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    ".molecule/ansible_inventory.yml"
).get_hosts("all")


def test_sshd_cis_settings(host):
    cmd = host.run("/usr/sbin/sshd -T")
    assert cmd.rc == 0
    output = cmd.stdout.lower()
    assert "passwordauthentication no" in output
    assert "permitrootlogin no" in output

    cfg = host.file("/etc/ssh/sshd_config")
    assert cfg.exists
    content = cfg.content_string.lower()
    assert "passwordauthentication no" in content
    assert "permitrootlogin no" in content


def test_sudoers_use_pty(host):
    sudoers = host.file("/etc/sudoers")
    assert sudoers.exists
    assert "Defaults    use_pty" in sudoers.content_string

    visudo = host.run("visudo -cf /etc/sudoers")
    assert visudo.rc == 0
