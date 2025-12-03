# Capabilities Matrix (SK keys vs PAM MFA vs Legacy)

| Requisito | MODE_A sk_keys | MODE_B pam_mfa | MODE_C legacy |
| --- | --- | --- | --- |
| OpenSSH server | >= 8.2 (ed25519-sk/ecdsa-sk) | cualquier versión | cualquier versión |
| MFA | opcional (`security_capabilities_mfa_for_humans_even_with_sk_keys`) | obligatorio (PAM) | no (compensatorio) |
| PAM módulos | no requerido | pam_u2f/pam_fido2 (+ TOTP breakglass) | opcional |
| Compatibilidad | modernos | moderno/legacy | legacy |

Auto-selección (`security_capabilities_auth_mode: auto`):
- Si OpenSSH >= 8.2 => `sk_keys`
- Else si pam_u2f/pam_fido2 disponible => `pam_mfa`
- Else => `legacy`

Variables:
- `security_capabilities_auth_mode` (auto|sk_keys|pam_mfa|legacy)
- `security_capabilities_mfa_for_humans_even_with_sk_keys` (bool)
- `security_capabilities_force_openssh_version` / `security_capabilities_force_mode` (testing)

Precaución: en legacy aplicar controles compensatorios (sin password auth, service accounts restringidas).
