# antivirus

ClamAV antivirus installation, freshclam updates, and scheduled scan timer. Supports EPEL on RHEL-family hosts and container-aware skipping. Review mode audits ClamAV state; enforce mode installs and configures.

## Requirements

- Ansible >= 2.16
- Collection: `malpanez.security`
- RHEL-family hosts: EPEL repository must be available (the role installs it automatically on RHEL 8+).

## Role Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `antivirus_enabled` | `false` | Gate variable. Set `true` with `security_mode: enforce` to install and configure ClamAV. Review tasks always run. |
| `antivirus_update_db` | `true` | Run `freshclam` to update the virus database during role execution. Set `false` in CI to skip the ~200 MB freshclam download. |
| `antivirus_scan_enabled` | `true` | Deploy a systemd scan timer that runs `clamscan` on a schedule. |
| `antivirus_scan_dirs` | `[/home, /tmp, /var/tmp]` | List of directories to scan with `clamscan`. |
| `antivirus_scan_schedule` | `daily` | systemd `OnCalendar` value for the scan timer. Accepts any systemd calendar expression (e.g. `*-*-* 02:00:00`). |
| `antivirus_scan_log` | `/var/log/clamav/scan.log` | Path to the `clamscan` output log file. |
| `antivirus_freshclam_checks` | `12` | freshclam `Checks` directive. Controls how many times per day freshclam checks for database updates. |
| `antivirus_max_file_size` | `25M` | `MaxFileSize` directive for ClamAV. Files larger than this value are not scanned. |
| `antivirus_max_scan_size` | `100M` | `MaxScanSize` directive for ClamAV. Maximum data to scan from a file, used for compressed/archive scanning. |
| `antivirus_selinux_contexts` | `true` | Restore SELinux file contexts and set the `antivirus_can_scan_system` SELinux boolean on RHEL-family hosts. |

## Scan service privilege model

The `clamav-scan.service` runs as the ClamAV daemon user (not root). This resolves AUDIT-MED-02 (privilege reduction) without requiring additional systemd hardening directives that would break scan functionality.

## Example Playbook

```yaml
- name: Install and configure ClamAV
  hosts: all
  roles:
    - role: malpanez.security.antivirus
      vars:
        antivirus_enabled: true
        security_mode: enforce
        antivirus_update_db: false
```

## Compliance

| Framework | Controls |
|-----------|----------|
| PCI-DSS | 5.2 — Anti-malware on all applicable components |
| NIS2 | Art. 21(2)(e) — Malware protection |
| SOC2 | CC6.8 — Prevention of malicious software |

## License

MIT

## Author

Miguel Alpañez
