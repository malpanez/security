## Evidencias generadas

Salida base en `compliance_evidence_output_dir` (default: `/var/log/compliance`).

- `capabilities.json` y `capabilities.md`: versión de OpenSSH, capacidades detectadas, modo elegido.
- `sshd_effective_policy.md`: resumen de Match blocks y AuthenticationMethods.
- `selinux_status.md`: salida de `sestatus` (si aplica).
- Copias o archivos empaquetados de rutas (`sshd_config`, `sudoers`, `audit_rules`), con reglas cargadas en `auditctl -l` si aplica.
- Salidas de comandos en `.log` (por ejemplo `pam_chain`, `sudoers_summary`).

> No incluye secretos; solo configuraciones y estados.
