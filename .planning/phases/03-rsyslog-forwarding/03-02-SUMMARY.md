---
phase: 03-rsyslog-forwarding
plan: "02"
subsystem: infra
tags: [ansible, rsyslog, logging, tls, review-enforce, drop-in]

requires:
  - phase: 03-rsyslog-forwarding-plan-01
    provides: role scaffold, defaults, vars, handlers, argument_specs, meta, templates stub

provides:
  - tasks/main.yml gate pattern with _rsyslog_in_container container detection
  - tasks/review.yml read-only audit of rsyslog package, service, drop-in, and TLS state
  - tasks/enforce.yml with TLS pre-flight assertions, package install, template deploy with validate, service management

affects: [03-03-templates, 03-04-molecule, 03-05-ci]

tech-stack:
  added: []
  patterns:
    - "ntp_hardening gate pattern replicated exactly for rsyslog_forwarding"
    - "TLS pre-flight assertions block anonymous auth, UDP, missing CA cert before any file changes"
    - "Template validate: rsyslogd -N1 -f %s enforces syntax before deploy"
    - "Container-aware service management via _rsyslog_in_container fact"

key-files:
  created:
    - roles/rsyslog_forwarding/tasks/review.yml
    - roles/rsyslog_forwarding/tasks/enforce.yml
  modified:
    - roles/rsyslog_forwarding/tasks/main.yml

key-decisions:
  - "enforce.yml tags: all tasks carry both role-level (rsyslog_forwarding) and section-level (install/configure/service/verify) tags for fine-grained --tags targeting"
  - "TLS pre-flight assertions run before package install to fail fast on misconfiguration"
  - "changed_when: false on all review.yml command tasks ensures review mode is truly read-only"

patterns-established:
  - "review.yml: all command tasks have changed_when: false and failed_when: false"
  - "enforce.yml: assert tasks use quiet: true and clear fail_msg messages"
  - "enforce.yml: install tasks split by OS family with when: condition for idempotent multi-distro support"

requirements-completed: [STD-02, STD-03, STD-04, STD-05, LOG-01, LOG-02, LOG-03, LOG-04, LOG-05]

duration: 2min
completed: 2026-04-18
---

# Phase 03 Plan 02: rsyslog_forwarding Task Files Summary

**rsyslog_forwarding tasks/main.yml, review.yml, enforce.yml with TLS pre-flight assertions, rsyslogd -N1 validate, and container-aware service management**

## Performance

- **Duration:** 2 min
- **Started:** 2026-04-18T10:43:37Z
- **Completed:** 2026-04-18T10:45:53Z
- **Tasks:** 2
- **Files modified:** 3

## Accomplishments

- tasks/main.yml follows exact ntp_hardening gate pattern with `_rsyslog_in_container` fact and review/enforce include_tasks guards
- tasks/review.yml is purely read-only: 3 command tasks + stat + slurp + set_fact + debug, all with `changed_when: false`
- tasks/enforce.yml has 4 tagged sections (install/configure/service/verify) with TLS pre-flight assertions blocking anonymous auth, UDP protocol, and missing CA cert

## Task Commits

1. **Task 1: Implement tasks/main.yml gate pattern** - `b5cc3bd` (feat)
2. **Task 2: Implement tasks/review.yml and tasks/enforce.yml** - `c6fa5c9` (feat)

## Files Created/Modified

- `roles/rsyslog_forwarding/tasks/main.yml` - Gate pattern: setup, assert OS, include_vars, container detect, review/enforce
- `roles/rsyslog_forwarding/tasks/review.yml` - Read-only audit: package check, service status, drop-in stat, TLS detection via slurp+b64decode
- `roles/rsyslog_forwarding/tasks/enforce.yml` - Pre-flight assertions, OS-split package install, template with validate, logrotate, container-aware service

## Decisions Made

- All enforce.yml tasks carry both `rsyslog_forwarding` and section-level tags (install/configure/service/verify) for fine-grained targeting
- TLS pre-flight assertions ordered before package install to fail fast on misconfiguration without touching the system
- `changed_when: false` on all review.yml command tasks — review mode never produces spurious change reports

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered

None.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- Task files are complete and ready for plan 03-03 (templates: 99-forwarding.conf.j2 and rsyslog-logrotate.j2)
- Plan 03-04 (molecule scenarios) depends on templates being in place first
- enforce.yml references `rsyslog_forwarding_tls_package` var — Suse uses `rsyslog-module-gtls` (in vars/Suse.yml from 03-01)

---
*Phase: 03-rsyslog-forwarding*
*Completed: 2026-04-18*
