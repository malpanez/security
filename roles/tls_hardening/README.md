# tls_hardening

System-wide TLS/crypto policy hardening. Uses `update-crypto-policies` on RHEL 8/9 and `openssl.cnf` lineinfile on Debian/Ubuntu/SUSE. Supports review mode (reports current posture) and enforce mode (applies target policy).

> **Note:** Policy changes apply to new TLS connections. Callers must reload any daemons that hold open TLS sockets (e.g. httpd, nginx, sshd) after this role runs.

## Requirements

- Ansible >= 2.16
- Collection: `malpanez.security`

## Role Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `tls_hardening_enabled` | `false` | Gate variable. Set `true` with `security_mode: enforce` to apply TLS hardening. Review tasks always run. |
| `tls_hardening_rhel_policy` | `"DEFAULT:NO-SHA1"` | RHEL 8/9 crypto-policies string passed to `update-crypto-policies --set`. Common values: `DEFAULT`, `DEFAULT:NO-SHA1`, `FUTURE`, `FIPS`. Has no effect on Debian, SUSE, or RHEL < 8. |
| `tls_hardening_min_protocol` | `"TLSv1.2"` | Minimum TLS protocol version written to `MinProtocol` in `openssl.cnf` on Debian, SUSE, and RHEL < 8. Choices: `TLSv1.2`, `TLSv1.3`. |
| `tls_hardening_openssl_cipher_string` | `"HIGH:!aNULL:!MD5:!RC4:!3DES"` | OpenSSL `CipherString` written to `openssl.cnf` on Debian, SUSE, and RHEL < 8. Passed directly to the `[system_default_sect]` section. |

## Example Playbook

```yaml
- name: Harden system-wide TLS policy
  hosts: all
  roles:
    - role: malpanez.security.tls_hardening
      vars:
        tls_hardening_enabled: true
        security_mode: enforce
```

To target RHEL hosts with a stricter policy while keeping Debian defaults, use `host_vars`:

```yaml
# host_vars/rhel9-server.yml
tls_hardening_rhel_policy: FUTURE

# host_vars/debian12-server.yml
tls_hardening_min_protocol: TLSv1.3
tls_hardening_openssl_cipher_string: "HIGH:!aNULL:!MD5:!RC4:!3DES:!DHE"
```

## Compliance

| Framework | Controls |
|-----------|----------|
| PCI-DSS | 4.2.1 — Strong cryptography for data in transit |
| HIPAA | 164.312(e)(1) — Transmission security |
| NIS2 | Art. 21 — Cryptographic controls |
| SOC2 | CC6.7 — Encryption in transit |

## License

Apache-2.0

## Author

Miguel Alpañez
