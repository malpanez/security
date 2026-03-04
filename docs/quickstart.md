# Quickstart (ND-friendly)

1) Run `ansible-galaxy collection install -r requirements.yml`.
2) Adjust the inventory (`inventory`) and, if desired, `group_vars/all.yml` with your human/service groups.
3) Apply capabilities automatically with `security_capabilities` (mode `auto` by default).
4) Launch a simple playbook (enforce mode):
```yaml
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
5) Review evidence in `compliance_evidence_output_dir` (default: `/var/log/compliance`).

Tips: short steps, clear variables per role (`*_` with role prefix), read `docs/runbooks.md` for breakglass/MFA and `docs/capabilities-matrix.md` for modes.***

### Review First, Enforce Later

1. Adjust `group_vars/all.yml` or inventory with `security_mode: review`.
2. Run `ansible-playbook playbooks/review.yml -i inventory` to collect capabilities and evidence (`tags: review`).
3. Analyze `/var/log/compliance` (capabilities, policy, `.tar.gz` config archives, command outputs).
4. Once you have sign-off, switch back to `security_mode: enforce` and run `playbooks/site.yml`.

### Devcontainer

For a curated experience:

```bash
cd security
devcontainer up --config .devcontainer/devcontainer.compliance.json
```

The `postCreateCommand` installs `pre-commit` hooks.
The tooling (`install-security-tools`) and the SBOM (`generate-sbom`) are run manually when needed.

Note: the compliance devcontainer requires `GITLEAKS_CHECKSUM` (and optionally `UV_CHECKSUM`) for verified downloads. Define both in `.devcontainer/devcontainer.compliance.json` before building.

The container runs read-only with `tmpfs` for `/tmp`/`/run`, minimal capabilities and audit logging at `$ANSIBLE_AUDIT_LOG`.
