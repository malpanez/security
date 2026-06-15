# security_capabilities

Detects system security capabilities at runtime — OpenSSH version, available PAM MFA modules, SELinux availability — and selects the optimal authentication mode. Publishes its results as Ansible facts consumed by downstream roles (`sshd_hardening`, `pam_mfa`, `service_accounts_transfer`).

This role is designed to run **first** in the hardening playbook so that all subsequent roles can make capability-aware decisions without duplicating detection logic.

## Platform Support

Debian, Ubuntu, RHEL, Rocky, Alma, SUSE, openSUSE — detection is platform-agnostic.

## What It Detects

| Capability | Fact Key | Condition |
|------------|----------|-----------|
| OpenSSH version | `security_capabilities.openssh_version_detected` | Package facts |
| SK key support (FIDO2) | `security_capabilities.openssh_supports_sk_keys` | OpenSSH >= 8.2 |
| sshd_config.d include support | `security_capabilities.supports_sshd_include_d` | OpenSSH >= 8.2 |
| pam_u2f available | `security_capabilities.pam_u2f_available` | `libpam-u2f` or `pam_u2f` in packages |
| pam_fido2 available | `security_capabilities.pam_fido2_available` | `libpam-fido2` or `pam_fido2` in packages |
| SELinux available | `security_capabilities.selinux_available` | `os_family == 'RedHat'` |
| MFA capable | `security_capabilities.mfa_capable` | Any MFA PAM module installed |

## Authentication Mode Selection

The selected mode is published as `security_capabilities_selected_auth_mode` and consumed by `sshd_hardening` and `pam_mfa`:

| Mode | Condition |
|------|-----------|
| `sk_keys` | OpenSSH >= 8.2 (hardware FIDO2/U2F resident keys) |
| `pam_mfa` | pam_u2f or pam_fido2 installed, OpenSSH < 8.2 |
| `legacy` | No MFA modules detected |

Override automatic selection with `security_capabilities_force_mode` or `security_capabilities_auth_mode`.

## Role Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `security_capabilities_auth_mode` | `auto` | Mode selection strategy: `auto`, `sk_keys`, `pam_mfa`, `legacy` |
| `security_capabilities_force_mode` | `""` | Override auto-detection (empty = respect auto) |
| `security_capabilities_force_openssh_version` | `""` | Override detected OpenSSH version (for testing) |
| `security_capabilities_human_groups` | `[linux-admins, devops]` | Unix groups for human users requiring MFA |
| `security_capabilities_service_groups` | `[svc-automation, svc-transfer]` | Unix groups for service accounts |
| `security_capabilities_mfa_for_humans_even_with_sk_keys` | `false` | Require PAM MFA even when SK keys are available |
| `security_capabilities_totp_breakglass_enabled` | `true` | Enable TOTP fallback when hardware keys unavailable |
| `security_capabilities_pkg_names` | See below | OpenSSH package names per distribution |

Default package name map:

```yaml
security_capabilities_pkg_names:
  debian: openssh-server
  ubuntu: openssh-server
  redhat: openssh-server
  rocky: openssh-server
  centos: openssh-server
```

## Published Facts

After execution the following facts are available to all subsequent roles:

| Fact | Type | Description |
|------|------|-------------|
| `security_capabilities` | dict | Full capability map (see above) |
| `security_capabilities_selected_auth_mode` | str | Selected auth mode (`sk_keys`/`pam_mfa`/`legacy`) |
| `security_selected_auth_mode` | str | Backward-compatible alias |
| `security_capabilities_mfa_capable` | bool | True when any MFA PAM module is installed |
| `security_capabilities_yubikey_available` | bool | True when YubiKey/FIDO2 PAM module is installed |
| `security_capabilities_human_groups` | list | Forwarded from variable for downstream consumption |
| `security_capabilities_service_groups` | list | Forwarded from variable for downstream consumption |

## Dependencies

None.

## Example Playbook

```yaml
# Detect capabilities and let downstream roles auto-configure
- hosts: all
  roles:
    - role: malpanez.security.security_capabilities
    - role: malpanez.security.sshd_hardening
    - role: malpanez.security.pam_mfa
    - role: malpanez.security.service_accounts_transfer

# Force a specific mode (e.g., testing PAM MFA on an OpenSSH 8.9 host)
- hosts: all
  vars:
    security_capabilities_force_mode: pam_mfa
    security_capabilities_human_groups:
      - linux-admins
    security_capabilities_service_groups:
      - svc-deploy
  roles:
    - role: malpanez.security.security_capabilities
    - role: malpanez.security.pam_mfa
```

## Compliance Mapping

| Control | Framework |
|---------|-----------|
| MFA capability assessment | NIST 800-53 IA-2(1), PCI-DSS 8.4.2 |
| Continuous configuration awareness | NIST 800-53 CM-8, CIS Control 1 |
| Least-privilege auth mode selection | NIST 800-53 AC-17, NIS2 Art.21(2)(i) |

## License

Apache-2.0

## Author

Miguel Alpañez
