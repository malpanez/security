# boot_hardening

GRUB2 bootloader hardening following **CIS 1.4.x**. Optionally sets a GRUB superuser and PBKDF2 password, disables os-prober and recovery menu entries, and enforces `grub.cfg` permissions. Uses **update-grub** on Debian/Ubuntu and **grub2-mkconfig** on RHEL/SUSE. Supports review mode (audit-only) and enforce mode.

## :warning: SAFETY — read before setting a GRUB password

A wrong GRUB password can **lock the machine out of boot**. This role applies a password **only** when `boot_hardening_grub_password_hash` is a non-empty, pre-hashed PBKDF2 value. The default is empty, so the password step is **skipped**. This role **never** generates or sets a plaintext password.

Generate a hash on the target's GRUB tooling and copy the full `grub.pbkdf2.sha512...` string:

```bash
grub2-mkpasswd-pbkdf2   # RHEL/SUSE
grub-mkpasswd-pbkdf2    # Debian/Ubuntu
```

Pass it (e.g. via Vault) as `boot_hardening_grub_password_hash`. Test booting before relying on it.

## Requirements

- Ansible >= 2.16
- Collection: `malpanez.security`

## Role Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `boot_hardening_enabled` | `false` | Gate variable. Set `true` with `security_mode: enforce` to apply changes. Review tasks always run. |
| `boot_hardening_grub_superuser` | `admin` | GRUB superuser name (used only when a password hash is set). |
| `boot_hardening_grub_password_hash` | `""` | Pre-hashed PBKDF2 password. **Empty = no password set (safe default).** Never a plaintext value. |
| `boot_hardening_cfg_mode` | `"0600"` | Permissions enforced on the generated `grub.cfg`. |
| `boot_hardening_disable_os_prober` | `true` | Set `GRUB_DISABLE_OS_PROBER=true` in the GRUB default file. |
| `boot_hardening_disable_recovery` | `false` | Set `GRUB_DISABLE_RECOVERY` in the GRUB default file. |

## OS support

| OS family | grub.cfg | Regenerate command |
|-----------|----------|--------------------|
| RedHat, Suse | `/boot/grub2/grub.cfg` | `grub2-mkconfig -o <cfg>` |
| Debian | `/boot/grub/grub.cfg` | `update-grub` |

In containers there is no bootloader, so all bootloader changes are skipped; the role still runs its review tasks.

## Example Playbook

```yaml
- name: Harden the bootloader
  hosts: all
  roles:
    - role: malpanez.security.boot_hardening
      vars:
        boot_hardening_enabled: true
        security_mode: enforce
        boot_hardening_disable_recovery: true
        # boot_hardening_grub_password_hash: "{{ vault_grub_pbkdf2 }}"
```

## Compliance

CIS 1.4.x (bootloader), NIST CM-6 (configuration settings).

## License

Apache-2.0
