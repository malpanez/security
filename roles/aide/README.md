# malpanez.security.aide

File Integrity Monitoring (FIM) with [AIDE](https://aide.github.io/).

Installs AIDE, deploys a hardened configuration that monitors critical system
paths, builds the initial integrity database, and schedules periodic checks via
a systemd timer. Reports are written to `/var/log/aide/`.

## Requirements

- Ansible 2.16+
- `community.general` collection (for SUSE support)
- On RHEL 8/9: AIDE is available in the AppStream repo — no EPEL required

## Role Variables

| Variable | Default | Description |
|---|---|---|
| `aide_enabled` | `false` | Gate — set `true` + `security_mode: enforce` to apply |
| `aide_config_file` | `/etc/aide/aide.conf` | AIDE config path (overridden per OS) |
| `aide_db_path` | `/var/lib/aide/aide.db` | Active database path |
| `aide_db_new_path` | `/var/lib/aide/aide.db.new` | Newly built DB before promotion |
| `aide_log_dir` | `/var/log/aide` | Report and log directory |
| `aide_report_file` | `/var/log/aide/aide-report.log` | Report output path |
| `aide_init_db` | `true` | Initialise DB on first run (set `false` in CI/containers) |
| `aide_timer_enabled` | `true` | Deploy and enable `aide-check.timer` |
| `aide_check_schedule` | `0 5 * * *` | systemd `OnCalendar` for periodic checks |
| `aide_monitored_paths` | see defaults | List of `{path, rules}` dicts |
| `aide_excluded_paths` | see defaults | Paths excluded from monitoring |

## Tags

| Tag | Action |
|---|---|
| `review` | Report current aide status, no changes |
| `install` | Install aide package |
| `configure` | Deploy aide.conf, create directories |
| `service` | Initialise DB, deploy and enable systemd timer |
| `verify` | Assert binary, config, timer, and DB are in place |

## OS differences

| Attribute | Debian/Ubuntu | RHEL/Rocky/Alma | SUSE |
|---|---|---|---|
| Package | `aide` | `aide` | `aide` |
| Config | `/etc/aide/aide.conf` | `/etc/aide.conf` | `/etc/aide.conf` |
| Init command | `aideinit` | `aide --init` | `aide --init` |
| DB path | `/var/lib/aide/aide.db` | `/var/lib/aide/aide.db.gz` | `/var/lib/aide/aide.db` |

## Example Playbook

```yaml
- hosts: servers
  become: true
  vars:
    aide_enabled: true
    security_mode: enforce
    aide_timer_enabled: true
    aide_check_schedule: "0 3 * * *"
    aide_monitored_paths:
      - path: /etc
        rules: p+i+n+u+g+s+b+m+c+md5+sha256
      - path: /usr/bin
        rules: p+i+n+u+g+s+b+m+c+md5+sha256
      - path: /boot
        rules: p+i+n+u+g+s+b+m+c+md5+sha256
  roles:
    - malpanez.security.aide
```

## Supported Platforms

- Debian (buster, bullseye, bookworm, trixie)
- Ubuntu (bionic, focal, jammy, noble)
- RHEL / Rocky Linux / AlmaLinux (all)
- SUSE / openSUSE (15.5, all)

## Frameworks

CIS Benchmark 1.3.x (file integrity) / NIST SP 800-53 SI-7 (Software, Firmware,
and Information Integrity) / NIS2 Article 21 (integrity measures) /
PCI-DSS 11.5 (change-detection mechanisms)
