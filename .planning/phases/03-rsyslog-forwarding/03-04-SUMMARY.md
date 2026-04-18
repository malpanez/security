---
phase: 03-rsyslog-forwarding
plan: "04"
subsystem: rsyslog_forwarding
tags: [molecule, testing, rsyslog, integration-test]
dependency_graph:
  requires: ["03-02", "03-03"]
  provides: [rsyslog_forwarding_molecule_scenario]
  affects: [ci_molecule_matrix]
tech_stack:
  added: []
  patterns: [molecule-docker-driver, container-aware-verify, nsswitch-sss-fix]
key_files:
  created:
    - roles/rsyslog_forwarding/molecule/default/molecule.yml
    - roles/rsyslog_forwarding/molecule/default/prepare.yml
    - roles/rsyslog_forwarding/molecule/default/converge.yml
    - roles/rsyslog_forwarding/molecule/default/verify.yml
  modified: []
decisions:
  - "rsyslog_forwarding molecule: verify.yml uses container-aware guards (not _in_container) for rsyslogd -N1 and systemctl checks — containers cannot run full systemd"
  - "prepare.yml: failed_when: false on nsswitch sed — no-op on Debian, fix on Rocky 9; no distro guard needed"
  - "converge.yml: TLS disabled for container testing — no CA cert chain available in Docker containers"
metrics:
  duration_minutes: 3
  completed_date: "2026-04-18"
  tasks_completed: 1
  tasks_total: 1
  files_changed: 4
requirements: [STD-10, STD-11]
---

# Phase 03 Plan 04: rsyslog_forwarding Molecule Scenario Summary

**One-liner:** Molecule default scenario for rsyslog_forwarding with ubuntu2204 + rockylinux9, nsswitch fix, enforce-mode converge (TLS disabled), and 8 container-aware verify assertions.

## What Was Built

Complete molecule default scenario enabling integration testing of the rsyslog_forwarding role on two platform targets.

### Files Created

- `roles/rsyslog_forwarding/molecule/default/molecule.yml` — Docker driver, ubuntu2204 + rockylinux9, privileged + cgroupns_mode: host
- `roles/rsyslog_forwarding/molecule/default/prepare.yml` — Rocky 9 nsswitch sss fix (failed_when: false, no-op on Debian)
- `roles/rsyslog_forwarding/molecule/default/converge.yml` — enforce mode via FQCN include_role, TLS disabled, host 127.0.0.1
- `roles/rsyslog_forwarding/molecule/default/verify.yml` — 8 assertions: rsyslog installed, drop-in exists, mode 0644, RainerScript syntax, target host, rsyslogd -N1, service enabled, service active (last 4 skipped in containers)

## Verification Results

- `yamllint roles/rsyslog_forwarding/molecule/` — 0 errors
- `ansible-lint roles/rsyslog_forwarding/ --profile production` — 0 failures on 20 files
- Acceptance criteria: all passed

## Decisions Made

1. Container-aware guards: `when: not _in_container | bool` applied to rsyslogd -N1, systemctl is-enabled, and systemctl is-active assertions — Docker containers cannot run full systemd so these checks are deferred to VM tests
2. `failed_when: false` on prepare.yml nsswitch fix — simplest approach; sed is a no-op when `sss` not present (Debian), actual fix on Rocky 9
3. TLS disabled in converge: no CA cert chain available in Docker containers; TLS path covered by unit tests in plan 03-03

## Deviations from Plan

None - plan executed exactly as written.

## Commits

| Task | Description | Hash |
|------|-------------|------|
| 1 | Add molecule default scenario for rsyslog_forwarding | 18e131a |

## Self-Check: PASSED
