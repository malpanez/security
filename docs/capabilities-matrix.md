# Capabilities Matrix (SK keys vs PAM MFA vs Legacy)

| Requirement | MODE_A sk_keys | MODE_B pam_mfa | MODE_C legacy |
| --- | --- | --- | --- |
| OpenSSH server | >= 8.2 (ed25519-sk/ecdsa-sk) | any version | any version |
| MFA | optional (`security_capabilities_mfa_for_humans_even_with_sk_keys`) | mandatory (PAM) | no (compensating) |
| PAM modules | not required | pam_u2f/pam_fido2 (+ TOTP breakglass) | optional |
| Compatibility | modern | modern/legacy | legacy |

Auto-selection (`security_capabilities_auth_mode: auto`):
- If OpenSSH >= 8.2 => `sk_keys`
- Else if pam_u2f/pam_fido2 available => `pam_mfa`
- Else => `legacy`

Variables:
- `security_capabilities_auth_mode` (auto|sk_keys|pam_mfa|legacy)
- `security_capabilities_mfa_for_humans_even_with_sk_keys` (bool)
- `security_capabilities_force_openssh_version` / `security_capabilities_force_mode` (testing)

Caution: in legacy mode apply compensating controls (no password auth, restricted service accounts).
