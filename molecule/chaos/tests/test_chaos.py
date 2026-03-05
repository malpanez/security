import testinfra.utils.ansible_runner


testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    ".molecule/ansible_inventory.yml"
).get_hosts("all")


def test_sshd_config_valid(host):
    cmd = host.run("sshd -t")
    assert cmd.rc == 0


def test_sudoers_config_valid(host):
    cmd = host.run("visudo -cf /etc/sudoers")
    assert cmd.rc == 0
