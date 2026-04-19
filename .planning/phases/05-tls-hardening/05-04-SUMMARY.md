---
phase: 05-tls-hardening
plan: "04"
subsystem: tls_hardening
tags: [molecule, integration-test, tls, ubuntu2204, rockylinux9]
dependency_graph:
  requires:
    - 05-02 (tls_hardening tasks/enforce.yml — openssl.cnf + crypto-policies)
    - 05-03 (tls_hardening CI matrix entries)
  provides:
    - molecule/default scenario for tls_hardening
    - STD-10, STD-11, STD-12 coverage
  affects:
    - roles/tls_hardening/molecule/default/
tech_stack:
  added: []
  patterns:
    - geerlingguy docker images (latest tag, collection-consistent)
    - Rocky 9 nsswitch sss fix in prepare.yml
    - set_fact for OS-specific paths in verify.yml (no include_vars relative paths)
    - ansible.builtin.slurp + b64decode for file content assertions
key_files:
  created:
    - roles/tls_hardening/molecule/default/molecule.yml
    - roles/tls_hardening/molecule/default/prepare.yml
    - roles/tls_hardening/molecule/default/converge.yml
    - roles/tls_hardening/molecule/default/verify.yml
  modified: []
decisions:
  - verify.yml uses set_fact for OS-specific openssl.cnf path (no include_vars relative paths — self-contained)
  - verify.yml does not gate RHEL checks behind _tls_in_container per D-16 (filesystem operations work in containers)
  - prepare.yml uses changed_when:true (collection convention) + failed_when:false (no-op on Debian)
metrics:
  duration_minutes: 3
  completed_date: "2026-04-19T10:51:49Z"
  tasks_completed: 1
  files_created: 4
  files_modified: 0
requirements_covered:
  - STD-10
  - STD-11
  - STD-12
---

# Phase 05 Plan 04: tls_hardening Molecule Scenario Summary

**One-liner:** Molecule default scenario with ubuntu2204 + rockylinux9, enforce-mode converge, and OS-conditional TLS assertions (MinProtocol on Debian, DEFAULT:NO-SHA1 on RHEL 9).

## What Was Built

Four Molecule scenario files for `roles/tls_hardening/molecule/default/`:

- **molecule.yml** — Docker driver, ubuntu2204 + rockylinux9 platforms with systemd support (privileged, cgroupns_mode:host). Matches collection-wide pattern from antivirus/ntp_hardening/user_audit.
- **prepare.yml** — Rocky 9 nsswitch sss fix (sed removes ` sss` from /etc/nsswitch.conf; changed_when:true, failed_when:false — no-op on Debian).
- **converge.yml** — Runs tls_hardening role with `tls_hardening_enabled: true` and `security_mode: enforce` via `ansible.builtin.include_role`.
- **verify.yml** — 5 assertions: openssl.cnf exists (all platforms), MinProtocol=TLSv1.2 (Debian/Suse), CipherString (Debian/Suse), ssl_conf=ssl_sect linkage (Debian/Suse), DEFAULT:NO-SHA1 crypto policy (RHEL 8/9).

## Verification Results

- `yamllint roles/tls_hardening/molecule/` — 0 errors
- `ansible-lint --profile production roles/tls_hardening/molecule/` — 0 failures, 0 warnings
- 5 `ansible.builtin.assert` tasks in verify.yml (all with `fail_msg`)
- 0 `include_vars` in verify.yml (uses `set_fact` for OS-specific paths)

## Decisions Made

- **verify.yml self-contained paths:** Used `set_fact` for OS-specific openssl.cnf path instead of `include_vars` with relative paths. Avoids ambiguous path resolution in molecule context and makes verify.yml fully standalone.
- **D-16 honored:** RHEL crypto policy check not gated behind container detection. `update-crypto-policies --show` reads `/etc/crypto-policies/config` file — works in containers. `failed_when: false` handles edge cases gracefully.
- **prepare.yml changed_when:true:** Collection convention for command tasks in prepare.yml (matches antivirus pattern). `failed_when: false` ensures no-op on Debian where `/etc/nsswitch.conf` has no ` sss` entries.

## Commits

| Task | Description | Commit | Files |
|------|-------------|--------|-------|
| 1 | Add molecule default scenario | 51faa1d | molecule.yml, prepare.yml, converge.yml, verify.yml |

## Deviations from Plan

None — plan executed exactly as written.

## Known Stubs

None — verify.yml makes concrete assertions against role outputs. No placeholder data.

## Self-Check: PASSED

- `roles/tls_hardening/molecule/default/molecule.yml` — FOUND
- `roles/tls_hardening/molecule/default/prepare.yml` — FOUND
- `roles/tls_hardening/molecule/default/converge.yml` — FOUND
- `roles/tls_hardening/molecule/default/verify.yml` — FOUND
- Commit 51faa1d — FOUND
