from pathlib import Path

import yaml
from hypothesis import given, strategies as st
from jinja2 import BaseLoader, Environment


REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULTS_PATH = REPO_ROOT / "roles/sudoers_baseline/defaults/main.yml"
TEMPLATE_MAIN = REPO_ROOT / "roles/sudoers_baseline/templates/sudoers.j2"
TEMPLATE_D = REPO_ROOT / "roles/sudoers_baseline/templates/sudoers.d.j2"


def _load_defaults():
    return yaml.safe_load(DEFAULTS_PATH.read_text()) or {}


def _render(template_path, **overrides):
    context = _load_defaults()
    context.update(overrides)
    env = Environment(loader=BaseLoader(), autoescape=False, keep_trailing_newline=True)
    template = env.from_string(template_path.read_text())
    return template.render(**context)


def test_main_sudoers_includes_secure_path():
    content = _render(TEMPLATE_MAIN)
    assert "Defaults secure_path=" in content
    assert "@includedir" in content


SAFE_GROUP = st.text(alphabet="abcdefghijklmnopqrstuvwxyz0123456789-_", min_size=1, max_size=16)
SAFE_CMD = st.text(alphabet="abcdefghijklmnopqrstuvwxyz0123456789-_", min_size=1, max_size=16)


@st.composite
def sudoers_group_config(draw):
    group = draw(SAFE_GROUP)
    require_password = draw(st.booleans())
    commands = draw(st.lists(SAFE_CMD, min_size=1, max_size=5, unique=True))
    commands = [f"/usr/bin/{cmd}" for cmd in commands]
    return group, {"require_password": require_password, "commands": commands}


@given(sudoers_group_config())
def test_sudoers_group_rendering(config):
    group, cfg = config
    content = _render(TEMPLATE_D, sudoers_baseline_groups={group: cfg})
    line = f"%{group} ALL=(ALL)"
    assert line in content
    if cfg["require_password"]:
        assert "NOPASSWD" not in content
    else:
        assert "NOPASSWD:" in content
