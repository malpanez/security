# Action Plan (Seguridad y calidad)

Plan corto y ejecutable basado en el estado actual del repo.

## Prioridad P0 (bloqueante)

1) Alinear documentación con comportamiento real.
   - Fuentes de verdad: `roles/*/defaults/main.yml`, `roles/*/tasks/*`, `meta/argument_specs.yml`.
   - Marcar como “plan” todo lo que no exista en código.

2) Corregir defaults inseguros en `sudoers_baseline`.
   - Revisar `sudoers_baseline_defaults` y eliminar opciones peligrosas (`!authenticate`, `requiretty`).
   - Añadir tests de plantilla para defaults seguros.

3) Definir reglas auditd reales o documentar su ausencia.
   - Establecer `audit_logging_rules` con reglas mínimas (SSH, sudo, config).
   - Si se deja vacío, documentar explícitamente “solo instala auditd”.

## Prioridad P1 (alta)

4) End-to-end tests realistas.
   - Expandir `molecule/complete_stack/verify.yml` con casos de login reales.
   - Añadir property tests para PAM y audit rules.

5) Secretos.
   - Documentar claramente que no hay integración.
   - Seleccionar backend (Vault/SM/Infisical) y definir interfaz.

6) CI mínimo viable.
   - Añadir workflows para lint + molecule (1-3 plataformas).
   - Documentar límites y tiempos.

## Prioridad P2 (media)

7) Observabilidad.
   - Métricas de ejecución (tiempo, fallos, cambios).
   - Logging estructurado para playbooks críticos.

8) Atomicidad.
   - Diseñar wrapper transaccional (staging + validate + commit).
   - Tests de rollback.

## Definición de “DONE”

- Documentación sin “features fantasma”.
- Defaults seguros en todos los roles.
- Tests mínimos para lockout-prevention.
- CI básico funcionando.
