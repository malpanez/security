# Docker Testing Guide (Estado real)

La validación con Docker se puede ejecutar localmente y también hay workflows en `.github/workflows/` para CI.

## Quick test (una plataforma)

```bash
./scripts/test-quick.sh
./scripts/test-quick.sh rockylinux:9
```

## Full test (plataformas script)

```bash
./scripts/test-all-platforms.sh
```

### Plataformas usadas por `scripts/test-all-platforms.sh`

- Ubuntu 22.04, 20.04
- Debian 12, 11
- Rocky Linux 9, 8
- UBI 9, 8

## Molecule (stack completo)

```bash
molecule test -s complete_stack
```

`molecule/complete_stack/molecule.yml` define 11 plataformas (Ubuntu 18/20/22/24, Debian 10/11/12, Rocky 8/9, Alma 8/9).

## Notas

- En Docker algunos checks pueden producir warnings (systemd/SELinux).
- El script `test-all-platforms.sh` corre preflight, audit-only, dry-run y `sshd_hardening`.
