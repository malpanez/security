from pathlib import Path

import yaml
from hypothesis import given, strategies as st
from jinja2 import BaseLoader, Environment


REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULTS_PATH = REPO_ROOT / "roles/sshd_hardening/defaults/main.yml"
TEMPLATE_PATH = REPO_ROOT / "roles/sshd_hardening/templates/sshd_config.j2"


def _load_defaults():
    data = yaml.safe_load(DEFAULTS_PATH.read_text()) or {}
    data.setdefault("sshd_hardening_effective_ciphers", [])
    data.setdefault("sshd_hardening_effective_macs", [])
    data.setdefault("sshd_hardening_effective_kex", [])
    data.setdefault("sshd_hardening_effective_hostkeys", [])
    data.setdefault("sshd_hardening_human_groups", [])
    data.setdefault("sshd_hardening_service_groups", [])
    data.setdefault("security_capabilities_selected_auth_mode", "legacy")
    data.setdefault("security_capabilities_mfa_for_humans_even_with_sk_keys", False)
    return data


def _render_sshd_config(**overrides):
    context = _load_defaults()
    context.update(overrides)
    env = Environment(loader=BaseLoader(), autoescape=False, keep_trailing_newline=True)
    template = env.from_string(TEMPLATE_PATH.read_text())
    return template.render(**context)


def test_required_lines_present():
    config = _render_sshd_config()
    assert "PasswordAuthentication" in config
    assert "PermitRootLogin" in config
    assert "UsePAM" in config


SAFE_TOKEN = st.text(alphabet="abcdefghijklmnopqrstuvwxyz0123456789-_", min_size=1, max_size=16)


@given(st.lists(SAFE_TOKEN, min_size=1, max_size=10, unique=True))
def test_allow_users_rendered(users):
    config = _render_sshd_config(sshd_hardening_allow_users=users)
    assert f"AllowUsers {' '.join(users)}" in config


def test_allow_users_omitted_when_empty():
    config = _render_sshd_config(sshd_hardening_allow_users=[])
    assert "AllowUsers" not in config


@given(st.lists(SAFE_TOKEN, min_size=1, max_size=10, unique=True))
def test_allow_groups_rendered(groups):
    config = _render_sshd_config(sshd_hardening_allow_groups=groups)
    assert f"AllowGroups {' '.join(groups)}" in config


def test_allow_groups_omitted_when_empty():
    config = _render_sshd_config(sshd_hardening_allow_groups=[])
    assert "AllowGroups" not in config


@given(st.lists(SAFE_TOKEN, min_size=1, max_size=5, unique=True))
def test_service_group_block_hardens(groups):
    config = _render_sshd_config(sshd_hardening_service_groups=groups)
    assert f"Match Group {','.join(groups)}" in config
    assert "PermitTTY no" in config
    assert "AllowTcpForwarding no" in config


@given(st.lists(SAFE_TOKEN, min_size=1, max_size=5, unique=True))
def test_human_group_mfa_block(groups):
    config = _render_sshd_config(
        sshd_hardening_human_groups=groups,
        security_capabilities_selected_auth_mode="pam_mfa",
    )
    assert f"Match Group {','.join(groups)}" in config
    assert "AuthenticationMethods publickey,keyboard-interactive" in config
