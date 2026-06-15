# audit_logging

Installs and configures `auditd` with a curated ruleset covering SSH configuration, sudoers, PAM chains, identity files, password policy, kernel parameters, AppArmor/SELinux, cron, and time synchronization. All rules are written to a single drop-in file (`/etc/audit/rules.d/99-security.rules`) — existing OS rules are preserved.

## Platform Support

| OS Family | Audit Service | Auth Log |
|-----------|--------------|----------|
| Debian / Ubuntu | `auditd` | `/var/log/auth.log` |
| RHEL / Rocky / Alma | `auditd` | `/var/log/secure` |
| SUSE / openSUSE | `auditd` | `/var/log/messages` |

## What It Audits

| Category | Paths / Syscalls | Key |
|----------|-----------------|-----|
| SSH configuration | `/etc/ssh/sshd_config`, `/etc/ssh/sshd_config.d` | `sshd_config` |
| Sudoers | `/etc/sudoers`, `/etc/sudoers.d` | `sudoers` |
| PAM chains | `/etc/pam.d/sshd`, `/etc/pam.d/sudo`, `/etc/pam.d/common-auth`, `/etc/pam.d/system-auth` | `pam_*` |
| Identity files | `/etc/passwd`, `/etc/group`, `/etc/shadow`, `/etc/gshadow` | `identity` |
| Password policy | `/etc/security/pwquality.conf`, `faillock.conf`, `access.conf`, `limits.conf`, `limits.d`, `/etc/login.defs` | `pwquality`, `faillock`, etc. |
| AppArmor | `/etc/apparmor.d` | `apparmor` |
| Kernel parameters | `/etc/sysctl.conf`, `/etc/sysctl.d`, `/etc/modprobe.d` | `sysctl`, `modprobe` |
| Cron | `/etc/cron.allow`, `/etc/cron.deny`, `/etc/crontab`, `/etc/cron.d` | `cron_*` |
| Time sync | `/etc/chrony.conf`, `/etc/ntp.conf` | `chrony`, `ntp` |
| Process execution | `execve` syscall (b64) | `exec` |

All file rules use `-p wa` (write and attribute) to detect both modifications and permission changes.

## Modes

| Mode | Behaviour |
|------|-----------|
| `review` (default) | Skip; audit rules are not deployed |
| `enforce` | Install `auditd`, deploy rules file, enable and start service |

## Role Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `security_mode` | `review` | Set to `enforce` to apply changes |
| `audit_logging_enabled` | `true` | Enable auditd management |
| `audit_logging_package` | `auditd` | Package to install |
| `audit_logging_service` | `auditd` | Audit daemon service name |
| `audit_logging_rules` | See defaults | List of auditd rule lines (paths filtered if missing) |
| `audit_logging_syscall_rules` | `["-a always,exit -F arch=b64 -S execve -k exec"]` | Syscall audit rules |
| `audit_logging_rules_path` | `/etc/audit/rules.d/99-security.rules` | Destination for the rules file |
| `audit_logging_auth_log` | `/var/log/auth.log` | Auth log path (Debian/Ubuntu) |
| `audit_logging_secure_log` | `/var/log/secure` | Secure log path (RHEL/EL) |
| `audit_logging_verify_rules` | `true` | Verify rules loaded with `auditctl -l` |
| `audit_logging_verify_syscalls` | `true` | Verify syscall rules after load |

Rules referencing paths that do not exist on the target host are automatically filtered out before writing the rules file — this prevents auditd warnings on systems where optional paths (e.g., `/etc/apparmor.d` on RHEL) are absent.

## Dependencies

None.

## Example Playbook

```yaml
# Default ruleset
- hosts: all
  vars:
    security_mode: enforce
    audit_logging_enabled: true
  roles:
    - role: malpanez.security.audit_logging

# Custom additional rules
- hosts: all
  vars:
    security_mode: enforce
    audit_logging_enabled: true
    audit_logging_rules: "{{ audit_logging_rules_default + custom_rules }}"
  vars_files:
    - custom_audit_rules.yml
  roles:
    - role: malpanez.security.audit_logging
```

## Testing with Molecule

```bash
cd roles/audit_logging
molecule test
```

Tests verify: `auditd` installed and running, rules file present, identity rules present, `auditctl -l` shows loaded rules.

## Compliance Mapping

| Control | Framework |
|---------|-----------|
| Audit privileged commands | CIS 4.1.11, NIST 800-53 AU-2, PCI-DSS 10.2.2 |
| Audit identity changes | CIS 4.1.4, NIST 800-53 AC-2(12), STIG |
| Audit authentication events | CIS 4.1.5, PCI-DSS 10.2.4, HIPAA §164.312(b) |
| Audit policy changes | CIS 4.1.6, NIST 800-53 AU-12, NIS2 Art.21(2)(b) |
| Audit file access | CIS 4.1.8, NIST 800-53 AU-9 |
| Time synchronization audit | CIS 4.1.2, PCI-DSS 10.4 |

## License

Apache-2.0

## Author

Miguel Alpañez
