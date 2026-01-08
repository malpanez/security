# Evidence Pack

Generado por el rol `compliance_evidence` (configurable con `compliance_evidence_output_dir`, default: `/var/log/compliance`).

Incluye:
- Copias de configuración: `sshd_config`, `sudoers`, `audit_rules` (archivado si es directorio).
- Salida de comandos: `sestatus`, `pam_chain`, `pam_auth_update`, `sshd_effective_auth`, `sudoers_summary`, otros definidos en defaults.
- Se nombra por host: `<host>-<artefacto>`.
- Manifest de integridad: `evidence.sha256` con hashes SHA256.

Reproducción:
1. Establecer `compliance_evidence_enabled=true`.
2. Ejecutar play que incluya el rol `compliance_evidence`.
3. Revisar artefactos en el directorio configurado.
