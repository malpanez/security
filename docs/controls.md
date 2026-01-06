# Controles vs Marcos (PCI-DSS, HIPAA, SOC2, FedRAMP)

| Dominio | Control técnico | Evidencia | Marcos |
| --- | --- | --- | --- |
| Acceso SSH | SK keys/MFA (`security_capabilities`, `sshd_hardening`, `pam_mfa`) | capabilities.md/json, sshd_effective_policy.md, pam_chain.log | PCI 7/8, HIPAA 164.312(a)(c), SOC2 CC6/CC7, FedRAMP AC-2/AC-3 |
| Cuentas servicio | ForceCommand/chroot/allow_from (`service_accounts_transfer`) | sshd_effective_policy.md, authorized_keys evidencias | PCI 2/7/8, SOC2 CC6/CC7, FedRAMP AC-6 |
| Sudoers | Least privilege, use_pty (`sudoers_baseline`, `cis_baseline`) | sudoers_summary, audit rules | PCI 7, SOC2 CC6, FedRAMP AC-6 |
| SELinux | Enforcing/contexts (`selinux_enforcement`) | selinux_status.md | FedRAMP AC/SC, SOC2 CC7 |
| Audit | auditd reglas (`audit_logging`) | audit_rules, logs | PCI 10, HIPAA 164.312(b), SOC2 CC7, FedRAMP AU-* |
| CIS opcional | Checks/enforce mínimos (`cis_baseline`) | cis_review asserts / visudo | Alineación CIS L1 (parcial) |

> Soporta cumplimiento, no garantiza certificación. Ajusta controles por entorno y conserva trazabilidad en `compliance_evidence_output_dir` (default: `/var/log/compliance`).
