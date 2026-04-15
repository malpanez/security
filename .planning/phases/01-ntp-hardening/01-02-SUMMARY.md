---
phase: 1
plan: 2
subsystem: ntp_hardening
tags: [ansible, ntp, chrony, review-enforce, container-aware, idempotent]
dependency_graph:
  requires: [01-01]
  provides: [tasks/main.yml, tasks/review.yml, tasks/enforce.yml]
  affects: [molecule scenarios, handlers/main.yml]
tech_stack:
  added: []
  patterns: [review-enforce gate, container-aware via _ntp_in_container, OS-family task branching]
key_files:
  created:
    - roles/ntp_hardening/tasks/review.yml
    - roles/ntp_hardening/tasks/enforce.yml
  modified:
    - roles/ntp_hardening/tasks/main.yml
decisions:
  - security_mode defaults to review (not enforce) — locked project convention
  - Container detection via ansible_facts.virtualization_type in docker/podman/container/lxc
  - Competing daemon stop uses failed_when: false (daemon may not exist on all platforms)
metrics:
  duration: ~10min
  completed_date: "2026-04-15"
---

# Phase 1 Plan 2: NTP Hardening Tasks (main, review, enforce) Summary

**One-liner:** Review/enforce task split for chrony hardening with CVE-2013-5211 audit, container-aware service management, and OS-family branched install.

## What Was Built

Three task files implementing the core logic of the `ntp_hardening` role:

- **tasks/main.yml**: Standard gate pattern — gathers minimum facts, asserts OS support (Debian/RedHat/Suse), loads OS vars, detects container environment (`_ntp_in_container`), includes `review.yml` unconditionally and `enforce.yml` only when `ntp_hardening_enabled` and `security_mode == 'enforce'`.

- **tasks/review.yml**: Read-only NTP audit — checks chrony package installation (rpm/dpkg-query), service status (systemctl), chronyc tracking and sources (skipped in containers), and presence of the CVE-2013-5211 monitor/cmdallow directive. Reports all findings via `ansible.builtin.debug`. Every task has `changed_when: false`; all command probes have `failed_when: false`.

- **tasks/enforce.yml**: Install/configure/service/verify flow — installs chrony via `dnf` (RedHat), `apt` (Debian), or `zypper` (Suse); disables competing daemons (`systemd-timesyncd` on Debian, `ntpd` on RedHat) with `failed_when: false`; creates log directory; deploys `chrony.conf.j2` template with handler notification; enables and starts service (skipped in containers); verifies tracking (skipped in containers).

## Tasks Completed

| Task | Name | Commit | Files |
|------|------|--------|-------|
| 1 | Write tasks/main.yml gate pattern | 82d86ef | roles/ntp_hardening/tasks/main.yml |
| 2 | Write tasks/review.yml read-only audit | 7385e40 | roles/ntp_hardening/tasks/review.yml |
| 3 | Write tasks/enforce.yml install/configure/service/verify | 987be08 | roles/ntp_hardening/tasks/enforce.yml |

## Verification

- yamllint: PASS (0 errors on all three task files)
- All tasks use FQCN (ansible.builtin.*, community.general.*)
- No `changed_when: true` in review.yml
- Container guard (`when: not _ntp_in_container | bool`) on service and tracking tasks

## Deviations from Plan

None - plan executed exactly as written.

## Known Stubs

None.

## Self-Check: PASSED

- roles/ntp_hardening/tasks/main.yml: FOUND
- roles/ntp_hardening/tasks/review.yml: FOUND
- roles/ntp_hardening/tasks/enforce.yml: FOUND
- Commit 82d86ef: FOUND
- Commit 7385e40: FOUND
- Commit 987be08: FOUND
