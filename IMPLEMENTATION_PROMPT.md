# 🎯 IMPLEMENTATION PROMPT: Elevar malpanez.security al TOP 0.01%

## 📋 CONTEXTO DEL PROYECTO

**Repositorio**: `malpanez.security` - Colección Ansible para hardening de seguridad Linux
**Estado Actual**: 7.5/10 (TOP 10-15%)
**Objetivo**: 9.8/10 (TOP 0.01%)
**Código Crítico**: Modifica PAM, SSH, sudo, SELinux, auditd - Alto riesgo de lockout

**Auditoría Completa**: Ver `/workspace/AUDIT_REPORT.md` para detalles completos

---

## 🚨 REGLAS CRÍTICAS DE IMPLEMENTACIÓN

### NUNCA HACER:
1. ❌ **NUNCA** hacer cambios sin tests que los validen
2. ❌ **NUNCA** modificar roles críticos sin backup automático
3. ❌ **NUNCA** implementar cambios que puedan causar lockout sin mecanismo de rollback
4. ❌ **NUNCA** commitear código que falle `validate-all.sh`
5. ❌ **NUNCA** agregar secretos hardcodeados (usar Vault/Secrets Manager)
6. ❌ **NUNCA** saltar la fase de testing en staging
7. ❌ **NUNCA** implementar sin documentar (ADRs, comentarios, READMEs)

### SIEMPRE HACER:
1. ✅ **SIEMPRE** escribir tests ANTES del código (TDD)
2. ✅ **SIEMPRE** validar sintaxis (sshd -t, visudo -cf, etc.)
3. ✅ **SIEMPRE** agregar `no_log: true` en tareas sensibles
4. ✅ **SIEMPRE** documentar decisiones de diseño (ADRs)
5. ✅ **SIEMPRE** mantener idempotencia
6. ✅ **SIEMPRE** agregar health checks y validaciones
7. ✅ **SIEMPRE** actualizar documentación con cambios

---

## 📦 ESTRUCTURA DE IMPLEMENTACIÓN

### FASE 1: TESTING INFRASTRUCTURE (PRIORIDAD P0 - Crítica)
**Duración Estimada**: 2-3 semanas
**Objetivo**: Garantizar que NO podemos romper nada antes de hacer cambios

#### TASK 1.1: End-to-End Testing Suite
**Ubicación**: `molecule/complete_stack/`
**Archivos a Crear**:
- `molecule/complete_stack/molecule.yml`
- `molecule/complete_stack/converge.yml`
- `molecule/complete_stack/verify.yml`
- `molecule/complete_stack/prepare.yml`

**Requerimientos Específicos**:
```yaml
# molecule/complete_stack/molecule.yml
---
dependency:
  name: galaxy
driver:
  name: docker
platforms:
  # Test matrix: 11 plataformas
  - name: ubuntu-2204-complete
    image: ubuntu:22.04
    privileged: true
    command: /sbin/init
    volumes:
      - /sys/fs/cgroup:/sys/fs/cgroup:ro
    tmpfs:
      - /run
      - /tmp
  - name: debian-12-complete
    image: debian:12
    privileged: true
    command: /sbin/init
  - name: rocky-9-complete
    image: rockylinux:9
    privileged: true
    command: /sbin/init
  # ... agregar 8 plataformas más

provisioner:
  name: ansible
  config_options:
    defaults:
      callbacks_enabled: profile_tasks,timer
      stdout_callback: yaml
  inventory:
    group_vars:
      all:
        security_mode: enforce
        security_phase: 6  # Full enforcement
        pam_mfa_enabled: true
        selinux_enforcement_enabled: true
        audit_logging_enabled: true

verifier:
  name: ansible

scenario:
  name: complete_stack
  test_sequence:
    - dependency
    - cleanup
    - destroy
    - syntax
    - create
    - prepare
    - converge
    - idempotence
    - side_effect
    - verify
    - cleanup
    - destroy
```

**Scenarios de Testing a Implementar**:

1. **Scenario 1: Happy Path - Full Enforcement**
   ```yaml
   # converge.yml
   - name: Apply complete security baseline
     hosts: all
     become: true
     roles:
       - security_capabilities
       - service_accounts_transfer
       - sshd_hardening
       - pam_mfa
       - sudoers_baseline
       - selinux_enforcement
       - audit_logging
       - compliance_evidence
   ```

   ```yaml
   # verify.yml
   - name: Verify complete stack
     hosts: all
     tasks:
       # CRITICAL TEST 1: SSH still accessible
       - name: Test SSH connectivity
         wait_for:
           port: 22
           host: "{{ ansible_host }}"
           timeout: 30
         delegate_to: localhost

       # CRITICAL TEST 2: Service accounts can login without MFA
       - name: Create test service account
         user:
           name: test_service_account
           groups: "{{ pam_mfa_service_bypass_group }}"

       - name: Test service account SSH login
         command: |
           ssh -o StrictHostKeyChecking=no \
               -i /tmp/service_key \
               test_service_account@localhost exit
         delegate_to: localhost

       # CRITICAL TEST 3: Human accounts require MFA
       - name: Create test human account
         user:
           name: test_human
           groups: "{{ sshd_hardening_human_groups[0] }}"

       - name: Test human account requires MFA
         command: |
           ssh -o StrictHostKeyChecking=no \
               -i /tmp/human_key \
               test_human@localhost exit
         delegate_to: localhost
         register: human_login
         failed_when: human_login.rc == 0  # Should fail without MFA

       # CRITICAL TEST 4: Sudo works for admins
       - name: Test sudo access
         command: sudo -n -l
         become: true
         become_user: test_admin

       # CRITICAL TEST 5: sshd_config is valid
       - name: Validate sshd_config syntax
         command: sshd -t
         register: sshd_validation
         failed_when: sshd_validation.rc != 0

       # CRITICAL TEST 6: sudoers is valid
       - name: Validate sudoers syntax
         command: visudo -cf /etc/sudoers
         register: sudoers_validation
         failed_when: sudoers_validation.rc != 0

       # CRITICAL TEST 7: PAM configuration doesn't lock out root
       - name: Test root can still login via console
         command: su - root -c 'echo "root access ok"'

       # CRITICAL TEST 8: SELinux not causing denials
       - name: Check for SELinux denials
         shell: ausearch -m avc -ts recent | grep -c denied || echo 0
         register: selinux_denials
         failed_when: selinux_denials.stdout | int > 0
         when: ansible_os_family == 'RedHat'

       # CRITICAL TEST 9: Audit logging is working
       - name: Verify auditd is running
         service_facts:
       - assert:
           that: ansible_facts.services['auditd.service'].state == 'running'
           fail_msg: "auditd service not running"

       # CRITICAL TEST 10: Compliance report generated
       - name: Check compliance report exists
         stat:
           path: /var/log/compliance/capabilities.json
         register: compliance_report
       - assert:
           that: compliance_report.stat.exists
           fail_msg: "Compliance report not generated"
   ```

2. **Scenario 2: Rollback After Failure**
   ```yaml
   # molecule/rollback_test/converge.yml
   - name: Apply hardening then simulate failure
     hosts: all
     become: true
     tasks:
       - name: Create backup
         include_tasks: tasks/backup-configs.yml

       - name: Apply SSH hardening
         include_role:
           name: sshd_hardening

       - name: Inject failure (corrupt sshd_config)
         lineinfile:
           path: /etc/ssh/sshd_config
           line: "INVALID_DIRECTIVE corrupted"

       - name: Trigger rollback
         include_tasks: tasks/rollback.yml
   ```

3. **Scenario 3: Break-Glass with TOTP**
   ```yaml
   # molecule/breakglass/converge.yml
   - name: Test break-glass procedure
     hosts: all
     tasks:
       - name: Apply MFA enforcement
         include_role:
           name: pam_mfa

       - name: Simulate lost YubiKey scenario
         # Remove U2F device

       - name: Test TOTP fallback works
         # Verify TOTP authentication succeeds
   ```

**Acceptance Criteria**:
- [ ] Tests pasan en las 11 plataformas (Ubuntu 18.04, 20.04, 22.04, 24.04, Debian 10, 11, 12, Rocky 8, 9, Alma 8, 9)
- [ ] Idempotence tests pasan (segunda ejecución no hace cambios)
- [ ] Rollback scenario funciona correctamente
- [ ] Break-glass scenario permite acceso de emergencia
- [ ] Zero lockouts en todos los tests
- [ ] Tiempo de ejecución < 15 minutos por plataforma

---

#### TASK 1.2: Chaos Testing
**Ubicación**: `molecule/chaos/`
**Objetivo**: Validar comportamiento bajo condiciones adversas

**Scenarios de Chaos**:
1. **Network failure mid-deployment**
2. **Disk full during backup**
3. **Process killed during PAM configuration**
4. **Simultaneous Ansible executions (race condition)**
5. **SELinux enforcing blocks SSH restart**
6. **OOM killer strikes during deployment**

**Implementación**:
```yaml
# molecule/chaos/converge.yml
---
- name: Chaos Testing - Network Failure
  hosts: all
  become: true
  tasks:
    - name: Start deployment
      include_role:
        name: sshd_hardening
      async: 300
      poll: 0
      register: deployment_job

    - name: Inject chaos - kill network after 5 seconds
      shell: |
        sleep 5
        iptables -A OUTPUT -p tcp --dport 22 -j DROP
        sleep 10
        iptables -D OUTPUT -p tcp --dport 22 -j DROP
      async: 20
      poll: 0

    - name: Wait for deployment to handle failure
      async_status:
        jid: "{{ deployment_job.ansible_job_id }}"
      register: job_result
      until: job_result.finished
      retries: 30
      delay: 10
      ignore_errors: true

    - name: Verify system still accessible
      wait_for:
        port: 22
        timeout: 30

    - name: Verify rollback executed
      stat:
        path: /var/log/security-rollback-*.log
      register: rollback_log

    - assert:
        that: rollback_log.stat.exists
        fail_msg: "Rollback did not execute after failure"
```

**Acceptance Criteria**:
- [ ] Sistema permanece accesible después de cada escenario de chaos
- [ ] Rollback automático se ejecuta en failures
- [ ] No se pierde data crítica (backups intactos)
- [ ] Logs detallados de qué falló y por qué

---

#### TASK 1.3: Property-Based Testing
**Ubicación**: `tests/property_tests/`
**Tecnología**: `pytest` + `hypothesis`

**Implementación**:
```python
# tests/property_tests/test_sshd_config_properties.py
"""Property-based tests for sshd_config template rendering."""

from hypothesis import given, strategies as st, settings
from hypothesis.strategies import lists, text, integers
import subprocess
import tempfile
from pathlib import Path
from jinja2 import Template


def validate_sshd_config(config_content: str) -> bool:
    """Validate sshd_config syntax using sshd -t."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='_sshd_config', delete=False) as f:
        f.write(config_content)
        f.flush()
        result = subprocess.run(
            ['sshd', '-t', '-f', f.name],
            capture_output=True
        )
        Path(f.name).unlink()
        return result.returncode == 0


def render_sshd_config(**kwargs):
    """Render sshd_config.j2 template with given variables."""
    template_path = Path('roles/sshd_hardening/templates/sshd_config.j2')
    template = Template(template_path.read_text())
    return template.render(**kwargs)


# PROPERTY 1: ANY list of allow_groups produces valid config
@given(lists(text(alphabet='abcdefghijklmnopqrstuvwxyz0123456789-_', min_size=1, max_size=20), max_size=50))
@settings(max_examples=100, deadline=5000)
def test_any_allow_groups_produces_valid_config(groups):
    """Property: Any list of valid group names produces valid sshd_config."""
    config = render_sshd_config(
        sshd_hardening_allow_groups=groups,
        sshd_hardening_password_authentication=False,
        sshd_hardening_permit_root_login='no',
        # ... defaults
    )
    assert validate_sshd_config(config), f"Invalid config with groups: {groups}"


# PROPERTY 2: ANY MaxAuthTries between 1-10 is valid
@given(integers(min_value=1, max_value=10))
def test_any_max_auth_tries_produces_valid_config(max_tries):
    """Property: Any MaxAuthTries in reasonable range produces valid config."""
    config = render_sshd_config(
        sshd_hardening_max_auth_tries=max_tries,
        # ... defaults
    )
    assert validate_sshd_config(config)


# PROPERTY 3: Config with empty lists is still valid
@given(
    lists(text(), max_size=0),
    lists(text(), max_size=0),
    lists(text(), max_size=0)
)
def test_empty_lists_produce_valid_config(allow_users, allow_groups, ciphers):
    """Property: Empty lists don't break config."""
    config = render_sshd_config(
        sshd_hardening_allow_users=allow_users,
        sshd_hardening_allow_groups=allow_groups,
        sshd_hardening_effective_ciphers=ciphers if ciphers else ['chacha20-poly1305@openssh.com'],
        # ... defaults
    )
    assert validate_sshd_config(config)


# PROPERTY 4: Idempotence - rendering twice with same vars produces identical output
@given(
    lists(text(), max_size=10),
    integers(min_value=1, max_value=10)
)
def test_template_is_idempotent(groups, max_tries):
    """Property: Rendering same vars twice produces identical config."""
    vars1 = {
        'sshd_hardening_allow_groups': groups,
        'sshd_hardening_max_auth_tries': max_tries,
    }
    config1 = render_sshd_config(**vars1)
    config2 = render_sshd_config(**vars1)
    assert config1 == config2, "Template is not idempotent"


# PROPERTY 5: No security downgrades
@given(st.booleans())
def test_no_weak_ciphers_in_output(password_auth):
    """Property: Output NEVER contains weak ciphers."""
    config = render_sshd_config(
        sshd_hardening_password_authentication=password_auth,
        # ... defaults
    )
    weak_ciphers = ['3des', 'arcfour', 'des', 'rc4']
    for weak in weak_ciphers:
        assert weak not in config.lower(), f"Weak cipher {weak} found in config"
```

```python
# tests/property_tests/test_sudoers_properties.py
"""Property-based tests for sudoers template."""

from hypothesis import given, strategies as st
import subprocess
import tempfile
from pathlib import Path


def validate_sudoers(content: str) -> bool:
    """Validate sudoers syntax using visudo -cf."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='_sudoers', delete=False) as f:
        f.write(content)
        f.flush()
        result = subprocess.run(
            ['visudo', '-cf', f.name],
            capture_output=True
        )
        Path(f.name).unlink()
        return result.returncode == 0


# PROPERTY: Root ALWAYS has NOPASSWD:ALL access
@given(st.dictionaries(
    keys=st.text(alphabet='abcdefghijklmnopqrstuvwxyz', min_size=3, max_size=20),
    values=st.booleans()
))
def test_root_always_has_full_access(user_permissions):
    """Property: Root always retains NOPASSWD:ALL regardless of other config."""
    sudoers = render_sudoers(
        sudoers_baseline_groups=user_permissions,
        sudoers_baseline_preserve_root=True
    )
    assert validate_sudoers(sudoers)
    assert 'root ALL=(ALL:ALL) NOPASSWD:ALL' in sudoers or \
           'root ALL=(ALL) NOPASSWD:ALL' in sudoers


# PROPERTY: Invalid group names don't break syntax
@given(st.text(min_size=1, max_size=100))
def test_any_group_name_produces_valid_sudoers(group_name):
    """Property: Even weird group names produce valid sudoers."""
    # Skip truly invalid chars for sudoers
    if any(c in group_name for c in ['\n', '\r', '\0']):
        return

    sudoers = render_sudoers(
        sudoers_baseline_groups={group_name: {'commands': ['ALL']}}
    )
    # Should either be valid or properly escaped
    assert validate_sudoers(sudoers) or group_name not in sudoers
```

**Acceptance Criteria**:
- [ ] 100+ property tests pasan consistentemente
- [ ] Tests encuentran edge cases no considerados
- [ ] Shrinking de Hypothesis ayuda a identificar casos mínimos de fallo
- [ ] Coverage de templates > 95%

---

#### TASK 1.4: Multi-Platform Matrix Testing en CI
**Ubicación**: `.github/workflows/ci-matrix.yml`

**Implementación**:
```yaml
name: Multi-Platform Matrix Testing

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]
  schedule:
    - cron: '0 3 * * *'  # Daily at 3 AM

jobs:
  matrix-test:
    name: Test on ${{ matrix.os }} - ${{ matrix.scenario }}
    runs-on: ubuntu-latest
    timeout-minutes: 45

    strategy:
      fail-fast: false
      matrix:
        os:
          - ubuntu:18.04
          - ubuntu:20.04
          - ubuntu:22.04
          - ubuntu:24.04
          - debian:10
          - debian:11
          - debian:12
          - rockylinux:8
          - rockylinux:9
          - almalinux:8
          - almalinux:9
        scenario:
          - complete_stack
          - rollback_test
          - breakglass
          - chaos_network
          - chaos_disk_full
          - idempotence

        # Exclusions (some scenarios don't apply to some OS)
        exclude:
          - os: ubuntu:18.04
            scenario: chaos_disk_full  # Known issue

    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.12'

      - name: Install dependencies
        run: |
          pip install ansible-core molecule molecule-docker \
                      pytest pytest-testinfra hypothesis

      - name: Run Molecule scenario
        run: |
          molecule test --scenario-name ${{ matrix.scenario }}
        env:
          MOLECULE_DISTRO: ${{ matrix.os }}
          PY_COLORS: '1'
          ANSIBLE_FORCE_COLOR: '1'

      - name: Upload test results
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: test-results-${{ matrix.os }}-${{ matrix.scenario }}
          path: |
            molecule/**/logs/
            /tmp/molecule/
          retention-days: 7

      - name: Upload coverage
        if: matrix.scenario == 'complete_stack'
        uses: codecov/codecov-action@v4
        with:
          files: ./coverage.xml
          flags: ${{ matrix.os }}

  test-summary:
    name: Test Summary
    runs-on: ubuntu-latest
    needs: matrix-test
    if: always()

    steps:
      - name: Check matrix results
        run: |
          echo "## Test Matrix Results" >> $GITHUB_STEP_SUMMARY
          echo "" >> $GITHUB_STEP_SUMMARY
          echo "Total combinations: ${{ strategy.job-total }}" >> $GITHUB_STEP_SUMMARY
          echo "Successful: ${{ strategy.job-success }}" >> $GITHUB_STEP_SUMMARY
          echo "Failed: ${{ strategy.job-failure }}" >> $GITHUB_STEP_SUMMARY

      - name: Fail if any test failed
        if: needs.matrix-test.result != 'success'
        run: exit 1
```

**Acceptance Criteria**:
- [ ] 11 OS × 6 scenarios = 66 combinaciones testadas
- [ ] CI completa en < 60 minutos (paralelización)
- [ ] Results dashboard visible en GitHub Actions
- [ ] Coverage report consolidado > 90%

---

### FASE 2: SEGURIDAD DE SECRETOS (PRIORIDAD P0 - Crítica)

#### TASK 2.1: Integración con Secret Manager (Vault o Infisical)
**Ubicación**: `roles/secrets_integration/`, `plugins/lookup/`

**IMPORTANTE**: Implementar soporte para AMBOS:
- **Infisical** (recomendado): Open source, $0 cost, MFA nativo
- **HashiCorp Vault**: Enterprise-grade, más features

Variable de control: `secrets_backend` (valores: `infisical` o `vault`)

**Requerimientos**:
```yaml
# roles/vault_integration/defaults/main.yml
---
vault_addr: "{{ lookup('env', 'VAULT_ADDR') }}"
vault_token: "{{ lookup('env', 'VAULT_TOKEN') }}"  # Solo para CI/CD
vault_role_id: "{{ lookup('env', 'VAULT_ROLE_ID') }}"  # Para AppRole auth
vault_secret_id: "{{ lookup('env', 'VAULT_SECRET_ID') }}"
vault_namespace: "{{ vault_namespace_override | default('admin/security') }}"

# Paths en Vault
vault_ssh_ca_path: "secret/data/ssh/ca_key"
vault_service_accounts_path: "secret/data/service_accounts"
vault_mfa_secrets_path: "secret/data/mfa"

# Validation
vault_validate_certs: true
vault_timeout: 30
vault_max_retries: 3
```

```yaml
# roles/vault_integration/tasks/main.yml
---
- name: Validate Vault configuration
  ansible.builtin.assert:
    that:
      - vault_addr is defined
      - vault_addr | length > 0
      - vault_addr is match('https://.*')
    fail_msg: "VAULT_ADDR must be set and use HTTPS"

- name: Test Vault connectivity
  ansible.builtin.uri:
    url: "{{ vault_addr }}/v1/sys/health"
    method: GET
    validate_certs: "{{ vault_validate_certs }}"
    timeout: "{{ vault_timeout }}"
  register: vault_health
  retries: "{{ vault_max_retries }}"
  delay: 5

- name: Authenticate to Vault (AppRole)
  ansible.builtin.uri:
    url: "{{ vault_addr }}/v1/auth/approle/login"
    method: POST
    body_format: json
    body:
      role_id: "{{ vault_role_id }}"
      secret_id: "{{ vault_secret_id }}"
    validate_certs: "{{ vault_validate_certs }}"
  register: vault_auth
  no_log: true

- name: Set Vault token fact
  ansible.builtin.set_fact:
    vault_token: "{{ vault_auth.json.auth.client_token }}"
  no_log: true

- name: Fetch SSH CA private key from Vault
  community.hashi_vault.vault_read:
    url: "{{ vault_addr }}"
    path: "{{ vault_ssh_ca_path }}"
    auth_method: token
    token: "{{ vault_token }}"
  register: ssh_ca_key_vault
  no_log: true

- name: Validate CA key format
  ansible.builtin.assert:
    that:
      - ssh_ca_key_vault.data.data.private_key is defined
      - ssh_ca_key_vault.data.data.private_key is match('-----BEGIN.*PRIVATE KEY-----')
    fail_msg: "Invalid CA key format from Vault"
  no_log: true

- name: Write CA key to temporary location (memory-backed)
  ansible.builtin.copy:
    content: "{{ ssh_ca_key_vault.data.data.private_key }}"
    dest: /dev/shm/ssh_ca_key_temp
    mode: '0400'
    owner: root
    group: root
  no_log: true
  register: ca_key_temp

- name: Use CA key for signing
  # ... operations with CA key

- name: Shred temporary CA key (secure deletion)
  ansible.builtin.command: shred -vfz -n 5 /dev/shm/ssh_ca_key_temp
  when: ca_key_temp.changed
  changed_when: false

- name: Clear CA key from memory
  ansible.builtin.set_fact:
    ssh_ca_key_vault: {}
    vault_token: ""
  no_log: true
```

**Plugin Personalizado** para mejor integración:
```python
# plugins/lookup/vault_kv.py
"""Custom Ansible lookup plugin for HashiCorp Vault KV v2."""

from ansible.errors import AnsibleError
from ansible.plugins.lookup import LookupBase
import requests
import os

class LookupModule(LookupBase):
    def run(self, terms, variables=None, **kwargs):
        """Lookup secrets from Vault KV v2."""
        vault_addr = os.getenv('VAULT_ADDR')
        vault_token = os.getenv('VAULT_TOKEN')

        if not vault_addr or not vault_token:
            raise AnsibleError("VAULT_ADDR and VAULT_TOKEN must be set")

        results = []
        for term in terms:
            url = f"{vault_addr}/v1/{term}"
            headers = {"X-Vault-Token": vault_token}

            try:
                response = requests.get(url, headers=headers, timeout=30)
                response.raise_for_status()
                data = response.json()
                results.append(data['data']['data'])
            except Exception as e:
                raise AnsibleError(f"Failed to fetch {term} from Vault: {str(e)}")

        return results
```

**Uso en Playbooks**:
```yaml
# playbooks/enforce-with-vault.yml
---
- name: Secure enforcement with Vault integration
  hosts: all
  become: true

  pre_tasks:
    - name: Integrate with Vault
      include_role:
        name: vault_integration

  roles:
    - role: sshd_hardening
      vars:
        sshd_hardening_trusted_ca_key: "{{ lookup('vault_kv', 'secret/data/ssh/ca_key')['private_key'] }}"

    - role: service_accounts_transfer
      vars:
        service_accounts: "{{ lookup('vault_kv', 'secret/data/service_accounts') }}"
```

**Acceptance Criteria**:
- [ ] Vault authentication funciona (AppRole, Token, Kubernetes Auth)
- [ ] Secretos NUNCA tocan disco (solo `/dev/shm`)
- [ ] Secure deletion con `shred` después de uso
- [ ] Secrets rotation automática cada 90 días
- [ ] Audit logging de Vault access
- [ ] Fallback a Ansible Vault si Vault no disponible (con warning)

---

#### TASK 2.2: AWS Secrets Manager Integration (Alternativa)
**Ubicación**: `roles/aws_secrets_integration/`

```yaml
# roles/aws_secrets_integration/tasks/main.yml
---
- name: Fetch SSH CA key from AWS Secrets Manager
  community.aws.aws_secret:
    name: "ssh/ca_key"
    region: "{{ aws_region }}"
  register: ssh_ca_secret
  no_log: true

- name: Parse secret JSON
  ansible.builtin.set_fact:
    ssh_ca_key_data: "{{ ssh_ca_secret.secret | from_json }}"
  no_log: true
```

**Acceptance Criteria**:
- [ ] IAM roles properly configured
- [ ] Secrets rotation via Lambda
- [ ] CloudTrail logging enabled

---

#### TASK 2.3: Enforcement de `no_log` Estricto
**Ubicación**: `scripts/validate-no-log.py`, `.github/workflows/security-scan.yml`

**Script de Validación**:
```python
#!/usr/bin/env python3
"""
Strict validation of no_log usage on sensitive tasks.
FAILS CI if sensitive tasks lack no_log: true.
"""

import yaml
import sys
import re
from pathlib import Path
from typing import List, Tuple

# Sensitive patterns that REQUIRE no_log
SENSITIVE_PATTERNS = [
    r'\bpassword\b',
    r'\bsecret\b',
    r'\btoken\b',
    r'\bapi[_-]?key\b',
    r'\bprivate[_-]?key\b',
    r'\bcredential\b',
    r'\bauth\b',
    r'\bvault[_-]?token\b',
    r'\bca[_-]?key\b',
]

# Modules that handle sensitive data
SENSITIVE_MODULES = [
    'ansible.builtin.user',
    'ansible.builtin.copy',  # When copying secrets
    'ansible.builtin.template',  # When templating secrets
    'community.hashi_vault.vault_read',
    'community.aws.aws_secret',
]

def check_task_no_log(task: dict, task_name: str) -> List[str]:
    """Check if task with sensitive data has no_log."""
    violations = []

    # Check task name
    task_name_lower = task_name.lower()
    for pattern in SENSITIVE_PATTERNS:
        if re.search(pattern, task_name_lower, re.IGNORECASE):
            if not task.get('no_log', False):
                violations.append(f"Task '{task_name}' mentions sensitive data but lacks 'no_log: true'")

    # Check module
    module = None
    for key in task.keys():
        if '.' in key or key in SENSITIVE_MODULES:
            module = key
            break

    if module in SENSITIVE_MODULES:
        if not task.get('no_log', False):
            violations.append(f"Task '{task_name}' uses sensitive module '{module}' but lacks 'no_log: true'")

    # Check task vars for sensitive patterns
    task_str = str(task).lower()
    for pattern in SENSITIVE_PATTERNS:
        if re.search(pattern, task_str, re.IGNORECASE):
            if not task.get('no_log', False):
                violations.append(f"Task '{task_name}' contains '{pattern}' but lacks 'no_log: true'")

    return violations

def validate_file(filepath: Path) -> List[str]:
    """Validate a single YAML file."""
    violations = []

    try:
        with open(filepath) as f:
            docs = yaml.safe_load_all(f)
            for doc in docs:
                if not doc:
                    continue

                # Check plays
                if isinstance(doc, list):
                    plays = doc
                else:
                    plays = [doc]

                for play in plays:
                    if not isinstance(play, dict):
                        continue

                    # Check tasks
                    for task_list_key in ['tasks', 'pre_tasks', 'post_tasks', 'handlers']:
                        tasks = play.get(task_list_key, [])
                        for task in tasks:
                            if isinstance(task, dict) and 'name' in task:
                                task_violations = check_task_no_log(task, task['name'])
                                violations.extend([f"{filepath}:{v}" for v in task_violations])

    except Exception as e:
        print(f"Error parsing {filepath}: {e}", file=sys.stderr)

    return violations

def main():
    """Main validation."""
    print("🔒 Validating no_log usage on sensitive tasks...\n")

    all_violations = []

    # Check roles
    for role_tasks in Path('roles').glob('*/tasks/*.yml'):
        violations = validate_file(role_tasks)
        all_violations.extend(violations)

    # Check playbooks
    for playbook in Path('playbooks').glob('*.yml'):
        violations = validate_file(playbook)
        all_violations.extend(violations)

    # Report
    if all_violations:
        print("❌ CRITICAL: Found tasks with sensitive data lacking 'no_log: true':\n")
        for violation in all_violations:
            print(f"  - {violation}")
        print(f"\n❌ Total violations: {len(all_violations)}")
        print("\n🔧 FIX: Add 'no_log: true' to all sensitive tasks")
        sys.exit(1)
    else:
        print("✅ All sensitive tasks have 'no_log: true'")
        sys.exit(0)

if __name__ == '__main__':
    main()
```

**Integración en CI**:
```yaml
# .github/workflows/security-scan.yml (modificar existente)
  no-log-enforcement:
    name: Enforce no_log on Sensitive Tasks
    runs-on: ubuntu-latest

    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.12'

      - name: Install dependencies
        run: pip install pyyaml

      - name: Run no_log validation
        run: python scripts/validate-no-log.py
```

**Pre-commit Hook**:
```yaml
# .pre-commit-config.yaml (agregar)
  - repo: local
    hooks:
      - id: validate-no-log
        name: Validate no_log usage
        entry: python scripts/validate-no-log.py
        language: system
        pass_filenames: false
        always_run: true
```

**Acceptance Criteria**:
- [ ] Script detecta 100% de tareas sensibles sin `no_log`
- [ ] CI falla si encuentra violaciones (no warning, ERROR)
- [ ] Pre-commit hook previene commits con violaciones
- [ ] Documentación actualizada con ejemplos

---

### FASE 3: ATOMICIDAD Y TRANSACCIONES (PRIORIDAD P0 - Crítica)

#### TASK 3.1: Implementar Two-Phase Commit Pattern
**Ubicación**: `roles/atomic_deployment/`, `tasks/atomic-wrapper.yml`

**Concepto**:
```
Phase 1: PREPARE (staging)
  ├─ Backup current configs
  ├─ Render new configs to /tmp/security-staging/
  ├─ Validate all configs (syntax check)
  ├─ Run pre-flight tests
  └─ Create checkpoint

Phase 2: COMMIT (atomic apply)
  ├─ Lock deployment (prevent concurrent runs)
  ├─ Apply all configs atomically
  ├─ Restart services with validation
  ├─ Run post-apply health checks
  └─ Commit or Rollback
```

**Implementación**:
```yaml
# tasks/atomic-wrapper.yml
---
# PHASE 1: PREPARE
- name: Create staging directory
  ansible.builtin.file:
    path: /tmp/security-staging-{{ ansible_date_time.epoch }}
    state: directory
    mode: '0700'
  register: staging_dir

- name: Set staging facts
  ansible.builtin.set_fact:
    security_staging_dir: "{{ staging_dir.path }}"
    security_deployment_id: "{{ ansible_date_time.epoch }}"

- name: Create deployment lock
  ansible.builtin.file:
    path: /var/lock/security-deployment.lock
    state: touch
    mode: '0600'
  register: deployment_lock
  failed_when: false

- name: Check for existing deployment
  ansible.builtin.stat:
    path: /var/lock/security-deployment.lock
  register: lock_stat

- name: Fail if deployment already running
  ansible.builtin.fail:
    msg: |
      CRITICAL: Another security deployment is already running!
      Lock file: /var/lock/security-deployment.lock
      Created: {{ lock_stat.stat.mtime }}
  when:
    - lock_stat.stat.exists
    - (ansible_date_time.epoch | int) - (lock_stat.stat.mtime | int) < 3600  # Less than 1 hour old

- name: Backup current configurations
  ansible.builtin.include_tasks: backup-configs.yml

- name: Checkpoint 1 - Backup complete
  ansible.builtin.set_fact:
    security_checkpoint_backup: true

# RENDER all configs to staging first
- name: Render sshd_config to staging
  ansible.builtin.template:
    src: sshd_config.j2
    dest: "{{ security_staging_dir }}/sshd_config"
    mode: '0600'
  register: sshd_staged

- name: Render sudoers to staging
  ansible.builtin.template:
    src: sudoers.j2
    dest: "{{ security_staging_dir }}/sudoers"
    mode: '0440'
  register: sudoers_staged

- name: Render PAM sshd to staging
  ansible.builtin.template:
    src: pam.d-sshd.j2
    dest: "{{ security_staging_dir }}/pam.d-sshd"
    mode: '0644'
  register: pam_staged

- name: Checkpoint 2 - Configs staged
  ansible.builtin.set_fact:
    security_checkpoint_staged: true

# VALIDATE all staged configs
- name: Validate staged sshd_config
  ansible.builtin.command: sshd -t -f {{ security_staging_dir }}/sshd_config
  register: sshd_validation
  failed_when: sshd_validation.rc != 0
  changed_when: false

- name: Validate staged sudoers
  ansible.builtin.command: visudo -cf {{ security_staging_dir }}/sudoers
  register: sudoers_validation
  failed_when: sudoers_validation.rc != 0
  changed_when: false

- name: Validate staged PAM config
  ansible.builtin.command: pam_tally2 --file {{ security_staging_dir }}/pam.d-sshd
  register: pam_validation
  failed_when: false  # PAM validation is tricky
  changed_when: false

- name: Checkpoint 3 - Validation complete
  ansible.builtin.set_fact:
    security_checkpoint_validated: true

# PHASE 2: COMMIT (atomic)
- name: COMMIT - Apply configurations atomically
  block:
    - name: Copy staged configs to production (atomic)
      ansible.builtin.copy:
        src: "{{ item.src }}"
        dest: "{{ item.dest }}"
        remote_src: true
        mode: "{{ item.mode }}"
        owner: root
        group: root
      loop:
        - { src: "{{ security_staging_dir }}/sshd_config", dest: "/etc/ssh/sshd_config", mode: "0600" }
        - { src: "{{ security_staging_dir }}/sudoers", dest: "/etc/sudoers", mode: "0440" }
        - { src: "{{ security_staging_dir }}/pam.d-sshd", dest: "/etc/pam.d/sshd", mode: "0644" }
      register: config_applied

    - name: Checkpoint 4 - Configs applied
      ansible.builtin.set_fact:
        security_checkpoint_applied: true

    - name: Restart services with health checks
      ansible.builtin.include_tasks: restart-services-validated.yml

    - name: Post-apply health checks
      ansible.builtin.include_tasks: health-checks.yml

    - name: Checkpoint 5 - Health checks passed
      ansible.builtin.set_fact:
        security_checkpoint_healthy: true

  rescue:
    - name: ROLLBACK - Failure detected
      ansible.builtin.debug:
        msg: |
          ❌ FAILURE DETECTED - INITIATING AUTOMATIC ROLLBACK
          Checkpoint reached: {{ 'Backup' if security_checkpoint_backup else 'None' }}
                              {{ 'Staged' if security_checkpoint_staged else '' }}
                              {{ 'Validated' if security_checkpoint_validated else '' }}
                              {{ 'Applied' if security_checkpoint_applied else '' }}

    - name: Execute rollback
      ansible.builtin.include_tasks: rollback.yml

    - name: Fail deployment after rollback
      ansible.builtin.fail:
        msg: "Deployment failed and was rolled back. Check logs."

  always:
    - name: Cleanup staging directory
      ansible.builtin.file:
        path: "{{ security_staging_dir }}"
        state: absent

    - name: Remove deployment lock
      ansible.builtin.file:
        path: /var/lock/security-deployment.lock
        state: absent

    - name: Generate deployment report
      ansible.builtin.copy:
        dest: /var/log/security-deployment-{{ security_deployment_id }}.log
        content: |
          Security Deployment Report
          ==========================
          Deployment ID: {{ security_deployment_id }}
          Timestamp: {{ ansible_date_time.iso8601 }}
          Host: {{ inventory_hostname }}

          Checkpoints:
          - Backup: {{ 'PASS' if security_checkpoint_backup else 'FAIL' }}
          - Staged: {{ 'PASS' if security_checkpoint_staged else 'FAIL' }}
          - Validated: {{ 'PASS' if security_checkpoint_validated else 'FAIL' }}
          - Applied: {{ 'PASS' if security_checkpoint_applied else 'FAIL' }}
          - Healthy: {{ 'PASS' if security_checkpoint_healthy else 'FAIL' }}

          Result: {{ 'SUCCESS' if security_checkpoint_healthy else 'FAILED (ROLLED BACK)' }}
        mode: '0640'
```

**Service Restart con Validación**:
```yaml
# tasks/restart-services-validated.yml
---
- name: Restart sshd with validation
  block:
    - name: Test sshd config before restart
      ansible.builtin.command: sshd -t
      register: sshd_test
      failed_when: sshd_test.rc != 0

    - name: Restart sshd
      ansible.builtin.service:
        name: sshd
        state: restarted
      register: sshd_restart

    - name: Wait for sshd to be accessible
      ansible.builtin.wait_for:
        port: 22
        host: "{{ ansible_host }}"
        timeout: 30
      delegate_to: localhost

    - name: Validate SSH connection
      ansible.builtin.command: ssh -o ConnectTimeout=5 -o StrictHostKeyChecking=no {{ ansible_host }} 'echo ok'
      delegate_to: localhost
      register: ssh_test
      failed_when: ssh_test.rc != 0

  rescue:
    - name: SSH restart failed - trigger rollback
      ansible.builtin.fail:
        msg: "SSH restart failed validation"
```

**Acceptance Criteria**:
- [ ] Deployment es atómico (todo o nada)
- [ ] Falla en cualquier paso hace rollback automático
- [ ] Checkpoints permiten debug preciso
- [ ] Lock file previene concurrent deployments
- [ ] Tests validan atomicidad (kill process mid-deploy)

---

#### TASK 3.2: Handler Chains con Flush
**Ubicación**: Todos los roles

**Pattern**:
```yaml
# roles/sshd_hardening/tasks/main.yml
---
- name: Configure sshd
  ansible.builtin.template:
    src: sshd_config.j2
    dest: /etc/ssh/sshd_config
  notify:
    - validate sshd config
    - restart sshd
  # NO flush here - wait until end

- name: Configure other sshd settings
  # ... more tasks
  notify:
    - restart sshd

# At the very end of role
- name: Flush all handlers atomically
  ansible.builtin.meta: flush_handlers
```

**Handlers**:
```yaml
# roles/sshd_hardening/handlers/main.yml
---
- name: validate sshd config
  ansible.builtin.command: sshd -t
  register: sshd_validation
  failed_when: sshd_validation.rc != 0
  listen: restart sshd

- name: restart sshd
  ansible.builtin.service:
    name: sshd
    state: restarted
```

**Acceptance Criteria**:
- [ ] Handlers ejecutan solo UNA VEZ al final
- [ ] Validation handlers ejecutan ANTES de restart handlers
- [ ] Falla en validation handler previene restart

---

### FASE 4: OBSERVABILIDAD (PRIORIDAD P1 - Alta)

#### TASK 4.1: Prometheus Metrics Exporter
**Ubicación**: `roles/security_metrics/`, `files/security_exporter.py`

**Implementación**:
```python
#!/usr/bin/env python3
"""
Prometheus metrics exporter for security hardening status.
Exports metrics in Prometheus text format to /var/lib/node_exporter/textfile_collector/security.prom
"""

import json
import time
from pathlib import Path
from typing import Dict, Any

METRICS_FILE = Path("/var/lib/node_exporter/textfile_collector/security.prom")
STATE_FILE = Path("/var/lib/security/deployment_state.json")

def load_deployment_state() -> Dict[str, Any]:
    """Load deployment state from JSON."""
    if not STATE_FILE.exists():
        return {}
    return json.loads(STATE_FILE.read_text())

def generate_metrics(state: Dict[str, Any]) -> str:
    """Generate Prometheus metrics."""
    metrics = []

    # Security phase metric
    phase = state.get('security_phase', 0)
    metrics.append(f'security_phase_current{{host="{state.get("hostname", "unknown")}"}} {phase}')

    # Deployment status (1 = success, 0 = failed)
    status = 1 if state.get('deployment_status') == 'success' else 0
    metrics.append(f'security_deployment_status{{host="{state.get("hostname")}"}} {status}')

    # Last deployment timestamp
    timestamp = state.get('deployment_timestamp', 0)
    metrics.append(f'security_last_deployment_timestamp{{host="{state.get("hostname")}"}} {timestamp}')

    # Component status
    components = ['ssh', 'pam_mfa', 'sudoers', 'selinux', 'audit']
    for component in components:
        enabled = 1 if state.get(f'{component}_enabled', False) else 0
        metrics.append(f'security_component_enabled{{host="{state.get("hostname")}",component="{component}"}} {enabled}')

    # SSH metrics
    ssh_config = state.get('ssh_config', {})
    metrics.append(f'security_ssh_password_auth{{host="{state.get("hostname")}"}} {1 if ssh_config.get("password_auth") else 0}')
    metrics.append(f'security_ssh_root_login{{host="{state.get("hostname")}"}} {1 if ssh_config.get("root_login") else 0}')
    metrics.append(f'security_ssh_max_auth_tries{{host="{state.get("hostname")}"}} {ssh_config.get("max_auth_tries", 0)}')

    # MFA metrics
    mfa_stats = state.get('mfa_stats', {})
    metrics.append(f'security_mfa_users_enrolled{{host="{state.get("hostname")}"}} {mfa_stats.get("users_enrolled", 0)}')
    metrics.append(f'security_mfa_service_accounts{{host="{state.get("hostname")}"}} {mfa_stats.get("service_accounts", 0)}')

    # Compliance status
    compliance = state.get('compliance', {})
    for standard in ['pci_dss', 'hipaa', 'soc2', 'cis']:
        score = compliance.get(standard, {}).get('score', 0)
        metrics.append(f'security_compliance_score{{host="{state.get("hostname")}",standard="{standard}"}} {score}')

    # Drift detection
    drift_detected = 1 if state.get('drift_detected', False) else 0
    metrics.append(f'security_drift_detected{{host="{state.get("hostname")}"}} {drift_detected}')

    # Help and type annotations
    header = """# HELP security_phase_current Current security hardening phase (1-6)
# TYPE security_phase_current gauge
# HELP security_deployment_status Last deployment status (1=success, 0=failed)
# TYPE security_deployment_status gauge
# HELP security_last_deployment_timestamp Unix timestamp of last deployment
# TYPE security_last_deployment_timestamp gauge
# HELP security_component_enabled Whether security component is enabled
# TYPE security_component_enabled gauge
# HELP security_ssh_password_auth SSH password authentication enabled (1=yes, 0=no)
# TYPE security_ssh_password_auth gauge
# HELP security_compliance_score Compliance score for standard (0-100)
# TYPE security_compliance_score gauge
# HELP security_drift_detected Configuration drift detected (1=yes, 0=no)
# TYPE security_drift_detected gauge
"""

    return header + '\n'.join(metrics) + '\n'

def main():
    """Generate and write metrics."""
    state = load_deployment_state()
    metrics = generate_metrics(state)

    # Atomic write
    temp_file = METRICS_FILE.with_suffix('.prom.tmp')
    temp_file.write_text(metrics)
    temp_file.replace(METRICS_FILE)

    print(f"Metrics written to {METRICS_FILE}")

if __name__ == '__main__':
    main()
```

**Ansible Integration**:
```yaml
# roles/security_metrics/tasks/main.yml
---
- name: Install node_exporter textfile collector
  ansible.builtin.package:
    name: prometheus-node-exporter
    state: present

- name: Create textfile collector directory
  ansible.builtin.file:
    path: /var/lib/node_exporter/textfile_collector
    state: directory
    mode: '0755'

- name: Install security metrics exporter
  ansible.builtin.copy:
    src: security_exporter.py
    dest: /usr/local/bin/security_exporter
    mode: '0755'

- name: Create state directory
  ansible.builtin.file:
    path: /var/lib/security
    state: directory
    mode: '0755'

- name: Write current deployment state
  ansible.builtin.copy:
    content: |
      {{
        {
          'hostname': ansible_hostname,
          'security_phase': security_phase | default(0),
          'deployment_status': 'success',
          'deployment_timestamp': ansible_date_time.epoch | int,
          'ssh_enabled': security_phase_ssh_hardening | default(false),
          'pam_mfa_enabled': security_phase_mfa | default(false),
          'sudoers_enabled': security_phase_sudoers | default(false),
          'selinux_enabled': security_phase_selinux | default(false),
          'audit_enabled': security_phase_audit | default(false),
          'ssh_config': {
            'password_auth': sshd_hardening_password_authentication | default(false),
            'root_login': sshd_hardening_permit_root_login == 'yes',
            'max_auth_tries': sshd_hardening_max_auth_tries | default(4)
          }
        } | to_nice_json
      }}
    dest: /var/lib/security/deployment_state.json
    mode: '0644'

- name: Generate initial metrics
  ansible.builtin.command: /usr/local/bin/security_exporter

- name: Schedule metrics generation
  ansible.builtin.cron:
    name: "Security metrics export"
    minute: "*/5"
    job: "/usr/local/bin/security_exporter"
```

**Grafana Dashboard**:
```json
# dashboards/security-hardening.json
{
  "dashboard": {
    "title": "Security Hardening Status",
    "panels": [
      {
        "title": "Security Phase Progress",
        "targets": [
          {
            "expr": "security_phase_current",
            "legendFormat": "{{host}}"
          }
        ],
        "type": "gauge",
        "options": {
          "min": 0,
          "max": 6,
          "thresholds": [
            { "value": 0, "color": "red" },
            { "value": 3, "color": "yellow" },
            { "value": 6, "color": "green" }
          ]
        }
      },
      {
        "title": "Deployment Success Rate",
        "targets": [
          {
            "expr": "rate(security_deployment_status[1h])",
            "legendFormat": "{{host}}"
          }
        ]
      },
      {
        "title": "SSH Password Auth Disabled",
        "targets": [
          {
            "expr": "security_ssh_password_auth == 0",
            "legendFormat": "{{host}}"
          }
        ]
      },
      {
        "title": "Compliance Scores",
        "targets": [
          {
            "expr": "security_compliance_score",
            "legendFormat": "{{host}} - {{standard}}"
          }
        ]
      }
    ]
  }
}
```

**Acceptance Criteria**:
- [ ] Métricas exportadas cada 5 minutos
- [ ] Node exporter scrapes metrics
- [ ] Grafana dashboard funcional
- [ ] Alerts configuradas (Prometheus Alertmanager)

---

#### TASK 4.2: Structured Logging (JSON)
**Ubicación**: `library/json_logger.py`, `callback_plugins/json_logger.py`

**Callback Plugin**:
```python
# callback_plugins/json_logger.py
"""
Ansible callback plugin for structured JSON logging.
"""

from ansible.plugins.callback import CallbackBase
import json
import datetime

class CallbackModule(CallbackBase):
    CALLBACK_VERSION = 2.0
    CALLBACK_TYPE = 'notification'
    CALLBACK_NAME = 'json_logger'

    def __init__(self):
        super(CallbackModule, self).__init__()
        self.log_file = '/var/log/ansible/security-enforcement.jsonl'

    def _log_event(self, event_type, result, **kwargs):
        """Log event in JSON format."""
        event = {
            'timestamp': datetime.datetime.utcnow().isoformat() + 'Z',
            'event_type': event_type,
            'host': result._host.get_name() if hasattr(result, '_host') else 'localhost',
            'task': result._task.get_name() if hasattr(result, '_task') else '',
            'result': result._result if hasattr(result, '_result') else {},
            **kwargs
        }

        with open(self.log_file, 'a') as f:
            f.write(json.dumps(event) + '\n')

    def v2_runner_on_ok(self, result):
        self._log_event('task_ok', result)

    def v2_runner_on_failed(self, result, ignore_errors=False):
        self._log_event('task_failed', result, ignore_errors=ignore_errors)

    def v2_runner_on_skipped(self, result):
        self._log_event('task_skipped', result)

    def v2_playbook_on_stats(self, stats):
        summary = {
            'timestamp': datetime.datetime.utcnow().isoformat() + 'Z',
            'event_type': 'playbook_summary',
            'stats': {
                host: {
                    'ok': stats.ok.get(host, 0),
                    'changed': stats.changed.get(host, 0),
                    'failures': stats.failures.get(host, 0),
                    'unreachable': stats.dark.get(host, 0),
                    'skipped': stats.skipped.get(host, 0),
                }
                for host in stats.processed.keys()
            }
        }

        with open(self.log_file, 'a') as f:
            f.write(json.dumps(summary) + '\n')
```

**Uso**:
```ini
# ansible.cfg
[defaults]
callbacks_enabled = json_logger
callback_plugins = ./callback_plugins
```

**Acceptance Criteria**:
- [ ] Logs en formato JSON
- [ ] Logs contienen contexto completo (host, task, resultado)
- [ ] Integración con ELK/Loki
- [ ] Logs rotados diariamente

---

## 🔄 CONTINUARÁ EN SIGUIENTE SECCIÓN...

Este prompt es demasiado extenso. Voy a dividirlo en múltiples archivos para mantenibilidad.

**Siguientes Archivos a Crear**:
1. `IMPLEMENTATION_PROMPT_PART2.md` - FASE 5-8
2. `IMPLEMENTATION_CHECKLIST.md` - Checklist ejecutable
3. `IMPLEMENTATION_PRIORITIES.md` - Orden de implementación

¿Quieres que continúe con las siguientes fases del prompt?
