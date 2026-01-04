# Security Policy

## Reporting Security Vulnerabilities

**DO NOT** report security vulnerabilities through public GitHub issues.

### Preferred Method

Please report security vulnerabilities by email to: **alpanez.alcalde@gmail.com**

You can also use GitHub Security Advisories:
https://github.com/malpanez/security/security/advisories

Include as much information as possible:

- Type of vulnerability
- Affected components (roles, playbooks, tasks)
- Steps to reproduce
- Potential impact
- Suggested fix (if available)

### Response Timeline

- **Initial response**: Within 48 hours
- **Status update**: Within 7 days
- **Fix timeline**: Depends on severity (see below)

## Severity Levels

### Critical (Fix within 24-48 hours)

- Remote code execution
- Privilege escalation to root
- Authentication bypass
- Admin lockout scenarios

### High (Fix within 7 days)

- Local privilege escalation
- Information disclosure of credentials
- Denial of service affecting security

### Medium (Fix within 30 days)

- Information disclosure (non-sensitive)
- Security misconfiguration
- Missing security headers

### Low (Fix within 90 days)

- Best practice violations
- Documentation issues
- Minor hardening improvements

## Security Considerations

### This Collection Can Lock You Out

**CRITICAL**: This collection modifies security-critical configurations (SSH, PAM, sudo). Improper use can result in:

- Loss of SSH access
- Loss of sudo privileges
- Complete system lockout

### Always Follow These Rules

1. **NEVER skip review mode first**
   ```bash
   ansible-playbook playbooks/audit-only.yml
   ```

2. **ALWAYS keep emergency access open**
   - Keep an active SSH session open during deployment
   - Have console access available
   - Test in staging first

3. **ALWAYS backup before enforcement**
   - All enforcement playbooks create automatic backups
   - Know how to restore: `/root/security-backup-*/restore.sh`

4. **ALWAYS validate service accounts**
   - Ensure automation accounts bypass MFA
   - Test service account access after deployment

### Known Security Considerations

#### PAM MFA Implementation

- **Service account bypass**: Required for automation
- **TOTP backup**: Always enabled to prevent lockout
- **`nullok` option**: Used temporarily during setup
- **Order matters**: Service account bypass MUST come before MFA enforcement

#### SSH Hardening

- **Password authentication**: Disabled by default (requires SSH keys)
- **Root login**: Disabled by default
- **Active sessions**: Not affected by configuration changes

#### Sudoers Baseline

- **Syntax validation**: Always uses `visudo -cf` before applying
- **Root preservation**: Root sudo access always maintained
- **Modo actual**: Solo aplica cambios si `sudoers_baseline_strict=true` y escribe `/etc/sudoers`

#### SELinux Enforcement

- **Initial mode**: Starts in permissive to detect issues
- **Application impact**: Can break applications with incorrect contexts
- **Recovery**: Requires console access if enforcing breaks boot

## Supported Versions

| Version | Supported | Security Updates |
|---------|-----------|------------------|
| 1.x     | ✅ Yes    | Until 2026-12    |
| 0.x     | ❌ No     | Upgrade to 1.x   |

## Security Update Process

1. **Vulnerability disclosed** (privately)
2. **Impact assessed** by maintainers
3. **Fix developed** and tested
4. **Security advisory** published
5. **Patch released** with version bump
6. **Public disclosure** after fix available

## Security Testing

This collection includes:

- Molecule por rol (escenario default)
- Escenario `complete_stack` con 11 plataformas
- Escenario `chaos` básico
- Property tests de plantillas (`tests/property_tests/`)
- Validación de sintaxis (`sshd -t`, `visudo -cf`) en scripts/verifiers

## Security Best Practices

### For Users

1. **Read documentation** before running
2. **Test in staging** before production
3. **Use review mode** first
4. **Follow phase progression** (don't skip phases)
5. **Monitor logs** after deployment
6. **Validate access** before closing sessions

### For Contributors

1. **Never disable security** by default
2. **Validate all inputs** to prevent injection
3. **Add CRITICAL tests** for lockout prevention
4. **Document security implications**
5. **Test on all platforms** before PR
6. **Follow secure coding practices**

## Secure Deployment Checklist

Before deploying to production:

- [ ] Ran `playbooks/audit-only.yml` in production
- [ ] Tested in staging with `playbooks/enforce-staging.yml`
- [ ] Validated staging for 24-48 hours minimum
- [ ] Identified all service accounts (added to bypass list)
- [ ] Have emergency console access credentials
- [ ] Have rollback plan documented
- [ ] Scheduled maintenance window
- [ ] Have on-call engineer available
- [ ] Emergency SSH session open during deployment
- [ ] Validated backup and restore procedure

## Emergency Response

### If You Get Locked Out

1. **Use console access** (cloud console, IPMI, physical access)

2. **Boot into single-user mode** (if console unavailable)

3. **Restore from backup**:
   ```bash
   # Find most recent backup
   ls -lat /root/security-backup-*

   # Run restore script
   bash /root/security-backup-TIMESTAMP/restore.sh
   ```

4. **Manual restoration** (if backup script fails):
   ```bash
   # SSH
   cp /root/security-backup-TIMESTAMP/sshd_config /etc/ssh/sshd_config
   systemctl restart sshd

   # Sudo
   cp /root/security-backup-TIMESTAMP/sudoers /etc/sudoers

   # PAM
   cp /root/security-backup-TIMESTAMP/pam.d-sshd /etc/pam.d/sshd
   systemctl restart sshd
   ```

### If Automation Breaks

1. **Check service account bypass**:
   ```bash
   grep -i "pam_succeed_if.*mfa-bypass" /etc/pam.d/sshd
   ```

2. **Temporarily disable MFA** (emergency only):
   ```bash
   # Comment out MFA lines in /etc/pam.d/sshd
   sed -i 's/^auth.*pam_u2f/#&/' /etc/pam.d/sshd
   systemctl restart sshd
   ```

3. **Restore and retry** with service accounts in bypass list

## Security Hardening Features

This collection implements:

### SSH Hardening
- Strong ciphers only (ChaCha20, AES-GCM)
- Key-based authentication
- No root login
- Failed authentication limiting

### MFA Implementation
- YubiKey/FIDO2 support
- TOTP backup (Google Authenticator)
- Service account bypass
- Graceful fallback

### Sudo Hardening
- PTY requirement (prevents some exploits)
- Command logging
- Timestamp timeout
- Path security

### SELinux
- Enforcing mode (after validation)
- Policy management
- Context correction
- Denial monitoring

### Audit Logging
- SSH login attempts
- Sudo command execution
- Configuration changes
- Failed authentication

## Compliance

This collection helps achieve compliance with:

- **PCI-DSS** v4.0
- **HIPAA** Security Rule
- **SOC 2** Type II
- **FedRAMP** Moderate
- **CIS Benchmarks** Level 1/2
- **NIST 800-53** controls

## Responsible Disclosure

We practice responsible disclosure:

1. Security researchers: Report privately first
2. We acknowledge receipt within 48 hours
3. We develop and test fix
4. We coordinate public disclosure timeline
5. We credit researchers (with permission)

## Dependency Management

### Update Policy

We maintain strict dependency management to ensure security and reproducibility:

- **Python dependencies**: Pinned to exact versions (`==`) in `pyproject.toml`
- **Ansible collections**: Pinned with upper bounds (`>=X,<Y`) in `requirements.yml`
- **Lock files**: `uv.lock` committed to repository for reproducible builds

### Update Schedule

| Type | Frequency | Timeline |
|------|-----------|----------|
| **Security patches** | Immediate | <24h from CVE disclosure |
| **Minor updates** | Monthly | First Monday of month |
| **Major updates** | Quarterly | After testing period |

### Update Process

#### 1. Check for Updates

```bash
# Python dependencies
uv pip list --outdated

# Ansible collections
ansible-galaxy collection list --format=yaml | grep -A2 "version:"
```

#### 2. Security Vulnerability Scan

```bash
# Scan Python dependencies
pip-audit

# Scan Ansible content
ansible-lint --profile=production roles/ playbooks/
```

#### 3. Update Dependencies

**For security updates (immediate)**:
```bash
# Update specific package
uv pip compile --upgrade-package <package>==<version> pyproject.toml -o uv.lock

# Update collection
vim requirements.yml  # Update version constraint
ansible-galaxy collection install -r requirements.yml --upgrade
```

**For regular updates (monthly)**:
```bash
# Update all Python deps
uv pip compile --upgrade pyproject.toml -o uv.lock

# Update all collections
ansible-galaxy collection install -r requirements.yml --upgrade
```

#### 4. Testing Before Merge

**MANDATORY** - All updates must pass:

```bash
# 1. Unit tests
pytest tests/

# 2. Molecule tests (all roles)
molecule test --all

# 3. Ansible-lint
ansible-lint roles/ playbooks/

# 4. Integration tests
pytest tests/integration/

# 5. Validate no_log
python3 scripts/validate-no-log.py
```

#### 5. Update Lock Files

```bash
# Regenerate lock files after updates
uv pip compile pyproject.toml -o uv.lock

# Commit with descriptive message
git add uv.lock requirements.yml
git commit -m "security: Update dependencies (CVE-YYYY-XXXXX)"
```

### Dependency Review

**Before accepting PRs with dependency changes:**

1. ✅ Check for known vulnerabilities
2. ✅ Review changelog for breaking changes
3. ✅ Verify license compatibility
4. ✅ Run full test suite
5. ✅ Update documentation if API changed

### Automated Dependency Updates

We use **Renovate Bot** for automated dependency updates:

- **Schedule**: Weekly on Mondays
- **Auto-merge**: Only patch updates that pass CI
- **Manual review**: Minor/major version bumps

Configuration: [`.github/renovate.json`](.github/renovate.json)

### Version Pinning Rationale

**Why we pin Python deps to exact versions (`==`)**:
- Ensures reproducible builds
- Prevents surprise breakage
- Controlled update process
- Faster CI/CD (no resolution)

**Why we pin Ansible collections with ranges (`>=X,<Y`)**:
- Collections use semantic versioning
- Patch updates are safe
- Major version bumps are breaking
- Balance between security and stability

### Emergency Security Updates

**If a CRITICAL CVE is disclosed:**

1. **Assess impact**: Does it affect our dependencies?
2. **Create hotfix branch**: `git checkout -b hotfix/cve-YYYY-XXXXX`
3. **Update dependency**: Pin to patched version
4. **Fast-track testing**: Priority testing in staging
5. **Merge and deploy**: <24h timeline
6. **Notify users**: Security advisory + release notes

### Dependency Sources

**Trusted sources only:**
- **PyPI**: Python packages (official index)
- **Ansible Galaxy**: Ansible collections (official registry)
- **GitHub Releases**: For direct downloads (with SHA256 verification)

**Forbidden sources:**
- Unverified mirrors
- Direct git dependencies (use releases)
- Packages without source code

---

## Hall of Fame

Security researchers who have responsibly disclosed vulnerabilities will be listed here with their permission.

---

**Last Updated**: 2026-01-04
**Contact**: alpanez.alcalde@gmail.com
