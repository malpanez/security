# Examples - malpanez.security Collection

This directory contains comprehensive examples for using the malpanez.security Ansible collection in various scenarios.

## Directory Structure

```
examples/
├── README.md                          # This file
├── inventory/                         # Example inventory structure
│   ├── hosts.yml                     # Multi-environment inventory
│   ├── group_vars/
│   │   ├── all.yml                   # Global variables
│   │   ├── production.yml            # Production settings
│   │   ├── staging.yml               # Staging settings
│   │   └── new_servers.yml           # New server settings
│   └── host_vars/                    # Host-specific overrides
├── playbooks/                         # Example playbooks
│   ├── 01-initial-audit.yml          # Step 1: Audit current state
│   ├── 02-staging-validation.yml     # Step 2: Test in staging
│   ├── 03-production-phase1.yml      # Step 3: Production Phase 1
│   └── quick-start.yml               # Quick start example
└── scenarios/                         # Real-world scenarios
    ├── multi-ssh-instances.yml       # Multiple SSH on different ports
    ├── pci-dss-compliance.yml        # PCI-DSS specific setup
    └── legacy-migration.yml          # Migrating legacy systems
```

## Quick Start

### 1. Copy Example Inventory

```bash
# Copy example inventory to your project
cp -r examples/inventory/ /path/to/your/project/

# Edit for your environment
vi inventory/hosts.yml
vi inventory/group_vars/all.yml
```

### 2. Run Initial Audit

```bash
# Audit current state (NO changes)
ansible-playbook -i inventory/hosts.yml playbooks/audit-only.yml

# Review results
ls -la /tmp/security-review/
```

### 3. Test in Staging

```bash
# Deploy to staging first
ansible-playbook -i inventory/hosts.yml playbooks/enforce-staging.yml \
  --limit staging
```

### 4. Progressive Production Rollout

```bash
# Week 3-4: Phase 1 (SSH hardening)
ansible-playbook -i inventory/hosts.yml playbooks/enforce-production-gradual.yml \
  --limit production \
  -e "current_security_phase=1"

# Week 5-6: Phase 2 (Add sudoers)
ansible-playbook -i inventory/hosts.yml playbooks/enforce-production-gradual.yml \
  --limit production \
  -e "current_security_phase=2"

# Continue with phases 3-6...
```

## Example Inventory Explained

### Environment Structure

The example inventory demonstrates a typical enterprise setup:

#### Production Environment
- **prod_web**: Web servers (2 hosts)
- **prod_db**: Database servers (1 host with additional service accounts)
- **prod_app**: Application servers (2 hosts)

#### Other Environments
- **staging**: Full testing environment (3 hosts)
- **new_servers**: Newly provisioned servers (2 hosts)
- **dmz**: External-facing servers (2 hosts)
- **transfer_servers**: SFTP/rsync servers (2 hosts)

#### Compliance Groups
- **pci_scope**: PCI-DSS regulated systems
- **hipaa_systems**: HIPAA-covered systems

#### OS-Based Groups
- **rhel_based**: RHEL 7, 8, 9
- **debian_based**: Ubuntu 18.04, 20.04, 22.04

### Variable Hierarchy

Variables are applied in this order (later overrides earlier):

1. **all.yml** - Global defaults for all hosts
2. **group_vars/{environment}.yml** - Environment-specific
3. **host_vars/{hostname}.yml** - Host-specific overrides

Example:
```yaml
# all.yml
sshd_hardening_port: 22

# group_vars/dmz.yml
sshd_hardening_port: 2222  # Override for DMZ

# host_vars/bastion01.dmz.example.com.yml
sshd_hardening_port: 8022  # Override for specific host
```

## Common Scenarios

### Scenario 1: New Infrastructure (Aggressive)

For newly provisioned servers with no legacy constraints:

```bash
ansible-playbook playbooks/enforce-new-servers.yml \
  -i inventory/hosts.yml \
  --limit new_servers
```

**What it does:**
- Applies all 6 phases immediately
- Modular sudoers from start
- MFA enabled by default
- SELinux enforcing
- Full audit logging

### Scenario 2: Existing Production (Conservative)

For existing production systems:

```bash
# Phase 1: SSH hardening only
ansible-playbook playbooks/enforce-production-gradual.yml \
  -i inventory/hosts.yml \
  --limit production \
  -e "current_security_phase=1" \
  -e "rollout_percentage=10%"
```

**What it does:**
- 10% of servers at a time
- Only SSH hardening (Phase 1)
- Maintains existing sudoers
- No MFA yet
- Automatic rollback on failure

### Scenario 3: Compliance-Driven (PCI-DSS)

For PCI-DSS compliance:

```bash
ansible-playbook examples/scenarios/pci-dss-compliance.yml \
  -i inventory/hosts.yml \
  --limit pci_scope
```

**What it does:**
- Strict SSH hardening
- Mandatory MFA
- SELinux enforcing
- Comprehensive audit logging
- Evidence collection for auditors

### Scenario 4: Multi-SSH Instances

For servers with multiple SSH instances (different ports):

```bash
ansible-playbook examples/scenarios/multi-ssh-instances.yml \
  -i inventory/hosts.yml \
  --limit transfer_servers
```

**What it does:**
- SSH on port 22 (admin access with MFA)
- SSH on port 2222 (SFTP only, no MFA for service accounts)
- SSH on port 8443 (DMZ, ultra-restrictive)

## Customization Guide

### Adding Your Service Accounts

Edit `inventory/group_vars/all.yml`:

```yaml
pam_mfa_service_accounts:
  # Standard accounts
  - ansible
  - monitoring
  - backup

  # ADD YOUR ACCOUNTS HERE
  - your_app_service
  - your_ci_service
  - your_backup_tool
```

### Defining Custom Sudo Groups

Edit `inventory/group_vars/production.yml`:

```yaml
sudoers_baseline_groups:
  # Your custom group
  database_admins:
    require_password: true
    commands:
      - "/usr/bin/systemctl restart postgresql"
      - "/usr/bin/systemctl restart mysql"
      - "/usr/bin/pg_dump *"
```

### Customizing SSH Settings Per Host

Create `inventory/host_vars/bastion01.dmz.example.com.yml`:

```yaml
# Bastion host needs different port
sshd_hardening_port: 2222

# More lenient for external access
sshd_hardening_max_auth_tries: 6

# Specific allowed users
sshd_hardening_allowed_users:
  - admin
  - ops
```

## Phase-by-Phase Deployment

### Phase 0: Discovery (Week 1-2)

**Goal:** Understand current state

```bash
ansible-playbook playbooks/audit-only.yml \
  -i inventory/hosts.yml
```

**Checklist:**
- [ ] Audit ran successfully
- [ ] Reviewed `/tmp/security-review/` outputs
- [ ] Identified all service accounts
- [ ] Documented current configurations
- [ ] Identified compliance gaps

### Phase 1: SSH Hardening (Week 3-4)

**Goal:** Disable password authentication, use keys only

```bash
ansible-playbook playbooks/enforce-production-gradual.yml \
  -i inventory/hosts.yml \
  --limit production \
  -e "current_security_phase=1"
```

**Checklist:**
- [ ] All users have SSH keys configured
- [ ] Tested in staging first
- [ ] 10% rollout in production
- [ ] Validated SSH access after each batch
- [ ] Monitored for 1 week

### Phase 2: Sudoers (Week 5-6)

**Goal:** Modular sudoers management

```bash
ansible-playbook playbooks/enforce-production-gradual.yml \
  -i inventory/hosts.yml \
  --limit production \
  -e "current_security_phase=2"
```

**Checklist:**
- [ ] Phase 1 stable for 1 week
- [ ] Tested in staging
- [ ] Main `/etc/sudoers` preserved
- [ ] New rules in `/etc/sudoers.d/`
- [ ] Sudo still works

### Phase 3: MFA (Week 7-10) - MOST CRITICAL

**Goal:** Multi-factor authentication

```bash
ansible-playbook playbooks/enforce-production-gradual.yml \
  -i inventory/hosts.yml \
  --limit production \
  -e "current_security_phase=3"
```

**Checklist:**
- [ ] Phase 2 stable for 1 week
- [ ] ALL service accounts in bypass list
- [ ] Users have YubiKeys/TOTP configured
- [ ] Emergency console access verified
- [ ] Tested extensively in staging
- [ ] On-call engineer available
- [ ] Change control approved

### Phase 4: SELinux (Week 11-12)

**Goal:** Enable SELinux enforcing

```bash
# Week 1: Permissive
ansible-playbook playbooks/enforce-production-gradual.yml \
  -i inventory/hosts.yml \
  --limit production \
  -e "current_security_phase=4"

# Week 2: Enforcing (after validation)
ansible-playbook playbooks/enforce-production-gradual.yml \
  -i inventory/hosts.yml \
  --limit production \
  -e "current_security_phase=4" \
  -e "selinux_enforcement_production_ready=true"
```

**Checklist:**
- [ ] Phase 3 stable for 2 weeks
- [ ] Ran permissive for 1 week
- [ ] No critical denials
- [ ] Applications still functional
- [ ] Policies tuned if needed

### Phase 5: Audit (Week 13-14)

**Goal:** Comprehensive logging

```bash
ansible-playbook playbooks/enforce-production-gradual.yml \
  -i inventory/hosts.yml \
  --limit production \
  -e "current_security_phase=5"
```

**Checklist:**
- [ ] All phases stable
- [ ] Disk space monitored
- [ ] Log rotation configured
- [ ] Logs being collected centrally

### Phase 6: Full Enforcement (Week 15+)

**Goal:** All features active

```bash
ansible-playbook playbooks/enforce-production-gradual.yml \
  -i inventory/hosts.yml \
  --limit production \
  -e "current_security_phase=6"
```

**Checklist:**
- [ ] All phases individually stable
- [ ] Continuous monitoring active
- [ ] Compliance evidence collected
- [ ] Runbooks updated

## Testing Your Customizations

### 1. Syntax Check

```bash
ansible-playbook playbooks/your-playbook.yml --syntax-check
```

### 2. Dry-Run

```bash
ansible-playbook playbooks/your-playbook.yml \
  -i inventory/hosts.yml \
  --check --diff \
  --limit staging
```

### 3. Staging Deployment

```bash
ansible-playbook playbooks/your-playbook.yml \
  -i inventory/hosts.yml \
  --limit staging
```

### 4. Validate Results

```bash
# Check SSH
ssh -i ~/.ssh/id_rsa user@staging_host

# Check sudo
ssh staging_host sudo -l

# Check services
ansible staging -i inventory/hosts.yml -m shell -a "systemctl status sshd"
```

## Troubleshooting

### Can't Connect After SSH Hardening

**Cause:** Password authentication disabled, SSH keys not configured

**Solution:**
1. Use console access
2. Restore from backup:
   ```bash
   bash /root/security-backup-TIMESTAMP/restore.sh
   ```
3. Configure SSH keys for all users
4. Re-run with keys configured

### Sudo Not Working

**Cause:** Syntax error in sudoers

**Solution:**
1. Console access or existing root session
2. Check syntax:
   ```bash
   visudo -cf /etc/sudoers
   visudo -cf /etc/sudoers.d/*
   ```
3. Restore from backup if needed

### Locked Out After MFA

**Cause:** Service account not in bypass list

**Solution:**
1. Use console access
2. Temporarily disable MFA:
   ```bash
   sed -i 's/^auth.*pam_u2f/#&/' /etc/pam.d/sshd
   systemctl restart sshd
   ```
3. Add service account to bypass list
4. Re-enable MFA

## Best Practices

1. **Always test in staging first** - Never skip this step
2. **Always run review mode first** - Know what will change
3. **Keep emergency access open** - Console, recovery USB, etc.
4. **Deploy during maintenance windows** - Don't surprise users
5. **Deploy in small batches** - 10% at a time
6. **Monitor between batches** - Wait 15-30 minutes
7. **Document your changes** - Update runbooks
8. **Train your team** - Ensure everyone knows the new procedures

## Getting Help

- **Documentation**: `docs/` directory in collection
- **Real-world scenarios**: `docs/REAL_WORLD_SCENARIOS.md`
- **Best practices**: `docs/BEST_PRACTICES_IMPROVEMENTS.md`
- **Issues**: https://github.com/malpanez/security/issues

---

**Remember:** This collection can lock you out if misconfigured. Always follow the safety procedures!
