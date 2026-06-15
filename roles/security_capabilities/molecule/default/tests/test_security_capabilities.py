import os
import re

import pytest
import testinfra.utils.ansible_runner


testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ["MOLECULE_INVENTORY_FILE"]
).get_hosts("all")


SSHD_BIN = "/usr/sbin/sshd"


def _sshd_binary(host):
    """Return the sshd binary present on the host, or None if not installed."""
    for candidate in (SSHD_BIN, "/usr/bin/sshd", "/sbin/sshd"):
        f = host.file(candidate)
        if f.exists and f.is_file:
            return candidate
    return None


def test_sshd_binary_present(host):
    # security_capabilities only DETECTS capabilities; it does not install
    # openssh-server. The molecule prepare step installs it so the detection
    # has something to inspect. If it is still absent, skip rather than fail.
    binary = _sshd_binary(host)
    if binary is None:
        pytest.skip("openssh-server (sshd) not installed on this platform")
    sshd = host.file(binary)
    assert sshd.is_file
    assert sshd.mode & 0o111  # executable


def test_openssh_version_detectable(host):
    binary = _sshd_binary(host)
    if binary is None:
        pytest.skip("openssh-server (sshd) not installed on this platform")
    # `sshd -V` (OpenSSH >= 8.4) prints the version banner to stderr. Some
    # builds return a non-zero rc while still printing it, so check the output
    # rather than the return code.
    cmd = host.run("%s -V", binary)
    combined = cmd.stderr + cmd.stdout
    if not re.search(r"OpenSSH_\d+\.\d+", combined):
        # Fall back to `ssh -V` for older sshd that lacks the -V flag.
        cmd = host.run("ssh -V")
        combined = cmd.stderr + cmd.stdout
    assert re.search(
        r"OpenSSH_\d+\.\d+", combined
    ), f"could not detect OpenSSH version banner: {combined!r}"
