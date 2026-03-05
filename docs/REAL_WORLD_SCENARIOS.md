# Real-World Scenarios (Actual state)

## Scenario 1: Monolithic sudoers

Most environments keep everything in `/etc/sudoers`. The current `sudoers_baseline` role **only applies changes if** `sudoers_baseline_strict=true` and always writes:

- `/etc/sudoers`
- `/etc/sudoers.d/99-security`

**Implication**: there is no hybrid mode or automatic preservation of the main file. If you need a gradual migration, manage `/etc/sudoers` externally and enable the role only when you are ready to replace it.

## Scenario 2: Multiple SSH instances

`sshd_hardening` generates a single `/etc/ssh/sshd_config` by default (or a drop-in in `sshd_config.d` if enabled) and does not manage multiple instances or additional systemd units. If your environment requires separate instances (SFTP, DMZ, etc.), you must:

- create your own systemd units,
- maintain `sshd_config` per instance outside the role,
- use the role only if you accept it managing the main `sshd_config`.
