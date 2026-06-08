## [Unreleased]

### Added
- firewall role: default-deny host firewall (firewalld on RHEL/SUSE, ufw on Debian/Ubuntu) with explicit allowlist and SSH lockout protection (CIS 3.5.x, NIST CM-7/SC-7, NIS2 Art.21(2)(j))
- automated_patching role: security-only automatic patching (dnf-automatic / unattended-upgrades) with controlled, opt-in reboots (CIS 1.9, NIST SI-2, NIS2 Art.21(2)(i))
- SLSA build provenance attestation on the collection build (ci.yml, ci-uv.yml)
- cis_baseline: enforce + review for MaxAuthTries, sudo logfile, and NOPASSWD:ALL
- auditd: CIS L2 / STIG syscall rules (priv_esc, perm_mod, access, delete, mounts, time_change, modules) and login/session watches

### Changed
- License unified to Apache-2.0 across the collection (galaxy.yml, all role metadata, LICENSE)
- Supply chain hardened: all GitHub Actions, Docker images, pre-commit hooks, and the gitleaks binary pinned to verified digests/checksums; step-security/harden-runner on every CI job; per-job least-privilege permissions
- Replaced archived gaurav-nelson markdown link checker with lycheeverse/lychee-action
- Galaxy collections pinned in requirements.yml; added ansible.posix and community.docker dependencies
- Grype now fails CI on critical vulnerabilities
- README documents all 26 (now 28) roles; argument_specs parity across all roles

### Fixed
- Wired up 9 dormant testinfra suites (missing `verifier: testinfra`) so role tests actually run
- PAM/sshd backup idempotence (stable filenames instead of epoch timestamps; no more unbounded backup accumulation)

## [1.2.0] - 2026-04-20

### Added
- ntp_hardening role: chrony hardening with review/enforce mode (PCI-DSS 10.6.1, NIS2, SOC2 CC6.1)
- user_audit role: local account audit and expiry enforcement (SOC2 CC6.2, HIPAA, PCI-DSS 8.x)
- rsyslog_forwarding role: centralised log forwarding with optional TLS (NIS2, SOC2 CC7.2, PCI-DSS 10.5)
- antivirus role: ClamAV with freshclam and scan timer (PCI-DSS 5.2, NIS2, SOC2 CC6.8)
- tls_hardening role: system-wide TLS policy enforcement (PCI-DSS 4.2.1, HIPAA, NIS2)
- usbguard role: USB block-by-default with device whitelist (PCI-DSS 12.3.4, HIPAA, NIS2, SOC2 CC6.7)
- Renovate Bot integration for automated dependency management
- Molecule CI scenario with optimized 3-platform testing
- community.docker collection for Molecule Docker driver support
- Complete stack testing infrastructure with 11 platform coverage

### Changed
- Updated all GitHub Actions workflows to v5/v6
- Optimized CI execution time from 90+ to ~15-20 minutes
- Migrated from Dependabot to Renovate for better GitFlow integration

### Fixed
- Added missing community.docker collection requirement
- Improved molecule-complete-stack workflow variable handling

## [0.1.0] - Initial Release

### Added
- Initial automated hardening stack with capabilities, MFA, SELinux, sudoers, service accounts, audit, evidencias y CIS opcional
