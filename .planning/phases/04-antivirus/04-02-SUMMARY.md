---
phase: 04-antivirus
plan: "02"
subsystem: antivirus
tags: [clamav, antivirus, tasks, review, enforce, selinux, container-aware]
dependency_graph:
  requires: ["04-01"]
  provides: ["tasks/main.yml", "tasks/review.yml", "tasks/enforce.yml"]
  affects: ["roles/antivirus"]
tech_stack:
  added: []
  patterns:
    - Gate pattern with container detection (_antivirus_in_container)
    - review/enforce split with security_mode guard
    - SELinux boolean + restorecon for RHEL
    - antivirus_update_db flag to skip freshclam in CI
key_files:
  created:
    - roles/antivirus/tasks/review.yml
    - roles/antivirus/tasks/enforce.yml
  modified:
    - roles/antivirus/tasks/main.yml
decisions:
  - "antivirus_can_scan_system SELinux boolean set via ansible.posix.seboolean with restorecon on log + scan dirs"
  - "freshclam failed_when: rc not in [0,1] — rc=1 means DB already up to date (not a failure)"
  - "Container guard on service start, freshclam, and scan timer — same pattern as ntp_hardening"
metrics:
  duration_minutes: 8
  completed_date: "2026-04-18"
  tasks_completed: 3
  files_modified: 3
---

# Phase 04 Plan 02: Antivirus Task Files Summary

One-liner: ClamAV task files with gate pattern, read-only review, full EPEL+packages+SELinux+freshclam+systemd enforce.

## What Was Built

Three task files implementing the core antivirus role logic:

- **tasks/main.yml** — Gate pattern with OS assertion, OS vars load, container detection (`_antivirus_in_container`), always-run review, and gated enforce (`antivirus_enabled + security_mode==enforce`).
- **tasks/review.yml** — Read-only ClamAV posture report: binary presence, version, main.cvd/daily.cld existence, clamd service status, scan log presence. Zero system changes.
- **tasks/enforce.yml** — Full ClamAV installation and configuration across 4 tagged sections (install/configure/service/verify): EPEL install on RHEL, per-OS package install, log dirs, clamd.conf+freshclam.conf templates, SELinux boolean + restorecon, conditional freshclam run, systemd services, clamav-scan.{service,timer} units, and deployment assertion.

## Commits

| Task | Commit | Files |
|------|--------|-------|
| Task 1: tasks/main.yml | a674c88 | roles/antivirus/tasks/main.yml |
| Task 2: tasks/review.yml | d82657c | roles/antivirus/tasks/review.yml |
| Task 3: tasks/enforce.yml | 826e56d | roles/antivirus/tasks/enforce.yml |

## Decisions Made

1. **freshclam exit code handling** — `failed_when: rc not in [0, 1]` because freshclam returns rc=1 when databases are already current (not an error). This is the same pattern used in grype_scanner.
2. **SELinux boolean** — `antivirus_can_scan_system` boolean set persistently + `restorecon -Rv` on log directory and scan dirs. Required on RHEL 9 for clamd to access scan targets.
3. **Container guard scope** — `not _antivirus_in_container` guards: freshclam run, freshclam service start, clamd service start, and scan timer enable. All 4 guards present in enforce.yml.
4. **antivirus_update_db gate** — freshclam command and service assertion are both skippable via `antivirus_update_db: false` — analogous to `aide_init_db: false` for CI containers with no internet egress.

## Verification

- `yamllint roles/antivirus/tasks/` — 0 errors, 0 warnings
- `ansible-lint --profile production roles/antivirus/tasks/` — 0 failures, 0 warnings on 4 files

## Deviations from Plan

None — plan executed exactly as written.

## Known Stubs

- `roles/antivirus/tasks/enforce.yml` references `clamd.conf.j2`, `freshclam.conf.j2`, `clamav-scan.service.j2`, `clamav-scan.timer.j2` templates that do not yet exist — these will be created in plan 04-03 (templates).
- Templates being absent does not prevent this plan's goal (task file creation); they will cause a runtime failure if enforce mode is run before 04-03 completes.

## Self-Check: PASSED

- FOUND: roles/antivirus/tasks/main.yml
- FOUND: roles/antivirus/tasks/review.yml
- FOUND: roles/antivirus/tasks/enforce.yml
- FOUND: commit a674c88
- FOUND: commit d82657c
- FOUND: commit 826e56d
