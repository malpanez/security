---
phase: 1
plan: 3
subsystem: ntp_hardening
tags: [ntp, chrony, template, jinja2, cve-2013-5211]
dependency_graph:
  requires: [01-01]
  provides: [chrony.conf.j2 template for enforce.yml]
  affects: [roles/ntp_hardening/tasks/enforce.yml]
tech_stack:
  added: []
  patterns: [Jinja2 conditional blocks, loop over list variable]
key_files:
  created:
    - roles/ntp_hardening/templates/chrony.conf.j2
  modified: []
decisions:
  - "monitor directive absent entirely (not even in comments) per CVE-2013-5211 OMISSION pattern"
  - "leapsectz wrapped in conditional to support empty string disabling it"
  - "iburst already embedded in ntp_hardening_servers values — not appended in template"
metrics:
  duration: "5 minutes"
  completed_date: "2026-04-15"
  tasks: 1
  files: 1
---

# Phase 1 Plan 3: Template — chrony.conf.j2 Summary

Jinja2 template for hardened chrony.conf rendering all ntp_hardening_* variables with CVE-2013-5211 mitigation via intentional omission of monitor/cmdallow directives.

## Tasks Completed

| Task | Name | Commit | Files |
|------|------|--------|-------|
| 1 | Write templates/chrony.conf.j2 | 5b17b1c | roles/ntp_hardening/templates/chrony.conf.j2 |

## Decisions Made

1. **monitor/nomonitor words absent from template entirely** — success criteria required no occurrence of `monitor` even in comments; the comment references CVE-2013-5211 without using the word `monitor`.
2. **leapsectz conditional** — wrapped in `{% if ntp_hardening_leapsectz %}` to allow disabling by setting to empty string.
3. **iburst not appended in template** — `ntp_hardening_servers` defaults already include `iburst` suffix in each value; template renders `server {{ server }}` verbatim.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 2 - Missing constraint] Removed `monitor` word from comment block**
- **Found during:** Task 1 review
- **Issue:** Plan action block included `# CVE-2013-5211: monitor directive intentionally absent.` as a comment. The success criteria explicitly states "Template does NOT contain the word 'monitor' (not even as a comment)."
- **Fix:** Rewrote comment as `# CVE-2013-5211: amplification attack mitigation.` — preserves auditability without using the forbidden word.
- **Files modified:** roles/ntp_hardening/templates/chrony.conf.j2
- **Commit:** 5b17b1c

## Known Stubs

None — template wires all variables from defaults/main.yml with no placeholders or hardcoded values.

## Self-Check: PASSED

- `roles/ntp_hardening/templates/chrony.conf.j2` exists: FOUND
- Commit `5b17b1c` exists: FOUND
- `monitor`/`nomonitor` absent: CONFIRMED (0 matches)
- All 10 ntp_hardening_* variables present: CONFIRMED
