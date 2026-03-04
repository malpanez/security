# Docker Testing Guide (Actual state)

Docker-based validation can be run locally and there are also workflows in `.github/workflows/` for CI.

## Quick test (single platform)

```bash
./scripts/test-quick.sh
./scripts/test-quick.sh rockylinux@sha256:d7be1c094cc5845ee815d4632fe377514ee6ebcf8efaed6892889657e5ddaaa6
```

## Full test (platforms script)

```bash
./scripts/test-all-platforms.sh
```

### Platforms used by `scripts/test-all-platforms.sh`

- Ubuntu 22.04, 20.04 (Ansible images with digest)
- Debian 13, 12, 11 (Ansible images with digest)
- Rocky Linux 9, 8 (Ansible images with digest)
- UBI 9, 8 (digest)

## Molecule (full stack)

```bash
molecule test -s complete_stack
```

`molecule/complete_stack/molecule.yml` defines 11 platforms (Ubuntu 18/20/22/24, Debian 10/11/12, Rocky 8/9, Alma 8/9).

## Notes

- In Docker some checks may produce warnings (systemd/SELinux).
- The `test-all-platforms.sh` script runs preflight, audit-only, dry-run and `sshd_hardening`.
- Images are pinned by digest for reproducibility; update digests when necessary.
- Use `scripts/resolve-docker-digests.sh` to recalculate digests.
