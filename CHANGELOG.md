## [Unreleased]

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
