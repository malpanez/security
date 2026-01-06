# Arquitectura de hardening y control de acceso

## Componentes
- ssh_hardening: configura sshd con CA, algoritmos seguros y restricciones por rol.
- pam_mfa: MFA con YubiKey (FIDO2/U2F) y TOTP de contingencia.
- sudoers_baseline: mínimos privilegios, defaults auditables.
- selinux_enforcement: habilita SELinux y aplica booleans/contexts.
- service_accounts_transfer: cuentas de servicio con comandos forzados y restricciones.
- audit_logging: reglas de auditd para SSH/sudo/config.
- compliance_evidence: recogida de artefactos y outputs de control.

## Flujos
- Acceso humano: sshd confía en CA, exige MFA (pam_mfa) y aplica sudoers según grupo.
- Cuentas de servicio: certificados/keys con restricciones, ForceCommand y AllowUsers/AllowGroups según rol.
- SELinux: modo configurable, booleans/context definidos.
- Evidencias: se almacenan en `compliance_evidence_output_dir` (default: `/var/log/compliance`).
