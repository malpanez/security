#!/usr/bin/env python3
"""
Validate that all sensitive Ansible tasks have no_log: true

This script scans all task files in roles/ for tasks that handle sensitive data
and ensures they have no_log: true to prevent secrets from appearing in logs.

Exit codes:
    0: All sensitive tasks have no_log
    1: Violations found
    2: Script error
"""

import re
import sys
from collections.abc import Iterable
from pathlib import Path

import yaml

# Patterns that indicate sensitive data
SENSITIVE_PATTERNS = [
    r'password',
    r'secret',
    r'token',
    r'api[_-]?key',
    r'private[_-]?key',
    r'credential',
    r'auth',
    r'totp',
    r'mfa',
    r'yubikey',
    r'fido2',
]

# Tasks that are allowed to handle secrets without no_log (whitelist)
ALLOWED_TASKS = [
    'debug',  # Debug tasks showing sanitized info
    'assert',  # Assertions
    'set_fact',  # Facts without secrets
    'include',
    'import',
]

# Module types that don't leak secrets even with sensitive keywords
SAFE_MODULES = [
    'package',  # Installing packages
    'apt',
    'yum',
    'dnf',
    'file',  # Creating directories/files
    'group',  # Creating groups
    'user',  # Creating users (when not setting passwords)
    'stat',  # Checking file existence
    'pamd',  # PAM configuration (already structured, not leaking)
    'pause',  # User prompts
    'wait_for',
]


def find_task_files(base_path: Path) -> list[Path]:
    """Find all task YAML files in roles directory."""
    task_files = []
    for pattern in ["**/tasks/*.yml", "**/tasks/*.yaml"]:
        task_files.extend(base_path.glob(pattern))
    return sorted(task_files)


def is_sensitive_task(task: dict) -> bool:
    """Check if task handles sensitive data based on patterns."""
    # Get the module being used
    task_module = None
    for key in task.keys():
        if key not in ['name', 'when', 'tags', 'register', 'changed_when', 'failed_when', 'notify', 'become', 'vars']:
            task_module = key
            break

    # Check if this is a safe module
    if task_module:
        for safe in SAFE_MODULES:
            if safe in task_module:
                return False

    # Check if this is a whitelisted task type
    if isinstance(task_module, str):
        for allowed in ALLOWED_TASKS:
            if allowed in task_module:
                return False

    # Only check for secrets in register + shell/command tasks
    # or tasks with actual secret values
    has_register = 'register' in task
    is_command_like = task_module in ['command', 'shell', 'raw'] if task_module else False

    if not (has_register and is_command_like):
        # For non-command tasks, only flag if they have actual secret values
        task_str = str(task).lower()
        # Look for actual secret patterns, not just keywords
        secret_value_patterns = [
            r'password\s*[:=]\s*[\'"]?\S+',  # password: value or password="value"
            r'token\s*[:=]\s*[\'"]?\S+',
            r'api[_-]?key\s*[:=]\s*[\'"]?\S+',
            r'secret\s*[:=]\s*[\'"]?\S+',
            r'BEGIN.*PRIVATE.*KEY',  # Private keys
        ]

        for pattern in secret_value_patterns:
            if re.search(pattern, task_str, re.IGNORECASE):
                return True

        # Not a sensitive task
        return False

    # For register + command tasks, check if output might contain secrets
    task_str = str(task).lower()
    for pattern in SENSITIVE_PATTERNS:
        if re.search(pattern, task_str, re.IGNORECASE):
            return True

    return False


def has_no_log(task: dict) -> bool:
    """Check if task has no_log: true."""
    no_log = task.get('no_log', False)

    # Handle various representations of true
    if isinstance(no_log, bool):
        return no_log
    if isinstance(no_log, str):
        return no_log.lower() in ['true', 'yes']

    return False


def check_file(file_path: Path) -> list[tuple[str, dict]]:
    """
    Check a single task file for violations.

    Returns:
        List of (task_name, task_dict) tuples for violations
    """
    violations = []

    try:
        with open(file_path) as f:
            content = yaml.safe_load(f)

        if not isinstance(content, list):
            return violations

        for task in content:
            if not isinstance(task, dict):
                continue

            # Skip include/import tasks
            if any(key in task for key in ['include', 'import_tasks', 'include_tasks']):
                continue

            task_name = task.get('name', '<unnamed>')

            # Check if task handles sensitive data
            if is_sensitive_task(task):
                # Check if it has no_log
                if not has_no_log(task):
                    violations.append((task_name, task))

    except yaml.YAMLError as e:
        print(f"Warning: Could not parse {file_path}: {e}", file=sys.stderr)
    except Exception as e:
        print(f"Warning: Error processing {file_path}: {e}", file=sys.stderr)

    return violations


def _extract_tasks_from_play(play: dict) -> Iterable[dict]:
    for key in ("pre_tasks", "tasks", "post_tasks", "handlers"):
        items = play.get(key, [])
        if isinstance(items, list):
            for task in items:
                if isinstance(task, dict):
                    yield task


def check_playbook(file_path: Path) -> list[tuple[str, dict]]:
    violations = []

    try:
        with open(file_path) as f:
            content = yaml.safe_load(f)

        if not isinstance(content, list):
            return violations

        for play in content:
            if not isinstance(play, dict):
                continue
            for task in _extract_tasks_from_play(play):
                if any(key in task for key in ['include', 'import_tasks', 'include_tasks']):
                    continue
                task_name = task.get('name', '<unnamed>')
                if is_sensitive_task(task) and not has_no_log(task):
                    violations.append((task_name, task))

    except yaml.YAMLError as e:
        print(f"Warning: Could not parse {file_path}: {e}", file=sys.stderr)
    except Exception as e:
        print(f"Warning: Error processing {file_path}: {e}", file=sys.stderr)

    return violations


def main():
    """Main entry point."""
    repo_root = Path(__file__).parent.parent
    roles_path = repo_root / "roles"
    playbooks_path = repo_root / "playbooks"

    if not roles_path.exists():
        print(f"Error: {roles_path} not found", file=sys.stderr)
        return 2

    print("=" * 70)
    print("Scanning for sensitive tasks without no_log: true")
    print("=" * 70)
    print()

    task_files = find_task_files(roles_path)
    playbook_files = sorted(playbooks_path.glob("*.yml")) if playbooks_path.exists() else []
    print(f"Found {len(task_files)} task files to scan")
    print(f"Found {len(playbook_files)} playbooks to scan")
    print()

    all_violations = []

    for task_file in task_files:
        violations = check_file(task_file)
        if violations:
            all_violations.append((task_file, violations))

    for playbook in playbook_files:
        violations = check_playbook(playbook)
        if violations:
            all_violations.append((playbook, violations))

    if all_violations:
        print("VIOLATIONS FOUND:")
        print("-" * 70)
        for task_file, violations in all_violations:
            relative_path = task_file.relative_to(repo_root)
            print(f"\n{relative_path}:")
            for task_name, task in violations:
                print(f"  ❌ {task_name}")
                # Show why it's considered sensitive
                task_str = str(task).lower()
                matched_patterns = [p for p in SENSITIVE_PATTERNS if re.search(p, task_str, re.IGNORECASE)]
                print(f"     Sensitive patterns: {', '.join(matched_patterns)}")

        print()
        print("=" * 70)
        print(f"FAIL: {len(all_violations)} files with violations")
        print()
        print("Fix by adding 'no_log: true' to sensitive tasks:")
        print()
        print("  - name: Task that handles secrets")
        print("    ansible.builtin.command: do_something")
        print("    register: result_with_secret")
        print("    no_log: true  # ← Add this")
        print()
        return 1
    else:
        print("✓ All sensitive tasks have no_log: true")
        print()
        return 0


if __name__ == "__main__":
    sys.exit(main())
