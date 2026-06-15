# firewall

Host-based firewall hardening with a **default-deny** inbound policy and an explicit allowlist. SSH is always kept open to prevent administrative lockout. Uses **firewalld** on RHEL/SUSE and **ufw** on Debian/Ubuntu. Supports review mode (audit-only) and enforce mode.

## Requirements

- Ansible >= 2.16
- Collection: `malpanez.security` (pulls `ansible.posix` for firewalld, `community.general` for ufw)

## Role Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `firewall_enabled` | `false` | Gate variable. Set `true` with `security_mode: enforce` to apply the policy. Review tasks always run. |
| `firewall_default_incoming_policy` | `deny` | Default inbound policy (`deny`/`allow`/`reject`). `deny` maps to firewalld `DROP` / ufw `DROP`. |
| `firewall_default_outgoing_policy` | `allow` | Default outbound policy. |
| `firewall_default_routed_policy` | `deny` | Default forwarded/routed policy. |
| `firewall_ssh_port` | `22` | SSH port kept open unconditionally to avoid lockout. |
| `firewall_allowed_tcp_ports` | `[]` | Additional inbound TCP ports to allow, e.g. `[80, 443]`. |
| `firewall_allowed_udp_ports` | `[]` | Additional inbound UDP ports to allow. |
| `firewall_allowed_services` | `[]` | firewalld service names to allow (e.g. `http`). Ignored by the ufw backend. |
| `firewall_trusted_sources` | `[]` | Source CIDRs allowed all inbound traffic (e.g. a management subnet). |
| `firewall_logging` | `true` | Enable firewall logging. |
| `firewall_log_level` | `low` | ufw logging verbosity (`off`/`low`/`medium`/`high`/`full`). Ignored by firewalld. |
| `firewall_zone` | `public` | firewalld zone to manage. Ignored by the ufw backend. |

## Backends

| OS family | Backend | Notes |
|-----------|---------|-------|
| RedHat, Suse | `firewalld` | Default-deny via zone target; allowlist via services/ports; trusted sources via the `trusted` zone. |
| Debian | `ufw` | Default-deny via `DEFAULT_INPUT_POLICY`; allowlist via `ufw allow` rules. |

In containers, runtime firewall activation is skipped (netfilter is host-controlled); the role still installs the package and, for ufw, writes the policy configuration.

## Example Playbook

```yaml
- name: Harden the host firewall
  hosts: all
  roles:
    - role: malpanez.security.firewall
      vars:
        firewall_enabled: true
        security_mode: enforce
        firewall_allowed_tcp_ports: [443]
        firewall_trusted_sources:
          - 10.20.0.0/24      # management subnet
```

## Compliance

CIS 3.5.x (host firewall), NIST CM-7 (least functionality) / SC-7 (boundary protection), NIS2 Art.21(2)(j) (network security).

## License

Apache-2.0
