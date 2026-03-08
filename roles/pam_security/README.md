# pam_security

Hardens PAM configuration: password quality (`pwquality`), account lockout (`faillock`), login policy (`login.defs`), access control (`access.conf`), and resource limits (`limits.conf`).

Supports **review** mode (read-only posture report) and **enforce** mode (applies changes).

## Platform Support

| OS Family | Tested On | faillock.conf | pwquality |
|-----------|-----------|---------------|-----------|
| Debian    | Ubuntu 22.04, Debian 12 | Yes (libpam-faillock) | libpwquality-tools |
| RedHat    | RHEL 8/9, Rocky 9, Alma 9 | Yes (authselect) | libpwquality |
| Suse      | SLE 15.3+, openSUSE Leap 15 | Yes (15.3+) | libpwquality1 |

## Files Managed

| File | Purpose | Compliance |
|------|---------|------------|
| `/etc/security/pwquality.conf` | Password complexity rules | CIS 5.4, PCI-DSS 8.3 |
| `/etc/security/faillock.conf` | Account lockout policy | CIS 5.4, HIPAA §164.312(d) |
| `/etc/login.defs` | Password ageing, hash algorithm | CIS 5.4 |
| `/etc/security/access.conf` | Login access control | NIS2 Art.21 |
| `/etc/security/limits.d/99-pam-security.conf` | Resource limits (core dumps) | CIS 1.6 |

## Modes

| Mode | Behaviour |
|------|-----------|
| `review` (default) | Reads current config, reports gaps via `ansible.builtin.debug` |
| `enforce` | Deploys templates and sets `login.defs` values |

## Key Variables

```yaml
# Gate variables (both must be true to enforce)
security_mode: enforce          # Set to 'enforce' to apply changes
pam_security_enabled: true      # Role-level kill switch

# Password quality (pwquality.conf)
pam_security_pwquality_minlen: 14         # Minimum length (CIS: 14, PCI-DSS: 12)
pam_security_pwquality_dcredit: -1        # Require ≥1 digit
pam_security_pwquality_ucredit: -1        # Require ≥1 uppercase
pam_security_pwquality_lcredit: -1        # Require ≥1 lowercase
pam_security_pwquality_ocredit: -1        # Require ≥1 special char
pam_security_pwquality_maxrepeat: 3       # Max consecutive identical chars
pam_security_pwquality_difok: 8           # Chars that must differ from old password

# Account lockout (faillock.conf)
pam_security_faillock_deny: 5             # Lock after N failures (CIS: 5, PCI-DSS: 6)
pam_security_faillock_fail_interval: 900  # Failure window (seconds)
pam_security_faillock_unlock_time: 900    # Lockout duration (0 = permanent)

# Password ageing (login.defs)
pam_security_logindefs_pass_max_days: 90  # Max password age (PCI-DSS: 90)
pam_security_logindefs_pass_min_days: 1   # Min days before change
pam_security_logindefs_pass_warn_age: 14  # Warning before expiry

# Access control (access.conf)
pam_security_access_enabled: false        # Deploy access.conf (careful: can lock you out)
pam_security_access_rules: []            # List of +/- allow/deny rules

# Resource limits
pam_security_limits_enabled: true         # Deploy limits drop-in
pam_security_limits_rules:
  - domain: "*"
    type: hard
    item: core
    value: 0                              # Disable core dumps
```

## Quick Start

```yaml
# Review mode — safe, read-only
- hosts: all
  roles:
    - role: malpanez.security.pam_security

# Enforce mode — applies hardening
- hosts: all
  vars:
    security_mode: enforce
    pam_security_enabled: true
  roles:
    - role: malpanez.security.pam_security
```

## Testing with Molecule

```bash
cd roles/pam_security
molecule test
```

Tests verify: pwquality.conf content, faillock.conf lockout values, login.defs PASS_MAX_DAYS and ENCRYPT_METHOD, limits.d core dump rule.

## Compliance Mapping

| Control | Framework | Variable |
|---------|-----------|----------|
| Password complexity | CIS 5.4.1, PCI-DSS 8.3.6 | `pam_security_pwquality_*` |
| Account lockout | CIS 5.4.2, HIPAA §164.312(d) | `pam_security_faillock_*` |
| Password ageing | CIS 5.4.1.1, PCI-DSS 8.3.9 | `pam_security_logindefs_*` |
| Core dump disabled | CIS 1.6.1, STIG | `pam_security_limits_rules` |
| Login access control | NIS2 Art.21, ISO 27001 A.9 | `pam_security_access_rules` |

## License

Apache-2.0
