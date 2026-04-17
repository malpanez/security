# sshd_hardening

Hardens the OpenSSH daemon configuration via a drop-in file in `/etc/ssh/sshd_config.d/`. Never overwrites the OS-shipped `sshd_config`. Disables password authentication, root login, X11 forwarding, and compression; enforces strong algorithm sets; and supports per-group Match blocks for human users and service accounts.

Supports **review** mode (posture check) and **enforce** mode (applies drop-in).

## Platform Support

| OS Family | Notes |
|-----------|-------|
| Debian / Ubuntu | Drop-in requires OpenSSH >= 7.3 (Debian 9+, Ubuntu 16.04+) |
| RHEL / Rocky / Alma | Drop-in requires OpenSSH >= 7.4 (RHEL 7.4+) |
| SUSE / openSUSE | Drop-in requires SUSE 15+ |

Set `sshd_hardening_use_dropin: false` only if your OpenSSH predates 7.3.

## What It Hardens

| Area | Default Setting | Compliance |
|------|----------------|------------|
| Password authentication | Disabled | CIS 5.2.8, STIG V-238218 |
| Root login | `no` | CIS 5.2.10, DISA STIG |
| Empty passwords | Disabled | CIS 5.2.9 |
| X11 forwarding | Disabled | CIS 5.2.6 |
| Compression | Disabled | CIS 5.2 |
| Login grace time | 30 seconds | CIS 5.2.16 |
| Client keepalive | 300s / 2 unanswered | CIS 5.2.17 |
| Max auth tries | 4 | CIS 5.2.7 |
| Max startups | 10:30:60 | CIS 5.2.21 |
| Log level | VERBOSE | CIS 5.2.5 |
| Ciphers (modern) | ChaCha20-Poly1305, AES-GCM, AES-CTR | CIS 5.2.13 |
| MACs (modern) | HMAC-SHA2-512-ETM, HMAC-SHA2-256-ETM | CIS 5.2.14 |
| KEX algorithms | Curve25519, ECDH-nistp | CIS 5.2.15 |

## Modes

| Mode | Behaviour |
|------|-----------|
| `review` (default) | Check password auth, root login, X11, algorithm presence |
| `enforce` | Deploy drop-in to `/etc/ssh/sshd_config.d/20-auth-hardening.conf`, validate with `sshd -t`, reload service |

## Role Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `security_mode` | `review` | Set to `enforce` to apply changes |
| `sshd_hardening_password_authentication` | `false` | Enable password-based auth |
| `sshd_hardening_permit_root_login` | `"no"` | Root login control (`yes`/`no`/`prohibit-password`) |
| `sshd_hardening_permit_empty_passwords` | `false` | Allow empty-password accounts |
| `sshd_hardening_challenge_response_authentication` | `false` | Enable challenge-response auth |
| `sshd_hardening_kbd_interactive_authentication` | `null` | KbdInteractiveAuthentication override (null = unset) |
| `sshd_hardening_use_pam` | `true` | Enable PAM integration |
| `sshd_hardening_x11_forwarding` | `false` | Allow X11 forwarding |
| `sshd_hardening_login_grace_time` | `"30"` | Seconds to authenticate before disconnect |
| `sshd_hardening_client_alive_interval` | `300` | Keepalive interval in seconds |
| `sshd_hardening_client_alive_count_max` | `2` | Unanswered keepalives before disconnect |
| `sshd_hardening_max_auth_tries` | `4` | Max auth attempts per connection |
| `sshd_hardening_max_sessions` | `10` | Max open sessions |
| `sshd_hardening_max_startups` | `10:30:60` | Unauthenticated connection throttle (start:rate:full) |
| `sshd_hardening_log_level` | `VERBOSE` | Logging verbosity |
| `sshd_hardening_compression` | `false` | Enable SSH compression |
| `sshd_hardening_use_dns` | `false` | DNS reverse lookup for clients |
| `sshd_hardening_banner` | `""` | Path to legal banner file (empty = disabled) |
| `sshd_hardening_algorithm_profile` | `auto` | Algorithm set: `auto`, `modern`, or `legacy` |
| `sshd_hardening_authentication_methods` | `[]` | AuthenticationMethods directive values |
| `sshd_hardening_allow_users` | `[]` | Users explicitly allowed to connect |
| `sshd_hardening_allow_groups` | `[]` | Groups explicitly allowed to connect |
| `sshd_hardening_human_groups` | `[]` | Groups treated as human users (MFA Match blocks) |
| `sshd_hardening_service_groups` | `[]` | Groups treated as service accounts |
| `sshd_hardening_trusted_ca_key` | `""` | SSH CA public key for TrustedUserCAKeys |
| `sshd_hardening_trusted_ca_path` | `/etc/ssh/trusted_user_ca_keys` | Path to write the CA key |
| `sshd_hardening_use_dropin` | `true` | Write drop-in instead of replacing sshd_config |
| `sshd_hardening_dropin_path` | `/etc/ssh/sshd_config.d/20-auth-hardening.conf` | Drop-in file path |
| `sshd_hardening_service_name` | `sshd` | SSH daemon service name |
| `sshd_hardening_package_name` | `openssh-server` | Package providing sshd |
| `sshd_hardening_binary_path` | `/usr/sbin/sshd` | sshd binary for version detection |

## Dependencies

None. Optionally consumes `security_capabilities_human_groups` and `security_capabilities_service_groups` facts produced by `malpanez.security.security_capabilities`.

## Example Playbook

```yaml
# Review mode — safe, read-only
- hosts: all
  roles:
    - role: malpanez.security.sshd_hardening

# Enforce mode — key-only auth, modern algorithms, human group Match block
- hosts: all
  vars:
    security_mode: enforce
    sshd_hardening_password_authentication: false
    sshd_hardening_permit_root_login: "no"
    sshd_hardening_algorithm_profile: modern
    sshd_hardening_human_groups:
      - linux-admins
    sshd_hardening_authentication_methods:
      - publickey
  roles:
    - role: malpanez.security.sshd_hardening
```

## Drop-In Approach

The role writes **only** `/etc/ssh/sshd_config.d/20-auth-hardening.conf`. The OS-shipped `sshd_config` is never modified. To revert all changes, delete the drop-in file and reload sshd.

### Lexicographic load order

OpenSSH loads `sshd_config.d/*.conf` in **lexicographic (alphabetical) order** before the main `sshd_config`. For most directives, **the first definition wins** — a later file cannot override an earlier one.

Files are numbered to control precedence:

| Range | Owner | Examples |
|-------|-------|---------|
| `00–09` | OS vendor / cloud-init | `00-cloud-init.conf` (AWS, Azure) |
| `10–49` | Security hardening | **`20-auth-hardening.conf`** (this role) |
| `50–89` | Application / team config | `60-jumphost.conf` |
| `90–99` | Local admin overrides | `99-local.conf` |

**Why `20`?** The role sits above vendor defaults (which typically use `00–09`) so our settings are not silently overridden, while remaining below `50+` so team-level overrides can still take effect. If you need this role to always win, set:

```yaml
sshd_hardening_dropin_path: /etc/ssh/sshd_config.d/10-hardening.conf
```

**Conflict detection:** The role runs `sshd -t` after writing the drop-in and rolls back if validation fails. However, it does not scan for existing drop-ins that may conflict. Before enforcing, audit with:

```bash
grep -rh 'PasswordAuthentication\|PermitRootLogin\|AuthorizedKeysFile' /etc/ssh/sshd_config.d/
```

## Testing with Molecule

```bash
cd roles/sshd_hardening
molecule test
```

Tests verify: drop-in file exists, `PasswordAuthentication no` present, `PermitRootLogin no` present, `sshd -t` syntax check passes.

## Compliance Mapping

| Control | Framework |
|---------|-----------|
| Key-only authentication | CIS 5.2.8, PCI-DSS 8.3.6, STIG V-238218 |
| Root login disabled | CIS 5.2.10, DISA STIG, NIS2 Art.21 |
| Strong ciphers/MACs/KEX | CIS 5.2.13-15, NIST 800-53 SC-8 |
| Auth failure limiting | CIS 5.2.7, 5.2.21, NIST 800-53 AC-7 |
| Verbose logging | CIS 5.2.5, NIST 800-53 AU-3 |
| Idle timeout | CIS 5.2.17, NIST 800-53 AC-11 |

## License

GPL-2.0-or-later

## Author

Miguel Alpañez
