# cis_baseline

Verifies and optionally enforces a minimal CIS Benchmark control set for SSH daemon configuration and sudoers. Operates in two modes: `review` (non-destructive audit with pass/fail output) and `enforce` (applies corrections for failing controls). Designed as a lightweight verification layer complementary to the full hardening roles.

## Platform Support

Debian, Ubuntu, RHEL, Rocky, Alma, SUSE, openSUSE — any system with OpenSSH and sudo.

## Controls Covered

### SSH Daemon

| Control | Check |
|---------|-------|
| No password authentication | `PasswordAuthentication no` in effective config |
| Root login disabled | `PermitRootLogin no` |
| Max auth tries | `MaxAuthTries <= 4` |

### Sudoers

| Control | Check |
|---------|-------|
| PTY allocation | `use_pty` in Defaults |
| Audit log | `logfile` configured in Defaults |
| No unrestricted NOPASSWD | Absence of `NOPASSWD:ALL` |

## Modes

| Mode | Behaviour |
|------|-----------|
| `review` | Read sshd_config and sudoers, assert controls, report violations via `ansible.builtin.debug` |
| `enforce` | Apply minimal corrections for failing controls (requires `security_mode: enforce`) |

Set `cis_baseline_review_fail_on_violation: true` to fail the play on non-compliance — useful for CI enforcement pipelines.

## Role Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `security_mode` | `review` | Set to `enforce` to apply corrections |
| `cis_baseline_enabled` | `false` | Enable CIS baseline (required gate) |
| `cis_baseline_mode` | `enforce` | Operating mode: `enforce` or `review` |
| `cis_baseline_review_fail_on_violation` | `false` | Fail play on review violations (CI use) |
| `cis_baseline_controls` | See below | Controls map organized by service |
| `cis_baseline_sshd_config_path` | `/etc/ssh/sshd_config` | Path to sshd_config |
| `cis_baseline_sshd_service_name` | `ssh` (Debian) / `sshd` (EL) | SSH service name |
| `cis_baseline_sudoers_path` | `/etc/sudoers` | Path to main sudoers file |
| `cis_baseline_sudoers_dir` | `/etc/sudoers.d` | Path to sudoers.d directory |

Default controls:

```yaml
cis_baseline_controls:
  sshd:
    - No PasswordAuthentication
    - PermitRootLogin no
    - MaxAuthTries <=4
  sudoers:
    - require use_pty
    - logfile configured
    - no NOPASSWD:ALL
```

## Dependencies

None. This role is complementary to `malpanez.security.sshd_hardening` and `malpanez.security.sudoers_baseline`, which apply the actual hardening. Use `cis_baseline` to verify their output or to audit systems not managed by this collection.

## Example Playbook

```yaml
# Audit-only mode — report non-compliance without changes
- hosts: all
  vars:
    cis_baseline_enabled: true
    cis_baseline_mode: review
  roles:
    - role: malpanez.security.cis_baseline

# CI enforcement — fail pipeline on violations
- hosts: all
  vars:
    cis_baseline_enabled: true
    cis_baseline_mode: review
    cis_baseline_review_fail_on_violation: true
  roles:
    - role: malpanez.security.cis_baseline

# Enforce mode — apply corrections
- hosts: all
  vars:
    security_mode: enforce
    cis_baseline_enabled: true
    cis_baseline_mode: enforce
  roles:
    - role: malpanez.security.cis_baseline
```

## Recommended Use with Full Hardening

```yaml
roles:
  - malpanez.security.sshd_hardening      # Apply full SSH hardening
  - malpanez.security.sudoers_baseline    # Apply sudoers hardening
  - malpanez.security.cis_baseline        # Verify CIS controls were applied
```

## Compliance Mapping

| Control | CIS Reference | Framework |
|---------|---------------|-----------|
| SSH password auth disabled | CIS 5.2.8 | NIST 800-53 IA-5, PCI-DSS 8.3.6 |
| Root SSH login disabled | CIS 5.2.10 | NIST 800-53 AC-6, DISA STIG |
| Max auth tries | CIS 5.2.7 | NIST 800-53 AC-7, PCI-DSS 8.3.4 |
| Sudo PTY allocation | CIS 5.3.4 | NIST 800-53 AU-3, DISA STIG |
| Sudo audit log | CIS 5.3.6 | NIST 800-53 AU-2, PCI-DSS 10.2 |
| No NOPASSWD:ALL | CIS 5.3 | NIST 800-53 AC-6(5), NIS2 Art.21 |

## License

MIT

## Author

Miguel Alpañez
