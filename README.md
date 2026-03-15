# malpanez.security

[![CI](https://github.com/malpanez/security/actions/workflows/ci-uv.yml/badge.svg)](https://github.com/malpanez/security/actions/workflows/ci-uv.yml)
[![Quality Gates](https://github.com/malpanez/security/actions/workflows/quality-gates.yml/badge.svg)](https://github.com/malpanez/security/actions/workflows/quality-gates.yml)
[![Security Scan](https://github.com/malpanez/security/actions/workflows/security-scan.yml/badge.svg)](https://github.com/malpanez/security/actions/workflows/security-scan.yml)
[![CodeQL](https://github.com/malpanez/security/actions/workflows/codeql.yml/badge.svg)](https://github.com/malpanez/security/actions/workflows/codeql.yml)
[![Molecule](https://github.com/malpanez/security/actions/workflows/molecule-test.yml/badge.svg)](https://github.com/malpanez/security/actions/workflows/molecule-test.yml)

An Ansible collection for Linux security hardening — SSH, MFA, SELinux, sudoers, auditd, and compliance evidence — tested across Debian, Ubuntu, and RHEL-family systems.

Designed to be **audit-ready from day one**: run in review mode first to collect evidence without touching the system, then enforce when ready.

## What it does

| Role | Description |
|------|-------------|
| `security_capabilities` | Auto-detects OpenSSH version and available MFA modules; selects the right authentication mode |
| `sshd_hardening` | Enforces secure `sshd_config`: algorithms, access control, CA trust, Match blocks per user class |
| `pam_mfa` | MFA with YubiKey (FIDO2/U2F) for humans, TOTP as breakglass fallback, bypass for service accounts |
| `sudoers_baseline` | Least-privilege sudoers with visudo validation and auditable defaults |
| `selinux_enforcement` | Enables SELinux, configures booleans and file contexts (RHEL family) |
| `service_accounts_transfer` | SFTP/rsync accounts with ForceCommand, AllowUsers/AllowGroups, and certificate restrictions |
| `audit_logging` | auditd rules covering SSH, sudo, and configuration changes |
| `compliance_evidence` | Collects configuration snapshots and command outputs to `/var/log/compliance` |

## Authentication mode auto-selection

The `security_capabilities` role detects your environment and picks the right authentication mode automatically:

| Mode | Trigger | MFA method |
|------|---------|------------|
| `sk_keys` | OpenSSH ≥ 8.2 | Hardware key (ed25519-sk / ecdsa-sk) |
| `pam_mfa` | pam_u2f or pam_fido2 available | YubiKey U2F + TOTP fallback |
| `legacy` | Older systems | Compensating controls (no password auth, restricted accounts) |

Override with `security_capabilities_auth_mode: sk_keys|pam_mfa|legacy|auto`.

## Platform support

Public CI currently validates:

| Validation path | Platforms |
|--------|---------|
| GitHub-hosted VM tests | Ubuntu 22.04, Ubuntu 24.04 |
| Docker/container tests | Ubuntu 20.04, 22.04; Debian 11, 12, 13; Rocky Linux 8, 9 |

Legacy or customer-specific targets may still be supported, but should be
validated in self-hosted or private VM infrastructure instead of relying on
GitHub-hosted runners.

## Installation

```bash
ansible-galaxy collection install malpanez.security
```

Or pin a version in `requirements.yml`:

```yaml
collections:
  - name: malpanez.security
    version: ">=1.0.0"
```

## Usage

### 1. Review first (no changes applied)

Collect evidence and capabilities without touching the system:

```bash
ansible-playbook playbooks/review.yml -i inventory
```

Review the output in `/var/log/compliance`, then sign off.

### 2. Enforce

```yaml
# playbook.yml
- hosts: all
  become: true
  roles:
    - malpanez.security.security_capabilities
    - malpanez.security.sshd_hardening
    - malpanez.security.pam_mfa
    - malpanez.security.sudoers_baseline
    - malpanez.security.selinux_enforcement
    - malpanez.security.service_accounts_transfer
    - malpanez.security.audit_logging
    - malpanez.security.compliance_evidence
```

```bash
ansible-playbook playbook.yml -i inventory -e security_mode=enforce
```

## Examples

### Key variables

```yaml
security_mode: review                        # review | enforce
security_capabilities_auth_mode: auto        # auto | sk_keys | pam_mfa | legacy

sshd_hardening_password_authentication: false
sshd_hardening_permit_root_login: "no"
sshd_hardening_allow_users: [admin]
sshd_hardening_algorithm_profile: auto       # auto | modern | legacy

compliance_evidence_output_dir: /var/log/compliance
```

Full variable reference: [`roles/sshd_hardening/meta/argument_specs.yml`](roles/sshd_hardening/meta/argument_specs.yml)

## Dev environment

A compliance-hardened devcontainer is available:

```bash
devcontainer up --config .devcontainer/devcontainer.compliance.json
```

Runs read-only with tmpfs, minimal capabilities, and audit logging enabled.

## Documentation

- [Architecture](docs/architecture.md)
- [Capabilities matrix](docs/capabilities-matrix.md)
- [Runbooks](docs/runbooks.md) — breakglass, MFA recovery, rollback
- [Compliance evidence](docs/compliance-evidence.md)
- [Platform support](docs/PLATFORM_SUPPORT.md)
- [Workflows](docs/WORKFLOWS.md)
- [Publication strategy](docs/PUBLICATION_STRATEGY.md)

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md).

## License

MIT
