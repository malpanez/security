# Runbook Debian 13: SSH solo claves + sudo con TOTP (YubiKey OATH)

## Variables iniciales

```
ADMIN_USER="<mi_usuario_admin>"
MFA_GROUP="mfa-required"
MFA_SECRET_BASE="/var/lib/pam-google-authenticator"
SSHD_DROPIN="/etc/ssh/sshd_config.d/20-auth-hardening.conf"
```

## Diagnostico (antes de tocar nada)

```
cat /etc/os-release
sshd -V
grep -E '^[[:space:]]*Include[[:space:]]+.*/sshd_config.d/\\*\\.conf' /etc/ssh/sshd_config
sshd -T | egrep -i 'passwordauthentication|kbdinteractiveauthentication|challengeresponseauthentication|authenticationmethods|pubkeyacceptedalgorithms'
ls -la /etc/ssh/sshd_config.d/
grep -n '' /etc/pam.d/sudo | sed -n '1,120p'
pam-auth-update --list
```

Mantener una sesion SSH abierta durante todo el cambio.

## Diseno (opciones)

1) Debian 13 limpio (recomendado): drop-in en `sshd_config.d` + sudo con substack `mfa-totp` + TOTP solo para grupo `mfa-required`. No toca `common-*`.
2) Global via pam-auth-update: habilita MFA en `common-auth` (afecta login/sshd). Solo si quieres MFA en todo el sistema.
3) Legacy: editar directamente `/etc/pam.d/sudo` sin substack (no recomendado).

Se elige Opcion 1 por aislamiento y menor riesgo de lockout.

## Implementacion manual (paso a paso)

### 1) Paquetes requeridos

```
apt-get update
apt-get install -y openssh-server libpam-google-authenticator yubikey-manager pamtester
```

### 2) SSH (solo claves publicas, preferencia FIDO2)

Crear drop-in en `SSHD_DROPIN`:

```
cat > "$SSHD_DROPIN" <<'EOF'
# Managed by policy
PasswordAuthentication no
ChallengeResponseAuthentication no
KbdInteractiveAuthentication no
AuthenticationMethods publickey
# Opcional (gradual): limitar a SK keys con Match/User/Group
# PubkeyAcceptedAlgorithms sk-ssh-ed25519@openssh.com,sk-ecdsa-sha2-nistp256@openssh.com
UsePAM yes
PermitRootLogin no
EOF
```

Validar y recargar:

```
sshd -t
systemctl reload ssh
```

### 3) PAM sudo con TOTP (substack)

Crear grupo MFA y directorios:

```
groupadd -f "$MFA_GROUP"
usermod -a -G "$MFA_GROUP" "$ADMIN_USER"
install -d -m 0700 -o root -g root "$MFA_SECRET_BASE"
install -d -m 0700 -o root -g root "$MFA_SECRET_BASE/$ADMIN_USER"
```

Crear substack `/etc/pam.d/mfa-totp`:

```
cat > /etc/pam.d/mfa-totp <<'EOF'
#%PAM-1.0
auth [success=1 default=ignore] pam_succeed_if.so user notingroup mfa-required
auth required pam_google_authenticator.so secret=/var/lib/pam-google-authenticator/%u/.google_authenticator user=root allowed_perm=0400
EOF
```

Incluir substack en sudo (antes de `common-auth`):

```
cp -a /etc/pam.d/sudo /etc/pam.d/sudo.backup.$(date +%s)
awk 'NR==1{print; print "auth    include    mfa-totp"; next}1' /etc/pam.d/sudo > /etc/pam.d/sudo.new
install -m 0644 /etc/pam.d/sudo.new /etc/pam.d/sudo
rm -f /etc/pam.d/sudo.new
```

### 4) Generar secreto TOTP (servidor)

Evita historiales:

```
set +o history
google-authenticator -t -f -r 3 -R 30 -W -s "$MFA_SECRET_BASE/$ADMIN_USER/.google_authenticator"
chown root:root "$MFA_SECRET_BASE/$ADMIN_USER/.google_authenticator"
chmod 0400 "$MFA_SECRET_BASE/$ADMIN_USER/.google_authenticator"
set -o history
```

### 5) Provisionar YubiKey OATH/TOTP

```
ykman oath accounts add --touch "sudo:$HOSTNAME:$ADMIN_USER"
ykman oath accounts list
ykman oath accounts code "sudo:$HOSTNAME:$ADMIN_USER"
ykman oath access change
```

Cuando `ykman` pida el secreto, pega el mismo secreto generado por `google-authenticator`. No lo escribas en linea de comandos.

## Implementacion con Ansible (recomendado)

```
ADMIN_USER="$ADMIN_USER" MFA_GROUP="$MFA_GROUP" ansible-playbook playbooks/debian13-auth-hardening.yml -i <tu_inventario>
```

Para habilitar faillock via pam-auth-update (opcional):

```
ansible-playbook playbooks/debian13-auth-hardening.yml -i <tu_inventario> \
  -e pam_mfa_enable_faillock=true
```

Para SK-only gradual por grupo humano:

```
ansible-playbook playbooks/debian13-auth-hardening.yml -i <tu_inventario> \
  -e sshd_hardening_human_pubkey_accepted_algorithms='["sk-ssh-ed25519@openssh.com","sk-ecdsa-sha2-nistp256@openssh.com"]'
```

## Verificacion

Antes:

```
sshd -T | egrep -i 'passwordauthentication|kbdinteractiveauthentication|authenticationmethods|pubkeyacceptedalgorithms'
grep -n "mfa-totp" /etc/pam.d/sudo
```

Despues (desde otra sesion):

```
ssh -o PreferredAuthentications=publickey -o PubkeyAcceptedAlgorithms=sk-ssh-ed25519@openssh.com <host>
sudo -k
sudo -v   # Debe pedir password local y codigo TOTP
```

## Rollback

```
cp -a /etc/pam.d/sudo.backup.* /etc/pam.d/sudo
rm -f /etc/pam.d/mfa-totp
rm -f "$SSHD_DROPIN"
sshd -t
systemctl reload ssh
```

## Gotchas

- Si `/etc/ssh/sshd_config` no incluye `sshd_config.d/*.conf`, el drop-in no aplica. Habilita Include antes.
- `pam-auth-update` puede alterar `common-auth`; no lo uses para MFA si solo quieres sudo.
- `pam_google_authenticator` requiere secreto en el servidor; no uses `nullok` para evitar bypass.
- Validar siempre `sshd -t` antes de recargar; mantener sesion activa.
