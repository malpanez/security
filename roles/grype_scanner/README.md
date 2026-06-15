# malpanez.security.grype_scanner

Install and configure [Grype](https://github.com/anchore/grype) vulnerability scanner.

Downloads the appropriate architecture binary from GitHub releases, deploys a
configuration file, updates the vulnerability database, and optionally sets up
a systemd timer for periodic scans.

## Requirements

- Ansible 2.16+
- Internet access on the target host (for binary download and DB update)
- `community.general` collection (for SUSE support)

## Role Variables

| Variable | Default | Description |
|---|---|---|
| `grype_scanner_enabled` | `false` | Gate — set `true` + `security_mode: enforce` to install |
| `grype_version` | `0.111.0` | Grype release to install |
| `grype_install_dir` | `/usr/local/bin` | Binary destination |
| `grype_config_dir` | `/etc/grype` | Configuration directory |
| `grype_db_dir` | `/var/lib/grype/db` | Vulnerability DB cache |
| `grype_log_dir` | `/var/log/grype` | Scan output log directory |
| `grype_severity_fail` | `high` | Minimum severity for non-zero exit |
| `grype_output_format` | `table` | Output format (`table`, `json`, `sarif`) |
| `grype_ignore_unfixed` | `false` | Ignore findings with no available fix |
| `grype_scheduled_scan` | `false` | Deploy a systemd timer for periodic scans |
| `grype_scan_schedule` | `0 3 * * *` | systemd `OnCalendar` expression |

## Tags

| Tag | Action |
|---|---|
| `review` | Report installed version, no changes |
| `install` | Download and install binary |
| `configure` | Deploy config, update DB, manage timer |
| `verify` | Assert binary works and version matches |

## Example Playbook

```yaml
- hosts: servers
  become: true
  vars:
    grype_scanner_enabled: true
    security_mode: enforce
    grype_version: "0.111.0"
    grype_severity_fail: high
    grype_scheduled_scan: true
    grype_scan_schedule: "0 2 * * *"
  roles:
    - malpanez.security.grype_scanner
```

## Supported Platforms

- Debian (buster, bullseye, bookworm, trixie)
- Ubuntu (bionic, focal, jammy, noble)
- RHEL / Rocky Linux / AlmaLinux (all)
- SUSE / openSUSE (15.5, all)

## Frameworks

CIS Benchmark (vulnerability management) / NIST 800-53 SI-2 (Flaw Remediation) /
NIS2 Article 21 (vulnerability handling) / PCI-DSS 6.3.3 (vulnerability management)
