import re

import testinfra.utils.ansible_runner


testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    ".molecule/ansible_inventory.yml"
).get_hosts("all")


def test_sshd_service_running_and_enabled(host):
    services = [host.service("sshd"), host.service("ssh")]
    found = next((s for s in services if s.is_running or s.is_enabled), None)
    assert found is not None, "No ssh service detected running/enabled"
    assert found.is_running
    assert found.is_enabled


def test_sshd_port_listening(host):
    socket = host.socket("tcp://0.0.0.0:22")
    assert socket.is_listening


def test_sshd_config_file_permissions(host):
    cfg = host.file("/etc/ssh/sshd_config")
    assert cfg.exists
    assert cfg.user == "root"
    assert cfg.group == "root"
    assert cfg.mode == 0o600


def test_sshd_config_hardened(host):
    cmd = host.run("/usr/sbin/sshd -T")
    assert cmd.rc == 0
    output = cmd.stdout.lower()
    expected_flags = [
        "passwordauthentication no",
        "permitrootlogin no",
        "permitemptypasswords no",
        "challengeresponseauthentication no",
        "x11forwarding no",
        "clientaliveinterval 300",
        "clientalivecountmax 2",
        "maxauthtries 4",
        "maxsessions 10",
        "maxstartups 10:30:60",
        "usedns no",
        "printmotd no",
        "compression no",
        "loglevel verbose",
    ]
    for flag in expected_flags:
        assert flag in output
    # basic check that crypto lists are present
    assert re.search(r"ciphers\\s+.+", output)
    assert re.search(r"macs\\s+.+", output)
    assert re.search(r"kexalgorithms\\s+.+", output)
    assert re.search(r"hostkeyalgorithms\\s+.+", output)
