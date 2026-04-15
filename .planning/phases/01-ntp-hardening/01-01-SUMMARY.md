---
phase: 01-ntp-hardening
plan: "01"
subsystem: infra
tags: [ansible, chrony, ntp, galaxy, argument_specs, molecule]

requires: []
provides:
  - ntp_hardening role scaffold with Galaxy-valid metadata
  - 11 defaults variables with full argument_specs documentation
  - OS-family vars for Debian, RedHat, Suse with correct paths/service names
  - Restart chronyd handler with container guard
  - tests/test.yml with FQCN role reference
affects: [01-02, 01-03, 01-04, 01-05]

tech-stack:
  added: []
  patterns:
    - ansible-galaxy role init before any file creation
    - OS-family vars (vars/Debian.yml, vars/RedHat.yml, vars/Suse.yml) for package/service/path divergence
    - handler changed_when:true with container guard (_ntp_in_container)
    - Galaxy schema: EL versions:[all], Debian [buster,bullseye,bookworm], Ubuntu [bionic,focal,jammy]
    - argument_specs documents every defaults variable with type and description

key-files:
  created:
    - roles/ntp_hardening/defaults/main.yml
    - roles/ntp_hardening/vars/Debian.yml
    - roles/ntp_hardening/vars/RedHat.yml
    - roles/ntp_hardening/vars/Suse.yml
    - roles/ntp_hardening/handlers/main.yml
    - roles/ntp_hardening/meta/main.yml
    - roles/ntp_hardening/meta/argument_specs.yml
    - roles/ntp_hardening/tests/test.yml
  modified: []

key-decisions:
  - "ntp_hardening_service: chrony on Debian, chronyd on RedHat/Suse — service name diverges between OS families"
  - "handler uses _ntp_in_container guard so systemd restart is skipped inside containers"
  - "compliance tags pci/nis2/soc2/hipaa in galaxy_tags per NTP-06 requirement"
  - "deny_all defaults to true — client-only mode by default, serving requires explicit ntp_hardening_allow"

patterns-established:
  - "OS-family vars pattern: vars/Debian.yml + vars/RedHat.yml + vars/Suse.yml loaded by include_vars in main.yml"
  - "Handler pattern: changed_when:true + when: not _ntp_in_container | bool"
  - "argument_specs 1:1 coverage of defaults variables (all 11 documented)"

requirements-completed: [STD-01, STD-06, STD-07, STD-08, STD-09, STD-14, NTP-06]

duration: 10min
completed: 2026-04-15
---

# Phase 01 Plan 01: Scaffold ntp_hardening Role Summary

**ntp_hardening role scaffolded via ansible-galaxy with 11 chrony defaults, OS-family vars (Debian/RedHat/Suse), Galaxy-valid metadata, argument_specs covering all variables, and a container-aware chronyd handler**

## Performance

- **Duration:** 10 min
- **Started:** 2026-04-15T06:02:42Z
- **Completed:** 2026-04-15T06:12:08Z
- **Tasks:** 1
- **Files modified:** 11

## Accomplishments

- Role scaffold created via `ansible-galaxy role init` — all standard directories present
- All 11 defaults variables defined (enabled gate, 4 NTP servers, makestep, rtcsync, maxdistance, minsources, allow, deny_all, leapsectz, logdir, logchange)
- Three OS-family vars files provide correct package name, service name, config path, and conf.d path for Debian, RedHat, and Suse families
- Galaxy metadata with valid platform schema and compliance tags (pci, nis2, soc2, hipaa)
- argument_specs documents every defaults variable with type, default, and description
- All pre-commit hooks passed: ansible-lint, yamllint, secrets detection

## Task Commits

1. **Task 1: Scaffold role and populate defaults, vars, handler, tests, meta** - `f65136d` (feat)
2. **Task 1: Scaffold inventory** - `5f4c46c` (chore — scaffold artifact committed after pre-commit fix)

## Files Created/Modified

- `roles/ntp_hardening/defaults/main.yml` - 11 role defaults with correct types and values
- `roles/ntp_hardening/vars/Debian.yml` - chrony/chrony service, /etc/chrony/chrony.conf path
- `roles/ntp_hardening/vars/RedHat.yml` - chrony/chronyd service, /etc/chrony.conf path
- `roles/ntp_hardening/vars/Suse.yml` - chrony/chronyd service, /etc/chrony.conf path (mirrors RedHat)
- `roles/ntp_hardening/handlers/main.yml` - Restart chronyd with changed_when:true + container guard
- `roles/ntp_hardening/meta/main.yml` - Galaxy metadata, compliance tags, valid platform versions
- `roles/ntp_hardening/meta/argument_specs.yml` - All 11 defaults documented with type + description
- `roles/ntp_hardening/tests/test.yml` - FQCN role reference malpanez.security.ntp_hardening
- `roles/ntp_hardening/tasks/main.yml` - Empty scaffold placeholder (filled in plan 01-02)
- `roles/ntp_hardening/vars/main.yml` - Empty scaffold placeholder
- `roles/ntp_hardening/tests/inventory` - Scaffold localhost inventory

## Decisions Made

- `ntp_hardening_service: chrony` on Debian vs `chronyd` on RedHat/Suse — the service name diverges between OS families and must be sourced from OS vars
- Handler uses `when: not _ntp_in_container | bool` guard — containers reject `adjtimex()` syscalls, restarting chronyd inside containers fails
- `ntp_hardening_deny_all: true` by default — role runs in client-only mode unless `ntp_hardening_allow` is set explicitly (secure default)
- Compliance tags pci/nis2/soc2/hipaa added to galaxy_tags per NTP-06 requirement

## Deviations from Plan

None - plan executed exactly as written.

Minor note: `tests/inventory` scaffold file required a separate commit after pre-commit's `end-of-file-fixer` hook auto-corrected a trailing newline. Not a deviation — standard pre-commit behavior.

## Issues Encountered

- Pre-commit `end-of-file-fixer` hook modified `tests/inventory` (removed extra blank line from ansible-galaxy scaffold). Required re-staging and a second commit. Resolved immediately.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- Role scaffold complete. Plan 01-02 (tasks/main.yml, review.yml, enforce.yml, templates/) can proceed immediately.
- All variable contracts established — task authors know exact variable names and types.
- OS-family path divergence resolved — task files can reference `ntp_hardening_config_file` and `ntp_hardening_conf_d` directly.

---
*Phase: 01-ntp-hardening*
*Completed: 2026-04-15*
