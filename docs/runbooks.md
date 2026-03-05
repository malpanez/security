# Runbooks: FIDO2/SK Keys and MFA

## SK keys Enrolment (MODE_A)
- Generate key on client: `ssh-keygen -t ed25519-sk -O resident -O verify-required -C user@host`.
- Distribute cert/CA according to `sshd_hardening_trusted_ca_key` and assign human groups (`security_capabilities_human_groups`).
- If additional MFA is required, enable `security_capabilities_mfa_for_humans_even_with_sk_keys=true`.
- For a gradual SK-only rollout, use `sshd_hardening_human_pubkey_accepted_algorithms` in Match Group.

## PAM MFA (MODE_B)
- Enable `security_capabilities_auth_mode=pam_mfa` or leave auto on legacy with pam_u2f/pam_fido2 detected.
- Register YubiKey in `pam_mfa_u2f_keys_path`; configure TOTP breakglass if `security_capabilities_totp_breakglass_enabled=true` and group `mfa-breakglass`.
- Service accounts are exempted via Match Group (publickey only).
 - `pam_mfa_primary_module=auto` uses pam_fido2 if the module exists; otherwise uses pam_u2f.

## Legacy (MODE_C)
- Keep `PasswordAuthentication no`; service accounts with `restrict`, ForceCommand, no TTY/forwarding; document compensating controls.
- Consider migrating to SK or PAM as soon as feasible.

## Rotation and break-glass
- Revoke keys in authorized_keys or CA; re-enrol YubiKeys/TOTP and rotate secrets after use.
- Breakglass: temporarily add to the `mfa-breakglass` group, which skips U2F and allows TOTP; remove and rotate when done.

## Debian 13 sudo TOTP
- See `docs/debian13-authentication-runbook.md` for the sudo-only stack with SSHD drop-in.
