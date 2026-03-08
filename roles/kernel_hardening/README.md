# kernel_hardening

Hardens the Linux kernel via `sysctl` parameters and `modprobe` blacklists/install stubs. Drops a single file in `/etc/sysctl.d/` and `/etc/modprobe.d/` — never touches existing OS configuration.

Supports **review** mode (read-only posture report) and **enforce** mode (applies changes).

## Platform Support

Debian, Ubuntu, RHEL, Rocky, Alma, SUSE, openSUSE — no platform-specific packages required.

## Key sysctl Parameters

| Parameter | Default Value | Purpose | Compliance |
|-----------|---------------|---------|------------|
| `kernel.randomize_va_space` | `2` | Full ASLR | CIS 1.5.2 |
| `fs.suid_dumpable` | `0` | No core dumps from setuid | CIS 1.6.1 |
| `net.ipv4.tcp_syncookies` | `1` | SYN flood protection | CIS 3.3 |
| `net.ipv4.conf.all.send_redirects` | `0` | Disable ICMP redirect sending | CIS 3.2.2 |
| `net.ipv4.conf.all.accept_redirects` | `0` | Disable ICMP redirect acceptance | CIS 3.3.2 |
| `net.ipv4.conf.all.accept_source_route` | `0` | Disable source routing | CIS 3.3.1 |
| `net.ipv4.conf.all.log_martians` | `1` | Log impossible addresses | CIS 3.3.9 |
| `net.ipv4.conf.all.rp_filter` | `1` | Reverse path filtering | CIS 3.3.7 |
| `net.ipv6.conf.all.accept_redirects` | `0` | Disable IPv6 ICMP redirects | CIS 3.3.2 |
| `net.ipv6.conf.all.accept_source_route` | `0` | Disable IPv6 source routing | CIS 3.3.1 |
| `kernel.dmesg_restrict` | `1` | Restrict dmesg to root | CIS 1.5 |
| `kernel.perf_event_paranoid` | `2` | Restrict perf events | CIS 1.5 |
| `fs.protected_hardlinks` | `1` | Hardlink protection | CIS 1.5 |
| `fs.protected_symlinks` | `1` | Symlink protection | CIS 1.5 |

> **Note**: `net.ipv4.ip_forward` is intentionally not set — it is managed by roles that need it (e.g., router, container hosts). Do not add it here.

## Disabled Kernel Modules

| Module | Reason | Compliance |
|--------|--------|------------|
| `dccp` | Rarely used, known CVEs | CIS 3.4.1 |
| `sctp` | Rarely used, attack surface | CIS 3.4.2 |
| `rds` | Rarely used | CIS 3.4.3 |
| `tipc` | Rarely used | CIS 3.4.4 |
| `cramfs` | Legacy filesystem | CIS 1.1.1 |
| `freevxfs` | Legacy filesystem | CIS 1.1.1 |
| `jffs2` | Embedded filesystem | CIS 1.1.1 |
| `hfs` | macOS filesystem | CIS 1.1.1 |
| `hfsplus` | macOS filesystem | CIS 1.1.1 |
| `squashfs` | Compressed filesystem | CIS 1.1.1 |
| `udf` | DVD filesystem | CIS 1.1.1 |

Both `blacklist` and `install <module> /bin/false` stubs are applied so modules cannot be loaded even if explicitly requested.

## Modes

| Mode | Behaviour |
|------|-----------|
| `review` (default) | Reads current sysctl runtime values and loaded modules, reports gaps |
| `enforce` | Deploys `/etc/sysctl.d/99-security.conf` and `/etc/modprobe.d/99-security-disabled.conf`, applies sysctl live |

## Key Variables

```yaml
# Gate variables
security_mode: enforce
kernel_hardening_enabled: true

# Override any sysctl parameter
kernel_hardening_sysctl_params:
  kernel.randomize_va_space: 2
  fs.suid_dumpable: 0
  # ... (see defaults/main.yml for full list)

# Add extra modules to disable (without removing defaults)
kernel_hardening_disabled_modules_extra:
  - usb_storage
  - firewire_core
```

## Quick Start

```yaml
# Review mode
- hosts: all
  roles:
    - role: malpanez.security.kernel_hardening

# Enforce mode
- hosts: all
  vars:
    security_mode: enforce
    kernel_hardening_enabled: true
  roles:
    - role: malpanez.security.kernel_hardening
```

## Container Environments

`ansible.posix.sysctl` is called with `ignoreerrors: true` — parameters that are read-only in containers (e.g., `kernel.randomize_va_space`) are skipped gracefully. The molecule verify playbook also skips the runtime ASLR check when it cannot be set.

## Testing with Molecule

```bash
cd roles/kernel_hardening
molecule test
```

Tests verify: sysctl file exists with key parameters, modprobe file blacklists dccp/sctp/rds/tipc with install stubs.

## Compliance Mapping

| Control | Framework |
|---------|-----------|
| ASLR enabled | CIS 1.5.2, STIG V-238222 |
| Core dumps disabled | CIS 1.6.1, PCI-DSS 2.2.1 |
| Network hardening | CIS 3.2-3.4, NIS2 Art.21 |
| Legacy module blacklist | CIS 3.4, DISA STIG |
| Filesystem module blacklist | CIS 1.1.1, PCI-DSS 2.2 |

## License

Apache-2.0
