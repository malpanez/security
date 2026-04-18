---
phase: 04-antivirus
plan: "03"
subsystem: infra
tags: [clamav, antivirus, jinja2, systemd, rhel, debian, freshclam]

requires:
  - phase: 04-antivirus-01
    provides: defaults/main.yml and vars/RedHat.yml and vars/Debian.yml with antivirus_* variables

provides:
  - clamd.conf.j2: OS-specific ClamAV daemon config via antivirus_* vars
  - freshclam.conf.j2: DB update config with NotifyClamd pointing to antivirus_clamd_config
  - clamav-scan.service.j2: systemd oneshot unit iterating antivirus_scan_dirs
  - clamav-scan.timer.j2: periodic scan timer with OnCalendar, Persistent=true, RandomizedDelaySec

affects: [04-04-molecule, 04-05-ci, enforce.yml template tasks]

tech-stack:
  added: []
  patterns:
    - "Jinja2 for loop in systemd service ExecStart for multi-directory scan args"
    - "NotifyClamd references antivirus_clamd_config (config path, not socket) — Jinja2 var drives OS-specific path"
    - "OnCalendar value from antivirus_scan_schedule default — systemd accepts daily/weekly/hourly shorthands"

key-files:
  created:
    - roles/antivirus/templates/clamd.conf.j2
    - roles/antivirus/templates/freshclam.conf.j2
    - roles/antivirus/templates/clamav-scan.service.j2
    - roles/antivirus/templates/clamav-scan.timer.j2
  modified: []

key-decisions:
  - "clamav-scan.service.j2 uses Jinja2 for loop to build clamscan directory args — cleaner than space-joined string"
  - "freshclam.conf NotifyClamd uses antivirus_clamd_config (not socket path) — freshclam reads conf file to find socket"
  - "clamav-scan.timer.j2 includes Documentation= line for consistency with service unit"

patterns-established:
  - "Jinja2 loop.last check for backslash continuation in ExecStart multi-line args"

requirements-completed: [AV-03, AV-04]

duration: 4min
completed: 2026-04-18
---

# Phase 04 Plan 03: antivirus Templates Summary

**4 ClamAV Jinja2 templates with OS-specific vars: clamd.conf, freshclam.conf, clamav-scan.service, clamav-scan.timer**

## Performance

- **Duration:** 4 min
- **Started:** 2026-04-18T19:31:26Z
- **Completed:** 2026-04-18T19:35:00Z
- **Tasks:** 1
- **Files modified:** 4

## Accomplishments

- clamd.conf.j2 drives all config values (paths, user, limits) from antivirus_* vars — no hardcoded values
- freshclam.conf.j2 uses NotifyClamd with antivirus_clamd_config resolving to OS-specific path (/etc/clamd.d/scan.conf on RHEL, /etc/clamav/clamd.conf on Debian)
- clamav-scan.service.j2 iterates antivirus_scan_dirs with Jinja2 loop and correct backslash continuation
- clamav-scan.timer.j2 uses Persistent=true and RandomizedDelaySec=300 for reliability

## Task Commits

1. **Task 1: Create all 4 Jinja2 templates** - `2ee5209` (feat)

**Plan metadata:** TBD (docs commit)

## Files Created/Modified

- `roles/antivirus/templates/clamd.conf.j2` - ClamAV daemon config with OS-specific vars for paths, user, limits
- `roles/antivirus/templates/freshclam.conf.j2` - freshclam update config with NotifyClamd pointing at clamd config path
- `roles/antivirus/templates/clamav-scan.service.j2` - systemd oneshot unit running clamscan over antivirus_scan_dirs
- `roles/antivirus/templates/clamav-scan.timer.j2` - periodic timer with OnCalendar, Persistent, RandomizedDelaySec

## Decisions Made

- clamav-scan.service.j2 Jinja2 for loop uses `{% if not loop.last %} \{% endif %}` pattern from 04-RESEARCH.md for clean ExecStart continuation
- Timer template includes Documentation= for consistency with service unit

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered

None.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- All 4 templates ready for enforce.yml ansible.builtin.template tasks (04-04)
- antivirus_clamd_config resolves correctly to OS path via vars files created in 04-01
- ansible-lint --profile production passes on all 4 templates (0 failures)

---
*Phase: 04-antivirus*
*Completed: 2026-04-18*
