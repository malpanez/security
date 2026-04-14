# SSH + AD Integration: Design Rationale and Common Mistakes

**Role:** `malpanez.security.sssd_ad_integration`
**Audience:** Sysadmins deploying NIS2-compliant Linux servers joined to Active Directory

---

## The Layered Defense Model

This implementation enforces three independent layers. An attacker must bypass all three:

```
Internet → sshd AllowGroups gate (20-access-control.conf)
         → PAM access.conf (pam_access.so)
         → sshd Match Group blocks (40-43, restrict capabilities)
         → sudoers.d (restrict privilege escalation)
```

Each layer is independent. If sshd is misconfigured, pam_access still denies.
If pam_access is absent, sshd AllowGroups still gates. Defense in depth.

---

## Common Mistakes — What Most References Get Wrong

### 1. `ForceCommand none` is not valid

You will find examples using `ForceCommand none` to "unset" a ForceCommand from a
previous Match block. **This is invalid.** OpenSSH has no ForceCommand unset token.

Attempting it causes `sshd -t` to fail with a parse error. The role never uses
`ForceCommand none`. Service account command restrictions belong in `authorized_keys`
using the `command=` option, not in sshd_config.

### 2. `!ALL` negation in sudoers locks you out

The sudoers `!` negation operator (`!ALL`, `!/sbin/reboot`) creates implicit deny rules
that interact badly with other grants. The canonical CERT advisory documents cases where:

```
%linux-admins ALL=(ALL) ALL
%linux-admins ALL=(ALL) !/bin/su
```

...still allows `sudo su` because the PATH resolution differs. **Never use `!`.**
Grant only what is needed. If a group needs less than another, give it less explicitly.
This implementation has no `!` in any sudoers template.

### 3. `sudo_provider = ad` is not viable in practice

AD schema extensions required for `sudo_provider = ad` (RFC 2307 and sudoRule
objectClass) are rarely approved by AD teams. The schema modification requires
Enterprise Admin rights and affects all AD-joined machines.

This role uses `sudo_provider = sssd`, which means SSSD exposes the NSS sudoers
source, but the rules themselves live in `/etc/sudoers.d/`. No AD schema changes needed.

### 4. Multiline values in sssd.conf

`sssd.conf` is INI format. It does **not** support backslash line continuation for values.
An `ad_access_filter` split across lines will be silently truncated or cause a parse error.

```ini
# WRONG — second line is ignored or causes error
ad_access_filter = (&(objectClass=user)
  (memberOf=CN=linux-access,...))

# CORRECT — single line
ad_access_filter = (&(objectClass=user)(memberOf=CN=linux-access,...))
```

### 5. TCP Wrappers removal in RHEL 8+

`/etc/hosts.allow` and `/etc/hosts.deny` are **ignored** on RHEL 8+ and recent Debian.
`tcpwrappers` has been removed from the default install. Any references to TCP Wrappers
for SSH access control are obsolete. Use `pam_access.so` instead (this role deploys it).

### 6. `use_fully_qualified_names = true` breaks group membership

With `use_fully_qualified_names = true`, AD users must log in as `user@domain`.
But group membership in sshd `AllowGroups` is resolved by NSS, which sees the
fully-qualified username. `Match Group linux-admins` stops matching because SSSD
returns group members as `user@domain`, not `user`.

Use `use_fully_qualified_names = false` (this role default) unless you have overlapping
usernames across trusted domains.

### 7. `AllowGroups` inside a Match block does not gate access

`AllowGroups` at the global level (outside any Match block) is evaluated **before**
any Match block. Placing `AllowGroups` inside a Match block means it only applies
when that specific Match condition is true — other connections bypass it entirely.

This role places `AllowGroups` globally in `20-access-control.conf` (no Match block),
ensuring all connections are gated before any group-specific block runs.

---

## sshd_config.d File Ordering

OpenSSH includes drop-ins **lexicographically**. Within each file, sshd processes
directives in order. When multiple Match blocks are triggered by the same connection,
all matching blocks apply — but **the first occurrence of each directive wins**.

```
00-hardening.conf       # crypto (KexAlgorithms, Ciphers, MACs, RekeyLimit)
10-auth-hardening.conf  # global restrictive defaults (sshd_hardening role)
20-access-control.conf  # AllowGroups gate (this role)
30-network-zones.conf   # Match Address: corp, vpn, bastion
40-group-admins.conf    # Match Group linux-admins
41-group-users.conf     # Match Group linux-users
42-group-service.conf   # Match Group linux-service
43-group-readonly.conf  # Match Group linux-readonly
```

### Zone-aware 2FA without AND conditions

OpenSSH Match blocks support `Match Address`, `Match Group`, and `Match User` but
**not** combined conditions like `Match Address X Group Y`. We exploit first-occurrence
ordering to achieve zone-aware 2FA:

```
30-network-zones.conf, Match Address corp:
    AuthenticationMethods publickey          ← relaxed, first occurrence for corp users

40-group-admins.conf, Match Group linux-admins:
    AuthenticationMethods publickey,keyboard-interactive  ← 2FA, first occurrence from internet
```

When an admin connects **from corp LAN**: both Match blocks fire. `30` sorts before `40`,
so `AuthenticationMethods publickey` (from `30`) is seen first → single-factor auth.

When an admin connects **from internet**: only the group block fires →
`publickey,keyboard-interactive` → 2FA required.

`keyboard-interactive` maps to PAM (TOTP via `pam_google_authenticator` or FIDO2 via
`pam_u2f`). Requires `malpanez.security.pam_mfa` to configure the PAM stack.

### Directives NOT valid inside Match blocks

These must remain global (in `10-auth-hardening.conf`):
- `LoginGraceTime`
- `MaxStartups`
- `UseDNS`
- `ListenAddress`
- `Port`

Attempting to use them inside a Match block causes `sshd -t` to fail.

---

## SSSD Configuration Decisions

### id_provider = ad vs ldap

`id_provider = ad` is the correct choice for AD. It handles Kerberos ticket renewal,
SID-based ID mapping, and cross-domain trust automatically. `id_provider = ldap` with
an AD backend requires manual Kerberos configuration and misses AD-specific LDAP schema.

### ldap_id_mapping = true (default)

Derives UID/GID from the AD SID using a deterministic algorithm (same SID → same UID
on every machine). No AD schema changes needed. Consistent UIDs across a fleet.

Disable only if your AD team has provisioned explicit `uidNumber`/`gidNumber` attributes
(RFC 2307). Mixing both modes on different machines with the same AD accounts creates
file ownership mismatches.

### Offline Credentials Expiration

`offline_credentials_expiration = 0` (never expire) is the SSSD default and this role's
default. This means:

- **Benefit**: Users can authenticate even during extended AD outages.
- **Risk**: A revoked or disabled AD account can still authenticate from a machine that
  has cached credentials, until the cache is manually cleared or the machine reconnects
  to AD.

**Teams must decide this explicitly for their threat model:**

| `offline_credentials_expiration` | Implication |
|---|---|
| `0` | Never expire. Best availability. Revocation not enforced offline. |
| `1` | Expire after 1 day. Revocation enforced within 24h of AD reconnect. |
| `7` | Expire after 7 days. Balance for remote/field deployments. |

For NIS2 Article 21(2)(i) (access control measures): set to `1` or `7` and document
the decision in your risk register.

### ad_access_filter

Use this to restrict which AD objects can log in without requiring group membership
at the sudoers/sshd level:

```yaml
# Allow only members of a specific AD group to even reach SSSD auth
sssd_access_filter: '(&(objectClass=user)(memberOf=CN=linux-access,OU=Groups,DC=corp,DC=example,DC=com))'
```

This is an AD-side gate complementing `AllowGroups` (sshd gate) and `pam_access.conf`
(PAM gate). Not all AD environments have this group pre-created — hence the variable
is empty by default and the access_provider=ad default already enforces the account must
be enabled and not expired.

---

## AD Group Verification: Closing the Silent Lockout Gap

The hardest failure mode in this deployment is a group that exists in `AllowGroups`
but has no members (or doesn't exist) in AD. sshd accepts the TCP connection, initiates
auth, and then silently rejects it — no error on the client beyond "Permission denied".

The role includes a built-in verification step (`tasks/verify_groups.yml`) that runs
`getent group` for each enabled group after configuration is applied.

### Variables

```yaml
ssh_verify_ad_groups: true        # enable/disable the check
ssh_verify_ad_groups_strict: false # false=warn, true=fail the play
```

### Failure modes detected

| `getent group` result | State | Meaning |
|---|---|---|
| rc=0, members present | `ok` | Group resolved, has members — safe to deploy |
| rc=0, member field empty | `empty` | Group exists in NSS but nobody is in it |
| rc=2 | `not_found` | SSSD not joined, group doesn't exist in AD, or cache cold |

### Recommended usage by environment

**Development / initial rollout** — `ssh_verify_ad_groups_strict: false`
The role warns but doesn't fail. You can deploy sshd config and see which
groups resolve before the AD team has finished provisioning.

**CI pipelines and post-join playbooks** — `ssh_verify_ad_groups_strict: true`
Fails the play immediately if any configured group is missing or empty.
Gates deployment on confirmed AD state. Use in a dedicated verification playbook:

```yaml
- name: Verify AD group state before SSH hardening
  hosts: linux_servers
  roles:
    - role: malpanez.security.sssd_ad_integration
      vars:
        security_mode: review          # no file writes
        sssd_ad_configure: false       # SSSD already configured
        ssh_verify_ad_groups: true
        ssh_verify_ad_groups_strict: true
```

### Diagnosing a failed check

```bash
# 1. Is SSSD running and joined?
systemctl status sssd
realm list

# 2. Can SSSD resolve the group at all?
getent group linux-admins

# 3. Force cache refresh (group membership changed in AD recently)
sss_cache -G linux-admins
sss_cache -u someuser

# 4. Check SSSD logs for AD connectivity errors
journalctl -u sssd --since "10 minutes ago" | grep -i error

# 5. Verify the group exists in AD (requires adcli or ldapsearch)
adcli info corp.example.com
ldapsearch -H ldap://dc.corp.example.com -b "DC=corp,DC=example,DC=com" \
  "(sAMAccountName=linux-admins)" member
```

### NIS2 alignment

For NIS2 Article 21(2)(i), the verification step provides **continuous control
evidence**: every Ansible run produces a log entry confirming group membership
state. When `ssh_verify_ad_groups_strict: true`, a missing group blocks deployment
— enforcing the principle that access controls must be verifiably active, not
just configured.

Integrate with your monitoring stack by scraping Ansible run logs or by running
the verification playbook on a schedule via AWX/AAP.

---

## PAM access.conf: The Second Layer

`pam_access.conf` is enforced by `pam_access.so` in the PAM stack — independently of
sshd. Even if sshd is misconfigured or an admin bypasses it (e.g., via a jump host
config error), pam_access still denies based on source IP.

### Activation

The role automatically activates `pam_access.so` in the PAM sshd stack
(controlled by `ssh_pam_access_activate: true`, default true).

**Debian/Ubuntu:** `pam-auth-update --enable access` (non-interactive, idempotent)

**RHEL/Rocky 9:** Inserts `account required pam_access.so` into `/etc/pam.d/sshd`
before `pam_unix.so`. The role does NOT touch `system-auth` or `password-auth`
(authselect-managed symlinks on RHEL 8+).

To disable when PAM is managed externally (authselect profiles, Puppet, etc.):
```yaml
ssh_pam_access_activate: false
```

**Verify activation:**
```bash
grep pam_access /etc/pam.d/sshd /etc/pam.d/system-auth /etc/pam.d/password-auth
```

### CIDR notation in pam_access

Modern `pam_access.so` (pam >= 1.3 on RHEL 8+, pam >= 1.2 on Debian 10+) supports
`network/prefix` notation:

```
+:@linux-admins:10.10.0.0/16 10.8.0.0/24
```

Older versions require dotted-decimal netmask: `10.10.0.0/255.255.0.0`. The role
uses CIDR notation from the `ssh_network_zones` variables. Verify your pam version
if deploying on RHEL 7 or Debian 9.

### Never remove the catch-all deny

The last line `-:ALL:ALL` denies everything not explicitly allowed. Without it,
pam_access allows all by default (fail open). Always keep this line last.

---

## sudoers Design Principles

### No ! negation — ever

The `!` operator in sudoers creates deny rules that interact unpredictably with other
grants. The Linux sudoers manual warns: "it is not possible to prevent users from
running privileged commands" using `!` because there are always alternative paths.

This implementation uses explicit allowlists only. If a group needs no sudo,
it gets no sudoers file (not a file that denies).

### linux-service: no sudoers file

Service accounts that need to run specific commands should do so via `authorized_keys`
`command=` restrictions, not sudo. If a service account genuinely needs one specific
privileged command, create a dedicated wrapper binary owned root with setuid, or use
a separate sudoers file with a single explicit command.

### visudo validation in the deploy pipeline

The `validate: "visudo -cf %s"` on `ansible.builtin.template` means Ansible validates
the sudoers file before writing it. If the template produces invalid syntax (e.g.,
from a variable containing a space or special character), the play fails before
the invalid file reaches disk.

---

## NIS2 Control Mapping

Article 21(2) of NIS2 (EU Directive 2022/2555) requires "appropriate and proportionate
technical and organisational measures." The following controls from this role map to
specific NIS2 obligations:

| Control | NIS2 Ref | Implementation |
|---------|----------|----------------|
| Network-zone-aware access control | Art.21(2)(b) network security | Match Address blocks in 30-network-zones.conf |
| Group-based privilege tiers | Art.21(2)(i) access control | Match Group blocks + sudoers.d |
| 2FA from untrusted networks | Art.21(2)(i) multi-factor auth | AuthenticationMethods in 40-group-admins.conf |
| Audit trail | Art.21(2)(j) logging | sshd_hardening LogLevel VERBOSE + sudo logfile |
| Offline access risk documented | Art.21(2)(a) risk management | offline_credentials_expiration documented here |
| Independent enforcement layer | Art.21(2)(b) defence in depth | pam_access.conf independent of sshd |

For a complete control inventory, run `malpanez.security.compliance_evidence`.

---

## The AD Group Discovery Problem

The hardest operational problem in this deployment is: **which AD groups actually exist,
and are they correctly populated?**

### The gap

This role configures SSH and PAM to enforce group membership. But if `linux-admins`
does not exist in AD (or has no members, or the SSSD cache is stale), the result is:
- `AllowGroups linux-admins` → no one can log in as admin
- Silent failure — sshd accepts the connection, then rejects auth

### Verification procedure

Before applying to production:

```bash
# 1. Confirm SSSD resolves the group
id someuser@corp.example.com
getent group linux-admins

# 2. Confirm group members are visible
getent group linux-admins | grep expecteduser

# 3. Force cache refresh if stale
sss_cache -G linux-admins
sss_cache -u someuser

# 4. Test SSH auth as a group member (from a second terminal — keep console open)
ssh -v -o BatchMode=no testuser@targethost
```

### Graceful degradation strategy

Set `ssh_local_fallback_group` to a **local** group (not an AD group) that contains
your Ansible deploy user. This group is always in `AllowGroups` and is not affected
by AD outages or group discovery failures.

```yaml
ssh_local_fallback_group: ansible-deploy  # local group, always present
```

The `ansible-deploy` user should be the only member. This is your emergency access path.

### Staged rollout

1. Deploy with `security_mode: review` — generates no drop-in files, only asserts variables
2. Deploy with `sssd_ad_configure: true` only — verify SSSD resolves groups
3. Deploy sshd drop-ins on a single non-production host
4. Test all four group tiers manually
5. Roll out to production fleet

---

## Safety Checklist

Before applying to a production server where SSH is the only access method:

- [ ] Console/IPMI/BMC access confirmed working
- [ ] `ssh_local_fallback_group` set to a local group with deploy user
- [ ] AD groups exist and are populated (`getent group linux-admins`)
- [ ] SSSD is joined to AD and resolving users (`id someuser`)
- [ ] `sshd -t` passes on a test host with same drop-ins
- [ ] `offline_credentials_expiration` decision documented in risk register
- [ ] pam_access.so activation verified on target distro
- [ ] Molecule test run passes for target platform
