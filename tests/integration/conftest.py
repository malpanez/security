"""
Pytest configuration for integration tests.

Sets up test fixtures for PAM+SSH+sudo integration testing.
"""
import pytest
import testinfra


@pytest.fixture(scope="module")
def test_host(request):
    """
    Provide testinfra host connection.

    Uses docker:// backend for molecule containers.
    """
    # Get container name from environment or use default
    import os
    container_name = os.environ.get('MOLECULE_INSTANCE_NAME', 'instance')

    return testinfra.get_host(f"docker://{container_name}")


@pytest.fixture(scope="module")
def test_user(test_host):
    """
    Create test user for integration tests.

    Returns dict with user credentials and MFA setup.
    """
    username = "testuser_integ"

    # Create user if doesn't exist
    user = test_host.user(username)
    if not user.exists:
        test_host.run(f"useradd -m -s /bin/bash {username}")
        test_host.run(f"echo '{username}:testpass123' | chpasswd")

    return {
        "username": username,
        "password": "testpass123",
        "home": f"/home/{username}",
    }


@pytest.fixture(scope="module")
def service_account(test_host):
    """
    Create service account for bypass testing.

    Returns dict with service account info.
    """
    username = "svc_integration"

    # Create service account if doesn't exist
    user = test_host.user(username)
    if not user.exists:
        test_host.run(f"useradd -m -s /usr/sbin/nologin {username}")

    # Add to mfa-bypass group
    test_host.run(f"usermod -aG mfa-bypass {username}")

    return {
        "username": username,
        "groups": ["mfa-bypass"],
    }


@pytest.fixture(scope="function")
def clean_sudo_timestamp(test_host, test_user):
    """
    Clean sudo timestamp before each test.

    Ensures timestamp_timeout is tested correctly.
    """
    username = test_user["username"]
    test_host.run(f"sudo -K -u {username}")

    yield

    # Cleanup after test
    test_host.run(f"sudo -K -u {username}")


@pytest.fixture(scope="module")
def pam_config_backup(test_host):
    """
    Backup PAM configuration before tests.

    Restores on cleanup to prevent test contamination.
    """
    import time
    backup_suffix = str(int(time.time()))

    # Backup PAM configs
    test_host.run(f"cp /etc/pam.d/sshd /etc/pam.d/sshd.backup-{backup_suffix}")
    test_host.run(f"cp /etc/pam.d/sudo /etc/pam.d/sudo.backup-{backup_suffix}")

    yield backup_suffix

    # Restore backups
    test_host.run(f"cp /etc/pam.d/sshd.backup-{backup_suffix} /etc/pam.d/sshd")
    test_host.run(f"cp /etc/pam.d/sudo.backup-{backup_suffix} /etc/pam.d/sudo")
    test_host.run(f"rm /etc/pam.d/sshd.backup-{backup_suffix}")
    test_host.run(f"rm /etc/pam.d/sudo.backup-{backup_suffix}")


@pytest.fixture(scope="module")
def sshd_running(test_host):
    """
    Ensure sshd is running for SSH tests.

    Starts service if not running.
    """
    service = test_host.service("sshd")

    if not service.is_running:
        test_host.run("systemctl start sshd")

    # Wait for port
    socket = test_host.socket("tcp://0.0.0.0:22")
    assert socket.is_listening, "sshd port 22 not listening"

    yield

    # Ensure still running after tests
    service = test_host.service("sshd")
    if not service.is_running:
        test_host.run("systemctl start sshd")
