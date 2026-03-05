# Renovate Bot Configuration

**Status**: requires installing the Renovate app on GitHub. CI workflows are in `.github/workflows/`.

## Overview

This repository uses [Renovate Bot](https://github.com/renovatebot/renovate) for automatic dependency management.

## Configuration

- **File**: [`renovate.json`](../renovate.json)
- **Base branch**: `develop` (following GitFlow)
- **Schedule**: Weekends (Europe/Madrid)
- **Auto-merge**: Enabled for minor/patch updates

## Enabled Features

### 1. Smart Auto-merge ✅

```json
{
  "automerge": true,
  "automergeType": "pr",
  "platformAutomerge": true
}
```

- ✅ **Minor/Patch**: Automatic auto-merge if all checks pass
- ⚠️ **Major**: Requires manual approval
- 🔒 **Pre-release (0.x.x)**: Requires manual approval

### 2. PR Grouping 📦

**GitHub Actions**: All GitHub Actions updates in a single PR
```
chore(deps): update GitHub Actions (actions/checkout, actions/upload-artifact, etc.)
```

**Ansible**: All Ansible dependencies in a single PR
```
chore(deps): update Ansible (ansible-core, ansible-lint, molecule)
```

### 3. Dependency Dashboard 📊

Renovate creates a centralised Issue with all pending updates:
- 🔍 View all outdated dependencies
- ⏸️ Pause specific updates
- 🔄 Force update of specific packages

**Link**: [Dependency Dashboard](https://github.com/malpanez/security/issues)

### 4. Security 🔒

- ✅ **Pin digests**: GitHub Actions are pinned with SHA digest for security
- ✅ **Vulnerability alerts**: Security updates are prioritised
- ✅ **Stability days**: Waits 3 days before updating (avoids problematic versions)

### 5. GitFlow Integration 🌿

```
Renovate → PR to develop → CI checks → Auto-merge
                               ↓
                           (if passing)
                               ↓
                            develop
```

## Auto-merge Rules

| Update Type | Auto-merge | Requires Checks | Grouped |
|-------------|-----------|-----------------|---------|
| **Patch** (1.0.x) | ✅ Yes | ✅ All | ✅ Yes |
| **Minor** (1.x.0) | ✅ Yes | ✅ All | ✅ Yes |
| **Major** (x.0.0) | ❌ No | ✅ All | ❌ No |
| **Pre-release** (0.x.x) | ❌ No | ✅ All | ❌ No |
| **Security** | ❌ No | ✅ All | ❌ No |

## Installation

### 1. Install Renovate GitHub App

1. Go to: https://github.com/apps/renovate
2. Click **"Install"**
3. Select the `malpanez/security` repository
4. Authorise the app

### 2. Automatic Configuration

Renovate will automatically detect `renovate.json` in the repo root and apply the configuration.

### 3. Verification

Within ~1 hour, Renovate will create:
- ✅ A "Dependency Dashboard" Issue
- ✅ Initial PRs with pending updates (if any)

## Commands in PRs

You can control Renovate by commenting on PRs:

| Command | Description |
|---------|-------------|
| `@renovate rebase` | Force rebase of the PR |
| `@renovate recreate` | Recreate the PR from scratch |
| `@renovate retry` | Retry creating the PR |

## Temporarily Disabling

To pause Renovate temporarily:

1. Go to the Dependency Dashboard Issue
2. Check the "Pause all updates" checkbox
3. Or edit `renovate.json` and add: `"enabled": false`

## Monitoring

### View all updates

```bash
# View open Renovate PRs
gh pr list --label "renovate"

# View the dashboard
gh issue list --label "renovate"
```

### View Renovate logs

Logs are available in:
- GitHub Actions runs (if using self-hosted)
- Renovate Dashboard: https://app.renovatebot.com/dashboard

## Troubleshooting

### Renovate does not create PRs

1. Verify the app is installed: https://github.com/apps/renovate
2. Check the Dependency Dashboard for errors
3. Verify `renovate.json` is valid JSON:
   ```bash
   python3 -c "import json; json.load(open('renovate.json'))"
   ```

### PRs do not auto-merge

1. Verify that **all** checks pass (including required checks)
2. Check that `platformAutomerge: true` is enabled
3. Verify Renovate app permissions on the repo

### Too many PRs

Adjust in `renovate.json`:
```json
{
  "prConcurrentLimit": 3,  // Maximum 3 open PRs at a time
  "schedule": ["on monday"]  // Mondays only
}
```

## Comparison with Dependabot

| Feature | Dependabot | Renovate |
|---------|-----------|----------|
| Native auto-merge | ❌ | ✅ |
| Advanced grouping | ⚠️ | ✅ |
| Dependency Dashboard | ❌ | ✅ |
| GitFlow support | ⚠️ | ✅ |
| Configuration | Limited | Very flexible |
| Pin digests | ❌ | ✅ |
| Stability days | ❌ | ✅ |

## Resources

- [Renovate Docs](https://docs.renovatebot.com/)
- [Configuration Options](https://docs.renovatebot.com/configuration-options/)
- [Presets](https://docs.renovatebot.com/config-presets/)
- [GitHub App](https://github.com/apps/renovate)

## Migration from Dependabot

✅ **Completed**
- Dependabot disabled: `.github/dependabot.yml` → `.github/dependabot.yml.disabled`
- Renovate configured: `renovate.json`
- GitFlow respected: PRs to `develop`
