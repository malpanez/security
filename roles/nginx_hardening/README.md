# nginx_hardening

Hardens Nginx web server via a drop-in configuration file (`/etc/nginx/conf.d/99-security-hardening.conf`). Never modifies `nginx.conf` or existing virtual hosts. Skips gracefully if Nginx is not installed.

Supports **review** mode (posture check) and **enforce** mode (applies drop-in).

## Platform Support

| Platform | Notes |
|----------|-------|
| Debian / Ubuntu | Package: `nginx` |
| RHEL / Rocky / Alma | Package: `nginx` (EPEL or RHEL repos) |
| SUSE / openSUSE | Package: `nginx` |

Skips automatically if `/etc/nginx/nginx.conf` does not exist.

## What It Hardens

| Area | Setting | Compliance |
|------|---------|------------|
| Version disclosure | `server_tokens off` | CIS Nginx 2.5.1 |
| TLS protocols | TLSv1.2 + TLSv1.3 only | PCI-DSS 4.2.1, CIS 4.1 |
| Cipher suites | AEAD ciphers only (ECDHE + DHE) | PCI-DSS 4.2.1 |
| DH parameters | 2048-bit generated on first run | CIS 4.1.8 |
| TLS session tickets | Disabled (forward secrecy) | CIS 4.1.11 |
| OCSP stapling | Enabled | CIS 4.1.6 |
| HSTS | `max-age=31536000; includeSubDomains` | CIS 4.1.14, PCI-DSS |
| X-Frame-Options | `SAMEORIGIN` | OWASP A05 |
| X-Content-Type-Options | `nosniff` | OWASP A05 |
| Referrer-Policy | `strict-origin-when-cross-origin` | OWASP |
| Permissions-Policy | Geo/mic/camera disabled | Privacy |
| Content-Security-Policy | `default-src 'self'` (configurable) | OWASP A05 |
| Request size limits | 10MB body, 1K header buffers | CIS 5.2.x |
| Rate limiting | 10 req/s, burst 20 | CIS 5.3 |
| Connection limiting | 10 connections per IP | CIS 5.3 |
| HTTP TRACE | Disabled | CIS 5.2.5 |
| Client timeouts | 10s body/header, 65s keepalive | CIS 5.2.x |

## Modes

| Mode | Behaviour |
|------|-----------|
| `review` (default) | Check server_tokens, HSTS, TLS 1.0/1.1 presence |
| `enforce` | Deploy drop-in config, validate `nginx -t`, reload |

## Key Variables

```yaml
# Gate variables
security_mode: enforce
nginx_hardening_enabled: true

# TLS
nginx_hardening_ssl_protocols: "TLSv1.2 TLSv1.3"
nginx_hardening_ssl_prefer_server_ciphers: "on"
nginx_hardening_ssl_session_tickets: "off"
nginx_hardening_generate_dhparam: true
nginx_hardening_dhparam_bits: 2048

# HSTS
nginx_hardening_hsts_enabled: true
nginx_hardening_hsts_max_age: 31536000
nginx_hardening_hsts_include_subdomains: true
nginx_hardening_hsts_preload: false      # Set true only for HSTS preload list submission

# Security headers
nginx_hardening_x_frame_options: "SAMEORIGIN"
nginx_hardening_csp: >-
  default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self' data:;
  font-src 'self'; frame-ancestors 'self'; form-action 'self'
nginx_hardening_referrer_policy: "strict-origin-when-cross-origin"
nginx_hardening_permissions_policy: "geolocation=(), microphone=(), camera=()"

# Rate/connection limiting
nginx_hardening_limit_req_zone: "binary_remote_addr zone=ratelimit:10m rate=10r/s"
nginx_hardening_limit_req_burst: 20
nginx_hardening_limit_conn_per_ip: 10

# Request limits
nginx_hardening_client_max_body_size: "10m"
nginx_hardening_large_client_header_buffers: "2 1k"
nginx_hardening_client_body_timeout: "10s"
nginx_hardening_client_header_timeout: "10s"
```

## Quick Start

```yaml
# Review mode — safe, read-only (skips if Nginx not installed)
- hosts: all
  roles:
    - role: malpanez.security.nginx_hardening

# Enforce mode
- hosts: web
  vars:
    security_mode: enforce
    nginx_hardening_enabled: true
  roles:
    - role: malpanez.security.nginx_hardening
```

## Drop-In Approach

The role writes **only** `/etc/nginx/conf.d/99-security-hardening.conf`. Your existing `nginx.conf` and virtual host configurations are never touched. To revert, delete that one file and reload Nginx.

The drop-in contains:
- Global `http {}` context directives: server_tokens, timeouts, buffers
- Limit zones for rate limiting and connection limiting
- Security header directives applied via `add_header`

> Per-vhost TLS certificates must be configured in your own server blocks. The drop-in sets global TLS hardening parameters inherited by all server blocks.

## Testing with Molecule

```bash
cd roles/nginx_hardening
molecule test
```

Tests verify: drop-in file exists, `server_tokens off` present, TLSv1 absent, HSTS header configured, `nginx -t` passes.

## Compliance Mapping

| Control | Framework |
|---------|-----------|
| TLS 1.2+ only | PCI-DSS 4.2.1, CIS Nginx 4.1, NIS2 Art.21(2)(h) |
| Security headers | OWASP Top 10 A05:2021, CIS Nginx 5.x |
| HSTS | PCI-DSS 4.2.1, CIS 4.1.14 |
| Rate limiting | OWASP A04, CIS Nginx 5.3 |
| Server info disclosure | CIS Nginx 2.5.1, PCI-DSS 6.2.4 |

## License

GPL-2.0-or-later
