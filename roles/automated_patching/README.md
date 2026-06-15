# automated_patching

Automated security patching. On RedHat installs and configures `dnf-automatic` for security-only updates via the `dnf-automatic.timer`; on Debian installs and configures `unattended-upgrades` restricted to the security origin. Supports review mode (audit-only) and enforce mode. Security-only updates by default; no automatic reboot by default to preserve controlled reboot windows.

## Requirements

- Ansible >= 2.16
- Collection: `malpanez.security`

## Role Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `automated_patching_enabled` | `false` | Gate variable. Set `true` with `security_mode: enforce` to install and configure the patching tool. Review tasks always run. |
| `automated_patching_security_only` | `true` | Restrict automated updates to security packages only (`upgrade_type=security` on RedHat; security origin on Debian). |
| `automated_patching_apply_updates` | `true` | Apply downloaded updates automatically. `false` = download-only mode. |
| `automated_patching_auto_reboot` | `false` | Reboot automatically after updates that require it. Disabled by default for controlled reboots. |
| `automated_patching_reboot_time` | `"02:00"` | Time of day (HH:MM) for automatic reboot when `automated_patching_auto_reboot` is true. |
| `automated_patching_exclude_packages` | `[]` | Package name patterns to exclude from updates (e.g. `["kernel*"]` to hold the kernel). |
| `automated_patching_notify_email` | `""` | Email address for patching notifications. Empty = no email. |
| `automated_patching_random_sleep` | `3600` | Maximum random delay in seconds added to the patching timer (jitter). |

## Example Playbook

```yaml
- name: Enable automated security patching
  hosts: all
  roles:
    - role: malpanez.security.automated_patching
      vars:
        automated_patching_enabled: true
        security_mode: enforce
        automated_patching_security_only: true
        automated_patching_exclude_packages:
          - kernel*
        automated_patching_notify_email: ops@example.com
```

## Compliance

| Framework | Controls |
|-----------|----------|
| CIS | 1.9 — Ensure updates, patches, and additional security software are installed |
| NIST 800-53 | SI-2 — Flaw remediation |
| NIS2 | Art. 21(2)(i) — Security in acquisition, development and maintenance |

## License

Apache-2.0

## Author

Miguel Alpañez
