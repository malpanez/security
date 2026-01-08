# Runbooks: FIDO2/SK Keys y MFA

## Enrolment SK keys (MODE_A)
- Generar key en cliente: `ssh-keygen -t ed25519-sk -O resident -O verify-required -C user@host`.
- Distribuir cert/CA según `sshd_hardening_trusted_ca_key` y asignar grupos humanos (`security_capabilities_human_groups`).
- Si se requiere MFA adicional, habilitar `security_capabilities_mfa_for_humans_even_with_sk_keys=true`.
- Para rollout gradual de SK-only, usar `sshd_hardening_human_pubkey_accepted_algorithms` en Match Group.

## PAM MFA (MODE_B)
- Habilitar `security_capabilities_auth_mode=pam_mfa` o dejar auto en legacy con pam_u2f/pam_fido2 detectado.
- Registrar YubiKey en `pam_mfa_u2f_keys_path`; configurar TOTP breakglass si `security_capabilities_totp_breakglass_enabled=true` y grupo `mfa-breakglass`.
- Service accounts quedan exentas por Match Group (solo publickey).
 - `pam_mfa_primary_module=auto` usa pam_fido2 si el módulo existe; si no, usa pam_u2f.

## Legacy (MODE_C)
- Se mantienen `PasswordAuthentication no`; service accounts con `restrict`, ForceCommand, no TTY/forwarding; documentar compensatorios.
- Considerar migrar a SK o PAM tan pronto como sea viable.

## Rotación y break-glass
- Revocar keys en authorized_keys o CA; reenrolar YubiKeys/TOTP y rotar secrets tras uso.
- Breakglass: añadir temporalmente al grupo `mfa-breakglass`, se omite U2F y se permite TOTP; retirar y rotar al finalizar.

## Debian 13 sudo TOTP
- Ver `docs/debian13-authentication-runbook.md` para el stack sudo-only con drop-in SSHD.
