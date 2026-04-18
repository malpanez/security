# Requirements: malpanez.security — Compliance Role Expansion

**Defined:** 2026-04-14
**Core Value:** Each new role shows the auditor the deficiency first (review mode) then fixes it (enforce mode)

## v1 Requirements

### Collection Standards (applies to all 6 roles)

- [x] **STD-01**: Each role initialised via `ansible-galaxy role init` before any files written
- [x] **STD-02**: tasks/main.yml uses review/enforce gate pattern (security_mode + role_enabled)
- [x] **STD-03**: review.yml contains only read-only tasks (command with changed_when: false, debug)
- [x] **STD-04**: enforce.yml split into tagged sections: install / configure / service / verify
- [x] **STD-05**: All modules use FQCN (ansible.builtin.*, community.general.*, ansible.posix.*)
- [x] **STD-06**: Multi-OS via ansible_os_family + vars/Debian.yml + vars/RedHat.yml + vars/Suse.yml
- [x] **STD-07**: meta/main.yml valid Galaxy schema (EL versions: [all], Debian: buster/bullseye/bookworm, Ubuntu: bionic/focal/jammy)
- [x] **STD-08**: meta/argument_specs.yml documents all defaults variables
- [x] **STD-09**: tests/test.yml has play name + FQCN role reference
- [x] **STD-10**: molecule/default/ scenario with ubuntu2204 + rockylinux9, prepare.yml for EL
- [x] **STD-11**: molecule/default/verify.yml asserts key outcomes (binary present, config exists, service enabled)
- [x] **STD-12**: yamllint and ansible-lint --profile production pass with 0 errors
- [x] **STD-13**: Role added to ci-uv.yml test-roles matrix and ci-cd-enterprise.yml test-molecule matrix
- [x] **STD-14**: Collection reinstalled after role creation

### ntp_hardening

- [ ] **NTP-01**: review.yml reports chrony/ntpd status, time drift, NTP servers, stratum
- [ ] **NTP-02**: enforce.yml installs chrony (preferred) or ntpd
- [x] **NTP-03**: Deploys chrony.conf drop-in with configurable NTP servers
- [ ] **NTP-04**: Enables and starts chronyd service
- [ ] **NTP-05**: Container-aware: skip drift check and service assertions in containers
- [x] **NTP-06**: Compliance tags: PCI-DSS 10.6.1, NIS2 Art.21, SOC2 CC6.1, HIPAA §164.312(b)

### user_audit

- [x] **USR-01**: review.yml reports accounts with no password expiry, UID 0 non-root, inactive accounts (>90 days), service accounts with login shells
- [ ] **USR-02**: enforce.yml locks accounts inactive beyond threshold (usermod -L)
- [ ] **USR-03**: enforce.yml sets password expiry via chage (max_days, min_days, warn_days)
- [ ] **USR-04**: Never touches root account or system accounts (UID < 1000) — hard-coded guard
- [ ] **USR-05**: Idempotent: repeated runs produce no changes on already-compliant accounts
- [x] **USR-06**: Compliance tags: SOC2 CC6.2/CC6.3, HIPAA §164.312(a)(2)(i), PCI-DSS 8.1.4/8.3.6, NIS2

### rsyslog_forwarding

- [x] **LOG-01**: review.yml reports rsyslog status, existing forwarding config, TLS state
- [x] **LOG-02**: enforce.yml deploys /etc/rsyslog.d/99-forwarding.conf drop-in (never touches rsyslog.conf)
- [x] **LOG-03**: Supports TCP (default) and UDP forwarding
- [x] **LOG-04**: Optional TLS via RsyslogGnuTLS (rsyslog_forwarding_tls_enabled)
- [x] **LOG-05**: Configurable remote host (rsyslog_forwarding_host required), port (default 514)
- [x] **LOG-06**: Compliance tags: NIS2 Art.21, SOC2 CC7.2, PCI-DSS 10.5.1/10.5.4, HIPAA §164.312(b)

### antivirus (ClamAV)

- [ ] **AV-01**: review.yml reports ClamAV installation status, DB age, clamd running state, last scan date
- [x] **AV-02**: enforce.yml installs clamav + daemon packages (names vary per OS)
- [ ] **AV-03**: Deploys freshclam config and enables freshclam timer/service for DB updates
- [ ] **AV-04**: Deploys systemd timer for periodic scans, reports to /var/log/clamav/
- [x] **AV-05**: antivirus_update_db (default true) — set false in CI molecule to skip 200MB download
- [x] **AV-06**: Container-aware: skip freshclam and scan in containers
- [x] **AV-07**: Compliance tags: PCI-DSS 5.2.1/5.3.2, NIS2 Art.21(2)(e), SOC2 CC6.8

### tls_hardening

- [ ] **TLS-01**: review.yml reports current TLS policy/min version, openssl default settings
- [ ] **TLS-02**: enforce.yml on RHEL: calls update-crypto-policies to set configurable policy
- [ ] **TLS-03**: enforce.yml on Debian/SUSE: deploys openssl.cnf drop-in with MinProtocol + CipherString
- [ ] **TLS-04**: Disable TLS 1.0 and 1.1 by default (configurable)
- [ ] **TLS-05**: Minimum TLS version configurable (default TLSv1.2)
- [ ] **TLS-06**: Compliance tags: PCI-DSS 4.2.1, HIPAA, NIS2 Art.21, SOC2

### usbguard

- [ ] **USB-01**: review.yml reports usbguard installation, policy (ImplicitPolicyTarget), existing rules
- [ ] **USB-02**: enforce.yml installs usbguard
- [ ] **USB-03**: Runs usbguard generate-policy BEFORE enabling block policy (captures existing devices)
- [ ] **USB-04**: Deploys usbguard-daemon.conf with ImplicitPolicyTarget=block (default)
- [ ] **USB-05**: Enables and starts usbguard.service
- [ ] **USB-06**: Container-aware: skip USB operations in containers (no USB subsystem)
- [ ] **USB-07**: Compliance tags: PCI-DSS 12.3.4, HIPAA §164.310(d)(1), NIS2, SOC2 CC6.7

## v2 Requirements

### Future enhancements (not in this milestone)

- **FUT-01**: Standalone Galaxy repos for each new role
- **FUT-02**: Pin molecule image SHAs for all new roles
- **FUT-03**: Integration with compliance_evidence role (generate evidence artifacts)
- **FUT-04**: rkhunter role (deferred — redundant with aide)
- **FUT-05**: network_baseline (nftables) — deferred scope

## Out of Scope

| Feature | Reason |
|---------|--------|
| rkhunter | Redundant with aide FIM role |
| fips_mode | Disruptive, niche use case |
| network_baseline | Enormous scope, distro conflicts |
| Standalone Galaxy repos | Next milestone |
| SHA-pinned molecule images | Tech debt, not this milestone |

## Traceability

| Requirement | Phase | Status |
|-------------|-------|--------|
| STD-01 | Phase 1, 2, 3, 4, 5, 6 (all phases) | Complete |
| STD-02 | Phase 1, 2, 3, 4, 5, 6 (all phases) | Complete |
| STD-03 | Phase 1, 2, 3, 4, 5, 6 (all phases) | Complete |
| STD-04 | Phase 1, 2, 3, 4, 5, 6 (all phases) | Complete |
| STD-05 | Phase 1, 2, 3, 4, 5, 6 (all phases) | Complete |
| STD-06 | Phase 1, 2, 3, 4, 5, 6 (all phases) | Complete |
| STD-07 | Phase 1, 2, 3, 4, 5, 6 (all phases) | Complete |
| STD-08 | Phase 1, 2, 3, 4, 5, 6 (all phases) | Complete |
| STD-09 | Phase 1, 2, 3, 4, 5, 6 (all phases) | Complete |
| STD-10 | Phase 1, 2, 3, 4, 5, 6 (all phases) | Complete |
| STD-11 | Phase 1, 2, 3, 4, 5, 6 (all phases) | Complete |
| STD-12 | Phase 1, 2, 3, 4, 5, 6 (all phases) | Complete |
| STD-13 | Phase 1, 2, 3, 4, 5, 6 (all phases) | Complete |
| STD-14 | Phase 1, 2, 3, 4, 5, 6 (all phases) | Complete |
| NTP-01 | Phase 1 | Pending |
| NTP-02 | Phase 1 | Pending |
| NTP-03 | Phase 1 | Complete |
| NTP-04 | Phase 1 | Pending |
| NTP-05 | Phase 1 | Pending |
| NTP-06 | Phase 1 | Complete |
| USR-01 | Phase 2 | Pending |
| USR-02 | Phase 2 | Pending |
| USR-03 | Phase 2 | Pending |
| USR-04 | Phase 2 | Pending |
| USR-05 | Phase 2 | Pending |
| USR-06 | Phase 2 | Complete |
| LOG-01 | Phase 3 | Complete |
| LOG-02 | Phase 3 | Complete |
| LOG-03 | Phase 3 | Complete |
| LOG-04 | Phase 3 | Complete |
| LOG-05 | Phase 3 | Complete |
| LOG-06 | Phase 3 | Complete |
| AV-01 | Phase 4 | Pending |
| AV-02 | Phase 4 | Complete |
| AV-03 | Phase 4 | Pending |
| AV-04 | Phase 4 | Pending |
| AV-05 | Phase 4 | Complete |
| AV-06 | Phase 4 | Complete |
| AV-07 | Phase 4 | Complete |
| TLS-01 | Phase 5 | Pending |
| TLS-02 | Phase 5 | Pending |
| TLS-03 | Phase 5 | Pending |
| TLS-04 | Phase 5 | Pending |
| TLS-05 | Phase 5 | Pending |
| TLS-06 | Phase 5 | Pending |
| USB-01 | Phase 6 | Pending |
| USB-02 | Phase 6 | Pending |
| USB-03 | Phase 6 | Pending |
| USB-04 | Phase 6 | Pending |
| USB-05 | Phase 6 | Pending |
| USB-06 | Phase 6 | Pending |
| USB-07 | Phase 6 | Pending |

---
*Requirements defined: 2026-04-14*
*Last updated: 2026-04-14 — traceability filled after roadmap creation*
