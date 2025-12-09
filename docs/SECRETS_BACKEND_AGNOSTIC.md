# Secrets Backend Agnostic Implementation

## 🎯 Objetivo

Implementar un **sistema unificado** de gestión de secretos que soporte múltiples backends:
- **Infisical** (default, recomendado)
- **HashiCorp Vault** (enterprise)
- **AWS Secrets Manager** (cloud-native)
- **Ansible Vault** (fallback)

---

## 🏗️ Arquitectura

```
┌─────────────────────────────────────────────┐
│         Ansible Playbooks/Roles             │
└────────────────┬────────────────────────────┘
                 │
                 │ lookup('secrets', 'path/to/secret')
                 ▼
┌─────────────────────────────────────────────┐
│    Unified Secrets Plugin (Abstraction)     │
│                                             │
│  if secrets_backend == 'infisical':         │
│      → InfisicalClient                      │
│  elif secrets_backend == 'vault':           │
│      → VaultClient                          │
│  elif secrets_backend == 'aws':             │
│      → AWSSecretsClient                     │
│  else:                                       │
│      → AnsibleVaultClient (fallback)        │
└────────────────┬────────────────────────────┘
                 │
        ┌────────┴────────┬────────────┬────────────┐
        ▼                 ▼            ▼            ▼
   ┌─────────┐      ┌─────────┐  ┌────────┐  ┌──────────┐
   │Infisical│      │  Vault  │  │AWS SM  │  │Ansible   │
   │   API   │      │   API   │  │  API   │  │  Vault   │
   └─────────┘      └─────────┘  └────────┘  └──────────┘
```

---

## 📁 Estructura de Archivos

```
roles/
└── secrets_integration/
    ├── defaults/
    │   └── main.yml                 # Configuración por defecto
    ├── tasks/
    │   ├── main.yml                 # Dispatcher
    │   ├── infisical.yml            # Infisical setup
    │   ├── vault.yml                # Vault setup
    │   ├── aws.yml                  # AWS SM setup
    │   └── validate.yml             # Validation tests
    ├── templates/
    │   └── secrets_config.j2        # Config template
    └── meta/
        └── argument_specs.yml       # Documentation

plugins/
└── lookup/
    ├── secrets.py                   # UNIFIED lookup plugin
    ├── infisical_backend.py         # Infisical implementation
    ├── vault_backend.py             # Vault implementation
    └── aws_backend.py               # AWS implementation
```

---

## 🔧 Implementación

### 1. Variables de Configuración

```yaml
# group_vars/all/secrets.yml
---
# Backend selection (infisical|vault|aws|ansible_vault)
secrets_backend: infisical  # DEFAULT

# Common settings
secrets_validate_certs: true
secrets_timeout: 30
secrets_max_retries: 3
secrets_cache_enabled: false  # Security: no caching by default

# Infisical settings (when secrets_backend == 'infisical')
infisical_api_url: "{{ lookup('env', 'INFISICAL_API_URL') | default('https://app.infisical.com') }}"
infisical_service_token: "{{ lookup('env', 'INFISICAL_SERVICE_TOKEN') }}"
infisical_project_id: "{{ lookup('env', 'INFISICAL_PROJECT_ID') }}"
infisical_environment: "{{ lookup('env', 'INFISICAL_ENVIRONMENT') | default('production') }}"

# Vault settings (when secrets_backend == 'vault')
vault_addr: "{{ lookup('env', 'VAULT_ADDR') }}"
vault_token: "{{ lookup('env', 'VAULT_TOKEN') }}"
vault_role_id: "{{ lookup('env', 'VAULT_ROLE_ID') }}"
vault_secret_id: "{{ lookup('env', 'VAULT_SECRET_ID') }}"
vault_namespace: "admin/security"

# AWS Secrets Manager settings (when secrets_backend == 'aws')
aws_region: "{{ lookup('env', 'AWS_REGION') | default('us-east-1') }}"
aws_secrets_prefix: "malpanez-security/"

# Ansible Vault settings (fallback)
ansible_vault_password_file: "{{ lookup('env', 'ANSIBLE_VAULT_PASSWORD_FILE') }}"
```

### 2. Unified Lookup Plugin

```python
# plugins/lookup/secrets.py
"""
Unified secrets lookup plugin supporting multiple backends.

DOCUMENTATION:
    name: secrets
    author: malpanez
    version_added: "2.0"
    short_description: Fetch secrets from configured backend
    description:
        - Retrieve secrets from Infisical, Vault, AWS SM, or Ansible Vault
        - Backend selected via 'secrets_backend' variable
    options:
      _terms:
        description: Secret path to fetch
        required: True
      backend:
        description: Override global secrets_backend
        choices: ['infisical', 'vault', 'aws', 'ansible_vault']
        env:
          - name: SECRETS_BACKEND

EXAMPLES:
    # Use default backend (from secrets_backend variable)
    - debug:
        msg: "{{ lookup('secrets', 'ssh/ca_key') }}"

    # Override backend
    - debug:
        msg: "{{ lookup('secrets', 'ssh/ca_key', backend='vault') }}"

    # Fetch multiple secrets
    - debug:
        msg: "{{ lookup('secrets', 'ssh/ca_key', 'db/password') }}"

RETURN:
    _raw:
        description: Secret value(s)
        type: string or list
"""

from ansible.errors import AnsibleError
from ansible.plugins.lookup import LookupBase
from ansible.utils.display import Display
import os

# Import backend implementations
try:
    from ansible.plugins.lookup.infisical_backend import InfisicalBackend
    from ansible.plugins.lookup.vault_backend import VaultBackend
    from ansible.plugins.lookup.aws_backend import AWSBackend
except ImportError:
    # Fallback paths
    import sys
    sys.path.append(os.path.dirname(__file__))
    from infisical_backend import InfisicalBackend
    from vault_backend import VaultBackend
    from aws_backend import AWSBackend

display = Display()

class LookupModule(LookupBase):

    BACKENDS = {
        'infisical': InfisicalBackend,
        'vault': VaultBackend,
        'aws': AWSBackend,
    }

    def run(self, terms, variables=None, **kwargs):
        """
        Main entry point for unified secrets lookup.
        """
        if not terms:
            raise AnsibleError("secrets lookup requires at least one secret path")

        # Determine backend
        backend_name = kwargs.get('backend') or \
                      os.getenv('SECRETS_BACKEND') or \
                      variables.get('secrets_backend', 'infisical')

        display.vvv(f"secrets lookup: using backend '{backend_name}'")

        # Validate backend
        if backend_name not in self.BACKENDS:
            if backend_name == 'ansible_vault':
                return self._fallback_ansible_vault(terms, variables)
            else:
                raise AnsibleError(
                    f"Unknown secrets backend: {backend_name}. "
                    f"Valid options: {', '.join(self.BACKENDS.keys())}, ansible_vault"
                )

        # Instantiate backend
        backend_class = self.BACKENDS[backend_name]

        try:
            backend = backend_class(variables, **kwargs)
            results = []

            for term in terms:
                display.vvv(f"Fetching secret: {term}")
                secret_value = backend.fetch_secret(term)
                results.append(secret_value)

            return results

        except Exception as e:
            raise AnsibleError(f"Failed to fetch secrets from {backend_name}: {str(e)}")

    def _fallback_ansible_vault(self, terms, variables):
        """
        Fallback to Ansible Vault for encrypted variables.
        """
        display.warning("Using Ansible Vault fallback (not recommended for production)")
        results = []

        for term in terms:
            # Lookup in group_vars/host_vars encrypted files
            var_name = term.replace('/', '_')
            value = variables.get(var_name)

            if value is None:
                raise AnsibleError(f"Secret not found in Ansible Vault: {term}")

            results.append(value)

        return results
```

### 3. Infisical Backend

```python
# plugins/lookup/infisical_backend.py
"""
Infisical backend implementation for unified secrets plugin.
"""

import requests
from ansible.errors import AnsibleError
from ansible.utils.display import Display

display = Display()

class InfisicalBackend:
    """Infisical secrets backend."""

    def __init__(self, variables, **kwargs):
        self.api_url = kwargs.get('api_url') or \
                      variables.get('infisical_api_url', 'https://app.infisical.com')
        self.service_token = kwargs.get('service_token') or \
                            variables.get('infisical_service_token')
        self.project_id = kwargs.get('project_id') or \
                         variables.get('infisical_project_id')
        self.environment = kwargs.get('environment') or \
                          variables.get('infisical_environment', 'production')

        # Validation
        if not self.service_token:
            raise AnsibleError("infisical_service_token is required")
        if not self.project_id:
            raise AnsibleError("infisical_project_id is required")

        self.session = requests.Session()
        self.session.headers.update({
            'Authorization': f'Bearer {self.service_token}'
        })

    def fetch_secret(self, secret_path):
        """
        Fetch a secret from Infisical.

        Args:
            secret_path: Path to secret (e.g., 'ssh/ca_key')

        Returns:
            Secret value as string
        """
        url = f"{self.api_url}/api/v3/secrets/raw/{secret_path}"
        params = {
            'workspaceId': self.project_id,
            'environment': self.environment
        }

        display.vvv(f"Infisical: GET {url}")

        try:
            response = self.session.get(url, params=params, timeout=30)
            response.raise_for_status()

            data = response.json()
            return data['secret']['secretValue']

        except requests.exceptions.RequestException as e:
            raise AnsibleError(f"Infisical API error for {secret_path}: {str(e)}")
        except KeyError as e:
            raise AnsibleError(f"Unexpected Infisical response format: {str(e)}")
```

### 4. Vault Backend

```python
# plugins/lookup/vault_backend.py
"""
HashiCorp Vault backend implementation for unified secrets plugin.
"""

import requests
from ansible.errors import AnsibleError
from ansible.utils.display import Display

display = Display()

class VaultBackend:
    """HashiCorp Vault secrets backend."""

    def __init__(self, variables, **kwargs):
        self.addr = kwargs.get('addr') or variables.get('vault_addr')
        self.token = kwargs.get('token') or variables.get('vault_token')
        self.namespace = kwargs.get('namespace') or \
                        variables.get('vault_namespace', 'admin/security')

        # Validation
        if not self.addr:
            raise AnsibleError("vault_addr is required")
        if not self.token:
            # Try AppRole authentication
            self._authenticate_approle(variables)

        self.session = requests.Session()
        self.session.headers.update({
            'X-Vault-Token': self.token,
            'X-Vault-Namespace': self.namespace
        })

    def _authenticate_approle(self, variables):
        """Authenticate using AppRole."""
        role_id = variables.get('vault_role_id')
        secret_id = variables.get('vault_secret_id')

        if not role_id or not secret_id:
            raise AnsibleError("vault_token or (vault_role_id + vault_secret_id) required")

        url = f"{self.addr}/v1/auth/approle/login"
        data = {'role_id': role_id, 'secret_id': secret_id}

        response = requests.post(url, json=data, timeout=30)
        response.raise_for_status()

        self.token = response.json()['auth']['client_token']

    def fetch_secret(self, secret_path):
        """
        Fetch a secret from Vault KV v2.

        Args:
            secret_path: Path to secret (e.g., 'ssh/ca_key')

        Returns:
            Secret value as string
        """
        # KV v2 path: /v1/{mount}/data/{path}
        url = f"{self.addr}/v1/secret/data/{secret_path}"

        display.vvv(f"Vault: GET {url}")

        try:
            response = self.session.get(url, timeout=30)
            response.raise_for_status()

            data = response.json()
            return data['data']['data']['value']

        except requests.exceptions.RequestException as e:
            raise AnsibleError(f"Vault API error for {secret_path}: {str(e)}")
        except KeyError as e:
            raise AnsibleError(f"Unexpected Vault response format: {str(e)}")
```

### 5. AWS Secrets Manager Backend

```python
# plugins/lookup/aws_backend.py
"""
AWS Secrets Manager backend implementation for unified secrets plugin.
"""

import boto3
from botocore.exceptions import ClientError
from ansible.errors import AnsibleError
from ansible.utils.display import Display

display = Display()

class AWSBackend:
    """AWS Secrets Manager backend."""

    def __init__(self, variables, **kwargs):
        self.region = kwargs.get('region') or \
                     variables.get('aws_region', 'us-east-1')
        self.prefix = kwargs.get('prefix') or \
                     variables.get('aws_secrets_prefix', 'malpanez-security/')

        # Initialize boto3 client
        self.client = boto3.client('secretsmanager', region_name=self.region)

    def fetch_secret(self, secret_path):
        """
        Fetch a secret from AWS Secrets Manager.

        Args:
            secret_path: Path to secret (e.g., 'ssh/ca_key')

        Returns:
            Secret value as string
        """
        # Full secret name with prefix
        secret_name = f"{self.prefix}{secret_path}"

        display.vvv(f"AWS SM: GET {secret_name}")

        try:
            response = self.client.get_secret_value(SecretId=secret_name)
            return response['SecretString']

        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == 'ResourceNotFoundException':
                raise AnsibleError(f"Secret not found in AWS SM: {secret_name}")
            else:
                raise AnsibleError(f"AWS SM error for {secret_name}: {str(e)}")
```

---

## 🎮 Uso

### En Playbooks

```yaml
# playbooks/enforce-with-secrets.yml
---
- name: Security enforcement with unified secrets
  hosts: all
  become: true

  vars:
    # Select backend (infisical|vault|aws|ansible_vault)
    secrets_backend: infisical  # or vault, aws, ansible_vault

  pre_tasks:
    - name: Setup secrets integration
      include_role:
        name: secrets_integration

  roles:
    - role: sshd_hardening
      vars:
        # Unified lookup - works with ANY backend
        sshd_hardening_trusted_ca_key: "{{ lookup('secrets', 'ssh/ca_key') }}"

    - role: service_accounts_transfer
      vars:
        service_account_keys: "{{ lookup('secrets', 'service_accounts/keys') | from_json }}"

    - role: pam_mfa
      vars:
        mfa_totp_seed: "{{ lookup('secrets', 'mfa/totp_seed') }}"
```

### Cambiar de Backend (Sin cambios de código)

```bash
# Usar Infisical (default)
ansible-playbook playbooks/enforce-with-secrets.yml

# Usar Vault
ansible-playbook playbooks/enforce-with-secrets.yml -e secrets_backend=vault

# Usar AWS Secrets Manager
ansible-playbook playbooks/enforce-with-secrets.yml -e secrets_backend=aws

# Fallback a Ansible Vault
ansible-playbook playbooks/enforce-with-secrets.yml -e secrets_backend=ansible_vault
```

---

## ✅ Testing

```yaml
# molecule/secrets_backend/verify.yml
---
- name: Verify secrets integration works with all backends
  hosts: all
  gather_facts: false

  tasks:
    - name: Test Infisical backend
      debug:
        msg: "{{ lookup('secrets', 'test/secret', backend='infisical') }}"
      when: infisical_service_token is defined

    - name: Test Vault backend
      debug:
        msg: "{{ lookup('secrets', 'test/secret', backend='vault') }}"
      when: vault_addr is defined

    - name: Test AWS backend
      debug:
        msg: "{{ lookup('secrets', 'test/secret', backend='aws') }}"
      when: aws_region is defined

    - name: Test fallback
      debug:
        msg: "{{ lookup('secrets', 'test/secret', backend='ansible_vault') }}"
```

---

## 📊 Comparison Matrix

| Feature | Infisical | Vault | AWS SM | Ansible Vault |
|---------|-----------|-------|--------|---------------|
| **Cost** | $0 | $0-5k+ | ~$0.40/secret/mo | $0 |
| **Setup** | Easy | Medium | Easy | Easy |
| **MFA** | ✅ Native | Enterprise | ✅ AWS IAM | ❌ |
| **UI** | ✅ Modern | Functional | ✅ AWS Console | ❌ CLI only |
| **Rotation** | ✅ Built-in | ✅ Built-in | ✅ Lambda | ❌ Manual |
| **HA** | Docker/K8s | Consul | ✅ AWS managed | N/A |
| **Audit** | ✅ | ✅ | ✅ CloudTrail | ❌ |
| **Recommended** | ✅ YES | Medium scale | Cloud-native | Development only |

---

## 🎯 Recommendation by Use Case

```yaml
# Development / Staging
secrets_backend: ansible_vault  # Simple, no setup

# Production (Open Source preference)
secrets_backend: infisical  # $0 cost, full features

# Production (Enterprise scale)
secrets_backend: vault  # If already using Vault

# Production (AWS-native)
secrets_backend: aws  # If everything else is in AWS
```

---

## 🔄 Migration Path

```bash
# Migrate from Ansible Vault to Infisical
./scripts/migrate-secrets.sh ansible_vault infisical

# Migrate from Vault to Infisical
./scripts/migrate-secrets.sh vault infisical

# Script handles:
# 1. Export secrets from source
# 2. Import to destination
# 3. Update playbooks (optional)
# 4. Validate migration
```

---

**Ventaja clave**: **ZERO vendor lock-in**. Cambiar de backend es cambiar una variable.

**Updated**: 2025-12-09
**Author**: Claude Sonnet 4.5
