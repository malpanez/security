# Security and Quality Status

This document summarizes the actual state of the repository and separates what is implemented from what is planned.

## Implemented (in this repo)

- Hardening roles: `sshd_hardening`, `pam_mfa`, `sudoers_baseline`, `selinux_enforcement`, `audit_logging`.
- Capability detection: `security_capabilities` (OpenSSH + PAM U2F/FIDO2 + SELinux).
- Evidence: `compliance_evidence` generates artifacts in `compliance_evidence_output_dir` (default: `/var/log/compliance`).
- Execution modes: `security_mode=review` avoids changes; `security_mode=enforce` applies changes.
- Backups and rollback: tasks in `tasks/backup-configs.yml` and `tasks/rollback.yml`.
- Local testing:
  - Molecule per role (`roles/*/molecule/default/`).
  - Full-stack scenario (`molecule/complete_stack`).
  - Basic chaos scenario (`molecule/chaos`).
  - Template property tests in `tests/property_tests/`.
- Local validation: `scripts/validate-all.sh` (lint, syntax, basic security checks).
- CI/CD workflows: `.github/workflows/*.yml` (lint, tests, scans, quality gates, etc.).
- Secret scanning: `gitleaks` with configuration in `.gitleaks.toml`.
- Supply-chain: `requirements.yml` with pinned collection versions for reproducibility.
- Supply-chain: Docker images pinned by digest in workflows and testing scripts.

## Not implemented / outside the repo

- Renovate App and automatic dashboards (requires installation on GitHub).
- SBOM in CI via `security-scan.yml` (syft + grype); no signatures/provenance.
- Observability (metrics, dashboards).
- Drift detection/continuous compliance.
- Secrets integration (Vault/SM/Infisical).
- Transactional atomicity (real 2PC).

## Recommended local validation

```bash
./scripts/validate-all.sh
molecule test -s complete_stack
molecule test -s chaos
```

## Current risks and limits

- The "review/dry-run" playbooks do not generate their own diffs; they depend on `security_mode` and `--check/--diff`.
- `sudoers_baseline` only applies changes if `sudoers_baseline_strict=true`; there is no hybrid mode in the role.
- `sshd_hardening` writes a complete `/etc/ssh/sshd_config` by default; it can use `sshd_config.d` when `sshd_hardening_use_dropin=true` and the Include is present.
- `pam_mfa` can use `pam_fido2` or `pam_u2f` depending on availability and `pam_mfa_primary_module` (auto by default).

## Suggested next steps

- Maintain existing CI/CD workflows and document which jobs are mandatory.
- Complete end-to-end tests and expand chaos/property tests.
- Define a secrets strategy and record the actual implementation.
