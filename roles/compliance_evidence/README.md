# compliance_evidence

Collects compliance evidence artifacts from managed hosts: configuration file snapshots, directory archives, and command outputs. All evidence is written to a local directory on the target host. Optionally generates a SHA-256 hash manifest for integrity verification and audit trail submission.

Designed to be run after all hardening roles as a non-destructive read-only collection step.

## Platform Support

Debian, Ubuntu, RHEL, Rocky, Alma, SUSE, openSUSE — no platform-specific packages required.

## What It Collects

The default evidence set covers the full collection managed by this role set:

| Category | Evidence Items |
|----------|---------------|
| SSH | `sshd_config`, `sshd_config.d/`, effective SSH policy (`sshd -T`) |
| Sudo | `/etc/sudoers`, PAM sudo chain |
| PAM / MFA | PAM chain grep (u2f, fido2, google_authenticator), `pam-auth-update --list` |
| Password policy | `pwquality.conf`, `faillock.conf`, `access.conf`, `limits.conf`, `limits.d/`, `login.defs`, `faillock` status |
| Kernel | `sysctl.d/99-security.conf`, `sysctl -a` output, `modprobe.d/99-security-disabled.conf`, `lsmod` output |
| AppArmor | `aa-status` output |
| SELinux | `sestatus` output |
| Audit | `/etc/audit/rules.d/`, `auditctl -l` output |
| Time sync | `/etc/chrony.conf`, `/etc/ntp.conf`, `timedatectl status` |
| Cron security | `/etc/cron.allow`, `/etc/cron.deny`, `/etc/at.allow`, `/etc/at.deny` |
| Capabilities | JSON and Markdown capability report (when `security_capabilities` fact is present) |

Files are copied directly; directories are archived as `.tar.gz`. Command outputs are written as `.log` files. Each file is named `{hostname}-{name}`.

## Role Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `compliance_evidence_enabled` | `true` | Enable evidence collection |
| `compliance_evidence_output_dir` | `/var/log/compliance` | Target directory for evidence files |
| `compliance_evidence_hash_manifest` | `true` | Generate a SHA-256 hash manifest |
| `compliance_evidence_hash_manifest_name` | `evidence.sha256` | Manifest filename within output dir |
| `compliance_evidence_items` | See defaults | List of evidence items to collect |

### Evidence item format

Each item in `compliance_evidence_items` is a dict with:

| Key | Required | Description |
|-----|----------|-------------|
| `name` | yes | Identifier used as output filename suffix |
| `path` | one of | Absolute path on target (file or directory) |
| `command` | one of | Shell command; stdout written to `.log` file |

`path` and `command` are mutually exclusive per item. Use `|| true` in commands to prevent failures on optional paths.

## Dependencies

None required. Optionally consumes the `security_capabilities` fact dict produced by `malpanez.security.security_capabilities` to generate a capabilities report.

## Example Playbook

```yaml
# Collect evidence with default items
- hosts: all
  roles:
    - role: malpanez.security.compliance_evidence

# Custom output directory and additional items
- hosts: all
  vars:
    compliance_evidence_output_dir: /srv/audit/{{ inventory_hostname }}
    compliance_evidence_items: "{{ compliance_evidence_items_default + custom_items }}"
  roles:
    - role: malpanez.security.compliance_evidence
```

## Recommended Playbook Position

Run this role last in the hardening playbook so that evidence reflects the final applied state:

```yaml
roles:
  - malpanez.security.security_capabilities
  - malpanez.security.kernel_hardening
  - malpanez.security.sshd_hardening
  - malpanez.security.pam_security
  - malpanez.security.pam_mfa
  - malpanez.security.sudoers_baseline
  - malpanez.security.audit_logging
  - malpanez.security.compliance_evidence   # always last
```

## Hash Manifest

When `compliance_evidence_hash_manifest: true`, the role generates `evidence.sha256` in `compliance_evidence_output_dir`. This file contains SHA-256 hashes of all collected evidence files and can be used to:

- Detect tampering with stored evidence.
- Submit as an artefact to a GRC platform or ticketing system.
- Verify evidence integrity during audit reviews.

## Compliance Mapping

| Control | Framework |
|---------|-----------|
| Audit log retention and integrity | NIST 800-53 AU-9, AU-11, PCI-DSS 10.5 |
| Evidence collection for assessments | ISO 27001 A.18.2, NIST 800-53 CA-7 |
| Configuration state documentation | CIS 1.x, NIST 800-53 CM-6 |
| Continuous monitoring artefacts | NIS2 Art.21(2)(b), SOC 2 CC7.2 |

## License

Apache-2.0

## Author

Miguel Alpañez
