# Docker Testing Guide

**Collection:** malpanez.security
**Purpose:** Test security hardening across all supported platforms safely

---

## Why Docker Testing?

✅ **Safe** - No risk to real systems
✅ **Comprehensive** - Test all 9+ OS versions
✅ **Fast** - Spin up containers in seconds
✅ **Reproducible** - Consistent test environment
✅ **CI/CD Ready** - Automated testing on every commit

---

## Quick Start

### 1. Test Single Platform (Ubuntu 22.04)

```bash
# Start test container
docker run -d \
  --name security-test \
  --privileged \
  --volume /sys/fs/cgroup:/sys/fs/cgroup:ro \
  ubuntu:22.04 \
  /lib/systemd/systemd

# Install prerequisites
docker exec security-test apt-get update
docker exec security-test apt-get install -y python3 sudo openssh-server

# Run preflight check
ansible-playbook -i localhost, \
  playbooks/preflight-check.yml \
  --connection=docker \
  --extra-vars "ansible_host=security-test"

# Run audit (review mode)
ansible-playbook -i localhost, \
  playbooks/audit-only.yml \
  --connection=docker \
  --extra-vars "ansible_host=security-test"

# Cleanup
docker stop security-test
docker rm security-test
```

### 2. Test All Platforms Automatically

```bash
# Use the provided script
./scripts/test-all-platforms.sh
```

---

## Supported Platforms

| Platform | Docker Image | Status |
|----------|--------------|--------|
| **RHEL 9** | redhat/ubi9:latest | ✅ Tested |
| **RHEL 8** | redhat/ubi8:latest | ✅ Tested |
| **Rocky Linux 9** | rockylinux:9 | ✅ Tested |
| **Rocky Linux 8** | rockylinux:8 | ✅ Tested |
| **Ubuntu 22.04** | ubuntu:22.04 | ✅ Tested |
| **Ubuntu 20.04** | ubuntu:20.04 | ✅ Tested |
| **Debian 12** | debian:12 | ✅ Tested |
| **Debian 11** | debian:11 | ✅ Tested |

---

## Test Scenarios

### Scenario 1: New Server Hardening

Test aggressive hardening on fresh systems:

```bash
docker run -d --name new-server --privileged ubuntu:22.04 /lib/systemd/systemd

# Install prerequisites
docker exec new-server apt-get update
docker exec new-server apt-get install -y python3 sudo openssh-server

# Create test inventory
cat > test-inventory.yml <<EOF
all:
  hosts:
    new-server:
      ansible_connection: docker
  vars:
    current_security_phase: 6
    security_mode: enforce
EOF

# Run enforcement
ansible-playbook -i test-inventory.yml playbooks/enforce-new-servers.yml

# Cleanup
docker stop new-server && docker rm new-server
```

### Scenario 2: Existing Production (Conservative)

Test gradual rollout on "existing" systems:

```bash
docker run -d --name prod-server --privileged rockylinux:9 /usr/sbin/init

# Install prerequisites
docker exec prod-server dnf install -y python3 sudo openssh-server

# Simulate existing config
docker exec prod-server bash -c 'echo "PermitRootLogin yes" >> /etc/ssh/sshd_config'

# Create test inventory
cat > test-inventory.yml <<EOF
all:
  hosts:
    prod-server:
      ansible_connection: docker
  vars:
    current_security_phase: 1  # Start conservative
    security_mode: enforce
EOF

# Run gradual enforcement
ansible-playbook -i test-inventory.yml playbooks/enforce-production-gradual.yml

# Cleanup
docker stop prod-server && docker rm prod-server
```

### Scenario 3: Compliance Report Generation

Test automated compliance evidence:

```bash
docker run -d --name compliance-test --privileged ubuntu:22.04 /lib/systemd/systemd

# Setup
docker exec compliance-test apt-get update
docker exec compliance-test apt-get install -y python3 sudo openssh-server

# Run hardening first
ansible-playbook -i localhost, \
  playbooks/site.yml \
  --connection=docker \
  --extra-vars "ansible_host=compliance-test"

# Generate compliance report
ansible-playbook -i localhost, \
  playbooks/generate-compliance-report.yml \
  --connection=docker \
  --extra-vars "ansible_host=compliance-test"

# Check reports
ls -la /tmp/compliance-reports/

# Cleanup
docker stop compliance-test && docker rm compliance-test
```

### Scenario 4: SSH Hardening Only

Test Phase 1 (SSH hardening):

```bash
docker run -d --name ssh-test --privileged debian:12 /lib/systemd/systemd

# Setup
docker exec ssh-test apt-get update
docker exec ssh-test apt-get install -y python3 sudo openssh-server systemd

# Test SSH hardening
ansible-playbook -i localhost, \
  -e '{"ansible_connection": "docker", "ansible_host": "ssh-test"}' \
  --tags sshd_hardening \
  playbooks/site.yml

# Verify SSH config
docker exec ssh-test sshd -t

# Cleanup
docker stop ssh-test && docker rm ssh-test
```

---

## CI/CD Integration

### GitHub Actions

The collection includes comprehensive GitHub Actions workflows:

**`.github/workflows/docker-test.yml`** - Automated platform testing

Runs on every push/PR:
- Tests all 8 supported platforms
- Runs preflight checks
- Tests audit-only mode
- Tests dry-run mode
- Generates compliance reports
- Security scanning with Trivy

View results:
```
https://github.com/YOUR-USERNAME/security/actions
```

### Running CI Tests Locally

```bash
# Install act (GitHub Actions local runner)
brew install act  # macOS
# or
curl https://raw.githubusercontent.com/nektos/act/master/install.sh | sudo bash

# Run Docker tests locally
act -j test-platforms

# Run specific platform
act -j test-platforms --matrix platform:"Ubuntu 22.04"
```

---

## Testing Best Practices

### 1. Always Start with Preflight

```bash
ansible-playbook playbooks/preflight-check.yml ...
```

Validates requirements before deployment.

### 2. Use Review Mode First

```bash
ansible-playbook playbooks/audit-only.yml ...
```

See current state without changes.

### 3. Test with --check --diff

```bash
ansible-playbook playbooks/dry-run.yml --check --diff ...
```

Preview changes before applying.

### 4. Test Rollback

```bash
# After enforcement
docker exec test-container ls -la /root/security-backup-*

# Test restore
docker exec test-container bash /root/security-backup-*/restore.sh
```

### 5. Validate Services

```bash
# Check SSH
docker exec test-container sshd -t

# Check sudoers
docker exec test-container visudo -cf /etc/sudoers

# Check services
docker exec test-container systemctl status sshd
```

---

## Troubleshooting

### Issue: Container Won't Start

**Problem:** `docker run` fails or exits immediately

**Solution:**
```bash
# Ensure privileged mode
docker run -d --privileged ...

# Check logs
docker logs container-name

# Try interactive mode
docker run -it --privileged ubuntu:22.04 /bin/bash
```

### Issue: Systemd Not Working

**Problem:** Services won't start in container

**Solution:**
```bash
# Ensure cgroup mount
--volume /sys/fs/cgroup:/sys/fs/cgroup:ro

# Ensure tmpfs
--tmpfs /run
--tmpfs /run/lock

# Use proper init
ubuntu: /lib/systemd/systemd
rhel: /usr/sbin/init
```

### Issue: SSH Tests Fail in Docker

**Expected:** SSH connections won't work in Docker (no networking)

**Solution:** Test configuration syntax instead:
```bash
docker exec test-container sshd -t  # Syntax check
docker exec test-container cat /etc/ssh/sshd_config  # Manual review
```

### Issue: PAM/MFA Can't Be Tested

**Expected:** YubiKey/FIDO2 requires hardware

**Solution:** Test with `pam_mfa_enabled: false` or verify config files:
```bash
docker exec test-container cat /etc/pam.d/sshd
```

---

## Advanced Testing

### Multi-Container Testing

Test across multiple "hosts":

```bash
# Start multiple containers
for i in {1..3}; do
  docker run -d \
    --name web0$i \
    --privileged \
    ubuntu:22.04 \
    /lib/systemd/systemd
done

# Create inventory
cat > multi-host.yml <<EOF
all:
  children:
    web_servers:
      hosts:
        web01:
          ansible_connection: docker
          ansible_host: web01
        web02:
          ansible_connection: docker
          ansible_host: web02
        web03:
          ansible_connection: docker
          ansible_host: web03
EOF

# Run against all
ansible-playbook -i multi-host.yml playbooks/site.yml

# Cleanup
docker stop web01 web02 web03
docker rm web01 web02 web03
```

### Performance Testing

Test with fact caching and parallelism:

```bash
# ansible.cfg already optimized
time ansible-playbook -i inventory playbooks/site.yml -f 10
```

### Compliance Validation

Test all compliance frameworks:

```bash
ansible-playbook playbooks/generate-compliance-report.yml \
  --extra-vars '{"compliance_frameworks": ["soc2", "pci-dss", "hipaa", "cis"]}'

# Verify reports
ls -la /tmp/compliance-reports/
cat /tmp/compliance-reports/*-compliance-*.json | jq .
```

---

## Continuous Testing Strategy

### Daily Automated Tests

Run in GitHub Actions on schedule:

```yaml
# .github/workflows/docker-test.yml
on:
  schedule:
    - cron: '0 2 * * *'  # 2 AM daily
```

### Pre-Deployment Testing

Before client deployments:

1. ✅ Run full Docker test suite
2. ✅ Generate compliance report
3. ✅ Verify all platforms pass
4. ✅ Review test artifacts

### Post-Deployment Validation

After client deployments:

1. ✅ Compare compliance reports (before/after)
2. ✅ Verify no regressions
3. ✅ Update test scenarios with lessons learned

---

## Test Artifacts

### Locations

- **Preflight reports:** `/tmp/preflight-check/`
- **Compliance reports:** `/tmp/compliance-reports/`
- **Backups:** `/root/security-backup-*/`
- **GitHub Actions artifacts:** Actions > Run > Artifacts

### Retention

- **Local:** Clean up after tests
- **CI/CD:** 7-30 days (configurable)
- **Important results:** Archive separately

---

## Next Steps

1. ✅ **Run local Docker tests** - Validate on your machine
2. ✅ **Push to GitHub** - Trigger automated CI/CD
3. ✅ **Review test results** - Ensure all platforms pass
4. ✅ **Use for client demos** - Safe demonstration environment

---

**Questions?** Open an issue: https://github.com/malpanez/security/issues

**Status:** Ready for comprehensive Docker testing across all platforms
