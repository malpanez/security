# usbguard

USB device control with block-by-default policy. Generates an initial device whitelist from attached hardware, deploys `usbguard-daemon.conf`, and starts/enables USBGuard. Gracefully skips enforcement in container environments where no USB bus is present. Supports review mode (audit-only) and enforce mode.

## Requirements

- Ansible >= 2.16
- Collection: `malpanez.security`
- RHEL 8 hosts: EPEL repository must be available (the role installs it automatically).

## Role Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `usbguard_enabled` | `false` | Gate variable. Set `true` with `security_mode: enforce` to install and configure USBGuard. Review tasks always run. |
| `usbguard_implicit_policy` | `block` | Policy applied to USB devices not matched by any explicit rule. Choices: `allow`, `block`, `reject`. `block` prevents device use; `reject` blocks and logs. |
| `usbguard_allow_existing_devices` | `true` | When `true`, `usbguard generate-policy` captures currently-attached devices and writes them to `00-initial-policy.conf` before the daemon starts. Prevents operator lockout on first run. |
| `usbguard_present_device_policy` | `apply-policy` | Policy applied to USB devices present at daemon startup. Choices: `allow`, `block`, `reject`, `apply-policy`, `keep`. |
| `usbguard_present_controller_policy` | `apply-policy` | Policy applied to USB host controllers present at daemon startup. Same choices as `usbguard_present_device_policy`. |
| `usbguard_restore_controller_state` | `false` | When `true`, restores USB host controller authorization state after policy reload or daemon restart. |
| `usbguard_audit_backend` | `LinuxAudit` | Audit backend for USB policy decisions. Choices: `LinuxAudit` (sends to Linux audit subsystem), `FileAudit` (writes to `usbguard_audit_file_path`). |
| `usbguard_audit_file_path` | `/var/log/usbguard/usbguard-audit.log` | Path to the audit log file. Only used when `usbguard_audit_backend: FileAudit`. |
| `usbguard_extra_rules` | `[]` | Additional USBGuard rules deployed to `rules.d/10-extra-rules.conf`. Each list item is a single USBGuard rule string. |

> **Note:** Run with `usbguard_allow_existing_devices: true` on first execution to capture currently-attached devices in the initial whitelist. After that, new devices are blocked by default. Review attached hardware before running in enforce mode on production systems.

## Example Playbook

```yaml
- name: Deploy USB device control policy
  hosts: all
  roles:
    - role: malpanez.security.usbguard
      vars:
        usbguard_enabled: true
        security_mode: enforce
        usbguard_allow_existing_devices: true
        usbguard_implicit_policy: block
```

## Compliance

| Framework | Controls |
|-----------|----------|
| PCI-DSS | 12.3.4 — Hardware and removable media controls |
| HIPAA | 164.310(d)(1) — Device and media controls |
| NIS2 | Art. 21 — Physical and environmental security |
| SOC2 | CC6.7 — Restriction of unauthorised access |

## License

Apache-2.0

## Author

Miguel Alpañez
