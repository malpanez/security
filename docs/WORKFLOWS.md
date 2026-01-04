# Workflow Map (Estado real)

Este repo sí tiene workflows en `.github/workflows/`. La fuente de verdad son esos archivos.

Workflows presentes:
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

## Flujos locales recomendados

1. Validación rápida:
   - `./scripts/validate-all.sh`

2. Testing por rol:
   - `molecule test` dentro de cada `roles/<role>/`

3. Stack completo:
   - `molecule test -s complete_stack`

4. Chaos básico:
   - `molecule test -s chaos`

## Nota

Algunos workflows pueden requerir secretos o permisos específicos en GitHub. Revisa cada YAML para conocer triggers y requisitos.
