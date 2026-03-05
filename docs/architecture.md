# Hardening and Access Control Architecture

## Components
- ssh_hardening: configures sshd with CA, secure algorithms and role-based restrictions.
- pam_mfa: MFA with YubiKey (FIDO2/U2F) and fallback TOTP.
- sudoers_baseline: least privilege, auditable defaults.
- selinux_enforcement: enables SELinux and applies booleans/contexts.
- service_accounts_transfer: service accounts with forced commands and restrictions.
- audit_logging: auditd rules for SSH/sudo/config.
- compliance_evidence: collection of artifacts and control outputs.

## Flows
- Human access: sshd trusts CA, requires MFA (pam_mfa) and applies sudoers by group.
- Service accounts: certificates/keys with restrictions, ForceCommand and AllowUsers/AllowGroups by role.
- SELinux: configurable mode, defined booleans/contexts.
- Evidence: stored in `compliance_evidence_output_dir` (default: `/var/log/compliance`).
