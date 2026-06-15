---
phase: 06-usbguard
plan: "04"
subsystem: infra
tags: [ansible, molecule, usbguard, docker, container-skip]

requires:
  - phase: 06-02
    provides: tasks/main.yml with _usbguard_usb_available fact and meta:end_host pattern
  - phase: 06-03
    provides: tasks/enforce.yml with container-aware graceful skip logic

provides:
  - Molecule default scenario (ubuntu2204 + rockylinux9) for usbguard role
  - converge.yml invoking role in enforce mode (triggers meta:end_host in containers)
  - verify.yml asserting USB bus absent and package not installed (container skip confirmed)

affects: [06-05]

tech-stack:
  added: []
  patterns:
    - "Molecule container-skip pattern: verify USB bus absent, assert package not installed instead of service running"
    - "Rocky 9 nsswitch fix in prepare.yml applied to all platforms (failed_when:false)"

key-files:
  created:
    - roles/usbguard/molecule/default/molecule.yml
    - roles/usbguard/molecule/default/prepare.yml
    - roles/usbguard/molecule/default/converge.yml
    - roles/usbguard/molecule/default/verify.yml
  modified: []

key-decisions:
  - "verify.yml asserts package NOT installed (not service running) — meta:end_host skips all enforcement including install"
  - "Both fail_msg assertions use multi-line >- syntax for clear diagnostic output"

patterns-established:
  - "usbguard molecule verify: check USB bus absent then check package absent (two-assertion container skip proof)"

requirements-completed: [STD-10, STD-11]

duration: 8min
completed: 2026-04-20
---

# Phase 6 Plan 04: usbguard Molecule Default Scenario Summary

**Molecule default scenario with ubuntu2204 + rockylinux9 asserting USB bus absent and graceful meta:end_host skip in Docker containers**

## Performance

- **Duration:** 8 min
- **Started:** 2026-04-20T12:57:06Z
- **Completed:** 2026-04-20T13:05:00Z
- **Tasks:** 2
- **Files modified:** 4

## Accomplishments

- Created molecule.yml with ubuntu2204 + rockylinux9 platforms, privileged:true, cgroup volumes, pre_build_image:true
- Created prepare.yml applying Rocky 9 nsswitch sss fix (failed_when:false for cross-distro compatibility)
- Created converge.yml invoking malpanez.security.usbguard with enforce mode — role hits meta:end_host in containers due to absent USB bus
- Created verify.yml with container-aware assertions: USB bus absent + usbguard package not installed + graceful skip debug message

## Task Commits

Each task was committed atomically:

1. **Task 1: Create molecule.yml and prepare.yml** - `26dcee4` (feat)
2. **Task 2: Create converge.yml and verify.yml** - `0457bdd` (feat)

**Plan metadata:** (docs commit — see final commit)

## Files Created/Modified

- `roles/usbguard/molecule/default/molecule.yml` - Platform config: ubuntu2204 + rockylinux9, privileged, cgroup volumes
- `roles/usbguard/molecule/default/prepare.yml` - Rocky 9 nsswitch fix for PAM/sudo in containers
- `roles/usbguard/molecule/default/converge.yml` - Role invocation with usbguard_enabled:true, security_mode:enforce
- `roles/usbguard/molecule/default/verify.yml` - Container-aware assertions: USB bus absent, package not installed

## Decisions Made

- verify.yml does NOT assert usbguard service running — meta:end_host fires before any install tasks when USB bus absent, so the package is never installed and the service never starts
- Both assert tasks use `fail_msg:` with descriptive multi-line text per STD-11
- prepare.yml applies nsswitch fix to all platforms (not just Rocky 9) using failed_when:false — consistent with ntp_hardening, user_audit, and antivirus patterns

## Deviations from Plan

None — plan executed exactly as written.

One infrastructure note: after Task 1 commit, the parallel 06-01 agent ran `ansible-galaxy role init` which deleted the molecule directory on disk. Files were recovered via `git checkout HEAD --` since they were already committed. No code changes required.

## Issues Encountered

- molecule.yml and prepare.yml committed in Task 1 were deleted from disk by concurrent ansible-galaxy role init run from 06-01 agent. Recovered with `git checkout HEAD -- roles/usbguard/molecule/default/molecule.yml roles/usbguard/molecule/default/prepare.yml`. All 4 files present in git and on disk after recovery.

## Next Phase Readiness

- molecule/default/ scenario is complete and passes yamllint + ansible-lint --profile production
- 06-05 can proceed to CI integration (add usbguard to ci-uv.yml and ci-cd-enterprise.yml matrices)
- Full molecule converge+verify requires the complete role tasks from 06-02/06-03

---
*Phase: 06-usbguard*
*Completed: 2026-04-20*
