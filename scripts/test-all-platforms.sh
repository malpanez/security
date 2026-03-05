#!/bin/bash
# Test security collection across all supported platforms
# Safe Docker-based testing - no risk to real systems

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test results tracking
PASSED=0
FAILED=0
WARNINGS=0

# Platforms to test
declare -A PLATFORMS=(
    ["ubuntu-2204"]="geerlingguy/docker-ubuntu2204-ansible@sha256:2744f5aca5e33c01a682ff1ea201dc3841b0eaaa1f5c448e6bd9a6156a831638|/lib/systemd/systemd|apt-get"
    ["ubuntu-2004"]="geerlingguy/docker-ubuntu2004-ansible@sha256:532fb09e9f152e9f85ae348befa9ef09a9d0d23ca6c3361714d041f5a998c826|/lib/systemd/systemd|apt-get"
    ["debian-13"]="geerlingguy/docker-debian13-ansible@sha256:afb2e84b6787fb89c687c8df557ebf465cc9ef2302aed4324bc6c7f3c65f07b5|/lib/systemd/systemd|apt-get"
    ["debian-12"]="geerlingguy/docker-debian12-ansible@sha256:f69527a18970386befd62a36f68d5c39422a7ad15e4005133670566dd3b0da7f|/lib/systemd/systemd|apt-get"
    ["debian-11"]="geerlingguy/docker-debian11-ansible@sha256:877c2660bfe9921190f975cc750987c0905300f54bd4879af2697ba12436153b|/lib/systemd/systemd|apt-get"
    ["rocky-9"]="geerlingguy/docker-rockylinux9-ansible@sha256:09c1074489a704687b2b1f3d16a4f537b211b49b64eb7a5b6e4d6d1eae5b8ba9|/usr/sbin/init|dnf"
    ["rocky-8"]="geerlingguy/docker-rockylinux8-ansible@sha256:4ec20ce51385c96a566c4141430ae2254f57c822e9e472abe70123987591f456|/usr/sbin/init|dnf"
    ["ubi-9"]="redhat/ubi9@sha256:2c9bb68a869abf7d7417f6639509ab5eb8500d8429ea11ab59e677be5545162b|/usr/sbin/init|dnf"
    ["ubi-8"]="redhat/ubi8@sha256:ceea2c6434cc16cd796b7fcab26f351c308675bd3256894f7377262f3ed2f277|/usr/sbin/init|dnf"
)

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Security Collection - Platform Testing${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""

# Function to test a platform
test_platform() {
    local platform_name=$1
    local platform_config=$2

    IFS='|' read -r image init pkg_mgr <<< "$platform_config"

    local container_name="security-test-${platform_name}"
    local inventory_file

    echo -e "${YELLOW}Testing: ${platform_name}${NC}"
    echo "  Image: ${image}"
    echo "  Container: ${container_name}"
    echo ""

    # Cleanup any existing container
    docker rm -f "${container_name}" 2>/dev/null || true

    # Start container
    echo "  → Starting container..."
    if ! docker run -d \
        --name "${container_name}" \
        --privileged \
        --volume /sys/fs/cgroup:/sys/fs/cgroup:ro \
        --tmpfs /run \
        --tmpfs /run/lock \
        "${image}" \
        "${init}" >/dev/null 2>&1; then
        echo -e "  ${RED}✗ Failed to start container${NC}"
        FAILED=$((FAILED + 1))
        return 1
    fi

    # Wait for systemd
    sleep 3

    # Install prerequisites
    echo "  → Installing prerequisites..."
    if [[ "${pkg_mgr}" == "apt-get" ]]; then
        docker exec "${container_name}" apt-get update -qq >/dev/null 2>&1
        docker exec "${container_name}" apt-get install -y -qq python3 sudo openssh-server systemd >/dev/null 2>&1
    else
        docker exec "${container_name}" "${pkg_mgr}" install -y -q python3 sudo openssh-server >/dev/null 2>&1
    fi

    # Create test inventory
    inventory_file=$(mktemp -t "test-inventory-${platform_name}.XXXXXX.yml")
    cat > "${inventory_file}" <<EOF
all:
  hosts:
    test:
      ansible_connection: docker
      ansible_host: ${container_name}
EOF

    # Test 1: Preflight check
    echo "  → Running preflight check..."
    if ansible-playbook -i "${inventory_file}" \
        playbooks/preflight-check.yml \
        >/dev/null 2>&1; then
        echo -e "  ${GREEN}✓ Preflight check passed${NC}"
    else
        echo -e "  ${YELLOW}⚠ Preflight check had warnings (expected in Docker)${NC}"
        WARNINGS=$((WARNINGS + 1))
    fi

    # Test 2: Audit-only (review mode)
    echo "  → Running audit-only playbook..."
    if ansible-playbook -i "${inventory_file}" \
        playbooks/audit-only.yml \
        >/dev/null 2>&1; then
        echo -e "  ${GREEN}✓ Audit-only passed${NC}"
    else
        echo -e "  ${RED}✗ Audit-only failed${NC}"
        FAILED=$((FAILED + 1))
        docker rm -f "${container_name}" >/dev/null 2>&1
        rm -f "${inventory_file}"
        return 1
    fi

    # Test 3: Dry-run (check mode)
    echo "  → Running dry-run playbook..."
    if ansible-playbook -i "${inventory_file}" \
        playbooks/dry-run.yml \
        --check --diff \
        >/dev/null 2>&1; then
        echo -e "  ${GREEN}✓ Dry-run passed${NC}"
    else
        echo -e "  ${RED}✗ Dry-run failed${NC}"
        FAILED=$((FAILED + 1))
        docker rm -f "${container_name}" >/dev/null 2>&1
        rm -f "${inventory_file}"
        return 1
    fi

    # Test 4: SSH hardening
    echo "  → Testing SSH hardening role..."
    if ansible-playbook -i "${inventory_file}" \
        playbooks/site.yml \
        --tags sshd_hardening \
        >/dev/null 2>&1; then
        echo -e "  ${GREEN}✓ SSH hardening passed${NC}"
    else
        echo -e "  ${RED}✗ SSH hardening failed${NC}"
        FAILED=$((FAILED + 1))
        docker rm -f "${container_name}" >/dev/null 2>&1
        rm -f "${inventory_file}"
        return 1
    fi

    # Test 5: Verify SSH config
    echo "  → Verifying SSH configuration..."
    if docker exec "${container_name}" sshd -t >/dev/null 2>&1; then
        echo -e "  ${GREEN}✓ SSH config valid${NC}"
    else
        echo -e "  ${RED}✗ SSH config invalid${NC}"
        FAILED=$((FAILED + 1))
        docker rm -f "${container_name}" >/dev/null 2>&1
        rm -f "${inventory_file}"
        return 1
    fi

    # Cleanup
    echo "  → Cleaning up..."
    docker rm -f "${container_name}" >/dev/null 2>&1
    rm -f "${inventory_file}"

    echo -e "  ${GREEN}✓ ${platform_name} - ALL TESTS PASSED${NC}"
    echo ""
    PASSED=$((PASSED + 1))
    return 0
}

# Main execution
echo "Pre-test checks..."
echo "  → Checking Docker..."
if ! docker info >/dev/null 2>&1; then
    echo -e "${RED}✗ Docker not running or not accessible${NC}"
    exit 1
fi
echo -e "  ${GREEN}✓ Docker ready${NC}"

echo "  → Checking Ansible..."
if ! command -v ansible-playbook >/dev/null 2>&1; then
    echo -e "${RED}✗ Ansible not installed${NC}"
    exit 1
fi
echo -e "  ${GREEN}✓ Ansible ready${NC}"
echo ""

# Pull all images first
echo "Pulling Docker images..."
for platform_config in "${PLATFORMS[@]}"; do
    IFS='|' read -r image _ _ <<< "$platform_config"
    echo "  → ${image}"
    docker pull "${image}" >/dev/null 2>&1
done
echo ""

# Test each platform
for platform_name in "${!PLATFORMS[@]}"; do
    test_platform "${platform_name}" "${PLATFORMS[$platform_name]}"
done

# Summary
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Test Summary${NC}"
echo -e "${GREEN}========================================${NC}"
echo -e "Platforms tested: ${#PLATFORMS[@]}"
echo -e "${GREEN}Passed: ${PASSED}${NC}"
echo -e "${RED}Failed: ${FAILED}${NC}"
echo -e "${YELLOW}Warnings: ${WARNINGS}${NC}"
echo ""

if [[ ${FAILED} -eq 0 ]]; then
    echo -e "${GREEN}✓ ALL TESTS PASSED${NC}"
    echo ""
    exit 0
else
    echo -e "${RED}✗ SOME TESTS FAILED${NC}"
    echo ""
    exit 1
fi
