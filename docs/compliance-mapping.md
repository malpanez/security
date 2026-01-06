# Compliance Mapping (informativo, no certifica)

| Control técnico | Evidencia | Marcos (ejemplos) |
| --- | --- | --- |
| SSH CA + MFA + restricciones de service accounts | `compliance_evidence_output_dir/*sshd*`, PAM configs, audit logs | NIST 800-53 AC/IA, PCI DSS Req 7/8, SOC2 CC6/CC7, HIPAA 164.312(a)(b)(c) |
| Sudoers mínimo privilegio + logging | `/etc/sudoers`, sudo log, audit rules | NIST AC-6, PCI Req 7, SOC2 CC6 |
| SELinux enforcing | `sestatus`, contextos, booleans | NIST SC/CM, PCI Req 2, SOC2 CC7 |
| Auditd reglas | `/etc/audit/rules.d/`, logs | NIST AU, PCI Req 10, SOC2 CC7 |
| Evidencias recopiladas | `compliance_evidence_output_dir` (default: `/var/log/compliance`) | Soporte a auditoría (no certifica) |

> Nota: Esto soporta cumplimiento; no garantiza certificación.
