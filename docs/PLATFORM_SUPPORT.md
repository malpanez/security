# Platform Support Matrix (Estado real)

## Familias soportadas

- Debian/Ubuntu (ansible_os_family: `Debian`)
- RHEL-like (ansible_os_family: `RedHat`)

## Requisitos mínimos (preflight-check)

- Debian: >= 10
- Ubuntu: >= 18.04
- RedHat family: >= 7

## Probado localmente

### Molecule `complete_stack`
- Ubuntu: 18.04, 20.04, 22.04, 24.04
- Debian: 10, 11, 12
- Rocky: 8, 9
- Alma: 8, 9

### Scripts Docker
- `scripts/test-all-platforms.sh`: Ubuntu 20/22, Debian 11/12, Rocky 8/9, UBI 8/9
- `scripts/test-quick.sh`: imagen Docker indicada por el usuario

## Notas importantes

- Los workflows CI existen en `.github/workflows/`; valida en local si necesitas reproducir fallos.
- SELinux solo se aplica en RedHat family.
- `sshd_hardening` escribe `/etc/ssh/sshd_config` completo; no usa `sshd_config.d`.
