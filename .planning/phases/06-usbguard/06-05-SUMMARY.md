---
phase: 06-usbguard
plan: "05"
subsystem: ci-integration
tags:
  - ci
  - galaxy
  - changelog
  - release
  - usbguard
dependency_graph:
  requires:
    - "06-02"
    - "06-03"
    - "06-04"
  provides:
    - "usbguard in CI matrices"
    - "collection v1.2.0 build"
  affects:
    - ".github/workflows/ci-uv.yml"
    - ".github/workflows/ci-cd-enterprise.yml"
    - "galaxy.yml"
    - "CHANGELOG.md"
tech_stack:
  added: []
  patterns:
    - "usbguard added to CI matrix after tls_hardening (ROADMAP phase order)"
    - "ansible-galaxy collection build --force for tarball verification"
key_files:
  created: []
  modified:
    - ".github/workflows/ci-uv.yml"
    - ".github/workflows/ci-cd-enterprise.yml"
    - "galaxy.yml"
    - "CHANGELOG.md"
decisions:
  - "Tarball malpanez-security-1.2.0.tar.gz produced but not committed (galaxy.yml build_ignore: '*.tar.gz')"
  - "ansiblelint invoked via python3 module + /tmp/ansiblelint-bin/ansible wrapper to resolve venv shebang breakage (old path /repos/malpanez vs /repos/wcl/malpanez)"
metrics:
  duration_seconds: 395
  completed_date: "2026-04-20"
  tasks_completed: 2
  files_modified: 4
---

# Phase 06 Plan 05: CI Integration and v1.2.0 Milestone Close Summary

**One-liner:** usbguard added to CI matrices, galaxy.yml bumped to 1.2.0, CHANGELOG promoted with all 6 new roles and compliance tags, collection tarball builds successfully.

## Tasks Completed

| Task | Name | Commit | Files |
|------|------|--------|-------|
| 1 | Add usbguard to CI matrices and run full lint | c6a732b | ci-uv.yml, ci-cd-enterprise.yml |
| 2 | Bump galaxy.yml to 1.2.0, update CHANGELOG.md, build collection | 1d7766c | galaxy.yml, CHANGELOG.md |

## Verification Results

- `grep 'usbguard' .github/workflows/ci-uv.yml` — PASS (line 139, after tls_hardening)
- `grep 'usbguard' .github/workflows/ci-cd-enterprise.yml` — PASS (line 342, after tls_hardening)
- `yamllint roles/usbguard/` — EXIT 0, 0 errors
- `ansible-lint --profile production roles/usbguard/` — PASS, 0 failures, 0 warnings, 19 files processed
- `grep 'version: 1.2.0' galaxy.yml` — PASS
- `grep '[1.2.0] - 2026-04-20' CHANGELOG.md` — PASS
- All 6 new roles listed in CHANGELOG.md [1.2.0] Added section — PASS
- `ansible-galaxy collection build --force` — EXIT 0, produces malpanez-security-1.2.0.tar.gz (7.3MB)

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] Broken venv shebangs preventing ansible-lint execution**
- **Found during:** Task 1
- **Issue:** All venv scripts (ansible-lint, ansible-galaxy, ansible) have shebang `#!/home/malpanez/repos/malpanez/security/.venv/bin/python` (old path pre-worktree migration). Shell cannot execute them. System `/usr/bin/ansible` at 2.16.3 conflicts with venv ansible-core 2.17.14, causing ansiblelint version-mismatch abort.
- **Fix:** Invoked ansiblelint via `python3 -m ansiblelint`; created `/tmp/ansiblelint-bin/ansible` shell wrapper pointing to venv python3 so ansiblelint version detection resolves 2.17.14. Used `python3 -m ansible galaxy` for collection install.
- **Files modified:** None (runtime workaround only)
- **Commit:** N/A (workaround, not committed)

## Known Stubs

None.

## Self-Check: PASSED

- `.github/workflows/ci-uv.yml` — FOUND, contains `usbguard` at line 139
- `.github/workflows/ci-cd-enterprise.yml` — FOUND, contains `usbguard` at line 342
- `galaxy.yml` — FOUND, `version: 1.2.0`
- `CHANGELOG.md` — FOUND, `[1.2.0] - 2026-04-20` with all 6 roles
- `malpanez-security-1.2.0.tar.gz` — FOUND (7.3MB, not committed per build_ignore)
- Commit c6a732b — FOUND
- Commit 1d7766c — FOUND
