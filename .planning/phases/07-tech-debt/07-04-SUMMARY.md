---
phase: 07-tech-debt
plan: "04"
subsystem: tooling
tags: [pre-commit, venv, uv, python, ci-quality]
dependency_graph:
  requires: []
  provides: [working-pre-commit-hooks]
  affects: [git-commit-workflow, ci-quality-gates]
tech_stack:
  added: []
  patterns: [uv-sync-venv-rebuild]
key_files:
  created: []
  modified:
    - .venv/bin/pre-commit
key_decisions:
  - "uv sync --extra dev used to rebuild .venv — reads pyproject.toml + uv.lock, produces correct shebang for current repo path"
  - "No code committed — .venv/ is gitignored; only planning artifact committed"
metrics:
  duration_minutes: 5
  completed_date: "2026-04-21"
  tasks_completed: 2
  files_changed: 0
requirements:
  - TECH-06
---

# Phase 7 Plan 04: venv rebuild Summary

**One-liner:** Rebuilt .venv with `uv sync --extra dev` to fix broken pre-commit shebangs after repo path migration from `/repos/malpanez` to `/repos/wcl/malpanez`.

## What Was Done

### Problem

The `.venv` was originally created when the repository lived at:

```
/home/malpanez/repos/malpanez/security/
```

The repo was later moved to:

```
/home/malpanez/repos/wcl/malpanez/security/
```

All shebang lines in `.venv/bin/` still referenced the old path. The pre-commit binary at `.venv/bin/pre-commit` had:

```
#!/home/malpanez/repos/malpanez/security/.venv/bin/python3
```

That path no longer exists. Every `git commit` invocation failed with:

```
cannot execute: required file not found
```

A temporary workaround (a `/tmp/bin/pre-commit` wrapper script) was in place since Phase 05.1 to unblock commits.

### Fix

Rebuilt the virtual environment in place using uv:

```bash
rm -rf .venv
uv sync --extra dev
```

`uv sync` reads `pyproject.toml` and `uv.lock`, installs all dependencies including the `dev` extras group (ansible-lint, yamllint, molecule, molecule-plugins, pytest, pytest-testinfra, pre-commit), and creates a fresh `.venv` with shebangs referencing the current interpreter path.

### Result

New shebang in `.venv/bin/pre-commit`:

```
#!/home/malpanez/repos/wcl/malpanez/security/.venv/bin/python
```

The path exists and is executable.

## Verification

Human verification performed (checkpoint approved):

- `.venv/bin/pre-commit` shebang confirmed: `#!/home/malpanez/repos/wcl/malpanez/security/.venv/bin/python`
- Hooks fire without "cannot execute: required file not found"
- Normal `git commit` invokes pre-commit hooks without `--no-verify` or wrapper scripts

## Deviations from Plan

None — plan executed exactly as written.

The temporary `/tmp/bin/pre-commit` wrapper installed in Phase 05.1 is superseded by this fix. No cleanup task was needed as /tmp is ephemeral.

## Known Stubs

None.

## Self-Check: PASSED

- SUMMARY.md created at `.planning/phases/07-tech-debt/07-04-SUMMARY.md`
- No code commits for this plan (`.venv/` is gitignored)
- Verification confirmed by human checkpoint approval
