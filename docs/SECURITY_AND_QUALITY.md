# Security and Quality Status

Este documento resume el estado real del repositorio y separa lo implementado de lo planificado.

## Implementado (en este repo)

- Roles de hardening: `sshd_hardening`, `pam_mfa`, `sudoers_baseline`, `selinux_enforcement`, `audit_logging`.
- Detección de capacidades: `security_capabilities` (OpenSSH + PAM U2F/FIDO2 + SELinux).
- Evidencias: `compliance_evidence` genera artefactos en `compliance_evidence_output_dir` (default: `/var/log/compliance`).
- Modos de ejecución: `security_mode=review` evita cambios; `security_mode=enforce` aplica cambios.
- Backups y rollback: tareas en `tasks/backup-configs.yml` y `tasks/rollback.yml`.
- Testing local:
  - Molecule por rol (`roles/*/molecule/default/`).
  - Escenario full-stack (`molecule/complete_stack`).
  - Escenario básico de chaos (`molecule/chaos`).
  - Property tests de plantillas en `tests/property_tests/`.
- Validación local: `scripts/validate-all.sh` (lint, sintaxis, checks básicos de seguridad).
- Workflows CI/CD: `.github/workflows/*.yml` (lint, pruebas, scans, quality gates, etc.).
- Supply-chain: `requirements.yml` con versiones de colecciones fijadas para reproducibilidad.

## No implementado / fuera del repo

- Renovate App y dashboards automáticos (requiere instalación en GitHub).
- SBOM en CI vía `security-scan.yml` (syft + grype); sin firmas/provenance.
- Observabilidad (métricas, dashboards).
- Drift detection/continuous compliance.
- Integración de secretos (Vault/SM/Infisical).
- Atomicidad transaccional (2PC real).

## Validación local recomendada

```bash
./scripts/validate-all.sh
molecule test -s complete_stack
molecule test -s chaos
```

## Riesgos y límites actuales

- Los playbooks de “review/dry-run” no generan diffs propios; dependen de `security_mode` y `--check/--diff`.
- `sudoers_baseline` solo aplica cambios si `sudoers_baseline_strict=true`; no hay modo híbrido en el rol.
- `sshd_hardening` escribe `/etc/ssh/sshd_config` completo por defecto; puede usar `sshd_config.d` cuando `sshd_hardening_use_dropin=true` y el Include está presente.
- `pam_mfa` puede usar `pam_fido2` o `pam_u2f` según disponibilidad y `pam_mfa_primary_module` (auto por defecto).

## Próximos pasos sugeridos

- Mantener workflows CI/CD existentes y documentar qué jobs son obligatorios.
- Completar pruebas end-to-end y ampliar chaos/property tests.
- Definir estrategia de secretos y registrar implementación real.
