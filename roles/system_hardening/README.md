# system_hardening

OS-level hardening for Linux servers: filesystem mount security, `/proc` access controls, system account lockdown, SUID/SGID auditing, and host hardening primitives. Drop-in approach — never rewrites existing config files.

Supports **review** mode (read-only posture report) and **enforce** mode (applies changes).

## Platform Support

| Platform | Versions | Notes |
|----------|----------|-------|
| Debian | 11, 12+ | Full support |
| Ubuntu | 20.04, 22.04, 24.04 | Full support |
| RHEL / Rocky / Alma | 7, 8, 9, 10 | Full support |
| SUSE / openSUSE Leap | 15.5+ | Full support |

## What It Hardens

| Area | Controls | Compliance |
|------|----------|------------|
| `/tmp` mount | `nodev,nosuid,noexec` via tmpfs | CIS 1.1.2 |
| `/var/tmp` | Bind-mount onto `/tmp` | CIS 1.1.6 |
| `/dev/shm` | `nodev,nosuid,noexec` | CIS 1.1.7 |
| `/home` | `nodev,nosuid` | CIS 1.1.9 |
| `/proc hidepid` | `hidepid=2,gid=proc` + systemd-logind drop-in | CIS 1.1.x / STIG V-238218 |
| Ctrl+Alt+Del | Masked via systemd | CIS 1.5.5 |
| securetty | Restrict root TTY logins | CIS 5.5 |
| System accounts | Force `/sbin/nologin` shell (UID < 1000) | CIS 5.5.2 |
| SUID/SGID audit | Report or remove unlisted SUID/SGID bits | CIS 1.1.x, 6.1.x |
| `.rhosts`/`.netrc` | Find and optionally remove | CIS 5.3.x |
| Package GPG | Enforce signed packages (`apt`/`dnf`) | CIS 1.2.x |
| Umask | Set `027` system-wide via `profile.d` drop-in | CIS 5.4.x |
| Core dumps | Disable via `profile.d` drop-in | HIPAA §164.312 |

## Modes

| Mode | Behaviour |
|------|-----------|
| `review` (default) | Read-only report: shows misconfigurations, SUID binaries, legacy files |
| `enforce` | Applies all hardening: mounts, hidepid, account shells, removes .rhosts/.netrc |

## Key Variables

```yaml
# Gate variables
security_mode: enforce
system_hardening_enabled: true

# Mount hardening
system_hardening_tmp_enabled: true
system_hardening_tmp_options: "defaults,nodev,nosuid,noexec"
system_hardening_dev_shm_enabled: true
system_hardening_home_enabled: true

# /proc hidepid
system_hardening_hidepid_enabled: true
system_hardening_hidepid_value: 2          # 1=hide entries, 2=hide completely
system_hardening_proc_group: proc
system_hardening_proc_group_extra_members: []  # Extra users needing /proc access

# Accounts
system_hardening_uid_min: 1000
system_hardening_accounts_shell_whitelist:
  - root
  - sync
  - shutdown
  - halt

# SUID/SGID
system_hardening_suid_enabled: true
system_hardening_suid_report: true
system_hardening_suid_remove_unlisted: false   # true = remove in enforce mode
system_hardening_suid_whitelist:
  - /usr/bin/sudo
  - /usr/bin/su
  - /usr/bin/passwd
  # ... see defaults/main.yml for full list

# Umask
system_hardening_umask: "027"

# GPG enforcement
system_hardening_apt_allow_unauthenticated: false
system_hardening_dnf_gpgcheck: true
```

## Quick Start

```yaml
# Review mode — safe, read-only
- hosts: all
  roles:
    - role: malpanez.security.system_hardening

# Enforce mode
- hosts: all
  vars:
    security_mode: enforce
    system_hardening_enabled: true
  roles:
    - role: malpanez.security.system_hardening
```

## hidepid Notes

The role uses the modern mount approach compatible with RHEL 8+ / kernel 5.8+:

- `/etc/systemd/system/proc.mount` drop-in with `hidepid=2,gid=proc`
- `/etc/systemd/system/systemd-logind.service.d/proc.conf` → `SupplementaryGroups=proc`
- Systemd daemon reload + systemd-logind restart

For RHEL 7 (kernel 3.10), set `system_hardening_hidepid_value: 1` — the `gid=proc` mount option is not available on older kernels.

## SUID/SGID Whitelist

In review mode all SUID/SGID binaries are reported. In enforce mode with `system_hardening_suid_remove_unlisted: true`, any binary not in the whitelist loses the setuid/setgid bit. The default whitelist covers all standard system tools: `sudo`, `su`, `newgrp`, `passwd`, `chsh`, `chfn`, `gpasswd`, `ping`, `mount`, `umount`, `pkexec`, `ssh-keysign`, `dbus-daemon-launch-helper`, `unix_chkpwd`.

## Testing with Molecule

```bash
cd roles/system_hardening
molecule test
```

Tests verify: mount options applied, hidepid active, Ctrl+Alt+Del masked, umask profile present, system accounts use nologin.

## Compliance Mapping

| Control | Framework |
|---------|-----------|
| Filesystem mount restrictions | CIS 1.1.2–1.1.9, PCI-DSS 2.2.1 |
| `/proc` access control | CIS 1.1.x, STIG V-238218 |
| Ctrl+Alt+Del disabled | CIS 1.5.5, DISA STIG |
| System account lockdown | CIS 5.5.2, HIPAA §164.312(a) |
| SUID/SGID removal | CIS 1.1.x, 6.1.x, PCI-DSS 2.2.4 |
| Package integrity | CIS 1.2.x, NIS2 Art.21(2)(e) |
| Umask hardening | CIS 5.4.x, SOC2 CC6.1 |
| Core dumps disabled | HIPAA §164.312(c), CIS 1.6.1 |

## License

GPL-2.0-or-later
