# GitHub Branch Protection Setup

This document provides instructions for enabling branch protection rules on the main branch to achieve TOP 0.01% security standards.

## Prerequisites

- Admin access to the GitHub repository
- OpenSSF Scorecard workflow configured (already done ✅)
- CI/CD workflows configured (already done ✅)

## Branch Protection Rules

### Navigate to Settings

1. Go to your repository on GitHub: `https://github.com/malpanez/security`
2. Click **Settings** → **Branches**
3. Click **Add branch protection rule**

### Configure Protection for `main`

#### Branch name pattern
```
main
```

#### Required Settings

**Protect matching branches:**

- ✅ **Require a pull request before merging**
  - ✅ Require approvals: **1**
  - ✅ Dismiss stale pull request approvals when new commits are pushed
  - ✅ Require review from Code Owners (optional)

- ✅ **Require status checks to pass before merging**
  - ✅ Require branches to be up to date before merging

  **Required status checks:**
  - `lint` (from CI with UV workflow)
  - `test-roles` (from CI with UV workflow)
  - `build` (from CI with UV workflow)
  - `ci-cd-enterprise` (from enterprise CI/CD)
  - `security-scan` (from security scanning)
  - `quality-gates` (from quality gates)
  - `Scorecard analysis` (from OpenSSF Scorecard)

- ✅ **Require conversation resolution before merging**

- ✅ **Require linear history** (optional, keeps history clean)

- ✅ **Do not allow bypassing the above settings**
  - ✅ Include administrators

- ✅ **Restrict who can push to matching branches** (optional)
  - Select specific teams/users if needed

#### Advanced Settings (Optional)

- ✅ **Require deployments to succeed before merging** (if you have deployment workflows)

- ⚠️ **Require signed commits** (see note below)

- ✅ **Lock branch** (prevents all pushes, use for release branches)

## Signed Commits (Optional)

### Why Skip for Now?

Signed commits require GPG key setup for all contributors. While this is a security best practice, it can create friction for contributors and automated processes.

**Recommendation:** Enable this later after:
1. Setting up GPG keys for all maintainers
2. Configuring bot accounts (like Dependabot) to sign commits
3. Adding documentation for contributors

### How to Enable Later

1. Follow GitHub's GPG key setup guide
2. Enable "Require signed commits" in branch protection
3. Update CI/CD workflows to sign commits
4. Document the process in CONTRIBUTING.md

## Verification

After enabling branch protection:

1. Try to push directly to main (should be blocked)
2. Create a test PR to verify required checks
3. Verify that all status checks must pass

## Current Workflows

The following workflows are configured and will run on PRs:

### Quality & Security
- **CI with UV** ([ci-uv.yml](../.github/workflows/ci-uv.yml))
  - Linting (ansible-lint, yamllint, ruff)
  - Role testing with Molecule
  - Collection build

- **OpenSSF Scorecard** ([scorecard.yml](../.github/workflows/scorecard.yml))
  - Security analysis
  - Weekly automated scans
  - SARIF upload to Security tab

- **Security Scan** ([security-scan.yml](../.github/workflows/security-scan.yml))
  - Gitleaks for secrets detection
  - SBOM generation with Syft
  - Dependency scanning

- **Quality Gates** ([quality-gates.yml](../.github/workflows/quality-gates.yml))
  - Code coverage
  - Complexity analysis
  - Security baseline checks

- **Enterprise CI/CD** ([ci-cd-enterprise.yml](../.github/workflows/ci-cd-enterprise.yml))
  - Multi-platform testing
  - Integration tests
  - Production readiness checks

## Monitoring

After setup, monitor:

1. **GitHub Security tab** for Scorecard results
2. **Actions tab** for workflow runs
3. **Pull Requests** to ensure rules are enforced

## Troubleshooting

### Status checks not appearing

- Wait for at least one workflow run to complete
- Check that workflows are configured with correct trigger events
- Verify workflow names match exactly

### Unable to merge despite passing checks

- Check if branch is up to date with main
- Verify all conversations are resolved
- Ensure you have required approvals

### Workflows failing

- Check workflow logs in Actions tab
- Verify dependencies are correctly installed
- Check for environment-specific issues

## Next Steps

After enabling branch protection:

1. ✅ Monitor first PR to verify all checks work
2. ✅ Update CONTRIBUTING.md with PR workflow
3. ✅ Consider enabling Dependabot for automated dependency updates
4. ✅ Set up branch naming conventions
5. ✅ Configure CODEOWNERS file for automated review requests

## References

- [GitHub Branch Protection Rules](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches/about-protected-branches)
- [OpenSSF Scorecard Documentation](https://github.com/ossf/scorecard)
- [Signed Commits Guide](https://docs.github.com/en/authentication/managing-commit-signature-verification)
