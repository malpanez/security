import re

import testinfra.utils.ansible_runner


testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    ".molecule/ansible_inventory.yml"
).get_hosts("all")


def test_sshd_binary_present(host):
    sshd = host.file("/usr/sbin/sshd")
    assert sshd.exists
    assert sshd.is_file
    assert sshd.mode & 0o111  # executable


def test_openssh_version_detectable(host):
    cmd = host.run("/usr/sbin/sshd -V")
    assert cmd.rc == 0
    # expect OpenSSH_X.Y in stderr
    assert re.search(r"OpenSSH_[0-9]+\\.[0-9]+", cmd.stderr)
