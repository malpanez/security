---
phase: 02-user-audit
plan: "03"
subsystem: infra
tags: [ansible, user_audit, account-hardening, chage, password-expiry, account-lock]

requires:
  - phase: 02-user-audit plan 01
    provides: defaults/main.yml, vars/OS.yml with user_audit_nologin_shell
  - phase: 02-user-audit plan 02
    provides: tasks/review.yml sets _ua_human_account_list, _ua_no_expiry, _ua_inactive_by_days, _ua_service_login_shells

provides:
  - tasks/main.yml gate pattern: setup -> OS assert -> include_vars -> review -> enforce (gated)
  - tasks/enforce.yml: account lock via ansible.builtin.user password_lock, two-step chage idempotence, service shell fix

affects: [02-user-audit plan 04 molecule, 02-user-audit plan 05 CI]

tech-stack:
  added: []
  patterns:
    - "Gate pattern: security_mode | default('review') == 'enforce' + role_enabled | bool"
    - "Two-step chage: collect (changed_when:false) then set only if maxdays matches -1|99999 regex"
    - "Triple guard: intersect(_ua_human_account_list) + item not in skip_users + item != root"
    - "ansible.builtin.user password_lock: true for idempotent account locking (not usermod -L)"

key-files:
  created:
    - roles/user_audit/tasks/main.yml
    - roles/user_audit/tasks/enforce.yml
  modified: []

key-decisions:
  - "ansible.builtin.user password_lock: true chosen over usermod -L for idempotence (module checks current state)"
  - "Two-step chage: pre-check maxdays -1 or 99999 before setting — avoids spurious changes when already compliant"
  - "intersect(_ua_human_account_list) as UID guard — lastlog --before includes system accounts, intersection scopes to UID>=1000 humans only"
  - "not ansible_check_mode gate on all state-modifying command tasks — enables safe dry-run"
  - "No container detection (_ua_in_container) needed — role has no systemd/service operations"

patterns-established:
  - "Gate pattern matches ntp_hardening/main.yml exactly — 5-task structure without container detection"
  - "changed_when:true on chage set task (genuinely changes state); changed_when:false on collect/verify (read-only)"

requirements-completed: [USR-02, USR-03, USR-04, USR-05, STD-02, STD-04, STD-05]

duration: 5min
completed: 2026-04-18
---

# Phase 2 Plan 03: Tasks enforce.yml and main.yml Summary

**Gate pattern + idempotent account enforcement: password_lock via ansible.builtin.user, two-step chage with -1|99999 regex, triple root/system guard on all enforce tasks**

## Performance

- **Duration:** 5 min
- **Started:** 2026-04-18T21:17:06Z
- **Completed:** 2026-04-18T21:22:00Z
- **Tasks:** 2
- **Files modified:** 2

## Accomplishments

- tasks/main.yml: standard 5-task gate pattern (setup, OS assert, include_vars, review, enforce-gated) matching ntp_hardening structure
- tasks/enforce.yml: account lock (password_lock:true), two-step chage (collect changed_when:false + set changed_when:true), service shell fix, verify + report
- Triple guard on every enforce task: intersect(_ua_human_account_list) + skip_users check + item != 'root'
- ansible-lint --profile production: 0 failures on 4 files

## Task Commits

1. **Task 1: Create tasks/main.yml with gate pattern** — `2fad350` (feat) — combined with Task 2
2. **Task 2: Create tasks/enforce.yml** — `2fad350` (feat)

## Files Created/Modified

- `roles/user_audit/tasks/main.yml` - Gate pattern: gather facts, OS assert, include_vars, review always, enforce when enabled+enforce mode
- `roles/user_audit/tasks/enforce.yml` - Lock inactive accounts, two-step chage expiry, service shell fix, verify enforcement results

## Decisions Made

- ansible.builtin.user password_lock:true chosen over usermod -L — module is idempotent (checks current shadow state before writing)
- Two-step chage pre-check (chage -l then regex search for -1|99999) avoids spurious changed=true on already-compliant accounts
- intersect(_ua_human_account_list) is the UID guard — lastlog --before output can include system accounts; intersection limits lock candidates to human accounts (UID>=1000) only
- No _ua_in_container fact needed — role has no service/systemd tasks, unlike ntp_hardening

## Deviations from Plan

None - plan executed exactly as written. Files matched spec on read; yamllint and ansible-lint passed with 0 errors.

## Issues Encountered

None - both files were pre-existing from a prior execution of this plan. Verification confirmed full compliance with acceptance criteria.

## Next Phase Readiness

- tasks/main.yml and tasks/enforce.yml complete — Molecule scenario (plan 02-04) can now test the full role
- review.yml facts (_ua_human_account_list, _ua_no_expiry, _ua_inactive_by_days, _ua_service_login_shells) are correctly consumed by enforce.yml

---
*Phase: 02-user-audit*
*Completed: 2026-04-18*
