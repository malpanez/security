# Platform Support Matrix (Actual state)

## Supported families

- Debian/Ubuntu (ansible_os_family: `Debian`)
- RHEL-like (ansible_os_family: `RedHat`)

## Minimum requirements (preflight-check)

- Debian: >= 10
- Ubuntu: >= 18.04
- RedHat family: >= 7

## Public CI validation

### GitHub-hosted VM workflow

- Ubuntu 22.04
- Ubuntu 24.04

### Docker-based workflow

- Ubuntu 20.04, 22.04
- Debian 11, 12, 13
- Rocky 8, 9

## Additional and legacy validation

Older or customer-specific targets can still be supported, but should be
validated in self-hosted runners or private VM infrastructure.

## Historical/local test coverage

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
- `sshd_hardening` uses an SSH drop-in by default (`sshd_config.d`) and can fall back to managing the main `sshd_config` when explicitly configured.
