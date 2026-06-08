# sssd_ad_integration

Network-zone-aware SSH access control with AD/SSSD group mapping.

Deploys layered SSH hardening using:
- `sshd_config.d/` drop-ins with Match Address (zones) and Match Group (tiers)
- SSSD configured for AD identity (`id_provider = ad`, `sudo_provider = sssd`)
- Per-group `sudoers.d/` files with explicit command allowlists
- `pam_access.conf` as a second enforcement layer independent of sshd

Designed to complement `malpanez.security.sshd_hardening`. See
[docs/ssh-ad-integration.md](../../docs/ssh-ad-integration.md) for the full
design rationale, common mistakes, and NIS2 alignment.

## Role execution order

```
1. malpanez.security.sshd_hardening   # crypto baseline + global auth defaults
2. malpanez.security.sssd_ad_integration  # zone/group access control + SSSD
```

Configure `sshd_hardening_dropin_path` to sort before `20-access-control.conf`:

```yaml
sshd_hardening_dropin_path: /etc/ssh/sshd_config.d/10-auth-hardening.conf
```

## Drop-in file map

| File | Content |
|------|---------|
| `00-hardening.conf` | Crypto baseline (sshd_hardening, manual) |
| `10-auth-hardening.conf` | Global auth defaults (sshd_hardening) |
| `20-access-control.conf` | AllowGroups whitelist — outermost gate |
| `30-network-zones.conf` | Match Address: corp, vpn, bastion |
| `40-group-admins.conf` | Match Group linux-admins |
| `41-group-users.conf` | Match Group linux-users |
| `42-group-service.conf` | Match Group linux-service |
| `43-group-readonly.conf` | Match Group linux-readonly + ChrootDirectory |

## First-occurrence-wins behaviour

sshd processes drop-ins lexicographically. When multiple Match blocks fire
simultaneously, the **first occurrence** of each directive wins.

This enables zone-aware 2FA without `Match Address AND Group` syntax (which
OpenSSH does not support):

- `30-network-zones.conf` controls `AuthenticationMethods` for corp/vpn
- `40-group-admins.conf` sets `AuthenticationMethods publickey,keyboard-interactive`
- Admin from internet → only group block fires → 2FA required
- Admin from corp → corp block fires first; `ssh_corp_require_mfa` controls the result:
  - `ssh_corp_require_mfa: false` (default) → corp block sets publickey (single factor)
  - `ssh_corp_require_mfa: true` → corp block sets publickey,keyboard-interactive (MFA)

Set `ssh_corp_require_mfa: true` to close **AUDIT-CRIT-01**.

## Groups

| Group | Shell | Forwarding | Auth | sudo |
|-------|-------|------------|------|------|
| `linux-admins` | yes | yes (VPN/LAN) | 2FA from internet | ALL |
| `linux-users` | yes | no | pubkey | status/journalctl |
| `linux-service` | no | no | pubkey (authorized_keys from=) | none |
| `linux-readonly` | no | no | pubkey | none, SFTP chroot |

## Variables

All variables have defaults. Required variables when `sssd_ad_configure: true`:

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `sssd_ad_domain` | yes | `""` | AD DNS domain |
| `sssd_ad_realm` | yes | `""` | Kerberos realm (uppercase) |
| `ssh_local_fallback_group` | no | `""` | Local group always in AllowGroups |
| `ssh_network_zones.corp` | no | `10.10.0.0/16` | Corporate LAN CIDR |
| `ssh_network_zones.vpn` | no | `10.8.0.0/24` | VPN CIDR |
| `ssh_network_zones.bastion` | no | `""` | Bastion IP (empty = disabled) |
| `ssh_corp_require_mfa` | no | `false` | Require MFA from corp LAN (set `true` to close AUDIT-CRIT-01) |
| `ssh_chroot_base` | no | `/data/readonly` | ChrootDirectory for readonly group |
| `ssh_service_allowed_sources` | no | `[]` | Source IPs for linux-service PAM access |
| `sssd_offline_credentials_expiration` | no | `7` | Days cached creds valid (0=never; 7=default, closes AUDIT-HIGH-01) |
| `ssh_verify_groups_strict` | no | `true` | Fail play on unresolvable AllowGroups entries (closes AUDIT-HIGH-03) |

See [defaults/main.yml](defaults/main.yml) and
[meta/argument_specs.yml](meta/argument_specs.yml) for all variables.

## Upgrade Notes

### Default changes in this version

The following defaults changed. Operators using the old defaults must set them
explicitly to preserve previous behavior.

| Variable | Old default | New default | Reason |
|----------|-------------|-------------|--------|
| `sssd_offline_credentials_expiration` | `0` (never expire) | `7` (days) | AUDIT-HIGH-01: disabled AD accounts could authenticate indefinitely when offline |
| `ssh_verify_groups_strict` | `false` | `true` | AUDIT-HIGH-03: unresolvable AllowGroups entries silently lock out all users |

`ssh_corp_require_mfa` is new (default `false`). Existing deployments are
unaffected. Set `true` to close AUDIT-CRIT-01 (MFA enforcement on corp LAN).

## ChrootDirectory

`/data/readonly` (or `ssh_chroot_base`) **must** be:
- Owned `root:root`
- Mode `0755`
- Not writable by the chrooted user

The role creates this directory and enforces ownership. Do not change it manually.

## SSSD: sudo_provider

`sudo_provider = sssd` is set but rules live in `/etc/sudoers.d/`, **not** in
AD schema. This avoids AD schema extensions and works with every AD version.

## Safety

- `sshd -t` runs before any service restart. The play fails if validation fails.
- `ssh_backup_config: true` snapshots `sshd_config.d/` before changes.
- `ssh_local_fallback_group` prevents automation lockout if AD is unreachable.
- **Test in a VM with console access before applying to production.**

## Example playbook

```yaml
- name: Harden SSH with AD integration
  hosts: linux_servers
  roles:
    - role: malpanez.security.sshd_hardening
      vars:
        security_mode: enforce
        sshd_hardening_dropin_path: /etc/ssh/sshd_config.d/10-auth-hardening.conf

    - role: malpanez.security.sssd_ad_integration
      vars:
        security_mode: enforce
        sssd_ad_domain: corp.example.com
        sssd_ad_realm: CORP.EXAMPLE.COM
        ssh_local_fallback_group: ansible-deploy
        ssh_network_zones:
          corp: "10.10.0.0/16"
          vpn: "10.8.0.0/24"
          bastion: ""
        ssh_service_allowed_sources:
          - "10.10.5.0/24"
```

## License

Apache-2.0

## Author

Miguel Alpañez
