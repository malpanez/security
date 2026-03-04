# Platform Support Matrix (Actual state)

## Supported families

- Debian/Ubuntu (ansible_os_family: `Debian`)
- RHEL-like (ansible_os_family: `RedHat`)

## Minimum requirements (preflight-check)

- Debian: >= 10
- Ubuntu: >= 18.04
- RedHat family: >= 7

## Tested locally

### Molecule `complete_stack`
- Ubuntu: 18.04, 20.04, 22.04, 24.04
- Debian: 10, 11, 12
- Rocky: 8, 9
- Alma: 8, 9

### Docker Scripts
- `scripts/test-all-platforms.sh`: Ubuntu 20/22, Debian 11/12, Rocky 8/9, UBI 8/9
- `scripts/test-quick.sh`: Docker image specified by the user

## Important notes

- CI workflows exist in `.github/workflows/`; validate locally if you need to reproduce failures.
- SELinux is only applied on RedHat family.
- `sshd_hardening` writes a complete `/etc/ssh/sshd_config`; it does not use `sshd_config.d`.
