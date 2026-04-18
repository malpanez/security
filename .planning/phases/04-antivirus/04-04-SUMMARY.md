---
phase: 04-antivirus
plan: "04"
subsystem: testing
tags: [molecule, clamav, antivirus, docker, ubuntu2204, rockylinux9]

requires:
  - phase: 04-antivirus-01
    provides: antivirus role defaults, vars/RedHat.yml, vars/Debian.yml
  - phase: 04-antivirus-02
    provides: antivirus role tasks (install, configure, enforce)
  - phase: 04-antivirus-03
    provides: antivirus role templates (clamd.conf.j2, freshclam.conf.j2, scan service/timer)
provides:
  - Molecule default scenario for antivirus role (ubuntu2204 + rockylinux9)
  - converge.yml with antivirus_update_db:false (skips 200MB freshclam in CI)
  - verify.yml asserting packages, configs, and timer units without DB/service state
affects:
  - ci-uv.yml (antivirus molecule matrix entry)
  - ci-cd-enterprise.yml (antivirus molecule matrix entry)

tech-stack:
  added: []
  patterns:
    - "antivirus_update_db:false pattern (analogous to aide_init_db:false) for CI containers"
    - "include_vars OS-family in verify.yml to resolve OS-specific config paths"
    - "_antivirus_in_container set_fact for container-aware assertions"

key-files:
  created:
    - roles/antivirus/molecule/default/molecule.yml
    - roles/antivirus/molecule/default/prepare.yml
    - roles/antivirus/molecule/default/converge.yml
    - roles/antivirus/molecule/default/verify.yml

key-decisions:
  - "antivirus_update_db:false in converge.yml skips 200MB freshclam download in CI containers"
  - "No DB file assertions in verify.yml — freshclam never ran so main.cvd absent"
  - "No service state assertions in verify.yml — clamd cannot start in Docker containers"
  - "include_vars OS-family in verify.yml resolves antivirus_clamd_config and antivirus_freshclam_config per OS"

patterns-established:
  - "Molecule verify pattern: load OS vars + container detection + package_facts + stat + assert (no service/DB state)"

requirements-completed: [AV-05, AV-06, STD-10, STD-11]

duration: 3min
completed: 2026-04-18
---

# Phase 04 Plan 04: Antivirus Molecule Scenario Summary

**Molecule default scenario for ClamAV antivirus role with ubuntu2204 + rockylinux9, skipping freshclam DB download in CI via antivirus_update_db:false**

## Performance

- **Duration:** 3 min
- **Started:** 2026-04-18T19:34:40Z
- **Completed:** 2026-04-18T19:37:30Z
- **Tasks:** 1
- **Files modified:** 4

## Accomplishments

- Created molecule.yml with Docker driver, privileged systemd containers for ubuntu2204 and rockylinux9
- Created prepare.yml with Rocky 9 nsswitch sss fix (failed_when: false, no-op on Debian)
- Created converge.yml with antivirus_update_db: false to skip 200MB freshclam CI download
- Created verify.yml asserting ClamAV package, clamd config, freshclam config, scan service, and scan timer — without DB file or service state checks

## Task Commits

1. **Task 1: Create Molecule scenario files** - `ed41605` (feat)

**Plan metadata:** _(pending docs commit)_

## Files Created/Modified

- `roles/antivirus/molecule/default/molecule.yml` - Docker driver, ubuntu2204 + rockylinux9 platforms with privileged systemd
- `roles/antivirus/molecule/default/prepare.yml` - Rocky 9 nsswitch sss fix
- `roles/antivirus/molecule/default/converge.yml` - Include antivirus role with antivirus_update_db: false
- `roles/antivirus/molecule/default/verify.yml` - Assert packages, configs, and timer units

## Decisions Made

- antivirus_update_db: false in converge.yml — freshclam database download is ~200MB; CI containers have limited egress and this mirrors the aide_init_db: false pattern
- No DB file assertions — with antivirus_update_db: false, main.cvd is never downloaded, so asserting its presence would always fail
- No service state assertions — clamd cannot start inside Docker containers; container-aware service assertions would require systemd mocking
- include_vars for OS family in verify.yml — resolves antivirus_clamd_config and antivirus_freshclam_config to the correct OS-specific path without duplicating paths

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered

None.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- Molecule scenario ready for CI matrix integration (04-05-PLAN.md)
- All 4 molecule files pass yamllint and ansible-lint --profile production
- verify.yml is container-safe: no DB or service state assertions that would fail in Docker

---
*Phase: 04-antivirus*
*Completed: 2026-04-18*
