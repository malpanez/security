---
phase: "05"
plan: "03"
subsystem: tls_hardening
tags: [tls, crypto-policies, openssl, rhel, debian, suse, fips, idempotent]
dependency_graph:
  requires: ["05-01", "05-02"]
  provides: ["roles/tls_hardening/tasks/enforce.yml"]
  affects: ["roles/tls_hardening"]
tech_stack:
  added: []
  patterns:
    - slurp+blockinfile+lineinfile for openssl.cnf idempotent section management
    - FIPS guard via /proc/sys/crypto/fips_enabled slurp
    - update-crypto-policies --show pre-check for RHEL 8/9 idempotence
    - ssl_conf = ssl_sect as canonical idempotence anchor (handles minimal Debian)
key_files:
  created:
    - roles/tls_hardening/tasks/enforce.yml
  modified: []
decisions:
  - FIPS guard reads /proc/sys/crypto/fips_enabled via slurp (failed_when: false) and skips all enforcement when active
  - ssl_conf = ssl_sect used as idempotence anchor (not [system_default_sect]) — single check sufficient because absent linkage means chain is unreachable even if section exists
  - Full TLS chain written as one blockinfile block including [openssl_init] header — handles minimal Debian where [openssl_init] may not exist
  - No notify directives anywhere per D-21 — TLS policy changes apply to new connections
  - crypto-policies-scripts package installed via ansible.builtin.package (not dnf) for cross-OS compatibility of the module call
metrics:
  duration_minutes: 2
  completed_date: "2026-04-19"
  tasks_completed: 1
  files_changed: 1
---

# Phase 05 Plan 03: tls_hardening enforce.yml Summary

One-liner: Two-branch TLS enforce (RHEL 8/9 crypto-policies + Debian/SUSE/RHEL<8 openssl.cnf) with FIPS guard and full section chain linkage.

## What Was Built

`roles/tls_hardening/tasks/enforce.yml` — 17-task file implementing:

1. **FIPS guard (all platforms):** Slurps `/proc/sys/crypto/fips_enabled`, sets `_tls_fips_active` fact, emits debug message and skips all enforcement when FIPS is active.

2. **RHEL 8/9 crypto-policies branch:** Installs `crypto-policies-scripts`, reads current policy via `--show`, calls `--set` only when policy differs (`_tls_current_policy.stdout != tls_hardening_rhel_policy`). Enforces TLS-04 via `DEFAULT:NO-SHA1` which requires TLS 1.2+.

3. **Debian/SUSE/RHEL<8 openssl.cnf branch:** Sets `_tls_use_openssl_cnf` fact, slurps openssl.cnf, checks for `ssl_conf = ssl_sect` as canonical idempotence anchor (`_tls_chain_absent`). When chain absent: writes full block (`[openssl_init]` + `ssl_conf = ssl_sect` + `[ssl_sect]` + `[system_default_sect]` + MinProtocol + CipherString + Options) via blockinfile. When chain present: updates only MinProtocol and CipherString via lineinfile. Enforces TLS-04 via `MinProtocol = TLSv1.2`.

4. **Post-apply verification (STD-04):** RHEL branch reads back `--show` and asserts policy matches target. openssl.cnf branch slurps file and asserts MinProtocol line present. Debug task reports enforcement method and outcome.

## Acceptance Criteria Results

| Check | Result |
|-------|--------|
| `grep 'update-crypto-policies --set'` | 1 match |
| `grep -c 'update-crypto-policies --show'` | 2 (pre-check + verify) |
| `grep 'ansible.builtin.blockinfile'` | 1 match |
| `grep -c 'ansible.builtin.lineinfile'` | 2 (MinProtocol + CipherString) |
| `grep -c 'ansible.builtin.slurp'` | 3 (FIPS + cnf configure + cnf verify) |
| `grep -c 'ansible.builtin.assert'` | 2 (RHEL policy + openssl.cnf MinProtocol) |
| `grep 'fips_enabled'` | 1 match |
| `grep 'major_version \| int >= 8'` | 7 matches (all RHEL 8/9 guards) |
| `grep 'major_version \| int < 8'` | 1 match (RHEL legacy guard) |
| `grep -c 'notify'` | 0 (no service restarts) |
| `grep 'ssl_conf = ssl_sect'` | 2 matches (anchor check + block content) |
| `grep 'system_default = system_default_sect'` | 1 match |
| `grep '\[openssl_init\]'` | 1 match (in blockinfile block) |
| `grep '_tls_chain_absent'` | 3 matches |
| yamllint | 0 errors |
| ansible-lint --profile production | 0 failures |

## Commits

| Task | Commit | Files |
|------|--------|-------|
| Task 1: Create enforce.yml | 8caf08b | roles/tls_hardening/tasks/enforce.yml |

## Deviations from Plan

None - plan executed exactly as written.

## Known Stubs

None — enforce.yml is fully implemented and wired to variables defined in plan 05-01 (defaults/main.yml, vars/OS.yml).

## Self-Check: PASSED

- `roles/tls_hardening/tasks/enforce.yml` — FOUND
- Commit `8caf08b` — FOUND
