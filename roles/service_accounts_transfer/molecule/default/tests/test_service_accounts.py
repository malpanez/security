import testinfra.utils.ansible_runner


testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    ".molecule/ansible_inventory.yml"
).get_hosts("all")


def test_service_account_exists(host):
    user = host.user("svc_ci")
    assert user.exists
    assert user.shell == "/usr/sbin/nologin"


def test_authorized_keys_restricted(host):
    keyfile = host.file("/home/svc_ci/.ssh/authorized_keys")
    assert keyfile.exists
    assert "restrict" in keyfile.content_string
    assert "no-pty" in keyfile.content_string
    assert "from=10.0.0.0/8" in keyfile.content_string
    assert 'command="/usr/lib/openssh/sftp-server"' in keyfile.content_string


def test_chroot_directory(host):
    chroot_dir = host.file("/srv/sftp/svc_ci")
    assert chroot_dir.exists
    assert chroot_dir.is_directory
    assert chroot_dir.user == "root"
    assert chroot_dir.group == "root"
    assert chroot_dir.mode == 0o755
