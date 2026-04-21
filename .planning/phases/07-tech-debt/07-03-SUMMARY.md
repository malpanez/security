---
phase: 07-tech-debt
plan: "03"
subsystem: molecule-prepare / sssd_ad_integration / ci
tags: [tech-debt, ansible-lint, molecule, argument_specs, ci-permissions]
dependency_graph:
  requires: []
  provides: [TECH-03, TECH-04, TECH-05]
  affects: [roles/*/molecule, roles/sssd_ad_integration, .github/workflows/ci-cd-enterprise.yml]
tech_stack:
  added: []
  patterns:
    - ansible.builtin.replace replaces sed -i in prepare.yml files (idempotent, module-based)
    - argument_specs choices field for constrained string vars
key_files:
  created: []
  modified:
    - roles/ntp_hardening/molecule/default/prepare.yml
    - roles/user_audit/molecule/default/prepare.yml
    - roles/rsyslog_forwarding/molecule/default/prepare.yml
    - roles/tls_hardening/molecule/default/prepare.yml
    - roles/antivirus/molecule/default/prepare.yml
    - roles/usbguard/molecule/default/prepare.yml
    - roles/sssd_ad_integration/molecule/default/prepare.yml
    - roles/aide/molecule/default/prepare.yml
    - molecule/complete_stack/prepare.yml
    - molecule/complete_stack_ci/prepare.yml
    - roles/sssd_ad_integration/meta/argument_specs.yml
    - .github/workflows/ci-cd-enterprise.yml
decisions:
  - "ansible.builtin.replace with regexp:' sss' and replace:'' is semantically equivalent to sed -i 's/ sss//g' and idempotent"
  - "complete_stack prepare.yml: replace task moved to second play (become:true) since first play has become:false"
  - "ci-cd-enterprise.yml: contents:write->read is safe — workflow_dispatch only, no push/tag/release operations"
metrics:
  duration_minutes: 15
  completed_date: "2026-04-21"
  tasks_completed: 2
  files_modified: 12
---

# Phase 7 Plan 03: Tech Debt Bundled Fixes (TECH-03, TECH-04, TECH-05) Summary

**One-liner:** Replaced 10 command/shell/raw sed anti-patterns with ansible.builtin.replace, added 4 IPA vars to sssd_ad_integration argument_specs, and tightened CI permissions to least-privilege.

## What Was Built

### TECH-03: Replace sed with ansible.builtin.replace in prepare.yml files

All molecule prepare.yml files that used `ansible.builtin.command`, `ansible.builtin.shell`, or `raw:` to run `sed -i 's/ sss//g' /etc/nsswitch.conf` now use:

```yaml
- name: Fix Rocky 9 nsswitch for sudo/PAM in containers
  ansible.builtin.replace:
    path: /etc/nsswitch.conf
    regexp: ' sss'
    replace: ''
  failed_when: false
```

This eliminates ansible-lint `command-instead-of-module` violations. The `ansible.builtin.replace` module is semantically equivalent to the sed one-liner and correctly reports `changed` only when it modifies the file.

For the complete_stack prepare.yml files (which had `become: false` on the first play), the replace task was placed in the second play which already has `become: true` — required because `/etc/nsswitch.conf` is root-owned.

### TECH-04: argument_specs gaps in sssd_ad_integration

Added 4 missing variables to `roles/sssd_ad_integration/meta/argument_specs.yml` after the `sssd_ad_configure` entry:

- `ssh_identity_backend`: type str, default "ad", choices [ad, ipa, local]
- `sssd_ipa_domain`: type str, default "", required when backend=ipa
- `sssd_ipa_server`: type str, default "_srv_" for DNS SRV lookup
- `sssd_ipa_access_provider`: type str, default "permit", choices [permit, ipa]

### TECH-05: Tighten CI permissions

Changed `contents: write` to `contents: read` in `.github/workflows/ci-cd-enterprise.yml` top-level permissions block. The workflow is `workflow_dispatch` only and performs no git push, tag, or release operations.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 2 - Missing coverage] Fixed roles/aide/molecule/default/prepare.yml**
- **Found during:** Task 1 verification (full glob check across roles/*/molecule)
- **Issue:** `roles/aide/molecule/default/prepare.yml` had the same `ansible.builtin.command` sed anti-pattern but was not listed in the plan's file list
- **Fix:** Applied same `ansible.builtin.replace` replacement
- **Files modified:** `roles/aide/molecule/default/prepare.yml`
- **Commit:** 07a3408

## Commits

| Hash | Message |
|------|---------|
| 377daa1 | fix(07-03): replace command/shell sed with ansible.builtin.replace in prepare.yml |
| 07a3408 | feat(07-03): fill argument_specs gaps, tighten CI permissions, fix aide prepare |

## Known Stubs

None — all changes are complete, no placeholder data or wired-but-empty paths.

## Self-Check: PASSED
