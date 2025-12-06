# Security Policy

## Reporting Security Vulnerabilities

**DO NOT** report security vulnerabilities through public GitHub issues.

### Preferred Method

Please report security vulnerabilities by email to: **security@[DOMAIN]** (replace with actual contact)

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
- **Production mode**: Never modifies main `/etc/sudoers` file

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

- **31+ CRITICAL tests** that prevent lockouts
- **Molecule tests** on all supported platforms
- **Syntax validation** (`sshd -t`, `visudo -cf`)
- **Idempotence testing** (no changes on second run)
- **Service validation** (SSH, sudo, PAM still work)

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

## Hall of Fame

Security researchers who have responsibly disclosed vulnerabilities will be listed here with their permission.

---

**Last Updated**: 2025-12-05
**Contact**: security@[DOMAIN] (replace with actual contact)
