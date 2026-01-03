# Ansible Collection - malpanez.security

[![CI (Legacy)](https://github.com/malpanez/security/actions/workflows/ci.yml/badge.svg)](https://github.com/malpanez/security/actions/workflows/ci.yml)
[![CI with UV](https://github.com/malpanez/security/actions/workflows/ci-uv.yml/badge.svg)](https://github.com/malpanez/security/actions/workflows/ci-uv.yml)
[![Quality Gates](https://github.com/malpanez/security/actions/workflows/quality-gates.yml/badge.svg)](https://github.com/malpanez/security/actions/workflows/quality-gates.yml)
[![Security Scan](https://github.com/malpanez/security/actions/workflows/security-scan.yml/badge.svg)](https://github.com/malpanez/security/actions/workflows/security-scan.yml)
[![Docker Test](https://github.com/malpanez/security/actions/workflows/docker-test.yml/badge.svg)](https://github.com/malpanez/security/actions/workflows/docker-test.yml)
[![Molecule Test](https://github.com/malpanez/security/actions/workflows/molecule-test.yml/badge.svg)](https://github.com/malpanez/security/actions/workflows/molecule-test.yml)
[![Molecule Complete Stack](https://github.com/malpanez/security/actions/workflows/molecule-complete-stack.yml/badge.svg)](https://github.com/malpanez/security/actions/workflows/molecule-complete-stack.yml)
[![Molecule Chaos](https://github.com/malpanez/security/actions/workflows/molecule-chaos.yml/badge.svg)](https://github.com/malpanez/security/actions/workflows/molecule-chaos.yml)
[![Enterprise CI/CD](https://github.com/malpanez/security/actions/workflows/ci-cd-enterprise.yml/badge.svg)](https://github.com/malpanez/security/actions/workflows/ci-cd-enterprise.yml)
[![Scorecard](https://github.com/malpanez/security/actions/workflows/scorecard.yml/badge.svg)](https://github.com/malpanez/security/actions/workflows/scorecard.yml)
[![Branch Management](https://github.com/malpanez/security/actions/workflows/branch-management.yml/badge.svg)](https://github.com/malpanez/security/actions/workflows/branch-management.yml)
[![CodeQL](https://github.com/malpanez/security/actions/workflows/codeql.yml/badge.svg)](https://github.com/malpanez/security/actions/workflows/codeql.yml)

> **📋 IMPORTANT**: Los documentos `START_HERE.md`, `EXECUTIVE_SUMMARY.md`, `IMPLEMENTATION_PROMPT.md`, e `IMPLEMENTATION_CHECKLIST.md` son **PLANIFICACIÓN** (roadmap futuro), NO reflejan el estado actual del código v1.0.0.
>
> Para el estado real implementado, ver **[Feature Status](#feature-status)** más abajo.

Colección orientada a hardening de SSH y controles base de seguridad (sudoers, SELinux, auditd y evidencias).

## Feature Status

| Feature | Status | Evidence |
|---------|--------|----------|
| ✅ SSH hardening + validation | **IMPLEMENTED** | [roles/sshd_hardening/tasks/common.yml:122](roles/sshd_hardening/tasks/common.yml#L122) |
| ✅ Sudoers baseline + visudo validation | **IMPLEMENTED** | [roles/sudoers_baseline/tasks/common.yml:14](roles/sudoers_baseline/tasks/common.yml#L14) |
| ✅ PAM MFA with lockout prevention | **IMPLEMENTED** | [roles/pam_mfa/tasks/common_mfa_config.yml](roles/pam_mfa/tasks/common_mfa_config.yml) |
| ✅ SELinux gradual enforcement | **IMPLEMENTED** | [roles/selinux_enforcement/](roles/selinux_enforcement/) |
| ✅ Audit logging (auditd) | **IMPLEMENTED** | [roles/audit_logging/](roles/audit_logging/) |
| ✅ Compliance evidence collection | **IMPLEMENTED** | [roles/compliance_evidence/](roles/compliance_evidence/) |
| ✅ Backup/rollback automation | **IMPLEMENTED** | [tasks/backup-configs.yml](tasks/backup-configs.yml) |
| ✅ Molecule testing per role | **IMPLEMENTED** | 9 roles with molecule/default/ |
| ✅ CI/CD workflows | **IMPLEMENTED** | [.github/workflows/](.github/workflows/) |
| ⚠️ Property-based testing | **PARTIAL** | 1 file (sudoers), not 100+ cases |
| ❌ HashiCorp Vault integration | **PLANNED** | docs only, not in code |
| ❌ Prometheus metrics exporter | **PLANNED** | not implemented |
| ❌ SLSA provenance attestation | **PLANNED** | not implemented |
| ❌ 66 multi-platform tests | **PLANNED** | molecule exists, not 11×6 matrix |

**Audit Score**: 4.2/5 (TOP 20-25%) - See [AUDIT_REPORT.md](AUDIT_REPORT.md) for details

## Workflow Map

Consulta `docs/WORKFLOWS.md` para el diagrama Mermaid de activaciones y dependencias.

## Installation

```bash
ansible-galaxy collection install malpanez.security
```

## Usage

Include the roles you need in your playbook or use the provided playbooks in `playbooks/`.

## Examples

See `examples/` and `playbooks/` for end-to-end scenarios.

## Security

Use `security_mode=review` for audit-only runs and `security_mode=enforce` to apply changes. Los roles que modifican el sistema están condicionados por `security_mode`.

## Contributing

Contributions are welcome. See `CONTRIBUTING.md`.

## License

MIT. See `LICENSE`.

## Roles (qué hace cada uno)

- `malpanez.security.security_capabilities`: detecta versión de OpenSSH/capacidades (SK keys, PAM, SELinux) y selecciona modo de autenticación.
- `malpanez.security.sshd_hardening`: aplica parámetros seguros en `sshd_config` y asegura que el servicio esté en marcha.
- `malpanez.security.pam_mfa`: configura MFA con YubiKey (U2F/FIDO2) y TOTP de contingencia, con bypass controlado para cuentas de servicio.
- `malpanez.security.sudoers_baseline`: sudoers mínimo privilegio y defaults auditables.
- `malpanez.security.selinux_enforcement`: habilita y configura SELinux, booleans y contextos.
- `malpanez.security.service_accounts_transfer`: cuentas de servicio (SFTP/rsync) con restricciones y ForceCommand.
- `malpanez.security.audit_logging`: reglas auditd para SSH/sudo/config.
- `malpanez.security.compliance_evidence`: recopila evidencias en `compliance_evidence_output_dir` (default: `/var/log/compliance`).

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

## Modos de ejecución (review vs enforce)

- Usa `security_mode=review` para evitar cambios disruptivos; los roles que tocan el sistema tienen `when: security_mode == 'enforce'`.
- El playbook `playbooks/review.yml` ejecuta únicamente `security_capabilities` + `compliance_evidence` con `tags: review` para obtener reportes sin tocar servicios.
- Para pasar a enforcement, vuelve a `security_mode=enforce` y ejecuta `playbooks/site.yml`.
- Aprovecha que `service_accounts_transfer` corre antes que `sshd_hardening`: primero define cuentas/certificados, luego `sshd_config` renderiza los `Match` según los facts generados.

## Evidencias

El rol `compliance_evidence` genera artefactos en `compliance_evidence_output_dir` (default: `/var/log/compliance`). Incluye copias de configuración y salidas de comandos definidos en `roles/compliance_evidence/defaults/main.yml`.
