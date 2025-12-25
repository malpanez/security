# Platform Support Matrix

## Supported Platforms

The `malpanez.security` collection officially supports the following platforms:

### Enterprise Linux (RHEL, CentOS, Rocky, Alma, Oracle)

| Platform | Version | Support Level | Notes |
|----------|---------|---------------|-------|
| **RHEL** | 7.x | ⚠️ Limited | Legacy, EOL June 2024, best-effort only |
| **RHEL** | 8.x | ✅ Production | Current LTS, EOL May 2029 |
| **RHEL** | 9.x | ✅ Production | Latest, EOL May 2032 |
| **CentOS** | 7.x | ⚠️ Limited | Legacy, EOL June 2024, best-effort only |
| **Rocky Linux** | 8.x | ✅ Production | RHEL 8 rebuild |
| **Rocky Linux** | 9.x | ✅ Production | RHEL 9 rebuild |
| **AlmaLinux** | 8.x | ✅ Production | RHEL 8 rebuild |
| **AlmaLinux** | 9.x | ✅ Production | RHEL 9 rebuild |
| **Oracle Linux** | 7.x | ✅ Production | RHEL 7 compatible |
| **Oracle Linux** | 8.x | ✅ Production | RHEL 8 compatible |
| **Oracle Linux** | 9.x | ✅ Production | RHEL 9 compatible |

### Debian

| Platform | Version | Codename | Support Level | Notes |
|----------|---------|----------|---------------|-------|
| **Debian** | 10 | Buster | ✅ Production | LTS until 2024 |
| **Debian** | 11 | Bullseye | ✅ Production | LTS until 2026 |
| **Debian** | 12 | Bookworm | ✅ Production | Current stable, LTS until 2028 |
| **Debian** | 13 | Trixie | ✅ Production | Next stable, recommended for new servers |

### Ubuntu

| Platform | Version | Codename | Support Level | Notes |
|----------|---------|----------|---------------|-------|
| **Ubuntu Server** | 18.04 LTS | Bionic Beaver | ✅ Production | ESM until 2028 |
| **Ubuntu Server** | 20.04 LTS | Focal Fossa | ✅ Production | LTS until April 2025 |
| **Ubuntu Server** | 22.04 LTS | Jammy Jellyfish | ✅ Production | Current LTS, until April 2027 |

## Platform-Specific Features

### SELinux Support

| Platform | SELinux Available | Default Mode | Notes |
|----------|-------------------|--------------|-------|
| RHEL 7+ | ✅ Yes | Enforcing | Native support |
| CentOS 7+ | ✅ Yes | Enforcing | Native support |
| Rocky/Alma 8+ | ✅ Yes | Enforcing | Native support |
| Oracle Linux 7+ | ✅ Yes | Enforcing | Native support |
| Debian | ⚠️ Optional | Permissive | Package: `selinux-basics` |
| Ubuntu | ⚠️ Optional | Permissive | Package: `selinux` |

### PAM MFA Support

All supported platforms can use PAM-based MFA with:
- **YubiKey U2F/FIDO2**: Requires `pam_u2f` or `pam_fido2`
- **TOTP**: Requires `pam_google_authenticator`

| Platform | PAM U2F Package | PAM TOTP Package | Authselect |
|----------|-----------------|------------------|------------|
| RHEL/CentOS 7 | `pam_u2f` | `google-authenticator` | ❌ No |
| RHEL/Rocky/Alma 8+ | `pam_u2f` | `google-authenticator` | ✅ Yes |
| Debian 10+ | `libpam-u2f` | `libpam-google-authenticator` | ❌ No |
| Ubuntu 18.04+ | `libpam-u2f` | `libpam-google-authenticator` | ❌ No |

### SSH Configuration

All platforms support modular SSH configuration via `/etc/ssh/sshd_config.d/`

| Platform | sshd_config.d Support | OpenSSH Version |
|----------|----------------------|-----------------|
| RHEL 7 | ✅ Yes (7.4+) | 7.4p1+ |
| RHEL 8+ | ✅ Yes | 8.0p1+ |
| Debian 10 | ✅ Yes | 7.9p1+ |
| Debian 11+ | ✅ Yes | 8.4p1+ |
| Ubuntu 18.04 | ✅ Yes | 7.6p1+ |
| Ubuntu 20.04+ | ✅ Yes | 8.2p1+ |

## Testing Strategy

### Molecule Test Platforms

The collection is tested using Molecule with Docker containers:

```yaml
platforms:
  # Ubuntu
  - ubuntu2204 (geerlingguy/docker-ubuntu2204-ansible)
  - ubuntu2004 (geerlingguy/docker-ubuntu2004-ansible) # To add
  - ubuntu1804 (geerlingguy/docker-ubuntu1804-ansible) # To add

  # Debian
  - debian12 (geerlingguy/docker-debian12-ansible)
  - debian13 (geerlingguy/docker-debian13-ansible)
  - debian11 (geerlingguy/docker-debian11-ansible) # To add
  - debian10 (geerlingguy/docker-debian10-ansible) # To add

  # RHEL-based
  - rockylinux9 (geerlingguy/docker-rockylinux9-ansible)
  - rockylinux8 (geerlingguy/docker-rockylinux8-ansible)
```

### CI/CD Platform Matrix

GitHub Actions tests against:
- ✅ All 9 roles
- ✅ Multiple OS versions (matrix)
- ✅ Parallel execution
- ✅ Build and install verification

## Compatibility Notes

### RHEL 7 / CentOS 7 Specific

Note: CI does not run Docker-based Molecule tests on CentOS 7 due to Python 3 availability.

**Differences from RHEL 8+:**
- ❌ No `authselect` (uses traditional PAM)
- ⚠️ Older OpenSSH (7.4)
- ⚠️ Older PAM version (1.1.8)
- ✅ Full support via direct PAM modification

**Configuration Approach:**
```yaml
# Detection
pam_supports_authselect: false  # RHEL 7
pam_version_legacy: true

# Uses community.general.pamd module directly
```

### Ubuntu 18.04 Specific

**Considerations:**
- OpenSSH 7.6p1 (older than 8.x)
- Uses `common-auth` PAM framework
- Full support for sshd_config.d

### Debian 10 (Buster) Specific

**Considerations:**
- OpenSSH 7.9p1
- EOL approaching (2024)
- Recommended: Upgrade to Debian 11+

## Version Support Policy

### Production Support (✅)
- Active security updates from vendor
- Full testing in CI/CD
- Bug fixes and features

### Legacy Support (⚠️)
- Best-effort support
- Security fixes only
- Limited testing

### Unsupported (❌)
- No testing
- No guarantees
- Use at own risk

## Minimum Requirements

### Ansible
- **ansible-core**: >= 2.16
- **Python**: >= 3.9

### Target Systems
- **Python**: >= 3.6 (Python 2.7 for RHEL 7)
- **systemd**: Required for service management
- **SELinux**: Optional (but recommended for RHEL-based)

## Adding New Platforms

To request support for a new platform:

1. Open an issue: https://github.com/malpanez/security/issues
2. Provide:
   - Platform name and version
   - Use case / business justification
   - Willingness to test

### Platform Evaluation Criteria

- ✅ Active vendor support
- ✅ Significant user base
- ✅ Available Molecule test images
- ✅ Compatible with core features (PAM, SSH, sudo)

## Known Limitations

### CentOS 7 / RHEL 7
- No authselect support (by design)
- Older OpenSSH lacks some modern ciphers
- Python 2.7 (requires `ansible_python_interpreter` override)

### Ubuntu 18.04
- Approaching EOL (standard support ended 2023)
- ESM available for security updates
- Recommended: Upgrade to 20.04 or 22.04

### Debian 10
- Approaching EOL (2024)
- Recommended: Upgrade to 11 or 12

## References

- **RHEL Lifecycle**: https://access.redhat.com/support/policy/updates/errata
- **Ubuntu Releases**: https://wiki.ubuntu.com/Releases
- **Debian Releases**: https://wiki.debian.org/LTS
- **OpenSSH Versions**: https://www.openssh.com/releasenotes.html

---

**Last Updated**: 2025-12-05
**Collection Version**: 1.0.0
**Maintainer**: Miguel Alpañez
