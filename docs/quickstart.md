# Quickstart (ND-friendly)

1) Ejecuta `ansible-galaxy collection install -r requirements.yml`.
2) Ajusta inventario (`inventory`) y, si quieres, `group_vars/all.yml` con tus grupos humanos/servicio.
3) Aplica capacidades auto con `security_capabilities` (modo `auto` por defecto).
4) Lanza playbook simple:
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
5) Revisa evidencias en `reports/`.

Tips: pasos cortos, variables claras por rol (`*_` con prefijo del rol), lee `docs/runbooks.md` para breakglass/MFA y `docs/capabilities-matrix.md` para modos.***
