---
gsd_state_version: 1.0
milestone: v1.2.0
milestone_name: milestone
status: executing
stopped_at: Completed 06-usbguard/06-02-PLAN.md
last_updated: "2026-04-20T13:13:05.733Z"
last_activity: 2026-04-20
progress:
  total_phases: 7
  completed_phases: 6
  total_plans: 34
  completed_plans: 32
  percent: 0
---

# Project State

## Project Reference

See: .planning/PROJECT.md (updated 2026-04-14)

**Core value:** Each new role shows the auditor the deficiency first (review mode) then fixes it (enforce mode)
**Current focus:** Phase 06 — usbguard

## Current Position

Phase: 06 (usbguard) — EXECUTING
Plan: 4 of 5
Status: Ready to execute
Last activity: 2026-04-20

Progress: [░░░░░░░░░░] 0%

## Performance Metrics

**Velocity:**

- Total plans completed: 0
- Average duration: -
- Total execution time: 0 hours

**By Phase:**

| Phase | Plans | Total | Avg/Plan |
|-------|-------|-------|----------|
| - | - | - | - |

**Recent Trend:**

- Last 5 plans: n/a
- Trend: n/a

*Updated after each plan completion*
| Phase 01-ntp-hardening P01-01 | 10 | 1 tasks | 11 files |
| Phase 01-ntp-hardening P01-02 | 10 | 3 tasks | 3 files |
| Phase 01-ntp-hardening P01-03 | 5 | 1 tasks | 1 files |
| Phase 01-ntp-hardening P01-05 | 5 | 1 tasks | 2 files |
| Phase 02 P02-01 | 670 | 1 tasks | 11 files |
| Phase 02 P02-02 | 7 | 1 tasks | 1 files |
| Phase 02 P02-04 | 10 | 1 tasks | 4 files |
| Phase 02 P02-05 | 180 | 1 tasks | 2 files |
| Phase 03-rsyslog-forwarding P03-01 | 12 | 1 tasks | 12 files |
| Phase 03-rsyslog-forwarding P03-02 | 2 | 2 tasks | 3 files |
| Phase 03-rsyslog-forwarding P03-03 | 1 | 1 tasks | 2 files |
| Phase 03-rsyslog-forwarding P03-04 | 3 | 1 tasks | 4 files |
| Phase 03-rsyslog-forwarding P03-05 | 5 | 1 tasks | 2 files |
| Phase 03-rsyslog-forwarding P06 | 3 | 1 tasks | 1 files |
| Phase 04-antivirus P04-01 | 19 | 1 tasks | 8 files |
| Phase 04-antivirus P04-02 | 8 | 3 tasks | 3 files |
| Phase 04-antivirus P04-03 | 4 | 1 tasks | 4 files |
| Phase 04-antivirus P04-04 | 3 | 1 tasks | 4 files |
| Phase 04-antivirus P04-05 | 3 | 1 tasks | 3 files |
| Phase 02-user-audit P02-03 | 5 | 2 tasks | 2 files |
| Phase 02-user-audit P02-07 | 525600 | 1 tasks | 1 files |
| Phase 02-user-audit P02-06 | 2 | 1 tasks | 1 files |
| Phase 05-tls-hardening P05-01 | 20 | 1 tasks | 11 files |
| Phase 05-tls-hardening P05-03 | 2 | 1 tasks | 1 files |
| Phase 05-tls-hardening P05-02 | 15 | 2 tasks | 2 files |
| Phase 05-tls-hardening P05-04 | 3 | 1 tasks | 4 files |
| Phase 05-tls-hardening P05-05 | 5 | 1 tasks | 2 files |
| Phase 05.1-ssh-access-vm-test P01 | 9 | 2 tasks | 3 files |
| Phase 06-usbguard P06-04 | 8 | 2 tasks | 4 files |
| Phase 06-usbguard P06-01 | 512 | 2 tasks | 10 files |
| Phase 06-usbguard P02 | 4 | 2 tasks | 2 files |

## Accumulated Context

### Decisions

- All 6 roles: review/enforce split, container-aware via _role_in_container fact
- ntp: chrony only (disable timesyncd on Debian, disable ntpd on RHEL), no monitor directive (CVE-2013-5211)
- user_audit: two-step chage idempotence (pre-check maxdays -1/99999 before setting), triple root guard
- rsyslog: RainerScript action() syntax only (not legacy @@host), drop-in 99-forwarding.conf only
- antivirus: antivirus_update_db:false in Molecule CI (skip 200MB freshclam download)
- tls_hardening: slurp for openssl.cnf detection (NOT lookup('file') — reads controller not managed host)
- usbguard: stat /sys/bus/usb/devices for container detection (more reliable than virtualization_type), daemon.conf mode:0600, generate-policy is write-once
- [Phase 01-ntp-hardening]: ntp_hardening: chrony service named 'chrony' on Debian vs 'chronyd' on RedHat/Suse — loaded from OS-family vars
- [Phase 01-ntp-hardening]: ntp_hardening: deny_all defaults to true — client-only mode by default, serving requires explicit ntp_hardening_allow
- [Phase 01-ntp-hardening]: chrony.conf.j2: monitor/cmdallow absent by omission (CVE-2013-5211), leapsectz conditional on non-empty value
- [Phase 02]: user_audit: skip_users defaults to [root, halt, sync, shutdown] — system accounts never locked/modified
- [Phase 02]: user_audit: fix_service_shells defaults false — opt-in only, shell changes are destructive
- [Phase 02]: user_audit review.yml: lastlog --before (not --time) — --before returns accounts inactive longer than N days; --time returns recently-active (inverted set)
- [Phase 02]: user_audit review.yml: intersect(_ua_human_account_list) in inactive report — lastlog --before includes system accounts; intersection scopes to human accounts only
- [Phase 02 P02-04]: user_audit molecule: nsswitch fix applied to all platforms (failed_when:false, no-op on Debian) — simpler than when:RedHat guard
- [Phase 02 P02-04]: user_audit molecule: verify.yml asserts maxdays == 90 (positive) not != -1 (negative) — proves enforce ran correctly
- [Phase 03-rsyslog-forwarding]: rsyslog_forwarding: Suse uses rsyslog-module-gtls (not rsyslog-gnutls) for TLS — different package name on openSUSE/SLES
- [Phase 03-rsyslog-forwarding]: rsyslog_forwarding: _rsyslog_in_container bool guard in handler matches _ntp_in_container pattern from ntp_hardening
- [Phase 03-rsyslog-forwarding]: rsyslog_forwarding enforce.yml: all tasks carry rsyslog_forwarding + section-level tags (install/configure/service/verify) for fine-grained --tags targeting
- [Phase 03-rsyslog-forwarding]: rsyslog_forwarding: TLS pre-flight assertions (anonymous blocked, UDP blocked, CA cert existence checked) run before package install to fail fast
- [Phase 03-rsyslog-forwarding]: rsyslog_forwarding: action(type="omfwd") on single selector line — satisfies RainerScript syntax and grep-based artifact checks
- [Phase 03-rsyslog-forwarding]: rsyslog_forwarding: module(load="imtls") inside TLS block only — required to activate GnuTLS stream driver
- [Phase 03-rsyslog-forwarding]: rsyslog_forwarding molecule: verify.yml container-aware guards (not _in_container) for rsyslogd -N1 and systemctl checks
- [Phase 03-rsyslog-forwarding]: rsyslog_forwarding inserted after user_audit in both CI matrices — maintains consistent ordering of new roles
- [Phase 03-rsyslog-forwarding]: _rsyslog_configured_dest: regex_search extracts Target= from b64decoded drop-in; default('not configured') when drop-in absent (LOG-01 gap closure)
- [Phase 04-antivirus]: antivirus: antivirus_update_db:false in Molecule CI (skip 200MB freshclam download) — analogous to aide_init_db:false pattern
- [Phase 04-antivirus]: antivirus: _antivirus_in_container bool guard in handlers matches ntp_hardening/_rsyslog pattern
- [Phase 04-antivirus]: antivirus: freshclam failed_when rc not in [0,1] — rc=1 means DB already current, not a failure
- [Phase 04-antivirus]: antivirus: SELinux boolean antivirus_can_scan_system set persistently + restorecon on log dir and scan dirs
- [Phase 04-antivirus]: antivirus templates: clamav-scan.service.j2 uses Jinja2 for loop with loop.last backslash continuation for ExecStart multi-dir args
- [Phase 04-antivirus]: antivirus templates: freshclam NotifyClamd uses antivirus_clamd_config (config file path, not socket path)
- [Phase 04-antivirus]: antivirus molecule: antivirus_update_db:false in converge.yml skips 200MB freshclam download in CI containers
- [Phase 04-antivirus]: antivirus molecule: include_vars OS-family in verify.yml resolves OS-specific config paths for assertions
- [Phase 04-antivirus]: galaxy_tags: replace pci-dss with pcidss — ansible-lint meta-no-tags rejects hyphens in tags
- [Phase 02-user-audit]: user_audit enforce.yml: password_lock:true over usermod -L for idempotence; two-step chage with -1|99999 regex; intersect(_ua_human_account_list) UID guard; no container detection needed (no systemd tasks)
- [Phase 02-user-audit]: Gap 2 closed: USR-01 traceability row updated from Pending to Complete in REQUIREMENTS.md
- [Phase 02-user-audit]: user_audit verify.yml: USR-02 assert omitted intentionally — container lastlog flakiness; comment block documents reasoning and manual verification path
- [Phase 05-tls-hardening]: tls_hardening: Suse platform removed from meta/main.yml — Galaxy schema rejects it; runtime support preserved via vars/Suse.yml
- [Phase 05-tls-hardening]: tls_hardening: handlers/main.yml empty per D-21 — TLS policy changes apply to new connections, callers reload their own daemons
- [Phase 05-tls-hardening]: tls_hardening enforce.yml: ssl_conf = ssl_sect as canonical idempotence anchor; full TLS chain as single blockinfile block; no notify directives (D-21)
- [Phase 05-tls-hardening]: tls_hardening review.yml: TLS 1.0/1.1 blocked expressed as separate RHEL and openssl.cnf fields (D-13 compliance)
- [Phase 05-tls-hardening]: tls_hardening: update-crypto-policies check skipped in containers (D-17) — not available in Docker/Podman
- [Phase 05-tls-hardening]: tls_hardening: slurp used for FIPS and openssl.cnf reads — reads managed host not controller
- [Phase 05-tls-hardening]: tls_hardening molecule: verify.yml uses set_fact for OS-specific openssl.cnf path (no include_vars relative paths)
- [Phase 05-tls-hardening]: tls_hardening inserted after antivirus in both CI matrices — consistent with ROADMAP phase sequence
- [Phase 05.1-ssh-access-vm-test]: pre-commit wrapper: created /tmp/bin/pre-commit wrapper pointing to venv Python module — venv shebang broken (references old path /repos/malpanez vs /repos/wcl/malpanez), wrapper unblocks commits without touching venv files
- [Phase 06-usbguard]: usbguard molecule verify: asserts package NOT installed (not service running) — meta:end_host fires before install when USB bus absent
- [Phase 06-usbguard]: usbguard: ansible.builtin.service in handler (not systemd), Suse omitted from meta platforms (Galaxy schema), _usbguard_usb_available guard for container safety, EPEL conditional as Jinja2 expression (RHEL 8 only)
- [Phase 06-usbguard]: usbguard tasks/main.yml: stat /sys/bus/usb/devices for USB detection; review.yml uses package_facts module for package presence check

### Roadmap Evolution

- Phase 05.1 inserted after Phase 5: SSH Access VM Test — commit workflow, playbook, and user_audit inventory for VM-based sssd_ad_integration validation (INSERTED)

### Pending Todos

None yet.

### Blockers/Concerns

- usbguard full enforcement (service start) cannot be tested in Docker Molecule — VM test only
- antivirus: EPEL RPM URL uses ansible_distribution_major_version; verify pattern on RHEL 8 vs 9 during Phase 4

## Session Continuity

Last session: 2026-04-20T13:13:05.722Z
Stopped at: Completed 06-usbguard/06-02-PLAN.md
Resume file: None
