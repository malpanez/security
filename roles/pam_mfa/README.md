# pam_mfa

Configures multi-factor authentication (MFA) via PAM using YubiKey/FIDO2 hardware tokens as the primary factor and TOTP (Google Authenticator) as a backup. Restricts MFA to human user groups, exempts service accounts, and integrates with SSH and sudo authentication chains.

Supports a **Debian 13 sudo-only TOTP stack** (substack file + `pam-auth-update`) for modern Debian deployments.

> **Warning**: Test in review mode on a staging host before enabling enforce mode. Misconfiguration can lock all users out of the system.

## Platform Support

| OS Family | Notes |
|-----------|-------|
| Debian / Ubuntu | pam-auth-update stack; Debian 13 mode uses substack |
| RHEL / Rocky / Alma | authselect integration |
| SUSE / openSUSE | pam_u2f / pam_fido2 direct configuration |

## What It Configures

| Area | Detail |
|------|--------|
| Primary MFA | YubiKey U2F (`pam_u2f`) or FIDO2 (`pam_fido2`), auto-selected |
| Backup MFA | TOTP via `pam_google_authenticator` |
| Human groups | Groups in `pam_mfa_human_groups` require MFA |
| Service bypass | Accounts in `pam_mfa_service_accounts` bypass MFA |
| Breakglass | Members of `pam_mfa_breakglass_group` can use TOTP when hardware key unavailable |
| Sudo integration | Substack file for sudo-only TOTP (Debian 13 mode) |
| Faillock | Optional `pam_faillock` integration for lockout enforcement |

## Modes

| Mode | Behaviour |
|------|-----------|
| `review` (default) | Skip all PAM changes |
| `enforce` | Deploy PAM configuration for human groups |

MFA is also activated when `security_capabilities_selected_auth_mode` (set by `malpanez.security.security_capabilities`) is `pam_mfa` or `sk_keys` with `security_capabilities_mfa_for_humans_even_with_sk_keys: true`.

## Role Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `security_mode` | `review` | Set to `enforce` to apply changes |
| `pam_mfa_enabled` | `false` | Enable PAM MFA (required gate) |
| `pam_mfa_method_primary` | `yubikey` | Primary MFA method (`yubikey`) |
| `pam_mfa_method_backup` | `totp` | Backup MFA method (`totp`) |
| `pam_mfa_primary_module` | `auto` | PAM module: `auto`, `u2f`, or `fido2` |
| `pam_mfa_human_groups` | `[humans]` | Groups requiring MFA |
| `pam_mfa_service_accounts` | `[ansible, ci, sftp, rsync]` | Accounts exempt from MFA |
| `pam_mfa_breakglass_group` | `mfa-breakglass` | Group allowed TOTP fallback |
| `pam_mfa_required_group` | `mfa-required` | Group for sudo TOTP (Debian 13 stack) |
| `pam_mfa_required_users` | `[]` | Users to add to `pam_mfa_required_group` |
| `pam_mfa_service_bypass_group` | `mfa-bypass` | Group bypassing MFA entirely |
| `pam_mfa_service_bypass_allow_from` | `[]` | IP allowlist for service account bypass |
| `pam_mfa_use_debian13_stack` | `false` | Use Debian 13 sudo-only TOTP substack |
| `pam_mfa_enable_su` | `false` | Apply Debian 13 stack to `su` as well |
| `pam_mfa_totp_enabled` | `true` | Enable TOTP backup |
| `pam_mfa_totp_allowed_group` | `mfa-breakglass` | Group allowed TOTP use |
| `pam_mfa_totp_rate_limit` | `true` | Enable TOTP rate limiting |
| `pam_mfa_totp_rate_limit_count` | `3` | Max TOTP attempts per window |
| `pam_mfa_totp_secret_base` | `/var/lib/pam-google-authenticator` | Base dir for TOTP secrets (Debian 13) |
| `pam_mfa_totp_secret_file` | `.../%u/.google_authenticator` | TOTP secret path template (Debian 13) |
| `pam_mfa_totp_allowed_perm` | `0400` | Permission mode for TOTP secrets |
| `pam_mfa_totp_owner` | `root` | Owner of TOTP secret files |
| `pam_mfa_totp_group` | `root` | Group of TOTP secret files |
| `pam_mfa_u2f_keys_path` | `/etc/Yubico/u2f_keys` | U2F/FIDO2 keys directory |
| `pam_mfa_fido2_authfile` | `/etc/fido2/authorized_fido2` | FIDO2 authorized keys file |
| `pam_mfa_totp_dir` | `/etc/google-authenticator.d` | TOTP secrets directory |
| `pam_mfa_rhel_authselect_profile` | `minimal` | Authselect profile (RHEL 8+) |
| `pam_mfa_rhel_authselect_features` | `[]` | Authselect features to enable |
| `pam_mfa_enable_faillock` | `false` | Enable pam_faillock (Debian 13 stack) |
| `pam_mfa_faillock_deny` | `5` | Lockout after N failures |
| `pam_mfa_faillock_unlock_time` | `900` | Lockout duration in seconds |
| `pam_mfa_faillock_fail_interval` | `900` | Failure counting window in seconds |
| `pam_mfa_pam_module_u2f` | `/lib/security/pam_u2f.so` | Path to pam_u2f.so |
| `pam_mfa_pam_module_fido2` | `/lib/security/pam_fido2.so` | Path to pam_fido2.so |
| `pam_mfa_pam_module_google_authenticator` | `/lib/security/pam_google_authenticator.so` | Path to pam_google_authenticator.so |
| `pam_mfa_sudo_substack_name` | `mfa-totp` | PAM substack file name for sudo (Debian 13) |
| `pam_mfa_enable_deadman_switch` | `true` | Abort if module validation fails |
| `pam_mfa_validation_timeout` | `300` | Seconds to wait for manual validation |
| `pam_mfa_skip_module_validation` | `false` | Skip validation checks (testing only) |

## Dependencies

None required. Optionally reads `security_capabilities_selected_auth_mode` and `security_capabilities_mfa_for_humans_even_with_sk_keys` facts from `malpanez.security.security_capabilities`.

## Example Playbook

```yaml
# Standard MFA for human users (YubiKey primary, TOTP backup)
- hosts: all
  vars:
    security_mode: enforce
    pam_mfa_enabled: true
    pam_mfa_human_groups:
      - linux-admins
      - developers
    pam_mfa_service_accounts:
      - ansible
      - ci
    pam_mfa_breakglass_group: mfa-breakglass
  roles:
    - role: malpanez.security.pam_mfa

# Debian 13 sudo-only TOTP stack
- hosts: debian
  vars:
    security_mode: enforce
    pam_mfa_enabled: true
    pam_mfa_use_debian13_stack: true
    pam_mfa_required_users:
      - alice
      - bob
  roles:
    - role: malpanez.security.pam_mfa
```

## Testing with Molecule

```bash
cd roles/pam_mfa
molecule test
```

Tests verify: PAM modules installed, breakglass group created, service accounts excluded from MFA stack, TOTP rate limit configured.

## Compliance Mapping

| Control | Framework |
|---------|-----------|
| MFA for interactive users | NIST 800-53 IA-2(1), PCI-DSS 8.4.2, NIS2 Art.21(2)(i) |
| Hardware token authentication | NIST 800-63B AAL2, DISA STIG |
| Service account exemption | NIST 800-53 IA-5(6) |
| Account lockout | CIS 5.4.2, NIST 800-53 AC-7 |
| Breakglass access | NIST 800-53 IA-2(3), CIS 5.4 |

## License

MIT

## Author

Miguel Alpañez
