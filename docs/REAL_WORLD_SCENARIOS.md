# Real-World Scenarios y Casos de Uso Comunes

## Escenarios Reales que Esta Colección Maneja

### 🔴 Problema 1: Sudoers Monolítico (90% de casos)

#### Situación Real
```bash
# La realidad en la mayoría de organizaciones
/etc/sudoers  # <-- TODO está aquí, sin /etc/sudoers.d/
```

**Características comunes:**
- ✅ Todo en un archivo `/etc/sudoers`
- ✅ Versionado en Git (si tienen suerte)
- ✅ Gestionado con Ansible/Puppet/Chef pero como archivo completo
- ❌ No usan `/etc/sudoers.d/` de forma modular
- ❌ Difícil de mantener (1000+ líneas)
- ❌ Cambios requieren editar todo el archivo

#### Cómo Esta Colección Lo Maneja

**Opción 1: Migración Gradual (Recomendado)**
```yaml
# playbook
- hosts: all
  become: true
  roles:
    - role: malpanez.security.sudoers_baseline
      vars:
        # Mantener /etc/sudoers existente
        sudoers_baseline_preserve_main: true
        # Solo agregar nuevos grupos en sudoers.d/
        sudoers_baseline_groups:
          linux_admins:
            require_password: true
            commands:
              - "/usr/bin/systemctl restart *"
```

Resultado:
```
/etc/sudoers           # <-- Archivo original intacto
/etc/sudoers.d/99-security  # <-- Solo nuevas reglas aquí
```

**Opción 2: Migración Completa**
```yaml
- hosts: all
  become: true
  tasks:
    # Paso 1: Backup del sudoers actual
    - name: Backup current sudoers
      copy:
        src: /etc/sudoers
        dest: /etc/sudoers.monolithic.backup
        remote_src: true

    # Paso 2: Aplicar baseline modular
    - include_role:
        name: malpanez.security.sudoers_baseline
      vars:
        sudoers_baseline_strict: true
```

**Opción 3: Hybrid (Mundo Real)**
```yaml
# Mantener reglas legacy en /etc/sudoers
# Agregar nuevas reglas en /etc/sudoers.d/

- hosts: all
  become: true
  roles:
    - role: malpanez.security.sudoers_baseline
      vars:
        # No tocar /etc/sudoers principal
        sudoers_baseline_manage_main_file: false
        # Solo gestionar sudoers.d/
        sudoers_baseline_groups:
          devops_team:
            require_password: false
            commands:
              - "/usr/bin/docker *"
              - "/usr/bin/systemctl restart myapp"
```

#### Validación Pre-Migración

```bash
# Script de validación
#!/bin/bash
# Verificar sintaxis ANTES de aplicar
visudo -cf /etc/sudoers
visudo -cf /etc/sudoers.d/99-security

# Test de acceso sudo
sudo -l -U devops_user

# Backup automático
cp /etc/sudoers /etc/sudoers.$(date +%Y%m%d_%H%M%S)
```

---

### 🔴 Problema 2: Múltiples Instancias SSH (Común en Segmentación)

#### Situación Real
```bash
# SSH por defecto para acceso normal
sshd (puerto 22)     → Usuarios normales, 2FA

# SSH para transfers SFTP
sshd (puerto 2222)   → Solo SFTP, cuentas de servicio

# SSH para conexiones externas (DMZ)
sshd (puerto 8443)   → Desde internet, solo keys
```

**Por qué se hace:**
- ✅ Segmentación de tráfico
- ✅ Diferentes políticas de seguridad por tipo de acceso
- ✅ Diferentes reglas de firewall
- ✅ Aislamiento de cuentas de servicio vs humanos
- ✅ Cumplimiento (ej: PCI-DSS requiere separación)

#### Cómo Esta Colección Lo Maneja

**Escenario: SSH Multi-Instancia**

```yaml
---
# playbooks/sshd-multi-instance.yml
- hosts: transfer_servers
  become: true
  tasks:
    # Instancia 1: SSH principal (puerto 22) - Usuarios humanos con MFA
    - name: Configure primary SSH for human access
      include_role:
        name: malpanez.security.sshd_hardening
      vars:
        sshd_hardening_instance_name: "primary"
        sshd_hardening_port: 22
        sshd_hardening_config_file: /etc/ssh/sshd_config
        sshd_hardening_service_name: sshd
        sshd_hardening_match_blocks:
          - name: "User *,!sftp*,!rsync*"
            directives:
              - "PasswordAuthentication no"
              - "PubkeyAuthentication yes"
              - "AuthenticationMethods publickey,keyboard-interactive"

    # Instancia 2: SSH SFTP (puerto 2222) - Solo transfers
    - name: Configure SFTP instance
      include_role:
        name: malpanez.security.sshd_hardening
      vars:
        sshd_hardening_instance_name: "sftp"
        sshd_hardening_port: 2222
        sshd_hardening_config_file: /etc/ssh/sshd_config_sftp
        sshd_hardening_service_name: sshd-sftp
        sshd_hardening_pid_file: /var/run/sshd-sftp.pid
        sshd_hardening_match_blocks:
          - name: "Group sftp-users"
            directives:
              - "ForceCommand internal-sftp"
              - "ChrootDirectory /srv/sftp/%u"
              - "PermitTTY no"
              - "X11Forwarding no"
              - "AllowTcpForwarding no"

    # Instancia 3: SSH DMZ (puerto 8443) - Acceso externo
    - name: Configure DMZ SSH instance
      include_role:
        name: malpanez.security.sshd_hardening
      vars:
        sshd_hardening_instance_name: "dmz"
        sshd_hardening_port: 8443
        sshd_hardening_config_file: /etc/ssh/sshd_config_dmz
        sshd_hardening_service_name: sshd-dmz
        sshd_hardening_pid_file: /var/run/sshd-dmz.pid
        sshd_hardening_strict_mode: true
        sshd_hardening_allowed_users:
          - "external-api"
          - "partner-sftp"
```

#### Configuración de Systemd para Multi-Instancia

```ini
# /etc/systemd/system/sshd-sftp.service
[Unit]
Description=OpenSSH SFTP Server (Port 2222)
After=network.target auditd.service
ConditionPathExists=!/etc/ssh/sshd_not_to_be_run

[Service]
Type=notify
ExecStart=/usr/sbin/sshd -D -f /etc/ssh/sshd_config_sftp
ExecReload=/bin/kill -HUP $MAINPID
KillMode=process
Restart=on-failure
RestartSec=42s

[Install]
WantedBy=multi-user.target
```

```ini
# /etc/systemd/system/sshd-dmz.service
[Unit]
Description=OpenSSH DMZ Server (Port 8443)
After=network.target auditd.service

[Service]
Type=notify
ExecStart=/usr/sbin/sshd -D -f /etc/ssh/sshd_config_dmz
ExecReload=/bin/kill -HUP $MAINPID
KillMode=process
Restart=on-failure
RestartSec=42s

[Install]
WantedBy=multi-user.target
```

#### Playbook Completo de Ejemplo

```yaml
---
# Ejemplo real: Servidor con 3 instancias SSH
- hosts: dmz_transfer_servers
  become: true
  vars:
    # Grupos de usuarios
    human_users:
      - alice
      - bob
    sftp_service_accounts:
      - sftp_backup
      - sftp_logs
    dmz_external_accounts:
      - partner_api

  tasks:
    # 1. Crear grupos
    - name: Create user groups
      group:
        name: "{{ item }}"
        state: present
      loop:
        - humans
        - sftp-users
        - dmz-users

    # 2. SSH Principal (22) - Humanos con MFA
    - include_role:
        name: malpanez.security.security_capabilities
    - include_role:
        name: malpanez.security.sshd_hardening
      vars:
        sshd_hardening_port: 22
        sshd_hardening_listen_address: "{{ internal_ip }}"
    - include_role:
        name: malpanez.security.pam_mfa
      vars:
        pam_mfa_enabled: true
        pam_mfa_service_accounts: "{{ sftp_service_accounts + dmz_external_accounts }}"

    # 3. SSH SFTP (2222) - Solo transfers, sin MFA
    - name: Configure SFTP instance
      template:
        src: sshd_config_sftp.j2
        dest: /etc/ssh/sshd_config_sftp
        validate: '/usr/sbin/sshd -t -f %s'
      notify: restart sshd-sftp

    - name: Create SFTP systemd service
      template:
        src: sshd-sftp.service.j2
        dest: /etc/systemd/system/sshd-sftp.service
      notify: reload systemd

    # 4. SSH DMZ (8443) - Solo keys, ultra restrictivo
    - name: Configure DMZ SSH instance
      template:
        src: sshd_config_dmz.j2
        dest: /etc/ssh/sshd_config_dmz
        validate: '/usr/sbin/sshd -t -f %s'
      notify: restart sshd-dmz

    # 5. Firewall rules
    - name: Configure firewall for multi-instance SSH
      firewalld:
        port: "{{ item.port }}/tcp"
        zone: "{{ item.zone }}"
        permanent: true
        state: enabled
      loop:
        - { port: 22, zone: internal }
        - { port: 2222, zone: transfer }
        - { port: 8443, zone: dmz }
      notify: reload firewalld

  handlers:
    - name: restart sshd-sftp
      systemd:
        name: sshd-sftp
        state: restarted
        daemon_reload: true

    - name: restart sshd-dmz
      systemd:
        name: sshd-dmz
        state: restarted
        daemon_reload: true

    - name: reload systemd
      systemd:
        daemon_reload: true

    - name: reload firewalld
      systemd:
        name: firewalld
        state: reloaded
```

---

### 🔴 Problema 3: Configuración SSH Existente (No Queremos Romper Nada)

#### Situación Real
```bash
# SSH configurado hace 5 años
# Tiene customizaciones que no recordamos por qué
# Funciona, no lo toques
```

#### Solución: Review Mode Primero

```yaml
- hosts: production
  become: true
  vars:
    # CRÍTICO: Modo review primero
    security_mode: review
  roles:
    - malpanez.security.sshd_hardening
    - malpanez.security.sudoers_baseline

# Resultado: Solo reporta diferencias, no cambia nada
```

Luego revisar en:
```
/tmp/security-review/
├── sshd_current.conf
├── sshd_proposed.conf
├── sshd_diff.txt
├── sudoers_current
├── sudoers_proposed
└── sudoers_diff.txt
```

---

## Casos de Uso por Industria

### Finanzas / PCI-DSS
```yaml
# Requisito: Separación de ambientes
- hosts: pci_scope
  vars:
    # SSH ultra restrictivo
    sshd_hardening_strict_mode: true
    # MFA obligatorio
    pam_mfa_enabled: true
    # Logging exhaustivo
    audit_logging_verbose: true
    # Evidencia para auditoría
    compliance_evidence_frameworks:
      - pci-dss
```

### Salud / HIPAA
```yaml
# Requisito: Auditoría de acceso
- hosts: hipaa_systems
  vars:
    # Logging de todos los comandos sudo
    sudoers_baseline_defaults:
      - "use_pty"
      - "logfile=/var/log/sudo.log"
      - "log_output"
      - "log_input"
```

### Gobierno / FedRAMP
```yaml
# Requisito: FIPS compliance
- hosts: fedramp_systems
  vars:
    sshd_hardening_fips_mode: true
    sshd_hardening_ciphers: "{{ fips_approved_ciphers }}"
```

---

## Estrategias de Adopción

### Nivel 1: Solo Auditoría (Sin Cambios)
```yaml
# Semana 1-2: Conocer el estado actual
- include_role:
    name: malpanez.security.compliance_evidence
  vars:
    security_mode: review
```

### Nivel 2: Nuevos Servidores Primero
```yaml
# Semana 3-4: Aplicar en servidores nuevos
- hosts: new_servers
  roles:
    - malpanez.security.sshd_hardening
    - malpanez.security.sudoers_baseline
```

### Nivel 3: Staging Environment
```yaml
# Semana 5-6: Probar en staging
- hosts: staging
  vars:
    security_mode: enforce
  roles:
    - malpanez.security.sshd_hardening
    - malpanez.security.pam_mfa
    - malpanez.security.sudoers_baseline
```

### Nivel 4: Producción Gradual
```yaml
# Semana 7+: Rollout gradual por grupos
- hosts: production_batch_1  # 10% servidores
  serial: 1  # Uno a uno
  max_fail_percentage: 0  # Stop si falla
  roles: [...]
```

---

## Troubleshooting Casos Comunes

### "Me bloqueé del servidor"
**Prevención:**
```yaml
# SIEMPRE en review primero
security_mode: review

# SIEMPRE mantener sesión SSH abierta
# SIEMPRE verificar acceso antes de cerrar última sesión
```

**Recuperación:**
```bash
# Opción 1: Console access (Cloud/VM)
# Opción 2: Single user mode
# Opción 3: Rescue disk

# Restaurar backup
cp /etc/sudoers.backup /etc/sudoers
cp /etc/pam.d/sshd.backup /etc/pam.d/sshd
systemctl restart sshd
```

### "Ansible no puede conectar después de aplicar"
**Causa común:** Service accounts sin bypass MFA

**Solución:**
```yaml
pam_mfa_service_accounts:
  - ansible  # <-- CRÍTICO
  - awx
  - jenkins
```

---

## Checklists de Validación

### Pre-Deployment
- [ ] Review mode ejecutado y revisado
- [ ] Backup de configuraciones actuales
- [ ] Sesión SSH de emergencia abierta
- [ ] Credenciales de console access disponibles
- [ ] Service accounts identificados
- [ ] Plan de rollback documentado

### Post-Deployment
- [ ] Acceso SSH funcionando
- [ ] sudo funcionando
- [ ] Ansible puede conectar
- [ ] Service accounts operativos
- [ ] Logs sin errores críticos
- [ ] MFA funcionando (si habilitado)

---

**Última Actualización:** 2025-12-05
**Mantenedor:** Miguel Alpañez
**Colección:** malpanez.security v1.0.0
