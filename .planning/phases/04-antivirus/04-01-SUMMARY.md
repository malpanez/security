---
phase: 04-antivirus
plan: "01"
subsystem: antivirus
tags: [antivirus, clamav, scaffold, defaults, vars, meta, handlers]
dependency_graph:
  requires: []
  provides: [antivirus-role-scaffold]
  affects: []
tech_stack:
  added: [ClamAV role skeleton]
  patterns: [review/enforce gate, OS-family vars, container-aware handlers]
key_files:
  created:
    - roles/antivirus/defaults/main.yml
    - roles/antivirus/vars/RedHat.yml
    - roles/antivirus/vars/Debian.yml
    - roles/antivirus/vars/Suse.yml
    - roles/antivirus/meta/main.yml
    - roles/antivirus/meta/argument_specs.yml
    - roles/antivirus/handlers/main.yml
    - roles/antivirus/tests/test.yml
  modified: []
decisions:
  - "antivirus_update_db:true default but set false in Molecule CI to skip 200MB freshclam download"
  - "handlers use _antivirus_in_container bool guard matching ntp_hardening/_rsyslog pattern"
  - "Reload systemd handler has no container guard (daemon_reload is always safe)"
  - "vars/main.yml removed — OS-family vars (RedHat/Debian/Suse) used exclusively"
metrics:
  duration: 19
  completed_date: "2026-04-18"
  tasks_completed: 1
  files_changed: 8
---

# Phase 04 Plan 01: Antivirus Role Scaffold Summary

ClamAV antivirus role scaffolded with 10 defaults, 3 OS-family vars files (RHEL/Debian/SUSE), Galaxy-valid meta, argument_specs covering all defaults, 3 handlers with container guard, and FQCN test playbook.

## Tasks Completed

| Task | Name | Commit | Files |
|------|------|--------|-------|
| 1 | Scaffold role and populate defaults, vars, meta, handlers, tests | 4682bfc | 8 files created |

## Decisions Made

1. **antivirus_update_db:true default** — CI molecule tests should set this false to skip 200MB freshclam download (analogous to aide_init_db:false pattern).
2. **_antivirus_in_container guard** — handlers Restart clamd and Restart freshclam have `when: not _antivirus_in_container | bool` matching the ntp_hardening and rsyslog_forwarding patterns.
3. **Reload systemd no container guard** — `daemon_reload: true` is always safe in containers, no guard needed.
4. **vars/main.yml removed** — ansible-galaxy init creates it as boilerplate; OS-family loading via `vars/{{ ansible_os_family }}.yml` is the collection pattern.

## Deviations from Plan

None - plan executed exactly as written.

## Known Stubs

None. This plan creates variable contracts and skeleton only. Tasks, templates, and molecule scenarios are intentionally deferred to subsequent plans (04-02 through 04-05).

## Self-Check: PASSED

Files exist:
- roles/antivirus/defaults/main.yml: FOUND
- roles/antivirus/vars/RedHat.yml: FOUND
- roles/antivirus/vars/Debian.yml: FOUND
- roles/antivirus/vars/Suse.yml: FOUND
- roles/antivirus/meta/main.yml: FOUND
- roles/antivirus/meta/argument_specs.yml: FOUND
- roles/antivirus/handlers/main.yml: FOUND
- roles/antivirus/tests/test.yml: FOUND

Commit 4682bfc: FOUND
