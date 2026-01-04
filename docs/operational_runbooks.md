# Operational Runbooks

## Break-glass / MFA
- Deshabilitar temporalmente MFA: `pam_mfa_enabled=false` en inventario/vars, aplicar play. Revertir a true tras incident.
- Grupo de contingencia: `pam_mfa_breakglass_group` permite TOTP de backup y omite U2F; revocar miembros tras uso.

## Enrolment YubiKey / FIDO2
- Registrar claves en `pam_mfa_u2f_keys_path` o authfile configurado.
- Verificar PAM no bloquea cuentas de servicio (bypass controlado en defaults).
 - `pam_mfa_primary_module=auto` usa pam_fido2 si el módulo está disponible.

## Recuperación TOTP
- Habilitar TOTP backup (`pam_mfa_totp_enabled=true`) solo para `pam_mfa_totp_allowed_group`.
- Rotar secretos tras uso.

## SELinux
- Fasear con `selinux_enforcement_enabled` y `selinux_enforcement_mode` (permissive → enforcing).
- Restaurar contextos con `selinux_enforcement_contexts` + `restorecon`.

## Sudoers
- Ajustar grupos/comandos en `sudoers_baseline_groups`; validar con `visudo -cf`.
- No usar `NOPASSWD:ALL`; forzar `use_pty` y `logfile`.

## Service Accounts
- Definir cuentas en `service_accounts_transfer_accounts` con `allow_from`, `command`, chroot.
- Revisar authorized_keys con restricciones y TTL de cert si aplica.

## Evidencias
- Ejecutar rol `compliance_evidence` para generar artefactos en `compliance_evidence_output_dir`.
