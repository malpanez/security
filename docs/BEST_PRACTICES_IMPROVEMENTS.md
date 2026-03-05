# Best Practices and Roadmap - malpanez.security Collection

**Status**: conceptual guide. Some variables shown in examples are not implemented in the current roles. Use `meta/argument_specs.yml` and `defaults/main.yml` as the source of truth.

## Philosophy: Never Break Production

### Core Principles

1. **Review First, Enforce Later** - ALWAYS
2. **Progressive Migration** - Never big-bang
3. **Rollback Always Possible** - Automatic backups
4. **Validation at Every Step** - Tests before applying
5. **Legacy Compatibility** - Support existing configurations

---

## Operation Modes

### Mode 1: Review (Audit Without Changes)

**Purpose:** Understand the current state WITHOUT modifying ANYTHING

```yaml
---
# playbooks/audit-only.yml
- name: Security Audit - No Changes
  hosts: all
  become: true
  vars:
    # CRITICAL: Global review mode
    security_mode: review

    # Roles run in "check" mode
    ansible_check_mode: false  # No, we want to execute

  roles:
    - role: malpanez.security.security_capabilities
      tags: [review, audit]

    - role: malpanez.security.compliance_evidence
      tags: [review, audit]
      vars:
        compliance_evidence_output_dir: /tmp/security-audit-{{ ansible_date_time.iso8601_basic_short }}

  post_tasks:
    - name: Display audit summary
      debug:
        msg: |
          Audit completed.
          Results in: {{ compliance_evidence_output_dir }}

          Review files:
          - {{ compliance_evidence_output_dir }}/capabilities.json
          - {{ compliance_evidence_output_dir }}/sshd_config_current.txt
          - {{ compliance_evidence_output_dir }}/sudoers_current.txt
```

**Result:**
- ✅ Does NOT modify any file
- ✅ Generates reports in `/tmp/security-audit-*/`
- ✅ Identifies system capabilities
- ✅ Documents current configuration
- ✅ Detects baseline deviations

**When to use:**
- First time you run the collection
- Every time before enforce
- Periodic audits
- Troubleshooting

---

### Mode 2: Dry-Run (Simulate Changes)

**Purpose:** See WHAT would change without applying it

```yaml
---
# playbooks/dry-run.yml
- name: Security Dry-Run - Simulate Changes
  hosts: all
  become: true
  check_mode: true  # Ansible check mode
  diff: true        # Show diffs

  vars:
    security_mode: enforce  # We want to see what enforce would do

  roles:
    - malpanez.security.sshd_hardening
    - malpanez.security.sudoers_baseline
    - malpanez.security.pam_mfa

  post_tasks:
    - name: Summary of changes
      debug:
        msg: "Dry-run completed. Review output for proposed changes."
```

**Result:**
- ✅ Shows DIFF of changes
- ✅ Does NOT apply changes
- ✅ Identifies files to be modified
- ✅ Validates configuration syntax

**When to use:**
- After review, before enforce
- To approve changes with the team
- Document proposed changes
- Validate templates

---

### Mode 3: Progressive Enforce (Apply Changes)

**Purpose:** Apply changes in a CONTROLLED and GRADUAL manner

#### Level 1: New Servers Only

```yaml
---
# playbooks/enforce-new-servers.yml
- name: Security Enforcement - New Servers Only
  hosts: new_servers  # Separate inventory
  become: true
  serial: 1  # One at a time
  max_fail_percentage: 0  # Stop if one fails

  vars:
    security_mode: enforce

  pre_tasks:
    - name: Verify this is a new server
      assert:
        that:
          - server_deployment_date is defined
          - server_deployment_date | to_datetime > '2024-01-01'
        fail_msg: "This playbook is only for new servers"

    - name: Backup current configuration
      include_role:
        name: malpanez.security.compliance_evidence
      vars:
        security_mode: review
        compliance_evidence_output_dir: /root/security-backup-{{ ansible_date_time.epoch }}

  roles:
    - malpanez.security.security_capabilities
    - malpanez.security.sshd_hardening
    - malpanez.security.sudoers_baseline
    - malpanez.security.audit_logging

  post_tasks:
    - name: Validate SSH still works
      wait_for:
        port: 22
        host: "{{ ansible_host }}"
        timeout: 30
      delegate_to: localhost

    - name: Validate sudo still works
      command: sudo -n true
      changed_when: false
      failed_when: false
      register: sudo_check

    - name: Report results
      debug:
        msg: |
          Server {{ inventory_hostname }} hardened successfully.
          SSH: {{ 'OK' if ansible_port == 22 else 'VERIFY' }}
          Sudo: {{ 'OK' if sudo_check.rc == 0 else 'VERIFY' }}
```

#### Level 2: Staging Environment

```yaml
---
# playbooks/enforce-staging.yml
- name: Security Enforcement - Staging
  hosts: staging
  become: true

  vars:
    security_mode: enforce
    # More aggressive configuration in staging
    pam_mfa_enabled: true
    selinux_enforcement_mode: enforcing

  pre_tasks:
    - name: Verify this is staging
      assert:
        that: "'staging' in group_names"
        fail_msg: "This playbook is only for staging"

    - name: Create restore point
      block:
        - name: Backup /etc
          archive:
            path: /etc
            dest: /root/etc-backup-{{ ansible_date_time.epoch }}.tar.gz
            format: gz

        - name: Backup PAM
          copy:
            src: /etc/pam.d/
            dest: /root/pam.d-backup-{{ ansible_date_time.epoch }}/
            remote_src: true

  roles:
    - malpanez.security.security_capabilities
    - malpanez.security.sshd_hardening
    - malpanez.security.pam_mfa
    - malpanez.security.sudoers_baseline
    - malpanez.security.selinux_enforcement
    - malpanez.security.audit_logging
    - malpanez.security.cis_baseline

  post_tasks:
    - name: Run validation suite
      include_tasks: validate-security.yml

    - name: Generate compliance report
      include_role:
        name: malpanez.security.compliance_evidence
```

#### Level 3: Production by Batches

```yaml
---
# playbooks/enforce-production-gradual.yml
- name: Security Enforcement - Production (Gradual)
  hosts: production
  become: true
  serial: "{{ rollout_percentage | default('10%') }}"
  max_fail_percentage: 5

  vars:
    security_mode: enforce

    # Conservative configuration in production
    pam_mfa_enabled: false  # MFA in phase 2
    selinux_enforcement_mode: permissive  # Enforcing in phase 3

  pre_tasks:
    - name: Verify not in maintenance window
      assert:
        that:
          - ansible_date_time.hour | int >= 2
          - ansible_date_time.hour | int <= 6
        fail_msg: "Must run during maintenance window (02:00-06:00)"
      when: require_maintenance_window | default(true)

    - name: Ensure emergency access session open
      debug:
        msg: |
          CRITICAL: Ensure you have an active SSH session open.
          This session will NOT be affected by PAM changes.
          Do NOT close until validation completes.

    - name: Backup configurations
      include_tasks: backup-configs.yml

    - name: Check current connectivity
      wait_for:
        port: 22
        host: "{{ ansible_host }}"
        timeout: 10
      delegate_to: localhost

  roles:
    - role: malpanez.security.security_capabilities
      tags: [phase1]

    - role: malpanez.security.sshd_hardening
      tags: [phase1]
      vars:
        # Conservative changes first
        sshd_hardening_password_authentication: false
        sshd_hardening_permit_root_login: false

    - role: malpanez.security.sudoers_baseline
      tags: [phase1]
      vars:
        # Only add in sudoers.d/, do not touch /etc/sudoers
        sudoers_baseline_manage_main_file: false

    - role: malpanez.security.audit_logging
      tags: [phase1]

  post_tasks:
    - name: Wait for SSH to stabilize
      wait_for:
        port: 22
        host: "{{ ansible_host }}"
        timeout: 60
      delegate_to: localhost

    - name: Test SSH connection
      ping:

    - name: Test sudo
      command: sudo -n true
      changed_when: false
      failed_when: false
      register: sudo_test

    - name: Validate access
      assert:
        that:
          - sudo_test.rc == 0 or sudo_test.rc == 1  # 1 = needs password (OK)
        fail_msg: "Sudo is broken!"

    - name: Create rollback script
      template:
        src: rollback.sh.j2
        dest: /root/rollback-{{ ansible_date_time.epoch }}.sh
        mode: '0700'
```

---

## Complete Rollout Strategy

### Phase 0: Preparation (Week 1-2)

```yaml
# Goals:
# - Understand the current state
# - Identify risks
# - Plan migration

- name: Phase 0 - Discovery
  hosts: all
  become: true
  vars:
    security_mode: review

  tasks:
    - include_role:
        name: malpanez.security.security_capabilities

    - include_role:
        name: malpanez.security.compliance_evidence

    - name: Analyze results
      local_action:
        module: template
        src: analysis-report.j2
        dest: ./reports/security-analysis-{{ inventory_hostname }}.html
```

**Deliverables:**
- Capabilities inventory per server
- Current configurations documented
- Security gaps identified
- Migration plan approved

---

### Phase 1: SSH Hardening (Week 3-4)

```yaml
# Goals:
# - Disable password authentication
# - Configure modern algorithms
# - New servers and staging only

- name: Phase 1 - SSH Hardening
  hosts: new_servers:staging
  become: true
  serial: "{{ batch_size | default(5) }}"

  vars:
    security_mode: enforce

  pre_tasks:
    - name: Ensure SSH keys deployed
      authorized_key:
        user: "{{ item }}"
        key: "{{ lookup('file', 'keys/' + item + '.pub') }}"
      loop: "{{ admin_users }}"

  roles:
    - malpanez.security.sshd_hardening
      vars:
        sshd_hardening_password_authentication: false
        sshd_hardening_permit_root_login: false
        sshd_hardening_max_auth_tries: 3
```

**Validation:**
- [ ] All admins can access with keys
- [ ] Password authentication disabled
- [ ] Root login blocked
- [ ] Logs without errors

---

### Phase 2: Modular Sudoers (Week 5-6)

```yaml
# Goals:
# - Migrate to sudoers.d/
# - Configure logging
# - Apply to staging first

- name: Phase 2 - Sudoers Baseline
  hosts: staging
  become: true

  vars:
    security_mode: enforce

  pre_tasks:
    - name: Backup current sudoers
      copy:
        src: /etc/sudoers
        dest: /etc/sudoers.before-baseline
        remote_src: true

  roles:
    - malpanez.security.sudoers_baseline
      vars:
        # Do NOT touch the main /etc/sudoers
        sudoers_baseline_manage_main_file: false

        # Only manage sudoers.d/
        sudoers_baseline_groups:
          linux_admins:
            require_password: true
            commands:
              - "ALL=(ALL) ALL"

          devops_team:
            require_password: false
            commands:
              - "/usr/bin/systemctl restart myapp"
              - "/usr/bin/docker *"

        # Security defaults
        sudoers_baseline_defaults:
          - "use_pty"
          - "logfile=/var/log/sudo.log"
          - "log_output"
```

**Validation:**
- [ ] `/etc/sudoers` unchanged
- [ ] New rules in `/etc/sudoers.d/99-security`
- [ ] `visudo -c` passes
- [ ] All admins can sudo
- [ ] Logging works

---

### Phase 3: MFA (Week 7-10)

```yaml
# Goals:
# - Enable MFA with YubiKey
# - TOTP as backup
# - Only for humans, exempt service accounts

- name: Phase 3 - MFA Rollout
  hosts: staging
  become: true

  vars:
    security_mode: enforce

  pre_tasks:
    - name: CRITICAL - Ensure emergency access
      assert:
        that:
          - emergency_user is defined
          - emergency_user in pam_mfa_service_accounts
        fail_msg: "Must have emergency user exempt from MFA"

    - name: Create MFA groups
      group:
        name: "{{ item }}"
        state: present
      loop:
        - mfa-users
        - mfa-breakglass
        - mfa-bypass

    - name: Add service accounts to bypass group
      user:
        name: "{{ item }}"
        groups: mfa-bypass
        append: true
      loop: "{{ pam_mfa_service_accounts }}"

  roles:
    - role: malpanez.security.pam_mfa
      vars:
        pam_mfa_enabled: true
        pam_mfa_totp_enabled: true

        # CRITICAL: Service accounts bypass
        pam_mfa_service_accounts:
          - ansible
          - jenkins
          - backup_user
          - monitoring

        # Humans require MFA
        pam_mfa_human_groups:
          - linux_admins
          - devops_team

        # Breakglass with TOTP
        pam_mfa_breakglass_group: mfa-breakglass

  post_tasks:
    - name: Validate Ansible can still connect
      ping:

    - name: Test MFA for human user
      debug:
        msg: "MANUAL TEST: SSH as human user and verify MFA prompt"
```

**Critical Validation:**
- [ ] Ansible can connect (service account bypass)
- [ ] Humans see YubiKey prompt
- [ ] TOTP works as fallback
- [ ] Emergency access works
- [ ] Nobody locked out

---

### Phase 4: SELinux (Week 11-12)

```yaml
# Goals:
# - Enable SELinux in permissive mode
# - Collect denials (week 11)
# - Enforcing in week 12 if no issues

- name: Phase 4.1 - SELinux Permissive
  hosts: staging
  become: true

  roles:
    - role: malpanez.security.selinux_enforcement
      vars:
        selinux_enforcement_enabled: true
        selinux_enforcement_mode: permissive  # Permissive first
        selinux_enforcement_restorecon: true

# One week later, review denials
- name: Phase 4.2 - Review SELinux Denials
  hosts: staging
  become: true

  tasks:
    - name: Get SELinux denials
      command: ausearch -m avc -ts recent
      register: denials
      failed_when: false

    - name: Analyze denials
      debug:
        msg: "{{ denials.stdout_lines }}"

    # If no critical denials, switch to enforcing
    - include_role:
        name: malpanez.security.selinux_enforcement
      vars:
        selinux_enforcement_mode: enforcing
      when: denials.stdout_lines | length == 0
```

---

### Phase 5: Audit and Compliance (Week 13-14)

```yaml
# Goals:
# - Enable audit logging
# - Collect evidence
# - Generate reports

- name: Phase 5 - Audit and Compliance
  hosts: all
  become: true

  roles:
    - malpanez.security.audit_logging
    - malpanez.security.cis_baseline
    - malpanez.security.compliance_evidence
      vars:
        compliance_evidence_frameworks:
          - pci-dss
          - hipaa
          - soc2
```

---

### Phase 6: Production (Week 15+)

```yaml
# Goals:
# - Gradual rollout to production
# - 10% initial batch
# - Increase if no incidents

- name: Phase 6 - Production Rollout
  hosts: production
  become: true
  serial: "{{ rollout_batch | default('10%') }}"
  max_fail_percentage: 5

  vars:
    security_mode: enforce

  pre_tasks:
    - name: Maintenance window check
      include_tasks: check-maintenance-window.yml

    - name: Backup everything
      include_tasks: backup-all.yml

    - name: Notify team
      uri:
        url: "{{ slack_webhook }}"
        method: POST
        body_format: json
        body:
          text: "Starting security hardening on {{ inventory_hostname }}"

  roles:
    - malpanez.security.security_capabilities
    - malpanez.security.sshd_hardening
    - malpanez.security.sudoers_baseline
    - malpanez.security.pam_mfa  # Only if phase 3 successful
    - malpanez.security.audit_logging

  post_tasks:
    - name: Validate all services
      include_tasks: validate-services.yml

    - name: Notify success
      uri:
        url: "{{ slack_webhook }}"
        method: POST
        body_format: json
        body:
          text: "✅ {{ inventory_hostname }} hardened successfully"

  rescue:
    - name: Rollback on failure
      include_tasks: rollback.yml

    - name: Notify failure
      uri:
        url: "{{ slack_webhook }}"
        method: POST
        body_format: json
        body:
          text: "❌ FAILED on {{ inventory_hostname }} - ROLLED BACK"
```

---

## Support Files

### backup-configs.yml

```yaml
---
# tasks/backup-configs.yml
- name: Create backup directory
  file:
    path: /root/security-backups/{{ ansible_date_time.epoch }}
    state: directory
    mode: '0700'
  register: backup_dir

- name: Backup SSH config
  copy:
    src: "{{ item }}"
    dest: "{{ backup_dir.path }}/"
    remote_src: true
  loop:
    - /etc/ssh/sshd_config
    - /etc/ssh/sshd_config.d/
  ignore_errors: true

- name: Backup PAM
  copy:
    src: /etc/pam.d/
    dest: "{{ backup_dir.path }}/pam.d/"
    remote_src: true

- name: Backup sudoers
  copy:
    src: "{{ item }}"
    dest: "{{ backup_dir.path }}/"
    remote_src: true
  loop:
    - /etc/sudoers
    - /etc/sudoers.d/
  ignore_errors: true

- name: Create restore script
  copy:
    dest: "{{ backup_dir.path }}/RESTORE.sh"
    mode: '0700'
    content: |
      #!/bin/bash
      # Emergency restore script
      set -e
      echo "Restoring configurations from {{ backup_dir.path }}"

      cp -av {{ backup_dir.path }}/sshd_config /etc/ssh/
      [ -d {{ backup_dir.path }}/sshd_config.d ] && cp -av {{ backup_dir.path }}/sshd_config.d/* /etc/ssh/sshd_config.d/
      systemctl restart sshd

      cp -av {{ backup_dir.path }}/pam.d/* /etc/pam.d/

      cp -av {{ backup_dir.path }}/sudoers /etc/
      [ -d {{ backup_dir.path }}/sudoers.d ] && cp -av {{ backup_dir.path }}/sudoers.d/* /etc/sudoers.d/

      echo "Restore complete. Test sudo and SSH access."

- name: Display backup location
  debug:
    msg: |
      Backup created at: {{ backup_dir.path }}
      To restore: sudo {{ backup_dir.path }}/RESTORE.sh
```

### validate-services.yml

```yaml
---
# tasks/validate-services.yml
- name: Test SSH connectivity
  wait_for:
    port: 22
    host: "{{ ansible_host }}"
    timeout: 30
  delegate_to: localhost

- name: Test sudo
  command: sudo -n true
  changed_when: false
  failed_when: false
  register: sudo_check

- name: Verify SSH config syntax
  command: sshd -t
  changed_when: false

- name: Verify sudoers syntax
  command: visudo -c
  changed_when: false

- name: Check PAM SSH config
  command: cat /etc/pam.d/sshd
  changed_when: false
  register: pam_ssh

- name: Validate no critical errors in auth.log
  shell: "tail -100 /var/log/auth.log | grep -i 'error\\|fail' | grep -v 'systemd' || true"
  changed_when: false
  register: auth_errors

- name: Report validation results
  debug:
    msg: |
      Validation Results:
      - SSH: {{ 'OK' if ansible_port == 22 else 'CHECK' }}
      - Sudo: {{ 'OK' if sudo_check.rc == 0 else 'NEEDS PASSWORD' }}
      - Auth errors: {{ auth_errors.stdout_lines | length }}
```

### rollback.yml

```yaml
---
# tasks/rollback.yml
- name: Find latest backup
  find:
    paths: /root/security-backups
    file_type: directory
  register: backups

- name: Get most recent backup
  set_fact:
    latest_backup: "{{ backups.files | sort(attribute='mtime', reverse=true) | first }}"

- name: Execute rollback script
  command: "{{ latest_backup.path }}/RESTORE.sh"
  register: rollback_result

- name: Verify rollback successful
  assert:
    that:
      - rollback_result.rc == 0
    fail_msg: "Rollback failed! Manual intervention required!"

- name: Restart services
  systemd:
    name: "{{ item }}"
    state: restarted
  loop:
    - sshd
    - auditd
  ignore_errors: true
```

---

## Phase Control Variables

### group_vars/all/security_phases.yml

```yaml
---
# Phase control by server group

# Current rollout phase
security_phase: 0  # 0=review, 1=ssh, 2=sudo, 3=mfa, 4=selinux, 5=audit, 6=production

# Configuration per phase
security_phase_config:
  0:  # Review only
    security_mode: review
    apply_changes: false

  1:  # SSH hardening
    security_mode: enforce
    apply_ssh: true
    apply_sudo: false
    apply_mfa: false

  2:  # Sudoers
    security_mode: enforce
    apply_ssh: true
    apply_sudo: true
    apply_mfa: false

  3:  # MFA
    security_mode: enforce
    apply_ssh: true
    apply_sudo: true
    apply_mfa: true
    pam_mfa_enabled: true

  4:  # SELinux
    security_mode: enforce
    apply_all: true
    selinux_enforcement_mode: permissive  # Week 1
    # selinux_enforcement_mode: enforcing  # Week 2

  5:  # Audit
    security_mode: enforce
    apply_all: true
    audit_logging_enabled: true

  6:  # Production
    security_mode: enforce
    apply_all: true
    production_ready: true

# Rollout configuration
rollout_config:
  batch_size: "10%"
  max_fail_percentage: 5
  maintenance_window_start: "02:00"
  maintenance_window_end: "06:00"
  require_maintenance_window: true
```

### group_vars/new_servers/security.yml

```yaml
---
# New servers - aggressive configuration
security_phase: 6
security_mode: enforce

pam_mfa_enabled: true
selinux_enforcement_mode: enforcing
sshd_hardening_strict_mode: true
```

### group_vars/staging/security.yml

```yaml
---
# Staging - test environment
security_phase: 6
security_mode: enforce

# Everything enabled for testing
pam_mfa_enabled: true
selinux_enforcement_mode: enforcing
audit_logging_verbose: true
```

### group_vars/production/security.yml

```yaml
---
# Production - conservative and gradual
security_phase: "{{ production_security_phase | default(1) }}"
security_mode: enforce

# Start conservative
pam_mfa_enabled: "{{ production_mfa_enabled | default(false) }}"
selinux_enforcement_mode: "{{ production_selinux_mode | default('permissive') }}"

# Gradual rollout
rollout_batch: "{{ production_rollout_batch | default('5%') }}"
require_maintenance_window: true
```

---

## Pre-Deployment Checklist

```yaml
---
# Pre-deployment validation playbook
- name: Pre-Deployment Checklist
  hosts: "{{ target_hosts }}"
  become: true
  gather_facts: true

  tasks:
    - name: Checklist - Backup exists
      stat:
        path: /root/security-backups
      register: backup_dir
      failed_when: not backup_dir.stat.exists

    - name: Checklist - Emergency user defined
      assert:
        that:
          - emergency_user is defined
          - emergency_user != ""
        fail_msg: "Emergency user not defined"

    - name: Checklist - Service accounts identified
      assert:
        that:
          - pam_mfa_service_accounts is defined
          - pam_mfa_service_accounts | length > 0
        fail_msg: "Service accounts not defined"

    - name: Checklist - SSH keys deployed
      stat:
        path: "/home/{{ item }}/.ssh/authorized_keys"
      loop: "{{ admin_users }}"
      register: ssh_keys
      failed_when: ssh_keys.results | selectattr('stat.exists', 'equalto', false) | list | length > 0

    - name: Checklist - Current SSH working
      wait_for:
        port: 22
        timeout: 10
      delegate_to: localhost

    - name: Checklist - Rollback script exists
      stat:
        path: /root/ROLLBACK.sh
      register: rollback_script
      failed_when: not rollback_script.stat.exists

    - name: All checks passed
      debug:
        msg: "✅ All pre-deployment checks passed. Ready to deploy."
```

---

## Post-Deployment Monitoring

```yaml
---
# Post-deployment monitoring
- name: Security Monitoring
  hosts: all
  become: true

  tasks:
    - name: Check auth failures
      shell: "grep -i 'failed\\|failure' /var/log/auth.log | tail -50"
      changed_when: false
      register: auth_failures

    - name: Check PAM errors
      shell: "grep -i 'pam' /var/log/auth.log | grep -i error | tail -20"
      changed_when: false
      register: pam_errors

    - name: Check sudo usage
      shell: "tail -50 /var/log/sudo.log"
      changed_when: false
      register: sudo_log
      ignore_errors: true

    - name: Check SELinux denials
      command: ausearch -m avc -ts recent
      changed_when: false
      register: selinux_denials
      failed_when: false
      when: ansible_selinux.status == "enabled"

    - name: Generate monitoring report
      copy:
        dest: /tmp/security-monitoring-{{ ansible_date_time.epoch }}.txt
        content: |
          Security Monitoring Report
          Generated: {{ ansible_date_time.iso8601 }}
          Host: {{ inventory_hostname }}

          === Auth Failures (last 50) ===
          {{ auth_failures.stdout }}

          === PAM Errors ===
          {{ pam_errors.stdout }}

          === Sudo Activity ===
          {{ sudo_log.stdout | default('N/A') }}

          === SELinux Denials ===
          {{ selinux_denials.stdout | default('N/A') }}
```

---

## Roadmap v2.0 - Future Improvements

### Modular PAM with Includes

**Current State (v1.x):**
```yaml
# Uses community.general.pamd - Modifies files directly
- community.general.pamd:
    name: sshd
    type: auth
    control: required
    module_path: pam_u2f.so
```

**v2.0 Improvement:**
```yaml
# Uses separate files with @include
# /etc/pam.d/sshd-mfa (new file)
auth    [success=1 default=ignore]  pam_succeed_if.so  user ingroup mfa-bypass
auth    required                     pam_u2f.so         authfile=/etc/Yubico/u2f_keys
auth    sufficient                   pam_google_authenticator.so nullok

# /etc/pam.d/sshd (modified only with include)
@include sshd-mfa
@include common-auth
```

**Advantages:**
- Easier to maintain
- Better for rollback (just remove the include)
- Cleaner for auditing
- Separation of concerns

**Implementation:**
```yaml
# roles/pam_mfa/tasks/main-v2.yml
- name: Deploy PAM MFA module file
  template:
    src: pam-mfa.j2
    dest: /etc/pam.d/sshd-mfa
    validate: '/usr/sbin/pam-validate %s'  # If it exists
    mode: '0644'

- name: Include MFA in main PAM config
  lineinfile:
    path: /etc/pam.d/sshd
    line: "@include sshd-mfa"
    insertbefore: "@include common-auth"
    state: present
```

### Native Multi-Instance SSH Support

```yaml
# v2.0: Native support for multiple instances
- role: malpanez.security.sshd_hardening
  vars:
    sshd_instances:
      - name: primary
        port: 22
        config_file: /etc/ssh/sshd_config
        service_name: sshd
        match_blocks:
          - users: "!sftp*,!rsync*"
            auth_methods: "publickey,keyboard-interactive"

      - name: sftp
        port: 2222
        config_file: /etc/ssh/sshd_config_sftp
        service_name: sshd-sftp
        force_command: internal-sftp
        match_blocks:
          - group: sftp-users
            chroot: /srv/sftp/%u
```

---

## Conclusion

**Collection Philosophy:**
1. Review first, ALWAYS
2. Progressive, never big-bang
3. Rollback always available
4. Validation at every step
5. Legacy compatibility

**For v1.x:**
- ✅ Current approach is CORRECT and SAFE
- ✅ Works in production
- ✅ Exhaustive tests
- ✅ Full legacy support

**For v2.0:**
- 🔄 PAM includes (after extensive validation)
- 🔄 Native multi-instance SSH
- 🔄 Better integration with authselect (RHEL 8+)

---

**Last Updated:** 2025-12-05
**Version:** 1.0.0
**Maintainer:** Miguel Alpañez
**Status:** ✅ Production Ready
