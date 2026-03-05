## Generated evidence

Base output in `compliance_evidence_output_dir` (default: `/var/log/compliance`).

- `capabilities.json` and `capabilities.md`: OpenSSH version, detected capabilities, chosen mode.
- `sshd_effective_policy.md`: summary of Match blocks and AuthenticationMethods.
- `selinux_status.md`: output of `sestatus` (if applicable).
- Copies or packaged archives of paths (`sshd_config`, `sshd_config.d`, `sudoers`, `pam.d/sudo`, `pam.d/mfa-totp`, `audit_rules`), with rules loaded in `auditctl -l` if applicable.
- Command outputs in `.log` files (for example `pam_chain`, `sudoers_summary`).
- `evidence.sha256`: SHA256 hash manifest for evidence traceability.

> Does not include secrets; only configurations and states.
