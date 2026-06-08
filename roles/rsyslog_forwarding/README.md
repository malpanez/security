# rsyslog_forwarding

Centralised log forwarding via rsyslog drop-in. Deploys `/etc/rsyslog.d/99-forwarding.conf` with RainerScript `action()` syntax, optional GnuTLS TLS, and disk-assisted queue. Never modifies `/etc/rsyslog.conf`. Supports review mode (audit-only) and enforce mode.

## Requirements

- Ansible >= 2.16
- Collection: `malpanez.security`
- For TLS: `rsyslog-gnutls` (RHEL/Debian) or `rsyslog-module-gtls` (openSUSE/SLES) installed on managed hosts.

## Role Variables

### Core

| Variable | Default | Description |
|----------|---------|-------------|
| `rsyslog_forwarding_enabled` | `false` | Gate variable. Set `true` with `security_mode: enforce` to install and configure forwarding. Review tasks always run. |
| `rsyslog_forwarding_host` | `""` | Hostname or IP of the remote syslog server. Required when `rsyslog_forwarding_enabled: true`. |
| `rsyslog_forwarding_port` | `514` | TCP or UDP port of the remote syslog server. |
| `rsyslog_forwarding_protocol` | `tcp` | Transport protocol: `tcp` or `udp`. TCP is strongly preferred for reliability and TLS support. |
| `rsyslog_forwarding_selector` | `"*.*"` | rsyslog selector filter. Follows `facility.severity` syntax. |

### Queue

| Variable | Default | Description |
|----------|---------|-------------|
| `rsyslog_forwarding_queue_type` | `LinkedList` | rsyslog queue type. Use `LinkedList` for in-memory or `LinkedList-DA` / `Disk` for disk-assisted spooling. |
| `rsyslog_forwarding_queue_size` | `10000` | Maximum messages in the forwarding queue before dropping or blocking. |
| `rsyslog_forwarding_queue_spool_dir` | `/var/spool/rsyslog/forwarding` | Filesystem directory for disk-assisted queue spool files. Must be writable by the rsyslog user. |
| `rsyslog_forwarding_queue_file_name` | `fwd-queue` | Base filename prefix for disk queue spool files. |
| `rsyslog_forwarding_resume_retry_count` | `-1` | Retries when the remote endpoint is unavailable before discarding messages. `-1` means retry indefinitely. |

### TLS

| Variable | Default | Description |
|----------|---------|-------------|
| `rsyslog_forwarding_tls_enabled` | `false` | Enable GnuTLS transport encryption. Requires `rsyslog_forwarding_tls_ca_cert` to be set. |
| `rsyslog_forwarding_tls_ca_cert` | `""` | Path to the CA certificate on the managed host used to verify the remote server TLS certificate. |
| `rsyslog_forwarding_tls_auth_mode` | `x509/name` | GnuTLS auth mode. `x509/name` validates server certificate CN/SAN against the target hostname. |
| `rsyslog_forwarding_tls_client_cert` | `""` | Path to the client TLS certificate on the managed host. Required for mutual TLS (mTLS). |
| `rsyslog_forwarding_tls_client_key` | `""` | Path to the client TLS private key on the managed host. Required for mTLS. |

### Logrotate

| Variable | Default | Description |
|----------|---------|-------------|
| `rsyslog_forwarding_logrotate_enabled` | `true` | Deploy a logrotate drop-in for rsyslog log files. |
| `rsyslog_forwarding_logrotate_rotate` | `4` | Number of rotated log files to retain. |
| `rsyslog_forwarding_logrotate_size` | `50M` | Maximum log file size before rotation. Follows logrotate size syntax. |
| `rsyslog_forwarding_log_dir` | `/var/log` | Base directory for rsyslog log files managed by logrotate. |
| `rsyslog_forwarding_file_create_mode` | `"0640"` | File creation mode for new rsyslog log files. `0640` restricts read access to the rsyslog group. |

## Example Playbook

```yaml
- name: Configure centralised log forwarding
  hosts: all
  roles:
    - role: malpanez.security.rsyslog_forwarding
      vars:
        rsyslog_forwarding_enabled: true
        security_mode: enforce
        rsyslog_forwarding_host: siem.corp.example.com
        rsyslog_forwarding_port: 6514
        rsyslog_forwarding_tls_enabled: true
        rsyslog_forwarding_tls_ca_cert: /etc/pki/tls/certs/siem-ca.crt
```

## Compliance

| Framework | Controls |
|-----------|----------|
| NIS2 | Art. 21 — Logging and monitoring |
| SOC2 | CC7.2 — System monitoring |
| PCI-DSS | 10.5 — Protect audit logs from modification |

## License

Apache-2.0

## Author

Miguel Alpañez
