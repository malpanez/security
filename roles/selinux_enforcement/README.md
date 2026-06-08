# selinux_enforcement

Manages SELinux enforcement mode, booleans, and file contexts on RHEL-family systems. Designed for a safe, graduated rollout: start in `permissive` mode to monitor denials, validate application behaviour, then switch to `enforcing` once the policy is confirmed clean.

Skips gracefully on non-RHEL systems where SELinux is not available.

## Platform Support

| OS Family | Notes |
|-----------|-------|
| RHEL / Rocky / Alma | Primary target; SELinux is built in |
| CentOS Stream | Supported |
| Debian / Ubuntu / SUSE | Role skips silently (`selinux_enforcement_enabled: false` by default) |

## What It Configures

| Area | Detail |
|------|--------|
| SELinux mode | `enforcing`, `permissive`, or `disabled` in `/etc/selinux/config` |
| Runtime mode | Applied immediately without reboot via `setenforce` |
| Booleans | Named booleans set persistently (`setsebool -P`) |
| File contexts | Custom file context mappings with optional `restorecon` |
| Packages | `policycoreutils`, `policycoreutils-python-utils`, `setools-console` |

## Safe Rollout Procedure

1. Start with `selinux_enforcement_mode: permissive` and monitor `/var/log/audit/audit.log` for AVC denials for at least 48 hours.
2. Use `audit2allow` to identify required policy adjustments.
3. Resolve all AVC denials (add booleans, fix contexts, or write policy modules).
4. Switch to `selinux_enforcement_mode: enforcing` only after validation.

## Role Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `security_mode` | `review` | Set to `enforce` to apply changes |
| `selinux_enforcement_enabled` | `false` | Enable SELinux configuration (required gate) |
| `selinux_enforcement_mode` | `permissive` | SELinux mode: `enforcing`, `permissive`, or `disabled` |
| `selinux_enforcement_force_enforcing` | `false` | Skip denial validation before enforcing (not recommended) |
| `selinux_enforcement_monitoring_period_hours` | `48` | Recommended monitoring period before enforcing |
| `selinux_enforcement_check_denials` | `true` | Fail if AVC denials detected when moving to enforcing |
| `selinux_enforcement_booleans` | `[]` | SELinux booleans to set (format: `name=value`) |
| `selinux_enforcement_contexts` | `[]` | File contexts to apply (list of dicts with path and context) |
| `selinux_enforcement_packages` | See below | SELinux management packages to install |
| `selinux_enforcement_restorecon` | `true` | Run `restorecon` after applying file contexts |

Default packages:

```yaml
selinux_enforcement_packages:
  - policycoreutils
  - policycoreutils-python-utils
  - setools-console
```

## Dependencies

None.

## Example Playbook

```yaml
# Phase 1: permissive mode — monitor denials
- hosts: rhel_servers
  vars:
    security_mode: enforce
    selinux_enforcement_enabled: true
    selinux_enforcement_mode: permissive
  roles:
    - role: malpanez.security.selinux_enforcement

# Phase 2: enforcing mode — after validation
- hosts: rhel_servers
  vars:
    security_mode: enforce
    selinux_enforcement_enabled: true
    selinux_enforcement_mode: enforcing
    selinux_enforcement_booleans:
      - httpd_can_network_connect=on
      - httpd_use_nfs=off
    selinux_enforcement_contexts:
      - path: /srv/myapp
        setype: httpd_sys_content_t
  roles:
    - role: malpanez.security.selinux_enforcement
```

## Compliance Mapping

| Control | Framework |
|---------|-----------|
| Mandatory access control | CIS RHEL 1.6, NIST 800-53 AC-3(3) |
| SELinux enforcing mode | DISA STIG RHEL-09-431010, CIS RHEL 9 1.6.1 |
| File context integrity | NIST 800-53 SC-3, SI-7 |
| Boolean least-privilege | NIST 800-53 AC-6, NIS2 Art.21(2)(j) |

## License

Apache-2.0

## Author

Miguel Alpañez
