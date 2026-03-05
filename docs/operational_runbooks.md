# Operational Runbooks

## Break-glass / MFA
- Temporarily disable MFA: set `pam_mfa_enabled=false` in inventory/vars, apply the play. Revert to true after the incident.
- Contingency group: `pam_mfa_breakglass_group` allows backup TOTP and bypasses U2F; revoke members after use.

## YubiKey / FIDO2 Enrolment
- Register keys in `pam_mfa_u2f_keys_path` or the configured authfile.
- Verify that PAM does not lock service accounts (controlled bypass in defaults).
 - `pam_mfa_primary_module=auto` uses pam_fido2 if the module is available.

## TOTP Recovery
- Enable TOTP backup (`pam_mfa_totp_enabled=true`) only for `pam_mfa_totp_allowed_group`.
- Rotate secrets after use.

## SELinux
- Phase in with `selinux_enforcement_enabled` and `selinux_enforcement_mode` (permissive → enforcing).
- Restore contexts with `selinux_enforcement_contexts` + `restorecon`.

## Sudoers
- Adjust groups/commands in `sudoers_baseline_groups`; validate with `visudo -cf`.
- Do not use `NOPASSWD:ALL`; enforce `use_pty` and `logfile`.

## Service Accounts
- Define accounts in `service_accounts_transfer_accounts` with `allow_from`, `command`, chroot.
- Review authorized_keys with restrictions and cert TTL if applicable.

## Evidence
- Run the `compliance_evidence` role to generate artifacts in `compliance_evidence_output_dir`.
