# UV Setup Guide

**UV** is an extremely fast Python package installer and resolver, written in Rust. It's 10-100x faster than pip.

---

## Why UV?

✅ **10-100x faster** than pip
✅ **Deterministic** dependency resolution
✅ **Lock files** for reproducible builds
✅ **Virtual environment** management
✅ **Cache-friendly** for CI/CD
✅ **Drop-in replacement** for pip

---

## Installation

### Quick Install

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### Or via Homebrew (macOS/Linux)

```bash
brew install uv
```

### Or via pip

```bash
pip install uv
```

---

## Usage

### Install All Dependencies

```bash
# Install with all extras (dev, test, lint, docs)
uv sync --all-extras

# Or specific groups
uv sync --extra dev
uv sync --extra test
```

### Run Commands

```bash
# Run ansible commands
uv run ansible-playbook playbooks/site.yml

# Run ansible-lint
uv run ansible-lint

# Run tests
uv run pytest

# Run molecule
cd roles/sshd_hardening
uv run molecule test
```

### Update Dependencies

```bash
# Update all dependencies
uv lock --upgrade

# Update specific package
uv lock --upgrade-package ansible-core
```

### Add New Dependency

```bash
# Add to dependencies
uv add package-name

# Add to dev dependencies
uv add --dev package-name

# Add to specific group
uv add --optional test pytest-custom
```

---

## Project Structure

### pyproject.toml

All dependencies are now in `pyproject.toml`:

```toml
[project]
dependencies = [
    "ansible-core>=2.16,<2.21",
]

[project.optional-dependencies]
dev = [
    "ansible-lint>=24.7.0",
    "yamllint>=1.35.1",
    # ...
]
```

### uv.lock

Lockfile (auto-generated, committed to git):
- Ensures reproducible builds
- Faster installs in CI/CD
- Tracks exact versions

---

## CI/CD Integration

### GitHub Actions

```yaml
- name: Install UV
  uses: astral-sh/setup-uv@v5
  with:
    enable-cache: true

- name: Install dependencies
  run: uv sync --all-extras

- name: Run tests
  run: uv run pytest
```

### Benefits in CI/CD

- **Faster:** 10-100x faster installs
- **Cached:** Automatic caching
- **Reproducible:** Lock file ensures consistency

---

## Migration from pip

### Old Way (pip)

```bash
pip install -r requirements-dev.txt
ansible-playbook playbooks/site.yml
```

### New Way (UV)

```bash
uv sync --all-extras
uv run ansible-playbook playbooks/site.yml
```

### Compatibility

UV is fully compatible with:
- requirements.txt (still works)
- pip (can coexist)
- virtualenv
- pipx

---

## Common Tasks

### Development Setup

```bash
# Clone repository
git clone https://github.com/malpanez/security.git
cd security

# Install UV
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install dependencies
uv sync --all-extras

# Install Ansible collections
uv run ansible-galaxy collection install -r requirements.yml

# Run validation
uv run ./scripts/validate-all.sh
```

### Run Tests

```bash
# Run all tests
uv run pytest

# Run specific test
uv run pytest tests/test_sshd.py

# Run with coverage
uv run pytest --cov

# Run molecule test
cd roles/sshd_hardening
uv run molecule test
```

### Linting

```bash
# Ansible lint
uv run ansible-lint

# YAML lint
uv run yamllint .

# Python lint (ruff)
uv run ruff check .

# Format Python code
uv run ruff format .
```

---

## Troubleshooting

### UV not found

```bash
# Ensure UV is in PATH
export PATH="$HOME/.cargo/bin:$PATH"

# Or reinstall
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### Lock file conflicts

```bash
# Regenerate lock file
uv lock --upgrade

# Force sync
uv sync --reinstall
```

### Virtual environment issues

```bash
# Remove and recreate
rm -rf .venv
uv sync --all-extras
```

---

## Performance Comparison

### Installation Time

| Tool | Time | Speedup |
|------|------|---------|
| pip | 45s | 1x |
| uv | 0.5s | **90x faster** |

### Lock File Generation

| Tool | Time | Speedup |
|------|------|---------|
| pip-tools | 30s | 1x |
| uv | 0.3s | **100x faster** |

---

## Best Practices

### 1. Always Use Lock File

```bash
# Commit uv.lock to git
git add uv.lock
git commit -m "chore: update dependencies"
```

### 2. Update Regularly

```bash
# Weekly dependency updates
uv lock --upgrade
uv sync
uv run pytest  # Verify tests pass
```

### 3. Use in CI/CD

- Enable caching
- Use lock file
- Pin UV version

### 4. Group Dependencies

```toml
[project.optional-dependencies]
dev = [...]    # Development tools
test = [...]   # Testing only
lint = [...]   # Linting only
docs = [...]   # Documentation
```

---

## Resources

- **UV Docs:** https://docs.astral.sh/uv/
- **GitHub:** https://github.com/astral-sh/uv
- **Announcement:** https://astral.sh/blog/uv

---

**Status:** Ready to use
**Migration:** Optional (pip still supported)
**Recommendation:** Use UV for 10-100x faster installs
