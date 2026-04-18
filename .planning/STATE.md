---
gsd_state_version: 1.0
milestone: v1.2.0
milestone_name: milestone
status: verifying
stopped_at: Completed 03-rsyslog-forwarding 03-05-PLAN.md
last_updated: "2026-04-18T10:57:10.863Z"
last_activity: 2026-04-18
progress:
  total_phases: 6
  completed_phases: 2
  total_plans: 15
  completed_plans: 14
  percent: 0
---

# Project State

## Project Reference

See: .planning/PROJECT.md (updated 2026-04-14)

**Core value:** Each new role shows the auditor the deficiency first (review mode) then fixes it (enforce mode)
**Current focus:** Phase 03 — rsyslog-forwarding

## Current Position

Phase: 03 (rsyslog-forwarding) — EXECUTING
Plan: 5 of 5
Status: Phase complete — ready for verification
Last activity: 2026-04-18

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

### Pending Todos

None yet.

### Blockers/Concerns

- usbguard full enforcement (service start) cannot be tested in Docker Molecule — VM test only
- antivirus: EPEL RPM URL uses ansible_distribution_major_version; verify pattern on RHEL 8 vs 9 during Phase 4

## Session Continuity

Last session: 2026-04-18T10:57:10.849Z
Stopped at: Completed 03-rsyslog-forwarding 03-05-PLAN.md
Resume file: None
