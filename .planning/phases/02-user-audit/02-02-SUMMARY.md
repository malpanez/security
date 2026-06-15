---
phase: 2
plan: "02-02"
subsystem: user_audit
tags: [user-audit, review, read-only, account-hardening]
dependency_graph:
  requires: ["02-01"]
  provides: ["tasks/review.yml", "_ua_human_account_list", "_ua_no_expiry", "_ua_inactive_by_days"]
  affects: ["02-03"]
tech_stack:
  added: []
  patterns:
    - "Read-only audit tasks with changed_when: false + failed_when: false"
    - "getent+awk for UID-filtered human account collection"
    - "lastlog --before for inactive account detection (NOT --time)"
    - "intersect() filter to remove system accounts from inactive list"
    - "Two-fact pattern: register raw -> set_fact filtered list"
key_files:
  created:
    - roles/user_audit/tasks/review.yml
  modified: []
decisions:
  - "Use lastlog --before (not --time): --before returns accounts inactive longer than N days; --time returns recently-active accounts (inverted set)"
  - "intersect(_ua_human_account_list) in debug report: lastlog --before includes system accounts (uid<1000); intersection scopes result to human accounts only"
  - "failed_when: false on pwck: Debian minimal images return non-zero rc for accounts without /etc/shadow entries — play must not fail"
metrics:
  duration_minutes: 7
  completed_date: "2026-04-17"
  tasks_completed: 1
  tasks_total: 1
  files_created: 1
  files_modified: 0
requirements_addressed: [USR-01, STD-03, STD-05]
---

# Phase 2 Plan 02: Tasks review.yml Summary

Read-only user account audit task file with awk-based human account collection, lastlog --before inactive detection, UID 0 non-root check, service account shell check, pwck consistency check, and debug report with intersect filter.

## What Was Built

`roles/user_audit/tasks/review.yml` — 9 tasks implementing the read-only audit layer of the `user_audit` role.

| Task | Description | Key Detail |
|------|-------------|------------|
| 1 | Collect human local accounts (UID >= 1000) | getent passwd + awk filter, registers `_ua_human_accounts` |
| 2 | Set human accounts list fact | `_ua_human_account_list` set_fact from stdout_lines |
| 3 | Check password expiry for each human account | chage -l loop, registers `_ua_chage_results` |
| 4 | Identify accounts with no password expiry | `_ua_no_expiry` set_fact via selectattr search on 'Password expires.*never' |
| 5 | Find UID 0 non-root accounts | awk /etc/passwd $3==0 && $1!="root" |
| 6 | Find accounts inactive longer than threshold | `lastlog --before {{ user_audit_inactive_days }}` + awk NR>1 filter |
| 7 | Find service accounts with interactive login shells | awk UID 1-999 with bash/sh/zsh shell |
| 8 | Check passwd/shadow consistency | pwck -r -q, failed_when: false |
| 9 | User account audit report | debug msg with all findings, intersect for inactive_accounts |

## Facts Produced for enforce.yml

| Fact | Source | Consumer (02-03) |
|------|--------|-----------------|
| `_ua_human_account_list` | getent+awk stdout_lines | Loop base for lock + expiry tasks |
| `_ua_no_expiry` | selectattr on chage results | chage --maxdays enforcement loop |
| `_ua_inactive_by_days` | lastlog --before register | Account lock loop (intersected with human_account_list) |

## Decisions Made

1. **lastlog --before vs --time**: `--before N` returns accounts with last login MORE THAN N days ago (inactive). `--time N` returns accounts with last login LESS THAN N days ago (recently active). Research confirmed this from man page. The ROADMAP described `--time` incorrectly — `--before` is used throughout.

2. **intersect(_ua_human_account_list) in debug report**: `lastlog --before` includes all UIDs (system accounts like daemon, bin, sys with no login history). The intersect filter scopes the inactive display to human accounts only. enforce.yml must apply the same intersection in its lock loop.

3. **failed_when: false on pwck**: Debian minimal docker images may not have /etc/shadow entries for accounts like sync/halt/shutdown. pwck -r -q exits non-zero in this case. The play must not fail — rc and stdout are surfaced in the debug report for the operator to evaluate.

4. **selectattr('stdout', 'defined') before search**: The chage results loop may produce items with undefined stdout on failed items (rc != 0). The defined filter prevents Jinja2 type errors on the selectattr search.

## Deviations from Plan

None - plan executed exactly as written.

## Known Stubs

None — review.yml is a pure read-only data collection file. No rendering or UI output is involved.

## Self-Check: PASSED

- roles/user_audit/tasks/review.yml: FOUND
- Commit 1da5d82: FOUND
