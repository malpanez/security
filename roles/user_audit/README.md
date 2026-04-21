# user_audit

Local user account audit and lockout enforcement. Reviews password expiry, inactive accounts, UID 0 duplicates, and service account shells. Enforces policy via `chage` and `usermod`. Supports review mode (audit-only) and enforce mode.

## Requirements

- Ansible >= 2.16
- Collection: `malpanez.security`

## Role Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `user_audit_enabled` | `false` | Gate variable. Set `true` with `security_mode: enforce` to apply enforcement tasks. Review tasks always run. |
| `user_audit_inactive_days` | `90` | Days since last login before an account is considered inactive. Accounts exceeding this are locked when `user_audit_lock_inactive: true`. |
| `user_audit_max_password_age` | `90` | Maximum days between password changes (`chage --maxdays`). PCI-DSS 8.3.6 requires ≤ 90 days. |
| `user_audit_min_password_age` | `1` | Minimum days between password changes (`chage --mindays`). Prevents immediate password cycling. |
| `user_audit_warn_days` | `14` | Days before password expiry to warn the user at login (`chage --warndays`). |
| `user_audit_lock_inactive` | `true` | When `true` and `user_audit_enabled: true`, lock accounts inactive beyond `user_audit_inactive_days`. |
| `user_audit_set_password_expiry` | `true` | When `true` and `user_audit_enabled: true`, apply password aging policy to accounts with no expiry set. |
| `user_audit_fix_service_shells` | `false` | When `true` and `user_audit_enabled: true`, change login shells of eligible service accounts to the OS nologin path. Opt-in only — shell changes are destructive. |
| `user_audit_skip_users` | `[root, halt, sync, shutdown]` | Usernames that enforce tasks will never modify. Excluded from locking, shell changes, and password expiry enforcement. |

## Example Playbook

```yaml
- name: Audit and enforce local user account policy
  hosts: all
  roles:
    - role: malpanez.security.user_audit
      vars:
        user_audit_enabled: true
        security_mode: enforce
        user_audit_inactive_days: 90
        user_audit_max_password_age: 90
```

## Compliance

| Framework | Controls |
|-----------|----------|
| SOC2 | CC6.2 — User access management, CC6.3 — User access removal |
| HIPAA | 164.308(a)(3) — Workforce clearance |
| PCI-DSS | 8.1.4 — Inactive account removal, 8.3.6 — Password age policy |
| NIS2 | Art. 21 — Access control |

## License

GPL-2.0-or-later

## Author

Miguel Alpañez
