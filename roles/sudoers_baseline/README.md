# sudoers_baseline

Establishes a secure sudo baseline by deploying hardened `Defaults` directives and group-based privilege rules via drop-in files in `/etc/sudoers.d/`. The main `/etc/sudoers` file is never rewritten — only verified with `visudo -c`. All hardening is isolated in two files, making it easy to audit and revert.

Supports **review** mode (validation only) and **enforce** mode (applies drop-ins).

## Platform Support

Debian, Ubuntu, RHEL, Rocky, Alma, SUSE, openSUSE — all distributions that support `@includedir /etc/sudoers.d`.

Set `sudoers_baseline_use_dropin: false` only if your distribution does not include the `@includedir` directive in `/etc/sudoers`.

## Files Managed

| File | Purpose |
|------|---------|
| `/etc/sudoers.d/10-security-defaults` | Defaults directives (PTY, log, timeout, etc.) |
| `/etc/sudoers.d/99-security-groups` | Group-based privilege rules |

## Modes

| Mode | Behaviour |
|------|-----------|
| `review` (default) | Validate `/etc/sudoers` with `visudo -c`, report violations |
| `enforce` | Deploy drop-ins when `sudoers_baseline_strict: true` and `security_mode: enforce` |

Hardening is applied only when both `sudoers_baseline_strict: true` and `security_mode: enforce` are set. This double gate prevents accidental lockout.

## Role Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `security_mode` | `review` | Set to `enforce` to apply changes |
| `sudoers_baseline_strict` | `false` | Enable drop-in deployment (required gate) |
| `sudoers_baseline_use_dropin` | `true` | Write to `/etc/sudoers.d/` instead of main file |
| `sudoers_baseline_defaults` | See below | List of Defaults directives to apply |
| `sudoers_baseline_secure_path` | `/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin` | `secure_path` value |
| `sudoers_baseline_groups` | `{}` | Map of group names to privilege rules |
| `sudoers_baseline_sudoers_path` | `/etc/sudoers` | Path to main sudoers file |
| `sudoers_baseline_files_path` | `/etc/sudoers.d` | Directory for drop-in snippets |
| `sudoers_baseline_dropin_defaults` | `{{ sudoers_baseline_files_path }}/10-security-defaults` | Path for defaults drop-in |
| `sudoers_baseline_dropin_groups` | `{{ sudoers_baseline_files_path }}/99-security-groups` | Path for groups drop-in |
| `sudoers_baseline_iolog_enabled` | `false` | Enable I/O logging for full session audit |
| `sudoers_baseline_iolog_dir` | `/var/log/sudo-io` | I/O log directory |
| `sudoers_baseline_iolog_maxseq` | `1000` | Rotate I/O logs after N sessions |

Default `sudoers_baseline_defaults`:

```yaml
sudoers_baseline_defaults:
  - use_pty
  - logfile=/var/log/sudo.log
  - timestamp_timeout=5
  - passwd_tries=3
  - "!visiblepw"
```

## Dependencies

None.

## Example Playbook

```yaml
# Review mode — validate sudoers file only
- hosts: all
  roles:
    - role: malpanez.security.sudoers_baseline

# Enforce mode — deploy hardened defaults and group rules
- hosts: all
  vars:
    security_mode: enforce
    sudoers_baseline_strict: true
    sudoers_baseline_groups:
      linux_admins:
        require_password: true
        commands:
          - /usr/bin/systemctl status *
          - /usr/bin/journalctl
      deploy_svc:
        require_password: true
        commands:
          - /usr/bin/systemctl restart myapp
  roles:
    - role: malpanez.security.sudoers_baseline
```

## Drop-In Approach

The role writes **only** two files in `/etc/sudoers.d/`. The OS `/etc/sudoers` is validated but never modified. To revert, delete the two drop-in files. `visudo -c` is always run before reloading to prevent syntax errors from breaking sudo access.

## I/O Logging

Set `sudoers_baseline_iolog_enabled: true` to capture full command session logs under `/var/log/sudo-io/`. This records all keystrokes and output for privileged sessions. Plan for log rotation as disk usage can be significant in active environments.

## Testing with Molecule

```bash
cd roles/sudoers_baseline
molecule test
```

Tests verify: drop-in files exist, `use_pty` present, `logfile` configured, `timestamp_timeout` set, `visudo -c` passes.

## Compliance Mapping

| Control | Framework |
|---------|-----------|
| PTY allocation for sudo | CIS 5.3.4, DISA STIG |
| Sudo session logging | CIS 5.3.6, NIST 800-53 AU-3, PCI-DSS 10.2 |
| Password requirement for sudo | CIS 5.3, NIST 800-53 AC-6(5) |
| Privilege minimization | CIS 5.3, NIS2 Art.21(2)(j) |
| No password disclosure | CIS 5.3, NIST 800-53 IA-6 |

## License

MIT

## Author

Miguel Alpañez
