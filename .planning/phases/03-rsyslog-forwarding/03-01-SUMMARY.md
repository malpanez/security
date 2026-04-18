---
phase: 03-rsyslog-forwarding
plan: 01
subsystem: infra
tags: [rsyslog, logging, syslog, tls, ansible-role, galaxy]

requires: []
provides:
  - rsyslog_forwarding role skeleton with all variable contracts
  - defaults/main.yml with 20 rsyslog_forwarding_* variables
  - OS-family vars for Debian, RedHat, Suse
  - Galaxy-valid meta/main.yml with compliance tags (pci, nis2, soc2, hipaa)
  - argument_specs.yml with 1:1 documentation for all defaults
  - Container-aware handler for rsyslog restart
  - FQCN test playbook
affects: [03-02, 03-03, 03-04, 03-05]

tech-stack:
  added: [rsyslog_forwarding Ansible role]
  patterns:
    - rsyslog_forwarding_ variable prefix for role scope
    - OS-family vars split (Debian/RedHat/Suse) for package differences
    - rsyslog-module-gtls on Suse vs rsyslog-gnutls on Debian/RedHat
    - _rsyslog_in_container container detection variable in handler

key-files:
  created:
    - roles/rsyslog_forwarding/defaults/main.yml
    - roles/rsyslog_forwarding/vars/Debian.yml
    - roles/rsyslog_forwarding/vars/RedHat.yml
    - roles/rsyslog_forwarding/vars/Suse.yml
    - roles/rsyslog_forwarding/meta/main.yml
    - roles/rsyslog_forwarding/meta/argument_specs.yml
    - roles/rsyslog_forwarding/handlers/main.yml
    - roles/rsyslog_forwarding/tests/test.yml
  modified: []

key-decisions:
  - "Suse uses rsyslog-module-gtls (not rsyslog-gnutls) for TLS — different package name on openSUSE/SLES"
  - "20 defaults defined (plan required 16 minimum) — logrotate variables included in base scaffold"
  - "rsyslog_forwarding_resume_retry_count defaults to -1 (retry indefinitely) for reliability"
  - "rsyslog_forwarding_file_create_mode: 0640 — restricts log read access to rsyslog group"

patterns-established:
  - "Pattern: rsyslog_forwarding_ prefix for all role variables"
  - "Pattern: _rsyslog_in_container bool guard in handlers (matches _ntp_in_container from ntp_hardening)"

requirements-completed: [STD-01, STD-05, STD-06, STD-07, STD-08, STD-09, STD-14, LOG-05, LOG-06]

duration: 12min
completed: 2026-04-18
---

# Phase 03 Plan 01: rsyslog_forwarding Role Scaffold Summary

**rsyslog_forwarding role scaffolded via ansible-galaxy with 20 defaults, 3 OS-family vars files, Galaxy metadata with compliance tags, full argument_specs, container-aware handler, and FQCN test playbook**

## Performance

- **Duration:** 12 min
- **Started:** 2026-04-18T10:29:28Z
- **Completed:** 2026-04-18T10:41:35Z
- **Tasks:** 1
- **Files modified:** 12

## Accomplishments

- Role skeleton created via `ansible-galaxy role init roles/rsyslog_forwarding --offline`
- 20 defaults variables defined covering forwarding config, disk-assisted queue, TLS options, logrotate
- OS-family vars for 3 families with correct TLS package names (rsyslog-module-gtls on Suse)
- Galaxy-valid meta/main.yml with pci, nis2, soc2, hipaa compliance tags and EL versions: [all]
- argument_specs.yml with 1:1 documentation for all 20 defaults variables
- Container-aware handler using `_rsyslog_in_container` with `changed_when: true`
- FQCN test playbook using `malpanez.security.rsyslog_forwarding`
- Collection reinstalled via `ansible-galaxy collection install . --force -p .ansible/collections`
- yamllint passes 0 errors

## Task Commits

1. **Task 1: Scaffold role and populate defaults, vars, meta, handlers, tests** - `1542649` (feat)

**Plan metadata:** (docs commit follows)

## Files Created/Modified

- `roles/rsyslog_forwarding/defaults/main.yml` - 20 rsyslog_forwarding_* variables
- `roles/rsyslog_forwarding/vars/Debian.yml` - rsyslog-gnutls TLS package, rsyslog service
- `roles/rsyslog_forwarding/vars/RedHat.yml` - rsyslog-gnutls TLS package, rsyslog service
- `roles/rsyslog_forwarding/vars/Suse.yml` - rsyslog-module-gtls TLS package (Suse-specific)
- `roles/rsyslog_forwarding/meta/main.yml` - Galaxy metadata with compliance tags
- `roles/rsyslog_forwarding/meta/argument_specs.yml` - Full variable documentation
- `roles/rsyslog_forwarding/handlers/main.yml` - Restart rsyslog with container guard
- `roles/rsyslog_forwarding/tests/test.yml` - FQCN role test playbook

## Decisions Made

- Suse uses `rsyslog-module-gtls` instead of `rsyslog-gnutls` — different package naming on openSUSE/SLES. This is a known pitfall documented in the plan.
- 20 variables defined (plan minimum was 16) — all logrotate variables included in the base scaffold since they are part of the complete role contract.
- `rsyslog_forwarding_resume_retry_count: -1` defaults to indefinite retry — prevents message loss when remote endpoint is temporarily unavailable.
- `rsyslog_forwarding_file_create_mode: "0640"` — CIS-aligned log file permissions.

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered

- ansible-lint takes >120s on this system (initial collection discovery overhead). Background run confirmed 0 violations — only the offline mode warning was emitted.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- Role scaffold ready for tasks implementation (plan 03-02)
- All variable contracts defined and documented — tasks/templates can reference all rsyslog_forwarding_* variables
- OS-family vars provide correct package names for all 3 supported families
- Handler is wired and ready to be notified by task changes
