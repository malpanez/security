# Action Plan (seguridad y calidad)

Plan corto y ejecutable basado en estado real del repo.

## Prioridad P0 (bloqueante)

1) **Rollback/lockout en playbooks por defecto.**
   - `playbooks/site.yml` y `playbooks/enforce-*.yml` deben incluir `tasks/backup-configs.yml` y gatillar `tasks/rollback.yml` ante validaciones fallidas.
   - Requisito: SSH/PAM/sudoers/SELinux con pre-checks + validación + rollback automático.

2) **Corrección de detección de versión OpenSSH.**
   - Reemplazar comparación `float` por `version()` para evitar `7.10` → `7.1`.
   - Impacto: selección correcta de perfiles `modern/legacy`.

3) **Validación real de PAM.**
   - Sustituir `grep -q` por checks estructurales y pruebas de autenticación controladas.
   - Agregar backup explícito de `/etc/pam.d/sudo` antes de cambios.

4) **Auditd: verificación de reglas cargadas.**
   - No silenciar errores en `augenrules --load`; fallar si no carga.
   - Verificar que `auditctl -l` contiene reglas esperadas.

## Prioridad P1 (alta)

5) **Check mode real.**
   - Evitar `command`/`shell` que ejecutan cambios en `--check`.
   - Añadir guards de `ansible_check_mode` o `check_mode: no` justificados.

6) **Claims vs realidad.**
   - Consolidar claims “TOP 0.1% / TOP 0.01% / battle-tested” como aspiracionales.
   - Mantener una sola fuente de verdad: `README.md#Feature-Status`.

7) **MFA bypass controlado.**
   - `pam_mfa_service_bypass_allow_from` debe aplicarse o eliminarse.
   - Definir scoping por origen o grupo para evitar bypass global.

## Prioridad P2 (media)

8) **Tests de regresión lockout.**
   - Añadir verificaciones de re-login (sshd + sudoers + PAM) en Molecule.
   - Crear escenarios negativos (bloqueo simulado con rollback).

9) **Supply chain.**
   - Pin explícito por versión/digest en Galaxy (`requirements.yml`) o justificar rangos.
   - Validar checksums en scripts de descarga.

## Definición de “DONE”

- Playbooks por defecto con backup + validación + rollback automático.
- Detección de OpenSSH correcta para 7.10+.
- PAM con precheck + validación real y backup completo.
- Auditd cargado y verificado.
- Claims documentales marcados como aspiracionales o respaldados con evidencia.
