---
phase: 06-usbguard
plan: "03"
subsystem: infra
tags: [usbguard, ansible, linux-hardening, usb-security]

requires:
  - phase: 06-01
    provides: role scaffold, defaults/main.yml, vars/RedHat.yml, handlers/main.yml

provides:
  - roles/usbguard/tasks/enforce.yml — full enforcement with safety-critical task ordering
  - roles/usbguard/templates/usbguard-daemon.conf.j2 — daemon configuration template

affects: [06-04, 06-05]

tech-stack:
  added: []
  patterns:
    - "meta:end_host for container skip before any install tasks"
    - "write-once generate-policy with empty-output guard"
    - "daemon.conf mode 0600 (usbguard daemon requirement)"

key-files:
  created:
    - roles/usbguard/tasks/enforce.yml
    - roles/usbguard/templates/usbguard-daemon.conf.j2
  modified: []

key-decisions:
  - "generate-policy is write-once: stat pre-check prevents overwriting existing rules on re-runs"
  - "generate-policy stdout | length > 0 guard prevents writing empty file when no USB devices present"
  - "daemon.conf requires both RuleFile and RuleFolder — RuleFolder alone silently ignores rules.d/ files"
  - "mode 0600 on daemon.conf is required — usbguard daemon refuses to start with broader permissions"
  - "EPEL URL uses ansible_distribution_major_version to support RHEL 8 (only version needing EPEL)"

patterns-established:
  - "Pattern 1: safety-critical install order — container-skip -> install -> generate-policy -> rules -> daemon.conf -> service"
  - "Pattern 2: write-once policy generation — stat existing file before running generate-policy"

requirements-completed: [STD-04, USB-02, USB-03, USB-04, USB-05, USB-06]

duration: 20min
completed: 2026-04-20
---

# Phase 06 Plan 03: usbguard enforce.yml and daemon.conf template Summary

**Safety-critical usbguard enforcement: container-aware meta:end_host skip, write-once generate-policy with empty-output guard, daemon.conf mode 0600 with both RuleFile and RuleFolder directives**

## Performance

- **Duration:** 20 min
- **Started:** 2026-04-20T13:10:00Z
- **Completed:** 2026-04-20T13:30:00Z
- **Tasks:** 2
- **Files modified:** 2

## Accomplishments

- enforce.yml implements the exact safety-critical task order: container-skip -> install -> generate-policy (write-once) -> rules.d/ -> daemon.conf (0600) -> service
- usbguard-daemon.conf.j2 contains both RuleFile and RuleFolder, all configurable policy directives, and conditional AuditFilePath
- All sections tagged (usbguard/enforce/install/configure/service/verify), all modules FQCN, yamllint and ansible-lint production profile pass

## Task Commits

Each task was committed atomically:

1. **Task 1: Implement tasks/enforce.yml with safety-critical task ordering** - `ee564d3` (feat)
2. **Task 2: Create usbguard-daemon.conf.j2 template** - `b19ada0` (feat)

**Plan metadata:** (docs commit below)

## Files Created/Modified

- `roles/usbguard/tasks/enforce.yml` — Full enforcement logic with container skip, EPEL conditional, write-once generate-policy, mode 0600 daemon.conf, service management
- `roles/usbguard/templates/usbguard-daemon.conf.j2` — Daemon configuration with RuleFile + RuleFolder, IPC group from OS var, conditional AuditFilePath

## Decisions Made

- generate-policy write-once: stat pre-check before running prevents policy overwrite on re-runs (idempotence)
- stdout | length > 0 guard: prevents writing empty 00-initial-policy.conf when no USB devices are enumerated
- Both RuleFile and RuleFolder in daemon.conf: without RuleFolder, usbguard silently ignores all files in rules.d/
- mode 0600 on daemon.conf: required by usbguard daemon — it refuses to start with world/group-readable config
- EPEL URL as block scalar (`>-`): keeps YAML line under 120 chars for yamllint compliance

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered

- yamllint 121-char line on the EPEL RPM URL — fixed with YAML block scalar (`>-`), yamllint then passes cleanly.
- venv shebang broken (old path `/repos/malpanez/security` vs `/repos/wcl/malpanez/security`) — used `/home/malpanez/ansible/bin/ansible-lint` directly, consistent with pre-commit wrapper pattern from Phase 05.1.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- enforce.yml and daemon.conf template ready for Molecule scenario (plan 06-04)
- Service enforcement cannot be tested in Docker containers — molecule scenario skips service verification when USB bus absent (meta:end_host fires before install)

---
*Phase: 06-usbguard*
*Completed: 2026-04-20*
