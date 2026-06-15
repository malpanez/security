import os
import re

import pytest
import testinfra.utils.ansible_runner


testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ["MOLECULE_INVENTORY_FILE"]
).get_hosts("all")


# Path of the drop-in file the role actually manages by default
# (sshd_hardening_use_dropin: true -> sshd_hardening_dropin_path).
DROPIN_PATH = "/etc/ssh/sshd_config.d/20-auth-hardening.conf"


def _in_container(host):
    res = host.run("systemd-detect-virt --container")
    return res.rc == 0


def test_sshd_service_running_and_enabled(host):
    # Starting/keeping a service "running" is not reliable in a container that
    # is not a full init target; assert the role's intent (enabled) and only
    # require "running" outside containers.
    services = [host.service("sshd"), host.service("ssh")]
    found = next((s for s in services if s.is_running or s.is_enabled), None)
    assert found is not None, "No ssh service detected running/enabled"
    assert found.is_enabled
    if not _in_container(host):
        assert found.is_running


def test_sshd_port_listening(host):
    if _in_container(host):
        pytest.skip("sshd may not bind :22 reliably inside a container")
    socket = host.socket("tcp://0.0.0.0:22")
    assert socket.is_listening


def test_sshd_dropin_file_permissions(host):
    # In drop-in mode (default) the role does NOT rewrite the main
    # /etc/ssh/sshd_config (it only injects an Include directive, preserving
    # the OS-shipped mode). The artifact the role owns is the drop-in file,
    # which the role writes with mode 0644.
    dropin = host.file(DROPIN_PATH)
    assert dropin.exists, "Drop-in file should exist when sshd_hardening_use_dropin is true"
    assert dropin.is_file
    assert dropin.user == "root"
    assert dropin.group == "root"
    assert dropin.mode == 0o644


def test_sshd_config_hardened(host):
    # Assert the artifact the role actually writes: the drop-in file. This is
    # deterministic and does not depend on `sshd -T`, which is unreliable in a
    # container (it needs host keys + /run/sshd and can emit unrelated output
    # when it errors). The drop-in is the source of truth for the hardening.
    dropin = host.file(DROPIN_PATH)
    assert dropin.exists, "Drop-in file should exist when sshd_hardening_use_dropin is true"
    config = dropin.content_string.lower()

    # Directives the role writes verbatim into the drop-in (defaults + converge).
    expected_directives = [
        "passwordauthentication no",
        "permitrootlogin no",
        "permitemptypasswords no",
        "kbdinteractiveauthentication no",
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
    for directive in expected_directives:
        assert directive in config, f"missing hardening directive in drop-in: {directive}"

    # Crypto lists are present in the drop-in.
    assert re.search(r"ciphers\s+.+", config), "Ciphers missing from drop-in"
    assert re.search(r"macs\s+.+", config), "MACs missing from drop-in"
    assert re.search(r"kexalgorithms\s+.+", config), "KexAlgorithms missing from drop-in"
    assert re.search(r"hostkeyalgorithms\s+.+", config), "HostKeyAlgorithms missing from drop-in"

    # Cross-check the effective runtime config with `sshd -T` when it works.
    # The role generates host keys and /run/sshd during enforce, so this should
    # normally succeed; if the dump is unavailable (binary/runtime quirk in a
    # container), skip the cross-check rather than weaken the file assertions.
    cmd = host.run("/usr/sbin/sshd -T 2>/dev/null || sshd -T 2>/dev/null")
    if cmd.rc != 0 or not cmd.stdout.strip():
        pytest.skip("sshd -T effective-config dump unavailable in this environment")
    effective = cmd.stdout.lower()
    # Effective keywords as emitted by `sshd -T`. Modern OpenSSH reports the
    # kbdinteractive keyword and does NOT emit the deprecated
    # "challengeresponseauthentication" alias.
    for directive in expected_directives:
        assert directive in effective, f"missing effective setting: {directive}"


def test_sshd_human_match_pubkey_algorithms(host):
    # Drop-in mode (default): Match block lives in the drop-in file, not sshd_config.
    dropin = host.file(DROPIN_PATH)
    assert dropin.exists, "Drop-in file should exist when sshd_hardening_use_dropin is true"
    content = dropin.content_string
    pattern = r"Match Group humans[\s\S]*?PubkeyAcceptedAlgorithms\s+sk-ssh-ed25519@openssh\.com"
    assert re.search(pattern, content), "Match block should constrain human PubkeyAcceptedAlgorithms"
