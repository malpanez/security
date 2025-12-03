# Evidence Pack

Generado por el rol `compliance_evidence` (configurable con `compliance_evidence_output_dir`).

Incluye:
- Copias de configuración: sshd_config, sudoers, audit rules, PAM/SELinux según se añadan.
- Salida de comandos: `sestatus`, otros checks definidos.
- Se nombra por host: `<host>-<artefacto>`.

Reproducción:
1. Establecer `compliance_evidence_enabled=true`.
2. Ejecutar play que incluya el rol `compliance_evidence`.
3. Revisar artefactos en el directorio configurado.
