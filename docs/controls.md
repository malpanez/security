# Controls vs Frameworks (PCI-DSS, HIPAA, SOC2, FedRAMP)

| Domain | Technical control | Evidence | Frameworks |
| --- | --- | --- | --- |
| SSH access | SK keys/MFA (`security_capabilities`, `sshd_hardening`, `pam_mfa`) | capabilities.md/json, sshd_effective_policy.md, pam_chain.log | PCI 7/8, HIPAA 164.312(a)(c), SOC2 CC6/CC7, FedRAMP AC-2/AC-3 |
| Service accounts | ForceCommand/chroot/allow_from (`service_accounts_transfer`) | sshd_effective_policy.md, authorized_keys evidence | PCI 2/7/8, SOC2 CC6/CC7, FedRAMP AC-6 |
| Sudoers | Least privilege, use_pty (`sudoers_baseline`, `cis_baseline`) | sudoers_summary, audit rules | PCI 7, SOC2 CC6, FedRAMP AC-6 |
| SELinux | Enforcing/contexts (`selinux_enforcement`) | selinux_status.md | FedRAMP AC/SC, SOC2 CC7 |
| Audit | auditd rules (`audit_logging`) | audit_rules, logs | PCI 10, HIPAA 164.312(b), SOC2 CC7, FedRAMP AU-* |
| CIS optional | Checks/enforce minimums (`cis_baseline`) | cis_review asserts / visudo | CIS L1 alignment (partial) |

> Supports compliance, does not guarantee certification. Adjust controls per environment and maintain traceability in `compliance_evidence_output_dir` (default: `/var/log/compliance`).
