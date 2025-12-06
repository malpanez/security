import testinfra.utils.ansible_runner


testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    ".molecule/ansible_inventory.yml"
).get_hosts("all")


def test_selinux_enforcing(host):
    sestatus = host.run("getenforce")
    assert sestatus.rc == 0
    assert sestatus.stdout.strip().lower() == "enforcing"


def test_selinux_boolean_applied(host):
    boolean = host.run("getsebool nis_enabled")
    assert boolean.rc == 0
    assert "on" in boolean.stdout.lower()


def test_selinux_context_applied(host):
    ctx = host.run("matchpathcon /srv/app/data")
    assert ctx.rc == 0
    assert "public_content_rw_t" in ctx.stdout
