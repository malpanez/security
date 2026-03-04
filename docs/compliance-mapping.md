# Compliance Mapping (informational, does not certify)

| Technical control | Evidence | Frameworks (examples) |
| --- | --- | --- |
| SSH CA + MFA + service account restrictions | `compliance_evidence_output_dir/*sshd*`, PAM configs, audit logs | NIST 800-53 AC/IA, PCI DSS Req 7/8, SOC2 CC6/CC7, HIPAA 164.312(a)(b)(c) |
| Sudoers least privilege + logging | `/etc/sudoers`, sudo log, audit rules | NIST AC-6, PCI Req 7, SOC2 CC6 |
| SELinux enforcing | `sestatus`, contexts, booleans | NIST SC/CM, PCI Req 2, SOC2 CC7 |
| Auditd rules | `/etc/audit/rules.d/`, logs | NIST AU, PCI Req 10, SOC2 CC7 |
| Collected evidence | `compliance_evidence_output_dir` (default: `/var/log/compliance`) | Audit support (does not certify) |

> Note: This supports compliance; it does not guarantee certification.
