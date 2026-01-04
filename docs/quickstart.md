# Quickstart (ND-friendly)

1) Ejecuta `ansible-galaxy collection install -r requirements.yml`.
2) Ajusta inventario (`inventory`) y, si quieres, `group_vars/all.yml` con tus grupos humanos/servicio.
3) Aplica capacidades auto con `security_capabilities` (modo `auto` por defecto).
4) Lanza playbook simple (modo enforce):
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
5) Revisa evidencias en `compliance_evidence_output_dir` (default: `/var/log/compliance`).

Tips: pasos cortos, variables claras por rol (`*_` con prefijo del rol), lee `docs/runbooks.md` para breakglass/MFA y `docs/capabilities-matrix.md` para modos.***

### Review primero, enforce después

1. Ajusta `group_vars/all.yml` o inventario con `security_mode: review`.
2. Ejecuta `ansible-playbook playbooks/review.yml -i inventory` para recolectar capacidades y evidencias (`tags: review`).
3. Analiza `/var/log/compliance` (capabilities, policy, archivos `.tar.gz` de config, salidas de comandos).
4. Cuando tengas sign-off, vuelve a `security_mode: enforce` y corre `playbooks/site.yml`.

### Devcontainer

Para una experiencia curada:

```bash
cd security
devcontainer up --config .devcontainer/devcontainer.compliance.json
```

El `postCreateCommand` ejecuta:

- `install-security-tools` (instala requirements-dev vía `uv`)
- `ensure-precommit-locked` (hooks + `pre-commit autoupdate --freeze`)
- `generate-sbom` (Syft -> `sbom.cyclonedx.json`)

Nota: el devcontainer compliance requiere `GITLEAKS_CHECKSUM` (y opcionalmente `UV_CHECKSUM`) para descargas verificadas. Define ambos en `.devcontainer/devcontainer.compliance.json` antes de construir.

El contenedor corre read-only con `tmpfs` para `/tmp`/`/run`, capabilities mínimas y logging audit en `$ANSIBLE_AUDIT_LOG`.
