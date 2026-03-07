# apparmor

Installs and enables AppArmor (Mandatory Access Control) on Debian, Ubuntu, and SUSE systems. Gracefully skips on RedHat family (use the `selinux_enforcement` role instead).

Supports **review** mode (read-only posture report) and **enforce** mode (enables AppArmor and sets profile modes).

## Platform Behaviour

| OS Family | Behaviour | MAC System |
|-----------|-----------|------------|
| Debian / Ubuntu | Installs apparmor + apparmor-utils, enables service | AppArmor |
| SUSE / openSUSE | Installs apparmor + apparmor-utils, enables service | AppArmor |
| RedHat / Rocky / Alma | Skips (`meta: end_host`) — use `selinux_enforcement` | SELinux |

## Modes

| Mode | Behaviour |
|------|-----------|
| `review` (default) | Runs `aa-status`, reports loaded profiles and deny count |
| `enforce` | Enables AppArmor service, sets profiles to enforce or complain |

## Profile Progression

AppArmor profiles move through two stages:

1. **Complain** (`aa-complain`) — logs violations but does not block; use initially to validate no false positives
2. **Enforce** (`aa-enforce`) — blocks violations; use once complain mode produces no unexpected denials

```
complain → [ validate logs ] → enforce
```

## Key Variables

```yaml
# Gate variables
security_mode: enforce
apparmor_enabled: true

# Profile mode (enforce or complain)
apparmor_profile_mode: enforce    # Default: enforce for all profiles

# Set all loaded profiles to enforce mode
apparmor_enforce_all: true

# Specific profiles to set (empty = all)
apparmor_enforce_profiles: []

# Complain mode profiles (lower-trust services during rollout)
apparmor_complain_profiles: []
```

## Quick Start

```yaml
# Review mode — safe, read-only
- hosts: all
  roles:
    - role: malpanez.security.apparmor

# Enforce mode
- hosts: ubuntu_servers
  vars:
    security_mode: enforce
    apparmor_enabled: true
  roles:
    - role: malpanez.security.apparmor
```

## Integration with site.yml

The `site.yml` playbook applies this role only on supported platforms:

```yaml
- role: apparmor
  when: ansible_os_family in ['Debian', 'Suse']
- role: selinux_enforcement
  when: ansible_os_family == 'RedHat'
```

## Testing with Molecule

```bash
cd roles/apparmor
molecule test
```

Tests verify: `apparmor` and `apparmor-utils` packages installed, AppArmor service enabled, `aa-status` command available.

> **Container note**: AppArmor kernel support is reported but not asserted in containers — the verify playbook uses `ignore_errors: true` for the service state and kernel module checks.

## Compliance Mapping

| Control | Framework |
|---------|-----------|
| Mandatory Access Control | CIS 1.7, STIG, NIS2 Art.21 |
| Least privilege enforcement | HIPAA §164.312(a), ISO 27001 A.9 |
| MAC profile coverage | PCI-DSS 2.2.3, SOC2 CC6.1 |

## License

Apache-2.0
