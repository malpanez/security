# Contributing to malpanez.security

Thank you for your interest in contributing to the malpanez.security Ansible collection! This document provides guidelines and instructions for contributing.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [How to Contribute](#how-to-contribute)
- [Testing Requirements](#testing-requirements)
- [Commit Message Guidelines](#commit-message-guidelines)
- [Pull Request Process](#pull-request-process)
- [Coding Standards](#coding-standards)

## Code of Conduct

This project adheres to a code of conduct that promotes a welcoming and inclusive environment:

- **Be respectful** - Treat all contributors with respect and kindness
- **Be collaborative** - Work together towards common goals
- **Be professional** - Focus on technical merit and constructive feedback
- **Be inclusive** - Welcome diverse perspectives and backgrounds

## Getting Started

### Prerequisites

- Ansible Core >= 2.16
- Python >= 3.12
- Docker (for Molecule testing)
- Git

### Fork and Clone

```bash
# Fork the repository on GitHub first, then:
git clone https://github.com/YOUR_USERNAME/security.git
cd security
git remote add upstream https://github.com/malpanez/security.git
```

## Development Setup

### Using Devcontainer (Recommended)

```bash
# Open in VS Code with Remote-Containers extension
code .
# VS Code will prompt to reopen in container
```

### Manual Setup

```bash
# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements-dev.txt

# Install pre-commit hooks
pre-commit install --install-hooks

# Install collection dependencies
ansible-galaxy collection install -r requirements.yml
```

## How to Contribute

### Types of Contributions

We welcome various types of contributions:

1. **Bug Reports** - Report issues with clear reproduction steps
2. **Feature Requests** - Propose new features or enhancements
3. **Bug Fixes** - Submit patches for reported issues
4. **New Features** - Implement new roles or functionality
5. **Documentation** - Improve or translate documentation
6. **Tests** - Add or improve test coverage

### Reporting Bugs

When reporting bugs, include:

```markdown
**Description**: Clear description of the bug

**Expected Behavior**: What should happen

**Actual Behavior**: What actually happens

**Steps to Reproduce**:
1. Step one
2. Step two
3. ...

**Environment**:
- OS: [e.g., Ubuntu 22.04]
- Ansible version: [e.g., 2.16.0]
- Collection version: [e.g., 1.0.0]

**Logs/Output**:
```
[paste relevant logs]
```
```

### Requesting Features

Feature requests should include:

- **Use case** - Why is this feature needed?
- **Proposed solution** - How should it work?
- **Alternatives** - What alternatives have you considered?
- **Additional context** - Any other relevant information

## Testing Requirements

**All code contributions must include tests.** This is non-negotiable for a security collection.

### Running Tests Locally

```bash
# Lint everything
make lint

# Test a specific role
cd roles/ROLE_NAME
molecule test

# Run all role tests
make test-all

# Check syntax of playbooks
make syntax-check
```

### Test Coverage Requirements

- **New roles**: Must have >= 80% test coverage
- **Role modifications**: Maintain or improve existing coverage
- **Critical security features**: Must have >= 95% coverage
- **All roles**: Must pass Molecule tests on all supported platforms

### Writing Tests

Use testinfra for role verification:

```python
def test_critical_feature(host):
    """Test description following Google style."""
    # Arrange
    config_file = host.file("/etc/some/config")

    # Act
    result = host.run("some command")

    # Assert
    assert config_file.exists
    assert result.rc == 0
```

### CRITICAL Test Requirements

For security-critical features (MFA, SSH, sudo):

```python
def test_prevents_lockout(host):
    """CRITICAL: Verify configuration prevents admin lockout."""
    # Must validate:
    # - Service account bypass exists
    # - Fallback mechanisms work
    # - Root/admin access preserved
    pass
```

## Commit Message Guidelines

We follow **Conventional Commits** specification:

### Format

```
<type>(<scope>): <subject>

<body>

<footer>
```

### Types

- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation only
- `style`: Code style changes (formatting)
- `refactor`: Code refactoring
- `perf`: Performance improvements
- `test`: Adding or updating tests
- `chore`: Maintenance tasks
- `ci`: CI/CD changes

### Examples

```
feat(pam_mfa): add FIDO2 passwordless authentication

Implement FIDO2 passwordless authentication support using
libpam-u2f with resident key requirement.

Closes #123
```

```
fix(sudoers_baseline): prevent syntax error with quotes in commands

Escape quotes in sudo command specifications to prevent
visudo syntax errors.

Fixes #456
```

### Commit Message Rules

1. Use imperative mood ("add" not "added")
2. Don't capitalize first letter of subject
3. No period at end of subject
4. Limit subject to 50 characters
5. Wrap body at 72 characters
6. Reference issues/PRs in footer

## Pull Request Process

### Before Submitting

- [ ] Code follows project style guidelines
- [ ] Tests added/updated and passing
- [ ] Documentation updated (if applicable)
- [ ] Pre-commit hooks pass
- [ ] Commit messages follow conventions
- [ ] Branch is up-to-date with main

### PR Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
Describe how you tested these changes

## Checklist
- [ ] Tests pass locally
- [ ] Documentation updated
- [ ] No new warnings
- [ ] Follows coding standards
```

### Review Process

1. **Automated checks** - CI/CD must pass
2. **Code review** - At least one maintainer approval required
3. **Testing** - Reviewer will test changes locally
4. **Documentation** - Verify documentation is complete
5. **Merge** - Maintainer will merge once approved

### After Merge

- Your contribution will be included in the next release
- You'll be added to CONTRIBUTORS file
- Release notes will credit your contribution

## Coding Standards

### Ansible Style

```yaml
# Use descriptive names
- name: Ensure SSH daemon is hardened
  # not: Configure SSH

# One task, one purpose
# Bad:
- name: Setup everything
  shell: |
    do_thing_1
    do_thing_2

# Good:
- name: Configure thing 1
  command: do_thing_1

- name: Configure thing 2
  command: do_thing_2

# Use become sparingly
- name: Read public file
  command: cat /etc/os-release
  # Don't add: become: true

# Always validate inputs
- name: Apply configuration
  template:
    src: config.j2
    dest: /etc/config
    validate: '/usr/bin/validate %s'
```

### Variable Naming

```yaml
# Role-specific variables: <role_name>_<var_name>
sshd_hardening_port: 22
pam_mfa_enabled: true

# Boolean variables: Use affirmative (enabled vs disabled)
sudoers_baseline_strict: true  # Good
sudoers_baseline_no_strict: false  # Bad

# List variables: Plural nouns
sshd_hardening_ciphers: [...]
pam_mfa_service_accounts: [...]
```

### File Organization

```
roles/ROLE_NAME/
├── README.md                    # Role documentation
├── defaults/main.yml            # Default variables
├── handlers/main.yml            # Handlers
├── meta/
│   ├── main.yml                # Role metadata
│   └── argument_specs.yml      # Variable specs
├── molecule/
│   └── default/
│       ├── converge.yml        # Test playbook
│       ├── molecule.yml        # Molecule config
│       └── tests/
│           └── test_*.py       # Testinfra tests
├── tasks/
│   ├── main.yml                # Main entry point
│   ├── Debian.yml              # Debian-specific
│   └── RedHat.yml              # RHEL-specific
├── templates/                   # Jinja2 templates
└── vars/                        # Internal variables
```

### Documentation Requirements

Every role must have:

1. **README.md** with:
   - Description
   - Requirements
   - Role Variables
   - Dependencies
   - Example Playbook
   - License
   - Author

2. **meta/argument_specs.yml** with:
   - All variables documented
   - Types specified
   - Defaults shown
   - Descriptions clear

3. **Inline comments** for:
   - Complex logic
   - Security considerations
   - Platform-specific behavior

### Security Considerations

When contributing security-related changes:

1. **Never disable security** by default
2. **Validate all inputs** - Prevent injection attacks
3. **Test for lockout prevention** - CRITICAL
4. **Document security implications** - In comments and docs
5. **Follow principle of least privilege** - Minimal permissions
6. **Use secure defaults** - Opt-in for permissive settings

### Python Code Style

```python
# Follow PEP 8
# Use type hints
def test_function(host: Any) -> None:
    """Docstring following Google style.

    Args:
        host: Testinfra host fixture

    Returns:
        None
    """
    pass

# Descriptive variable names
config_file = host.file("/etc/config")  # Good
cf = host.file("/etc/config")  # Bad
```

### YAML Formatting

```yaml
# Use 2-space indentation
# Use --- document separator
# Use explicit null, true, false
# Quote strings with special chars
# No trailing whitespace
# Blank line at end of file
```

## Development Workflow

### Feature Development

```bash
# 1. Create feature branch
git checkout -b feat/my-feature main

# 2. Make changes
# ... edit files ...

# 3. Test locally
molecule test

# 4. Commit with conventional commit message
git add .
git commit -m "feat(role): add new feature"

# 5. Push and create PR
git push origin feat/my-feature
```

### Keeping Branch Updated

```bash
# Fetch upstream changes
git fetch upstream

# Rebase your branch
git rebase upstream/main

# Force push if needed
git push origin feat/my-feature --force-with-lease
```

## Getting Help

- **Documentation**: Check docs/ directory
- **Examples**: See examples/ directory
- **Issues**: Search existing issues first
- **Discussions**: Use GitHub Discussions for questions

## Recognition

Contributors will be:
- Listed in CONTRIBUTORS file
- Credited in release notes
- Mentioned in documentation (if significant contribution)

## License

By contributing, you agree that your contributions will be licensed under the same license as the project (GPL-2.0-or-later).

---

**Thank you for contributing to make Linux systems more secure!**
