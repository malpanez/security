#!/bin/bash
# Quick single-platform test
# Default: Ubuntu 22.04 (most common)

set -e

PLATFORM=${1:-ubuntu:22.04}
CONTAINER_NAME="security-quick-test"

echo "=========================================="
echo "Quick Security Test"
echo "=========================================="
echo "Platform: ${PLATFORM}"
echo "Container: ${CONTAINER_NAME}"
echo ""

# Cleanup any existing
docker rm -f "${CONTAINER_NAME}" 2>/dev/null || true

# Determine init and package manager
if [[ "${PLATFORM}" =~ "ubuntu" ]] || [[ "${PLATFORM}" =~ "debian" ]]; then
    INIT="/lib/systemd/systemd"
    PKG_MGR="apt-get"
else
    INIT="/usr/sbin/init"
    PKG_MGR="dnf"
fi

# Start container
echo "→ Starting ${PLATFORM} container..."
docker run -d \
    --name "${CONTAINER_NAME}" \
    --privileged \
    --volume /sys/fs/cgroup:/sys/fs/cgroup:ro \
    --tmpfs /run \
    --tmpfs /run/lock \
    "${PLATFORM}" \
    ${INIT}

sleep 3

# Install prerequisites
echo "→ Installing prerequisites..."
if [[ "${PKG_MGR}" == "apt-get" ]]; then
    docker exec "${CONTAINER_NAME}" apt-get update -qq
    docker exec "${CONTAINER_NAME}" apt-get install -y -qq python3 sudo openssh-server systemd
else
    docker exec "${CONTAINER_NAME}" ${PKG_MGR} install -y -q python3 sudo openssh-server
fi

# Create inventory
cat > /tmp/quick-test-inventory.yml <<EOF
all:
  hosts:
    test:
      ansible_connection: docker
      ansible_host: ${CONTAINER_NAME}
EOF

echo ""
echo "→ Running tests..."
echo ""

# Test 1: Preflight
echo "1. Preflight check..."
ansible-playbook -i /tmp/quick-test-inventory.yml \
    playbooks/preflight-check.yml || echo "  (Warnings expected in Docker)"

echo ""

# Test 2: Audit
echo "2. Audit-only playbook..."
ansible-playbook -i /tmp/quick-test-inventory.yml \
    playbooks/audit-only.yml

echo ""

# Test 3: Dry-run
echo "3. Dry-run playbook..."
ansible-playbook -i /tmp/quick-test-inventory.yml \
    playbooks/dry-run.yml \
    --check --diff

echo ""

# Test 4: SSH hardening
echo "4. SSH hardening role..."
ansible-playbook -i /tmp/quick-test-inventory.yml \
    playbooks/site.yml \
    --tags sshd_hardening

echo ""

# Verify SSH config
echo "5. Verifying SSH config..."
docker exec "${CONTAINER_NAME}" sshd -t
echo "  ✓ SSH config is valid"

echo ""
echo "=========================================="
echo "✓ All tests passed!"
echo "=========================================="
echo ""
echo "Container is still running: ${CONTAINER_NAME}"
echo ""
echo "To inspect:"
echo "  docker exec -it ${CONTAINER_NAME} /bin/bash"
echo ""
echo "To cleanup:"
echo "  docker rm -f ${CONTAINER_NAME}"
echo ""
