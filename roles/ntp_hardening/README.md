# ntp_hardening

NTP/chrony hardening. Installs chrony, disables competing time daemons, deploys a hardened chrony.conf, and enables the service. Supports review mode (audit-only) and enforce mode.

## Requirements

- Ansible >= 2.16
- Collection: `malpanez.security`

## Role Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `ntp_hardening_enabled` | `false` | Gate variable. Set `true` with `security_mode: enforce` to install and configure chrony. Review tasks always run. |
| `ntp_hardening_servers` | `[0-3].pool.ntp.org iburst` | List of NTP server directives. Each entry is a full chrony server line (e.g. `0.pool.ntp.org iburst`). |
| `ntp_hardening_makestep` | `"1.0 3"` | chrony `makestep` directive value. Format: `threshold limit`. Allows stepping the clock on initial sync. |
| `ntp_hardening_rtcsync` | `true` | Enables the `rtcsync` directive so the kernel synchronises the hardware clock every 11 minutes. |
| `ntp_hardening_maxdistance` | `1.5` | Maximum root distance in seconds. Sources exceeding this value are rejected. |
| `ntp_hardening_minsources` | `1` | Minimum selectable sources required before chrony will update the system clock. |
| `ntp_hardening_allow` | `[]` | Subnets or hosts allowed to use this host as an NTP server. Empty list = client-only mode. |
| `ntp_hardening_deny_all` | `true` | Adds a `deny all` directive after any allow entries to block all other NTP clients. Only relevant when `ntp_hardening_allow` is non-empty. |
| `ntp_hardening_leapsectz` | `"right/UTC"` | Timezone for leap second handling. `right/UTC` uses the IANA timezone that embeds leap second data. |
| `ntp_hardening_logdir` | `/var/log/chrony` | Directory where chrony writes log files. |
| `ntp_hardening_logchange` | `0.5` | Threshold in seconds above which a clock change is logged. |

## Example Playbook

```yaml
- name: Harden NTP with chrony
  hosts: all
  roles:
    - role: malpanez.security.ntp_hardening
      vars:
        ntp_hardening_enabled: true
        security_mode: enforce
        ntp_hardening_servers:
          - ntp1.corp.example.com iburst
          - ntp2.corp.example.com iburst
```

## Compliance

| Framework | Controls |
|-----------|----------|
| PCI-DSS | 10.6.1 — Time synchronisation |
| NIS2 | Art. 21 — Time integrity |
| SOC2 | CC6.1 — Logical access controls |

## License

Apache-2.0

## Author

Miguel Alpañez
