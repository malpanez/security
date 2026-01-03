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

import sys
import re
from pathlib import Path
from typing import List, Tuple
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


def find_task_files(base_path: Path = Path("roles")) -> List[Path]:
    """Find all task YAML files in roles directory."""
    task_files = []
    for pattern in ["**/tasks/*.yml", "**/tasks/*.yaml"]:
        task_files.extend(base_path.glob(pattern))
    return sorted(task_files)


def is_sensitive_task(task: dict) -> bool:
    """Check if task handles sensitive data based on patterns."""
    # Convert task to string for pattern matching
    task_str = str(task).lower()

    # Check if any sensitive pattern matches
    for pattern in SENSITIVE_PATTERNS:
        if re.search(pattern, task_str, re.IGNORECASE):
            # Check if this is a whitelisted task type
            task_module = task.get('action', task.get('module', ''))
            if isinstance(task_module, str):
                for allowed in ALLOWED_TASKS:
                    if allowed in task_module:
                        return False
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


def check_file(file_path: Path) -> List[Tuple[str, dict]]:
    """
    Check a single task file for violations.

    Returns:
        List of (task_name, task_dict) tuples for violations
    """
    violations = []

    try:
        with open(file_path, 'r') as f:
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


def main():
    """Main entry point."""
    repo_root = Path(__file__).parent.parent
    roles_path = repo_root / "roles"

    if not roles_path.exists():
        print(f"Error: {roles_path} not found", file=sys.stderr)
        return 2

    print("=" * 70)
    print("Scanning for sensitive tasks without no_log: true")
    print("=" * 70)
    print()

    task_files = find_task_files(roles_path)
    print(f"Found {len(task_files)} task files to scan")
    print()

    all_violations = []

    for task_file in task_files:
        violations = check_file(task_file)
        if violations:
            all_violations.append((task_file, violations))

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
