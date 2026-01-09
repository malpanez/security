# Docker Testing Guide (Estado real)

La validación con Docker se puede ejecutar localmente y también hay workflows en `.github/workflows/` para CI.

## Quick test (una plataforma)

```bash
./scripts/test-quick.sh
./scripts/test-quick.sh rockylinux@sha256:d7be1c094cc5845ee815d4632fe377514ee6ebcf8efaed6892889657e5ddaaa6
```

## Full test (plataformas script)

```bash
./scripts/test-all-platforms.sh
```

### Plataformas usadas por `scripts/test-all-platforms.sh`

- Ubuntu 22.04, 20.04 (imágenes Ansible con digest)
- Debian 13, 12, 11 (imágenes Ansible con digest)
- Rocky Linux 9, 8 (imágenes Ansible con digest)
- UBI 9, 8 (digest)

## Molecule (stack completo)

```bash
molecule test -s complete_stack
```

`molecule/complete_stack/molecule.yml` define 11 plataformas (Ubuntu 18/20/22/24, Debian 10/11/12, Rocky 8/9, Alma 8/9).

## Notas

- En Docker algunos checks pueden producir warnings (systemd/SELinux).
- El script `test-all-platforms.sh` corre preflight, audit-only, dry-run y `sshd_hardening`.
- Las imágenes están fijadas por digest para reproducibilidad; actualiza los digests cuando sea necesario.
- Usa `scripts/resolve-docker-digests.sh` para recalcular digests.
