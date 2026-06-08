# service_accounts_transfer

Creates and secures service accounts for SFTP and rsync file transfer operations. Each account is created with a non-interactive shell (`/usr/sbin/nologin`), restricted to a forced command (SFTP internal server or rrsync), and optionally confined to a chroot jail. SSH `authorized_keys` entries are generated with `restrict` options when operating in `sk_keys` or `pam_mfa` authentication modes.

## Platform Support

Debian, Ubuntu, RHEL, Rocky, Alma, SUSE, openSUSE — any platform with OpenSSH.

## What It Configures

| Area | Detail |
|------|--------|
| User creation | Non-interactive accounts with `nologin` shell |
| SFTP chroot | ChrootDirectory configured in SSH Match blocks |
| Forced commands | `internal-sftp` or `rrsync` with no shell escape |
| authorized_keys | Per-account keys with `restrict` option when MFA mode is active |
| SSH Match blocks | Per-account Match blocks injected into the sshd configuration |
| IP restrictions | Per-account `from=` restriction in authorized_keys |

## Role Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `security_mode` | `review` | Set to `enforce` to apply changes |
| `service_accounts_transfer_accounts` | See below | List of service account definitions |
| `service_accounts_transfer_authorized_keys` | `{}` | Dictionary of username to authorized_keys config |
| `service_accounts_transfer_force_command` | `true` | Enforce forced command for all accounts |

### Account definition keys

Each item in `service_accounts_transfer_accounts` supports these keys:

| Key | Required | Default | Description |
|-----|----------|---------|-------------|
| `name` | yes | — | Unix username |
| `shell` | no | `/usr/sbin/nologin` | Login shell |
| `home` | yes | — | Home directory path |
| `sftp_only` | no | `false` | Restrict to SFTP only |
| `rsync_only` | no | `false` | Restrict to rsync only |
| `chroot` | no | — | ChrootDirectory for SFTP |
| `allow_from` | no | `[]` | IP addresses/networks allowed to connect |
| `command` | no | — | Forced command (`internal-sftp` or path to rrsync) |
| `keys` | no | `[]` | SSH public keys for authorized_keys |
| `match_extra` | no | `[]` | Extra SSH Match block directives |

Default accounts:

```yaml
service_accounts_transfer_accounts:
  - name: sftp_svc
    shell: /usr/sbin/nologin
    home: /srv/sftp_svc
    sftp_only: true
    chroot: /srv/sftp_svc
    allow_from: []
    command: internal-sftp
    keys: []
    match_extra:
      - AuthorizedKeysFile .ssh/authorized_keys
  - name: rsync_svc
    shell: /usr/sbin/nologin
    home: /srv/rsync_svc
    rsync_only: true
    allow_from: []
    command: /usr/bin/rrsync /srv/rsync_svc
    keys: []
    match_extra: []
```

## Dependencies

None required. Optionally reads the following facts (defaults apply when absent):

- `security_capabilities_selected_auth_mode` (from `malpanez.security.security_capabilities`) — determines whether to add `restrict` to authorized_keys entries.
- `pam_mfa_service_bypass_allow_from` (from `malpanez.security.pam_mfa`) — used as fallback IP allowlist when per-account `allow_from` is empty.

Run `malpanez.security.security_capabilities` and `malpanez.security.pam_mfa` before this role for full functionality.

## Example Playbook

```yaml
# Deploy SFTP and rsync service accounts
- hosts: all
  vars:
    security_mode: enforce
    service_accounts_transfer_accounts:
      - name: backup_svc
        shell: /usr/sbin/nologin
        home: /srv/backup
        rsync_only: true
        allow_from:
          - 10.0.1.0/24
        command: /usr/bin/rrsync /srv/backup
        keys:
          - "ssh-ed25519 AAAA... backup@controller"
        match_extra: []
      - name: upload_svc
        shell: /usr/sbin/nologin
        home: /srv/upload
        sftp_only: true
        chroot: /srv/upload
        command: internal-sftp
        keys:
          - "ssh-ed25519 AAAA... upload@app01"
        match_extra:
          - AuthorizedKeysFile .ssh/authorized_keys
  roles:
    - role: malpanez.security.service_accounts_transfer
```

## Recommended Role Order

```yaml
roles:
  - malpanez.security.security_capabilities     # Detect SSH version, auth mode
  - malpanez.security.pam_mfa                   # Configure MFA (sets bypass IP list)
  - malpanez.security.service_accounts_transfer # Create accounts using above facts
  - malpanez.security.sshd_hardening            # Apply sshd Match blocks
```

## Compliance Mapping

| Control | Framework |
|---------|-----------|
| Non-interactive service accounts | CIS 5.5, NIST 800-53 AC-6 |
| Forced command restriction | CIS 5.2, NIST 800-53 AC-3 |
| SFTP chroot isolation | NIST 800-53 SC-3, NIS2 Art.21(2)(e) |
| Key-based auth only | CIS 5.2.8, NIST 800-53 IA-5(2) |
| Source IP restriction | NIST 800-53 AC-17(3), NIS2 Art.21 |

## License

Apache-2.0

## Author

Miguel Alpañez
