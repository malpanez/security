# Workflow Map (Actual state)

This repo does have workflows in `.github/workflows/`. Those files are the source of truth.

Workflows present:
- `ci.yml`
- `ci-uv.yml`
- `ci-cd-enterprise.yml`
- `quality-gates.yml`
- `security-scan.yml`
- `docker-test.yml`
- `molecule-test.yml`
- `molecule-complete-stack.yml`
- `molecule-chaos.yml`
- `codeql.yml`
- `scorecard.yml`
- `branch-management.yml`

## Recommended local flows

1. Quick validation:
   - `./scripts/validate-all.sh`

2. Per-role testing:
   - `molecule test` inside each `roles/<role>/`

3. Full stack:
   - `molecule test -s complete_stack`

4. Basic chaos:
   - `molecule test -s chaos`

## Note

Some workflows may require secrets or specific permissions on GitHub. Review each YAML for triggers and requirements.
