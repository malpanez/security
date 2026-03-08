# tomcat_hardening

Hardens Apache Tomcat and Red Hat JBoss Web Server (JWS) installations. Supports both package installs and tarball/manual installs via configurable paths. Skips gracefully if Tomcat is not installed.

Supports **review** mode (posture check) and **enforce** mode (applies changes).

## Platform Support

| Platform | Tomcat Source | Notes |
|----------|---------------|-------|
| All Linux platforms | Tarball install | Primary — configure `tomcat_hardening_catalina_home` |
| RHEL / Rocky / Alma | `tomcat` package or JBoss Web Server (JWS 5/6) | JWS typically in `/opt/rh/jws*/root` |
| Debian / Ubuntu | `tomcat9`, `tomcat10` package | Standard paths auto-detected |

Skips automatically if `tomcat_hardening_conf_dir` does not exist.

## What It Hardens

| Area | Action | Compliance |
|------|--------|------------|
| Shutdown port | Disabled (`port="-1"`) | CIS Tomcat 1.x |
| AJP connector | Disabled by default (CVE-2020-1938 Ghostcat) | CVE-2020-1938 |
| Default webapps | Remove ROOT, examples, docs, host-manager, manager | CIS Tomcat 4.x |
| Server info in errors | Removed via custom error pages | CIS Tomcat 6.x |
| TLS protocols | TLSv1.2 + TLSv1.3 only | PCI-DSS 4.2.1 |
| Cipher suites | ECDHE + CHACHA20 AEAD ciphers | PCI-DSS 4.2.1 |
| HTTP/2 | Enabled (Tomcat 9.0.13+) | Performance + security |
| HTTP TRACE | Disabled (`allowTrace="false"`) | OWASP |
| HSTS | `HttpHeaderSecurityFilter` in web.xml | PCI-DSS |
| X-Frame-Options | Anti-clickjacking filter | OWASP A05 |
| Content-Type sniffing | `blockContentTypeSniffing="true"` | OWASP A05 |
| XSS protection | `xssProtectionEnabled="true"` | Legacy browser defence |
| Session timeout | 30 minutes (configurable) | CIS Tomcat 10.x |
| Session cookies | `HttpOnly=true`, `Secure=true` | CIS Tomcat 10.x |
| Custom error pages | Redirect to `/error` — suppress version info | CIS Tomcat 6.x |
| Connection timeout | 20 seconds | CIS Tomcat 7.x |
| Conf dir permissions | `0750`, `tomcat:tomcat` owner | CIS Tomcat 2.x |
| Logs dir permissions | `0750`, `tomcat:tomcat` owner | CIS Tomcat 2.x |
| Access logging | Structured log with timing (`%D`) | PCI-DSS 10.x |

## Modes

| Mode | Behaviour |
|------|-----------|
| `review` (default) | Check AJP status, shutdown port, default webapps, permissions |
| `enforce` | Write `server.xml` + `web.xml`, remove default webapps, fix permissions, restart |

## Key Variables

```yaml
# Gate variables
security_mode: enforce
tomcat_hardening_enabled: true

# Installation paths — adjust for your install
tomcat_hardening_catalina_home: /opt/tomcat     # Tarball installs
tomcat_hardening_catalina_base: /opt/tomcat
tomcat_hardening_user: tomcat
tomcat_hardening_group: tomcat
tomcat_hardening_service_name: tomcat

# Shutdown port — -1 disables it (recommended)
tomcat_hardening_shutdown_port: -1
tomcat_hardening_shutdown_command: DISABLED

# Default webapps to remove
tomcat_hardening_remove_default_webapps:
  - ROOT
  - examples
  - docs
  - host-manager
  - manager

# Manager app — keep if needed for CI/CD deployments
tomcat_hardening_manager_enabled: false
tomcat_hardening_manager_allowed_ip: "127.0.0.1"

# AJP — disabled by default (Ghostcat CVE-2020-1938)
tomcat_hardening_ajp_enabled: false

# Connectors
tomcat_hardening_http_port: 8080
tomcat_hardening_https_port: 8443
tomcat_hardening_connection_timeout: 20000
tomcat_hardening_max_threads: 150
tomcat_hardening_allow_trace: false
tomcat_hardening_http2_enabled: true

# TLS
tomcat_hardening_ssl_enabled: true
tomcat_hardening_ssl_protocol: "TLSv1.2+TLSv1.3"
tomcat_hardening_ssl_certificate_file: /etc/pki/tls/certs/tomcat.crt
tomcat_hardening_ssl_certificate_key_file: /etc/pki/tls/private/tomcat.key

# Session security
tomcat_hardening_session_timeout: 30
tomcat_hardening_session_cookie_http_only: true
tomcat_hardening_session_cookie_secure: true

# Security headers
tomcat_hardening_hsts_enabled: true
tomcat_hardening_hsts_max_age: 31536000
tomcat_hardening_anti_click_jacking: true
tomcat_hardening_block_content_type_sniffing: true
```

## Quick Start

```yaml
# Review mode — safe, read-only (skips if Tomcat not found)
- hosts: all
  roles:
    - role: malpanez.security.tomcat_hardening

# Enforce mode — tarball install
- hosts: app
  vars:
    security_mode: enforce
    tomcat_hardening_enabled: true
    tomcat_hardening_catalina_home: /opt/tomcat
    tomcat_hardening_user: tomcat
    tomcat_hardening_service_name: tomcat
  roles:
    - role: malpanez.security.tomcat_hardening

# JBoss Web Server (RHEL JWS 6)
- hosts: app
  vars:
    security_mode: enforce
    tomcat_hardening_enabled: true
    tomcat_hardening_catalina_home: /opt/rh/jws6/root/usr/share/tomcat
    tomcat_hardening_service_name: jws6-tomcat
  roles:
    - role: malpanez.security.tomcat_hardening
```

## AJP and Ghostcat (CVE-2020-1938)

AJP is **disabled by default**. This mitigates CVE-2020-1938 (Ghostcat), a critical file read/include vulnerability scored CVSS 9.8, affecting all Tomcat versions before 9.0.31 / 8.5.51 / 7.0.100.

If AJP is required for Apache httpd `mod_proxy_ajp`:

```yaml
tomcat_hardening_ajp_enabled: true
tomcat_hardening_ajp_port: 8009
# The role sets requiredSecret and address="127.0.0.1" automatically
```

## Manager Application

Removed by default. To keep it for CI/CD deployments:

```yaml
tomcat_hardening_manager_enabled: true
tomcat_hardening_manager_allowed_ip: "10.0.0.0/8"
```

Access is restricted via `RemoteAddrValve` to the configured IP/CIDR.

## Testing with Molecule

```bash
cd roles/tomcat_hardening
molecule test
```

Tests verify: AJP disabled, shutdown port `-1`, default webapps absent, session cookie flags set, `server.xml` and `web.xml` correctly configured.

## Compliance Mapping

| Control | Framework |
|---------|-----------|
| Remove default webapps | CIS Tomcat 4.x, PCI-DSS 2.2.4 |
| Shutdown port disabled | CIS Tomcat 1.x |
| AJP disabled | CVE-2020-1938, CIS Tomcat 9.x |
| TLS 1.2+ only | PCI-DSS 4.2.1, NIS2 Art.21(2)(h) |
| Session security | CIS Tomcat 10.x, OWASP A07:2021 |
| Security headers | OWASP Top 10 A05:2021 |
| File permissions | CIS Tomcat 2.x, HIPAA §164.312(a) |
| Access logging | PCI-DSS 10.x, SOC2 CC7.2 |

## License

GPL-2.0-or-later
