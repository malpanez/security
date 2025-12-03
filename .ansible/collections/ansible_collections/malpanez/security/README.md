# Ansible Collection - malpanez.security

Colección orientada a endurecer la configuración de SSH.

## Roles (qué hace cada uno)

- `malpanez.security.security_capabilities`: detecta versión de OpenSSH/capacidades (SK keys, PAM, SELinux) y selecciona modo de autenticación.
- `malpanez.security.sshd_hardening`: aplica parámetros seguros en `sshd_config` y asegura que el servicio esté en marcha.
- `malpanez.security.pam_mfa`: configura MFA con YubiKey (U2F/FIDO2) y TOTP de contingencia, con bypass controlado para cuentas de servicio.
- `malpanez.security.sudoers_baseline`: sudoers mínimo privilegio y defaults auditables.
- `malpanez.security.selinux_enforcement`: habilita y configura SELinux, booleans y contextos.
- `malpanez.security.service_accounts_transfer`: cuentas de servicio (SFTP/rsync) con restricciones y ForceCommand.
- `malpanez.security.audit_logging`: reglas auditd para SSH/sudo/config.
- `malpanez.security.compliance_evidence`: recopila evidencias en `reports/`.

## Uso rápido

```yaml
- hosts: all
  become: true
  roles:
    - role: malpanez.security.sshd_hardening
      vars:
        sshd_hardening_password_authentication: false
        sshd_hardening_allow_users:
          - admin
```

## Variables clave

- `sshd_hardening_password_authentication`: habilita autenticación por contraseña (default: `false`).
- `sshd_hardening_permit_root_login`: control de login de root (`no`, `prohibit-password`, `yes`; default: `no`).
- Algoritmos: controlados por `sshd_hardening_algorithm_profile` y `sshd_hardening_algorithm_sets` (ciphers, MACs, KEX, hostkey) para compatibilidad según versión de OpenSSH.
- `sshd_hardening_allow_users` / `sshd_hardening_allow_groups`: listas explícitas de acceso.
- `sshd_hardening_client_alive_interval` / `sshd_hardening_client_alive_count_max`: keepalives y desconexión de sesiones inactivas.
- Otras opciones endurecidas: `sshd_hardening_max_auth_tries`, `sshd_hardening_max_sessions`, `sshd_hardening_max_startups`, `sshd_hardening_use_dns`, `sshd_hardening_compression`, `sshd_hardening_banner`, `sshd_hardening_log_level`, `sshd_hardening_hostkey_algorithms`.
- `sshd_hardening_algorithm_profile`: `auto` selecciona algoritmos modernos salvo que se detecte OpenSSH < 7.8 (ej. RHEL7), en cuyo caso usa el set `legacy`. Puedes forzar `modern`/`legacy` o sobreescribir `sshd_hardening_algorithm_sets`.
- `sshd_hardening_trusted_ca_key`/`sshd_hardening_trusted_ca_path`: habilitan TrustedUserCAKeys para certificados SSH.
- `sshd_hardening_human_groups` / `sshd_hardening_service_groups`: definen Match blocks para exigir MFA a humanos (publickey+keyboard-interactive) y restringir cuentas de servicio a publickey sin TTY/forwarding.

Consulta `roles/sshd_hardening/meta/argument_specs.yml` para el catálogo completo de opciones.
