---
phase: 03-rsyslog-forwarding
plan: "03"
subsystem: infra
tags: [rsyslog, jinja2, rainerscript, tls, logrotate, ansible-template]

requires:
  - phase: 03-01
    provides: role scaffold, defaults/main.yml, enforce.yml task structure
provides:
  - 99-forwarding.conf.j2 — RainerScript omfwd action with conditional TLS global() and disk queue
  - rsyslog-logrotate.j2 — logrotate stanza with compress/delaycompress/HUP postrotate
affects:
  - 03-04-molecule
  - 03-05-ci-integration

tech-stack:
  added: []
  patterns:
    - "RainerScript action(type=\"omfwd\") with layered Jinja2 conditionals for TLS and disk queue"
    - "Logrotate HUP postrotate guarded with 2>/dev/null || true for container safety"

key-files:
  created:
    - roles/rsyslog_forwarding/templates/99-forwarding.conf.j2
    - roles/rsyslog_forwarding/templates/rsyslog-logrotate.j2
  modified: []

key-decisions:
  - "action(type=\"omfwd\" ...) placed on single line so grep/contains checks match the RainerScript action opening"
  - "module(load=\"imtls\") included inside TLS block only — required to activate the GnuTLS input module when TLS is enabled"
  - "mTLS client cert/key conditional on both variables being non-empty (D-11)"
  - "queue.spoolDirectory + queue.filename only emitted when queue_type == Disk (D-05, Pitfall 6)"
  - "$FileCreateMode directive placed at file scope above the action() block"

patterns-established:
  - "Jinja2 conditional: {% if var | bool %} for boolean flags, {% if var == 'Value' %} for string comparisons"
  - "postrotate: /usr/bin/systemctl kill -s HUP rsyslog.service 2>/dev/null || true — container-safe HUP signal"

requirements-completed: [LOG-02, LOG-03, LOG-04]

duration: 1min
completed: 2026-04-18
---

# Phase 3 Plan 03: rsyslog_forwarding Jinja2 Templates Summary

**RainerScript 99-forwarding.conf.j2 with conditional TLS global() block, mTLS opt-in, disk queue opt-in, and logrotate stanza with compress/HUP postrotate**

## Performance

- **Duration:** 1 min
- **Started:** 2026-04-18T10:48:53Z
- **Completed:** 2026-04-18T10:49:01Z
- **Tasks:** 1
- **Files modified:** 2

## Accomplishments

- 99-forwarding.conf.j2 uses RainerScript `action(type="omfwd")` exclusively — no legacy `@@` syntax
- TLS `global()` block with `module(load="imtls")` conditional on `rsyslog_forwarding_tls_enabled`
- mTLS client cert/key directives conditional on both client cert and key variables being non-empty
- Disk queue `queue.spoolDirectory` + `queue.filename` conditional on `queue_type == 'Disk'`
- rsyslog-logrotate.j2 with size-based rotation, compress/delaycompress, and container-safe HUP postrotate

## Task Commits

1. **Task 1: Create 99-forwarding.conf.j2 and rsyslog-logrotate.j2 templates** - `658e97b` (feat)

**Plan metadata:** pending docs commit

## Files Created/Modified

- `roles/rsyslog_forwarding/templates/99-forwarding.conf.j2` — RainerScript forwarding drop-in template with conditional TLS and disk queue
- `roles/rsyslog_forwarding/templates/rsyslog-logrotate.j2` — logrotate stanza for local log rotation with HUP signal

## Decisions Made

- Placed `action(type="omfwd"` on the selector line (same line) so the artifact `contains` check passes as specified in plan must_haves
- Included `module(load="imtls")` inside the TLS conditional block — required to load the GnuTLS stream driver input module
- Used `$FileCreateMode` legacy directive at file scope — acceptable per plan (Claude's discretion), sets default file permissions

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered

Minor: initial template had `action(` on the selector line with `type="omfwd"` indented on the next line. Restructured to `action(type="omfwd"` on a single line to satisfy the plan's acceptance criteria grep check. No functional impact.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- Both templates are ready for molecule testing (plan 03-04)
- enforce.yml already references both templates by correct filename — no changes needed there
- TLS disabled in molecule converge (no cert chain in containers) — validate still fires on the non-TLS path

---
*Phase: 03-rsyslog-forwarding*
*Completed: 2026-04-18*

## Self-Check: PASSED

- FOUND: roles/rsyslog_forwarding/templates/99-forwarding.conf.j2
- FOUND: roles/rsyslog_forwarding/templates/rsyslog-logrotate.j2
- FOUND: commit 658e97b (feat: templates)
- FOUND: commit 080a49a (docs: plan metadata)
