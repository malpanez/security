# mysql_hardening

Hardens MySQL and MariaDB database servers: removes default insecure objects, enforces connection restrictions, hardens `my.cnf`, and enforces file permissions. Skips gracefully if MySQL/MariaDB is not installed.

Requires the `community.mysql` collection.

Supports **review** mode (posture check) and **enforce** mode (applies changes).

## Platform Support

| Platform | MySQL | MariaDB |
|----------|-------|---------|
| Debian / Ubuntu | 5.7, 8.x | 10.x, 11.x |
| RHEL / Rocky / Alma | 8.x | 10.x |
| SUSE / openSUSE | 8.x | 10.x |

Skips automatically if the MySQL/MariaDB service is not found.

## What It Hardens

| Area | Action | Compliance |
|------|--------|------------|
| Anonymous users | Removed from `mysql.user` | CIS MySQL 4.1 |
| Remote root login | Revoked (`root@%` removed) | CIS MySQL 4.3 |
| Test database | Removed | CIS MySQL 4.2 |
| `local_infile` | Disabled (`local_infile=0`) | CIS MySQL 5.4 |
| Suspicious UDFs | `allow-suspicious-udfs=OFF` | CIS MySQL 7.1 |
| Symbolic links | Disabled (`symbolic-links=0`) | CIS MySQL 7.2 |
| `secure_file_priv` | Restricted path | CIS MySQL 7.3 |
| Skip grant tables | Enforced off | CIS MySQL 3.1 |
| Automatic SP privileges | Disabled | CIS MySQL 5.x |
| Safe user create | Enabled | CIS MySQL 4.x |
| Bind address | `127.0.0.1` (disable remote by default) | CIS MySQL 4.6 |
| Password expiry | 90 days for accounts without policy | CIS MySQL 4.x |
| Data directory | `0750` permissions, `mysql:mysql` owner | CIS MySQL 7.4 |
| Error log | `0640` permissions | CIS MySQL 7.4 |
| Log warnings | Level 2 | CIS MySQL 8.x |
| TLS (optional) | SSL cert/key/CA configurable | PCI-DSS 4.2.1 |
| Audit logging | MariaDB audit plugin / MySQL Enterprise (optional) | PCI-DSS 10.3 |

## Modes

| Mode | Behaviour |
|------|-----------|
| `review` (default) | Check anonymous users, remote root, local_infile, bind address |
| `enforce` | Remove insecure objects, write hardened config drop-in, fix permissions |

## Key Variables

```yaml
# Gate variables
security_mode: enforce
mysql_hardening_enabled: true

# Connection hardening
mysql_hardening_remove_anonymous_users: true
mysql_hardening_remove_remote_root: true
mysql_hardening_remove_test_db: true
mysql_hardening_bind_address: "127.0.0.1"

# my.cnf hardening
mysql_hardening_local_infile: false
mysql_hardening_symbolic_links: false
mysql_hardening_secure_file_priv: /tmp
mysql_hardening_skip_grant_tables: false
mysql_hardening_allow_suspicious_udfs: false
mysql_hardening_automatic_sp_privileges: false
mysql_hardening_safe_user_create: true

# Password policy
mysql_hardening_password_expiry_days: 90

# TLS (disabled by default — enable when certs are ready)
mysql_hardening_ssl_enabled: false
mysql_hardening_ssl_cert: /etc/mysql/ssl/server-cert.pem
mysql_hardening_ssl_key: /etc/mysql/ssl/server-key.pem
mysql_hardening_ssl_ca: /etc/mysql/ssl/ca-cert.pem
mysql_hardening_require_ssl: false     # Force TLS for all connections

# File permissions
mysql_hardening_datadir_mode: "0750"
mysql_hardening_error_log_mode: "0640"

# Audit logging
mysql_hardening_audit_enabled: false
mysql_hardening_audit_log_file: /var/log/mysql/audit.log
```

## Quick Start

```yaml
# Review mode — safe, read-only
- hosts: all
  roles:
    - role: malpanez.security.mysql_hardening

# Enforce mode
- hosts: db
  vars:
    security_mode: enforce
    mysql_hardening_enabled: true
  roles:
    - role: malpanez.security.mysql_hardening
```

## Requirements

The `community.mysql` collection must be installed:

```bash
ansible-galaxy collection install community.mysql
```

The role connects to MySQL/MariaDB via the Unix socket as `root` (no password required when Ansible runs with `become: true` on the DB host).

## Replication Environments

If this server is a replication primary or replica:

```yaml
mysql_hardening_bind_address: "0.0.0.0"   # Or the replication interface IP
mysql_hardening_remove_remote_root: true   # Still remove root remote access
```

Use a dedicated replication user with `REPLICATION SLAVE` privilege only.

## TLS for All Connections (PCI-DSS)

```yaml
mysql_hardening_ssl_enabled: true
mysql_hardening_ssl_cert: /etc/mysql/ssl/server-cert.pem
mysql_hardening_ssl_key: /etc/mysql/ssl/server-key.pem
mysql_hardening_ssl_ca: /etc/mysql/ssl/ca-cert.pem
mysql_hardening_require_ssl: true
```

## Testing with Molecule

```bash
cd roles/mysql_hardening
molecule test
```

Tests verify: anonymous users absent, remote root absent, test DB absent, `local_infile` off, bind address restricted.

## Compliance Mapping

| Control | Framework |
|---------|-----------|
| Remove default insecure objects | CIS MySQL 4.1–4.3, PCI-DSS 2.2.4 |
| Network binding restriction | CIS MySQL 4.6, NIS2 Art.21(2)(b) |
| File access restrictions | CIS MySQL 5.4, 7.1–7.3 |
| File permissions | CIS MySQL 7.4, HIPAA §164.312(a) |
| Audit logging | PCI-DSS 10.3, SOC2 CC7.2 |
| TLS for connections | PCI-DSS 4.2.1, HIPAA §164.312(e) |
| Password policy | CIS MySQL 4.x, PCI-DSS 8.3.6 |

## License

GPL-2.0-or-later
