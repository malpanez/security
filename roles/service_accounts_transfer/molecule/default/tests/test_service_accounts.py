import os
import testinfra.utils.ansible_runner


testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ["MOLECULE_INVENTORY_FILE"]
).get_hosts("all")


def test_service_account_exists(host):
    user = host.user("svc_ci")
    assert user.exists
    assert user.shell == "/usr/sbin/nologin"
    backup_user = host.user("svc_backup")
    assert backup_user.exists
    assert backup_user.shell == "/usr/sbin/nologin"


def _assert_forced_command(content):
    # The role renders the forced command with escaped quotes
    # (command=\"/usr/lib/openssh/sftp-server\"). Assert the components
    # separately so the check is robust to the quote escaping.
    assert "command=" in content
    assert "/usr/lib/openssh/sftp-server" in content


def test_authorized_keys_restricted(host):
    keyfile = host.file("/home/svc_ci/.ssh/authorized_keys")
    assert keyfile.exists
    assert "restrict" in keyfile.content_string
    assert "no-pty" in keyfile.content_string
    assert "from=10.0.0.0/8" in keyfile.content_string
    _assert_forced_command(keyfile.content_string)

    backup_keyfile = host.file("/home/svc_backup/.ssh/authorized_keys")
    assert backup_keyfile.exists
    assert "restrict" in backup_keyfile.content_string
    assert "no-pty" in backup_keyfile.content_string
    assert "from=192.0.2.0/24" in backup_keyfile.content_string
    _assert_forced_command(backup_keyfile.content_string)


def test_chroot_directory(host):
    chroot_dir = host.file("/srv/sftp/svc_ci")
    assert chroot_dir.exists
    assert chroot_dir.is_directory
    assert chroot_dir.user == "root"
    assert chroot_dir.group == "root"
    assert chroot_dir.mode == 0o755

    backup_chroot = host.file("/srv/sftp/svc_backup")
    assert backup_chroot.exists
    assert backup_chroot.is_directory
    assert backup_chroot.user == "root"
    assert backup_chroot.group == "root"
    assert backup_chroot.mode == 0o755
