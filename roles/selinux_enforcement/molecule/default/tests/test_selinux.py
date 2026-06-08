import os
import pytest
import testinfra.utils.ansible_runner


testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ["MOLECULE_INVENTORY_FILE"]
).get_hosts("all")


def _in_container(host):
    res = host.run("systemd-detect-virt --container")
    return res.rc == 0


def test_selinux_config_enforcing(host):
    # SELinux runtime mode cannot be enforced inside a container (it is governed
    # by the host kernel), so assert the persistent config — the artifact the
    # role actually manages — which is verifiable on any platform.
    config = host.file("/etc/selinux/config")
    if not config.exists:
        pytest.skip("SELinux not present on this platform")
    assert config.contains("^SELINUX=enforcing")


def test_selinux_runtime_enforcing(host):
    if _in_container(host):
        pytest.skip("SELinux runtime mode is not controllable in a container")
    sestatus = host.run("getenforce")
    assert sestatus.rc == 0
    assert sestatus.stdout.strip().lower() == "enforcing"


def test_selinux_boolean_applied(host):
    if _in_container(host):
        pytest.skip("SELinux booleans require a loaded policy (not in containers)")
    boolean = host.run("getsebool nis_enabled")
    assert boolean.rc == 0
    assert "on" in boolean.stdout.lower()


def test_selinux_context_applied(host):
    if _in_container(host):
        pytest.skip("SELinux fcontext requires a loaded policy (not in containers)")
    ctx = host.run("matchpathcon /srv/app/data")
    assert ctx.rc == 0
    assert "public_content_rw_t" in ctx.stdout
