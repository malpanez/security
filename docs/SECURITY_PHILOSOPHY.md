# Security Philosophy and Architecture Notes

Notes from architecture discussions on what this collection is trying to solve
and why the decisions were made the way they were.

---

## The core problem: security theater vs. defense in depth

Most organizations protect the perimeter (firewalls, WAFs, DLP, SIEM) but leave
the OS layer misconfigured. This creates a false sense of security:

- A perfectly configured Fortinet or Palo Alto does nothing once an attacker is
  already inside via lateral movement, a stolen SSH key, or a supply chain
  compromise.
- HaveIBeenPwned is full of leaks from trivial misconfigurations: public S3
  buckets, default credentials, unrotated service account keys.

The OS hardening layer is the last line of defense and the most neglected one.

---

## SSH key hygiene — the silent epidemic

SSH keys are the most abused credential type in enterprise environments:

- Keys are created, never rotated, never revoked.
- `AllowUsers *` with no `from=` restriction means any key works from anywhere.
- A stolen key from a decommissioned server from 3 years ago still opens doors.

**What this collection enforces:**

- `sshd_hardening` deploys `/etc/ssh/sshd_config.d/99-hardening.conf` (drop-in,
  never overwrites the base config).
- `AllowUsers` / `AllowGroups` gating — only explicitly authorized users/groups.
- `MaxAuthTries 3`, `LoginGraceTime 30` — rate-limiting brute force.
- Explicit `PubkeyAuthentication yes` with `PasswordAuthentication no` for
  privileged accounts.
- Optionally enforces `from=` on `authorized_keys` entries via
  `sshd_hardening_restrict_key_sources`.
- `pam_mfa` enforces FIDO2/YubiKey + TOTP for SSH, so a stolen key alone is not
  enough.

**What this collection does NOT do (intentionally):**

- Does not rotate SSH keys automatically. Key rotation is an operational process
  that needs human review. Automating it blindly can lock people out.
- Does not manage `authorized_keys` files — that belongs in a separate identity
  management layer (LDAP, Vault, etc.).

---

## The kernel layer: what containers cannot test

Docker containers share the host kernel. This means:

| What containers test | What they cannot test |
|---|---|
| File permissions, ownership | `sysctl` values actually applied |
| PAM configuration files | Module blacklists taking effect |
| SSH config syntax | `/proc hidepid` on real mount namespace |
| AppArmor profile loading | `kernel.yama.ptrace_scope` enforced |

This is why we have two test layers:

1. **`docker-test.yml`** — geerlingguy images for config file correctness across
   distros (Debian 11/12/13, Ubuntu 20/22, Rocky 8/9).
2. **`kernel-vm-test.yml`** — GitHub-hosted Ubuntu VMs where sysctl parameters
   are applied to the real kernel and verified by reading `/proc/sys/` values.

---

## Why sysctl hardening matters

### Network layer

```
net.ipv4.conf.all.accept_source_route = 0    # No IP source routing (spoofing vector)
net.ipv4.conf.all.accept_redirects = 0       # No ICMP redirect acceptance (MITM)
net.ipv4.conf.all.send_redirects = 0         # No redirects sent (router impersonation)
net.ipv4.conf.all.log_martians = 1           # Log spoofed/impossible source addresses
net.ipv4.tcp_syncookies = 1                  # SYN flood protection
net.ipv4.conf.all.rp_filter = 1             # Reverse path filtering (anti-spoofing)
```

These params don't help if someone is already inside. But they stop a class of
network-level attacks that often precede lateral movement.

### Kernel information leakage

```
kernel.dmesg_restrict = 1      # Non-root cannot read dmesg (kernel addresses, paths)
kernel.kptr_restrict = 2       # Kernel pointers hidden from /proc (KASLR bypass)
kernel.perf_event_paranoid = 3 # No perf events without CAP_SYS_ADMIN (side-channel)
```

These protect against local privilege escalation. An attacker with a shell but no
root cannot use dmesg or /proc/kallsyms to find kernel addresses for exploits.

### Process isolation

```
kernel.yama.ptrace_scope = 1   # Only parent can ptrace a child (no credential theft)
kernel.kexec_load_disabled = 1 # No kexec (prevents unsigned kernel loading)
vm.mmap_min_addr = 65536       # No NULL pointer dereference exploits
```

`ptrace_scope = 1` is critical: without it, any process can attach to and read
the memory of any other process owned by the same user. This is how tools like
`mimikatz`-equivalent for Linux work.

---

## PAM as a chokepoint

PAM is where authentication policy is enforced for everything: SSH, sudo, console,
cron. Most organizations have never audited their `/etc/pam.d/` files.

Common failures:
- `pam_sss.so` in the stack but SSSD not running → authentication hangs or fails
  (we hit this in CI with Rocky Linux containers).
- No `pam_faillock` → no lockout after N failed attempts (trivial brute force).
- `pam_pwquality` not enforced → users set passwords like `Password1!`.
- No `pam_tty_audit` → no audit trail of what was typed in privileged sessions.

**What this collection enforces:**
- `faillock` with configurable deny/unlock_time.
- `pwquality` with CIS-aligned minimums (minlen=14, complexity requirements).
- `login.defs` for password aging policy.
- `limits.conf` to prevent fork bombs and resource exhaustion.

---

## Sudoers: the most dangerous config file on the system

Every `NOPASSWD: ALL` entry is a privilege escalation waiting to happen.
Every wildcard in sudoers rules can be abused.

```
# This is a backdoor
jenkins ALL=(ALL) NOPASSWD: /bin/bash

# This is also a backdoor (bash can be called as /usr/bin/bash or via symlink)
jenkins ALL=(ALL) NOPASSWD: /bin/bash, /usr/bin/bash
```

**What this collection enforces:**
- Drop-in approach: `/etc/sudoers.d/` only. Never rewrites `/etc/sudoers`.
- `Defaults requiretty` — prevents sudo from non-terminal contexts (cron exploits).
- `Defaults logfile` — all sudo commands logged to a separate file.
- `Defaults !visiblepw` — never echoes password.
- `sudoers_baseline_strict: true` removes NOPASSWD from non-exempted groups.

---

## Defense layers and where each fits

```
Layer 7 — Application        → DAST, SAST, dependency scanning
Layer 6 — Container/Cloud    → Trivy, CSPM, misconfiguration scanning
Layer 5 — Network            → Firewall, IDS/IPS, WAF, Zero Trust
Layer 4 — Identity           → MFA, PAM, SSH key management, LDAP/AD hygiene
Layer 3 — OS hardening       → THIS COLLECTION
Layer 2 — Kernel             → sysctl, module blacklists, AppArmor/SELinux
Layer 1 — Physical/Firmware  → Secure Boot, TPM, UEFI password
```

Most organizations invest heavily in layers 5–7 and ignore layers 1–4.
An attacker who bypasses layer 5 (firewall, VPN) via a phishing or supply chain
attack lands directly at layer 4. If SSH keys aren't rotated, sudoers isn't
audited, and PAM isn't hardened, they have the run of the place.

---

## Commercial Unix (Solaris, AIX, HP-UX)

Still in production at many banks, telcos, and utilities. The hardening
principles are identical but the tooling is different:

| Concept | Linux | Solaris | AIX |
|---|---|---|---|
| Mandatory access | SELinux / AppArmor | Trusted Extensions | RBAC |
| Audit | auditd | BSM audit | AIX audit |
| Password quality | pam_pwquality | LDAP / NIS+ | `/etc/security/user` |
| Process accounting | psacct | prstat / dtrace | trcstop |
| Network params | sysctl | ndd / ipadm | no |

These platforms are harder to test in CI (no free images) but the same
audit-first, enforce-later pattern applies. An `audit-only.yml` equivalent
could be built for each using SSH + shell facts.

---

## Infrastructure as Code: the Netscaler / ADC problem

A firewall or ADC (Citrix Netscaler, F5 BIG-IP, Fortinet) configured manually
by a vendor or consultant is a time bomb:

- No change history.
- No way to reproduce the configuration after a failure.
- Configuration drift over time as people make "temporary" changes.
- Security policies that looked good in the design document but were loosened
  "for convenience" during implementation.

The same principles that apply here (version-controlled, tested, peer-reviewed
changes via PR) should apply to network infrastructure:
- Citrix ADC: Ansible `citrix.adc` collection or Terraform provider.
- F5: `f5networks.f5_modules` or AS3 declarations in git.
- Fortinet: `fortinet.fortios` Ansible collection.
- Palo Alto: `paloaltonetworks.panos` Ansible collection.

A WAF rule that exists only in a GUI and was added 3 years ago by a consultant
who no longer works there is not a security control. It is a mystery.

---

## What this collection is NOT

- Not a replacement for a SIEM or threat detection.
- Not a vulnerability scanner (use Trivy, Grype, OpenSCAP for that).
- Not a configuration audit tool (use OpenSCAP/XCCDF for formal CIS benchmarks).
- Not a key management solution (use Vault, AWS Secrets Manager, etc.).

It is the **baseline** — the floor below which no managed host should fall.
Everything else (SIEM, EDR, WAF) only makes sense if this floor is solid.
