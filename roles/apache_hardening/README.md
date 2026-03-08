# apache_hardening

Hardens Apache httpd (RHEL) / Apache2 (Debian/SUSE) via a drop-in configuration file. Never modifies the main `httpd.conf` / `apache2.conf`. Skips gracefully if Apache is not installed.

Supports **review** mode (posture check) and **enforce** mode (applies drop-in).

## Platform Support

| Platform | Package | Drop-in path |
|----------|---------|--------------|
| Debian / Ubuntu | `apache2` | `/etc/apache2/conf-available/99-security-hardening.conf` |
| RHEL / Rocky / Alma | `httpd` | `/etc/httpd/conf.d/99-security-hardening.conf` |
| SUSE / openSUSE | `apache2` | `/etc/apache2/conf.d/99-security-hardening.conf` |

Skips automatically if the platform config directory does not exist.

## What It Hardens

| Area | Setting | Compliance |
|------|---------|------------|
| Version disclosure | `ServerTokens Prod` + `ServerSignature Off` | CIS Apache 2.6 |
| TRACE method | `TraceEnable Off` | CIS Apache 2.7, OWASP |
| TLS protocols | TLSv1.2 + TLSv1.3 only (`-SSLv3 -TLSv1 -TLSv1.1`) | PCI-DSS 4.2.1 |
| Cipher suites | AEAD ciphers, server order enforced | PCI-DSS 4.2.1 |
| TLS session tickets | `Off` | CIS 4.x |
| OCSP stapling | Enabled | CIS 4.x |
| TLS compression | `Off` (CRIME attack) | CIS 4.x |
| HSTS | `max-age=31536000; includeSubDomains` | PCI-DSS, CIS |
| X-Frame-Options | `SAMEORIGIN` | OWASP A05 |
| X-Content-Type-Options | `nosniff` | OWASP A05 |
| X-XSS-Protection | `1; mode=block` | Legacy browser defence |
| Referrer-Policy | `strict-origin-when-cross-origin` | Privacy |
| Content-Security-Policy | `default-src 'self'` (configurable) | OWASP A05 |
| Directory listing | `Options -Indexes` | CIS Apache 3.x |
| FollowSymLinks | Disabled | CIS Apache 3.x |
| SSI | Disabled | CIS Apache 3.x |
| `.htaccess` | `AllowOverride None` | CIS Apache 3.x |
| Request limits | 10MB body, 100 fields, 8190 line | CIS Apache 5.x |
| Disabled modules | autoindex, status, info, userdir, cgi, dav, WebDAV | CIS Apache 2.x |
| Enabled modules | headers, ssl, rewrite | Required for hardening |

## Modes

| Mode | Behaviour |
|------|-----------|
| `review` (default) | Check ServerTokens, TraceEnable, TLS, security headers |
| `enforce` | Deploy drop-in, manage modules, validate config, reload |

## Key Variables

```yaml
# Gate variables
security_mode: enforce
apache_hardening_enabled: true

# TLS
apache_hardening_ssl_protocol: "all -SSLv3 -TLSv1 -TLSv1.1"
apache_hardening_ssl_honor_cipher_order: "On"
apache_hardening_ssl_session_tickets: "Off"
apache_hardening_ssl_compression: "Off"
apache_hardening_ssl_stapling: "On"

# Server info
apache_hardening_server_tokens: "Prod"
apache_hardening_server_signature: "Off"
apache_hardening_trace_enable: "Off"

# Security headers
apache_hardening_hsts_enabled: true
apache_hardening_hsts_max_age: 31536000
apache_hardening_x_frame_options: "SAMEORIGIN"
apache_hardening_csp: >-
  default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self' data:;
  frame-ancestors 'self'; form-action 'self'

# Directory hardening
apache_hardening_options_none: true
apache_hardening_follow_symlinks: false
apache_hardening_override_none: true

# Request limits
apache_hardening_limit_request_body: 10485760    # 10MB
apache_hardening_limit_request_fields: 100
apache_hardening_timeout: 60
apache_hardening_keep_alive_timeout: 5

# Modules to disable
apache_hardening_modules_disable:
  - autoindex
  - status
  - info
  - userdir
  - cgi
  - dav
  - dav_fs

# Modules to enable
apache_hardening_modules_enable:
  - headers
  - ssl
  - rewrite
```

## Quick Start

```yaml
# Review mode — safe, read-only
- hosts: all
  roles:
    - role: malpanez.security.apache_hardening

# Enforce mode
- hosts: web
  vars:
    security_mode: enforce
    apache_hardening_enabled: true
  roles:
    - role: malpanez.security.apache_hardening
```

## Drop-In Approach

Only one file is written — the platform-appropriate path shown above. Your `httpd.conf` / `apache2.conf` and virtual host files are never modified.

On Debian/Ubuntu the role also runs `a2enconf 99-security-hardening`, and `a2dismod`/`a2enmod` for module management. On RHEL/SUSE, module config is included inline in the drop-in.

## Testing with Molecule

```bash
cd roles/apache_hardening
molecule test
```

Tests verify: drop-in file exists, `ServerTokens Prod` present, TLSv1 absent, HSTS header configured, `apachectl -t` (or `httpd -t`) passes.

## Compliance Mapping

| Control | Framework |
|---------|-----------|
| TLS 1.2+ only | PCI-DSS 4.2.1, CIS Apache 4.x, NIS2 Art.21(2)(h) |
| Server info disclosure | CIS Apache 2.6–2.7, PCI-DSS 6.2.4 |
| Directory hardening | CIS Apache 3.x, OWASP A05:2021 |
| Security headers | OWASP Top 10 A05:2021 |
| Module reduction | CIS Apache 2.x, PCI-DSS 2.2.4 |
| Request limits | CIS Apache 5.x, OWASP A04 |

## License

GPL-2.0-or-later
