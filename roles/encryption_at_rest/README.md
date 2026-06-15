# encryption_at_rest

Audit and **evidence** of encryption-at-rest (LUKS / dm-crypt). This role is **audit-first** and **non-destructive**: it reports which block devices are encrypted, flags required mounts that are not encrypted, and hardens crypttab/tooling. Supports review mode (audit-only) and enforce mode.

## Safety / Scope

> **This role NEVER destroys data.**
>
> - It does **not** encrypt an existing root filesystem (that cannot be done idempotently in-place).
> - LUKS formatting only happens for devices explicitly listed in `encryption_at_rest_data_volumes`, **and only** when `encryption_at_rest_allow_format: true`, the host is not a container, the device exists, and the device is currently **empty** (no existing filesystem signature).
> - With the default `encryption_at_rest_allow_format: false`, the format tasks never run and no device is ever touched.
> - Review tasks are read-only (`lsblk`, `stat`, reading `/etc/crypttab`).

## Requirements

- Ansible >= 2.16
- Collection: `malpanez.security` (pulls `community.general` for zypper, `community.crypto` for `luks_device`)
- `cryptsetup` (installed by enforce mode when `encryption_at_rest_install_tools: true`)

## Role Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `encryption_at_rest_enabled` | `false` | Gate variable. Set `true` with `security_mode: enforce` to run hardening. Review tasks always run. |
| `encryption_at_rest_required_mounts` | `[]` | Mounts that SHOULD be encrypted, e.g. `["/", "/var", "swap"]`. Audited only, never modified. |
| `encryption_at_rest_fail_on_unencrypted` | `false` | Fail the play during review if a required mount is not encrypted. Default only reports. |
| `encryption_at_rest_install_tools` | `true` | Ensure the `cryptsetup` package is installed (enforce mode). |
| `encryption_at_rest_crypttab_mode` | `"0600"` | Permissions applied to `/etc/crypttab` when it exists. |
| `encryption_at_rest_data_volumes` | `[]` | List of `{device, name}` dicts eligible for guarded LUKS init, e.g. `[{device: /dev/sdb, name: cryptdata}]`. |
| `encryption_at_rest_allow_format` | `false` | **Hard guard.** LUKS-format a listed data volume ONLY when `true`. |

## Modes

| Mode | Behaviour |
|------|-----------|
| Review (always) | Enumerates block devices, reads `/etc/crypttab`, builds per-mount encryption findings, reports, and (optionally) asserts all required mounts are encrypted. |
| Enforce (`encryption_at_rest_enabled` + `security_mode: enforce`) | Installs `cryptsetup`, tightens `/etc/crypttab` permissions, and — only behind the hard guard — initialises LUKS on listed empty data volumes. |

In containers, runtime device enumeration and LUKS formatting are skipped (block-device state is host-controlled); tooling and crypttab hardening still apply.

## Example Playbook

```yaml
- name: Provide encryption-at-rest evidence
  hosts: all
  roles:
    - role: malpanez.security.encryption_at_rest
      vars:
        encryption_at_rest_enabled: true
        security_mode: enforce
        encryption_at_rest_required_mounts: ["/", "/var", "swap"]
        encryption_at_rest_fail_on_unencrypted: true
        # Guarded LUKS init of a NEW empty data disk (opt-in):
        encryption_at_rest_data_volumes:
          - {device: /dev/sdb, name: cryptdata}
        encryption_at_rest_allow_format: true
```

## Compliance

NIST SC-28 (protection of information at rest), NIS2 Art.21(2)(f) (cryptography and encryption).

## License

Apache-2.0
