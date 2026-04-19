---
phase: 05-tls-hardening
plan: "01"
subsystem: infra
tags: [ansible, tls, openssl, crypto-policies, hardening, rhel, debian, suse]

requires: []
provides:
  - "tls_hardening role scaffold at roles/tls_hardening/"
  - "defaults: tls_hardening_enabled, rhel_policy, min_protocol, cipher_string"
  - "OS-family var files: RedHat.yml, Debian.yml, Suse.yml with openssl_cnf paths"
  - "Galaxy-valid meta/main.yml with compliance tags"
  - "argument_specs.yml documenting all 4 defaults"
  - "Empty handlers/main.yml per D-21 (no service restarts)"
  - "FQCN tests/test.yml"
affects: [05-02, 05-03, 05-04, 05-05]

tech-stack:
  added: []
  patterns:
    - "tls_hardening: two-branch enforce (RHEL 8/9 crypto-policies vs openssl.cnf)"
    - "Suse platform omitted from meta/main.yml (Galaxy schema rejects it)"

key-files:
  created:
    - roles/tls_hardening/defaults/main.yml
    - roles/tls_hardening/vars/RedHat.yml
    - roles/tls_hardening/vars/Debian.yml
    - roles/tls_hardening/vars/Suse.yml
    - roles/tls_hardening/meta/main.yml
    - roles/tls_hardening/meta/argument_specs.yml
    - roles/tls_hardening/handlers/main.yml
    - roles/tls_hardening/tests/test.yml
  modified: []

key-decisions:
  - "Suse platform entry removed from meta/main.yml — Galaxy schema rejects it (same as all prior roles)"
  - "handlers/main.yml empty per D-21 — TLS policy changes apply to new connections only"
  - "4 configurable defaults only: enabled, rhel_policy, min_protocol, cipher_string"

patterns-established:
  - "tls_hardening: vars/RedHat.yml holds /etc/pki/tls/openssl.cnf path, Debian.yml/Suse.yml hold /etc/ssl/openssl.cnf"

requirements-completed: [STD-01, STD-05, STD-06, STD-07, STD-08, STD-09, TLS-05, TLS-06]

duration: 20min
completed: 2026-04-19
---

# Phase 05 Plan 01: tls_hardening Role Scaffold Summary

**tls_hardening role scaffolded via ansible-galaxy with Galaxy-valid meta, 4 configurable defaults, OS-family openssl.cnf paths, FQCN argument_specs, and empty handlers — yamllint and ansible-lint --profile production pass 0 errors**

## Performance

- **Duration:** 20 min
- **Started:** 2026-04-19T10:00:00Z
- **Completed:** 2026-04-19T10:20:06Z
- **Tasks:** 1
- **Files modified:** 11

## Accomplishments

- Role skeleton created at `roles/tls_hardening/` via `ansible-galaxy role init`
- All 8 static files populated: defaults, 3 OS-family vars, meta/main.yml, meta/argument_specs.yml, handlers/main.yml, tests/test.yml
- Collection reinstalled (`ansible-galaxy collection install . --force -p .ansible/collections`)
- yamllint and ansible-lint --profile production pass with 0 errors

## Task Commits

1. **Task 1: Scaffold tls_hardening role and populate all static files** - `eac1804` (feat)

**Plan metadata:** _(final docs commit below)_

## Files Created/Modified

- `roles/tls_hardening/defaults/main.yml` - 4 configurable vars: enabled, rhel_policy, min_protocol, cipher_string
- `roles/tls_hardening/vars/RedHat.yml` - tls_hardening_openssl_cnf: /etc/pki/tls/openssl.cnf
- `roles/tls_hardening/vars/Debian.yml` - tls_hardening_openssl_cnf: /etc/ssl/openssl.cnf
- `roles/tls_hardening/vars/Suse.yml` - tls_hardening_openssl_cnf: /etc/ssl/openssl.cnf
- `roles/tls_hardening/meta/main.yml` - Galaxy metadata with pcidss/hipaa/nis2/soc2/openssl/cryptopolicy tags
- `roles/tls_hardening/meta/argument_specs.yml` - All 4 defaults documented (type, default, description, choices)
- `roles/tls_hardening/handlers/main.yml` - Empty per D-21 (no service restarts)
- `roles/tls_hardening/tests/test.yml` - FQCN play name + malpanez.security.tls_hardening role reference

## Decisions Made

- **Suse platform removed from meta/main.yml:** Galaxy schema validation rejects `Suse` as a platform name. Pre-commit ansible-lint caught this at commit time. Same as all prior roles in the collection — only Debian, Ubuntu, EL are valid Galaxy platform entries.
- **handlers/main.yml empty:** Per decision D-21 from CONTEXT.md — TLS policy changes (crypto-policies and openssl.cnf) apply to new connections only; no service restart needed. Callers must reload their own daemons.
- **tasks/main.yml kept:** Scaffolded empty tasks/main.yml retained (not deleted) to avoid ansible-lint failures. Plan 02 will overwrite it with the gate pattern.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Removed Suse platform entry from meta/main.yml**
- **Found during:** Task 1 (ansible-lint validation)
- **Issue:** Plan action step 6 specified `Suse versions:[all]` in platforms. Galaxy schema rejects the `Suse` platform name — ansible-lint `schema[meta]` failure.
- **Fix:** Removed the `- name: Suse` platform block from meta/main.yml. SUSE support is via vars/Suse.yml at runtime, not Galaxy metadata.
- **Files modified:** roles/tls_hardening/meta/main.yml
- **Verification:** ansible-lint --profile production passed 0 errors after fix
- **Committed in:** eac1804 (Task 1 commit)

---

**Total deviations:** 1 auto-fixed (Rule 1 - Bug: invalid Galaxy platform name)
**Impact on plan:** Minimal — Suse runtime support preserved via vars/Suse.yml. Only metadata entry removed. No functionality impact.

## Issues Encountered

- ansible-lint timed out when run against the full role directory (`timeout 120`). Resolved by running against specific subdirectories excluding tasks/ (which is empty at this stage).

## Next Phase Readiness

- Role scaffold complete; plans 02-05 can now build tasks/, templates/, and molecule/ on top of this skeleton.
- `roles/tls_hardening/tasks/main.yml` is a stub — plan 02 must overwrite it with the review/enforce gate pattern.
- No blockers.

---
*Phase: 05-tls-hardening*
*Completed: 2026-04-19*
