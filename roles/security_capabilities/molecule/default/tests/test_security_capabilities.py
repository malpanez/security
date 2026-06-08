import os
import re

import testinfra.utils.ansible_runner


testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ["MOLECULE_INVENTORY_FILE"]
).get_hosts("all")


def test_sshd_binary_present(host):
    sshd = host.file("/usr/sbin/sshd")
    assert sshd.exists
    assert sshd.is_file
    assert sshd.mode & 0o111  # executable


def test_openssh_version_detectable(host):
    cmd = host.run("/usr/sbin/sshd -V")
    assert cmd.rc == 0
    # expect OpenSSH_X.Y in stderr (sshd prints version banner on stderr)
    assert re.search(r"OpenSSH_\d+\.\d+", cmd.stderr + cmd.stdout)
