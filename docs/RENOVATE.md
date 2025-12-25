# Renovate Bot Configuration

## Overview

Este repositorio usa [Renovate Bot](https://github.com/renovatebot/renovate) para gestión automática de dependencias.

## Configuración

- **Archivo**: [`renovate.json`](../renovate.json)
- **Rama base**: `develop` (siguiendo GitFlow)
- **Horario**: Fines de semana (Europe/Madrid)
- **Auto-merge**: Habilitado para minor/patch updates

## Features Habilitadas

### 1. Auto-merge Inteligente ✅

```json
{
  "automerge": true,
  "automergeType": "pr",
  "platformAutomerge": true
}
```

- ✅ **Minor/Patch**: Auto-merge automático si todos los checks pasan
- ⚠️ **Major**: Requiere aprobación manual
- 🔒 **Pre-release (0.x.x)**: Requiere aprobación manual

### 2. Agrupación de PRs 📦

**GitHub Actions**: Todas las actualizaciones de GitHub Actions en un solo PR
```
chore(deps): update GitHub Actions (actions/checkout, actions/upload-artifact, etc.)
```

**Ansible**: Todas las dependencias de Ansible en un solo PR
```
chore(deps): update Ansible (ansible-core, ansible-lint, molecule)
```

### 3. Dependency Dashboard 📊

Renovate crea un Issue centralizado con todas las actualizaciones pendientes:
- 🔍 Ver todas las dependencias desactualizadas
- ⏸️ Pausar actualizaciones específicas
- 🔄 Forzar actualización de paquetes específicos

**Link**: [Dependency Dashboard](https://github.com/malpanez/security/issues)

### 4. Seguridad 🔒

- ✅ **Pin digests**: GitHub Actions se pinean con SHA digest para seguridad
- ✅ **Vulnerability alerts**: Actualizaciones de seguridad se priorizan
- ✅ **Stability days**: Espera 3 días antes de actualizar (evita versiones problemáticas)

### 5. GitFlow Integration 🌿

```
Renovate → PR a develop → CI checks → Auto-merge
                             ↓
                         (si pasan)
                             ↓
                          develop
```

## Reglas de Auto-merge

| Tipo Update | Auto-merge | Requiere Checks | Agrupado |
|-------------|-----------|-----------------|----------|
| **Patch** (1.0.x) | ✅ Sí | ✅ Todos | ✅ Sí |
| **Minor** (1.x.0) | ✅ Sí | ✅ Todos | ✅ Sí |
| **Major** (x.0.0) | ❌ No | ✅ Todos | ❌ No |
| **Pre-release** (0.x.x) | ❌ No | ✅ Todos | ❌ No |
| **Security** | ❌ No | ✅ Todos | ❌ No |

## Instalación

### 1. Instalar Renovate GitHub App

1. Ve a: https://github.com/apps/renovate
2. Click en **"Install"**
3. Selecciona el repositorio `malpanez/security`
4. Autoriza la app

### 2. Configuración Automática

Renovate detectará automáticamente `renovate.json` en la raíz del repo y aplicará la configuración.

### 3. Verificación

Dentro de ~1 hora, Renovate creará:
- ✅ Un "Dependency Dashboard" Issue
- ✅ PRs iniciales con actualizaciones pendientes (si las hay)

## Comandos en PRs

Puedes controlar Renovate comentando en los PRs:

| Comando | Descripción |
|---------|-------------|
| `@renovate rebase` | Forzar rebase del PR |
| `@renovate recreate` | Recrear el PR desde cero |
| `@renovate retry` | Reintentar crear el PR |

## Desactivar Temporalmente

Para pausar Renovate temporalmente:

1. Ve al Dependency Dashboard Issue
2. Marca el checkbox "Pause all updates"
3. O edita `renovate.json` y añade: `"enabled": false`

## Monitoring

### Ver todas las actualizaciones

```bash
# Ver PRs de Renovate abiertos
gh pr list --label "renovate"

# Ver el dashboard
gh issue list --label "renovate"
```

### Ver logs de Renovate

Los logs están disponibles en:
- GitHub Actions runs (si usas self-hosted)
- Renovate Dashboard: https://app.renovatebot.com/dashboard

## Troubleshooting

### Renovate no crea PRs

1. Verifica que la app esté instalada: https://github.com/apps/renovate
2. Revisa el Dependency Dashboard para errores
3. Verifica que `renovate.json` sea JSON válido:
   ```bash
   python3 -c "import json; json.load(open('renovate.json'))"
   ```

### PRs no se auto-mergean

1. Verifica que **todos** los checks pasen (incluyendo required checks)
2. Revisa que `platformAutomerge: true` esté habilitado
3. Verifica permisos de la Renovate app en el repo

### Demasiados PRs

Ajusta en `renovate.json`:
```json
{
  "prConcurrentLimit": 3,  // Máximo 3 PRs abiertos a la vez
  "schedule": ["on monday"]  // Solo lunes
}
```

## Comparación con Dependabot

| Feature | Dependabot | Renovate |
|---------|-----------|----------|
| Auto-merge nativo | ❌ | ✅ |
| Agrupación avanzada | ⚠️ | ✅ |
| Dependency Dashboard | ❌ | ✅ |
| GitFlow support | ⚠️ | ✅ |
| Configuración | Limitada | Muy flexible |
| Pin digests | ❌ | ✅ |
| Stability days | ❌ | ✅ |

## Recursos

- [Renovate Docs](https://docs.renovatebot.com/)
- [Configuration Options](https://docs.renovatebot.com/configuration-options/)
- [Presets](https://docs.renovatebot.com/config-presets/)
- [GitHub App](https://github.com/apps/renovate)

## Migración desde Dependabot

✅ **Completada**
- Dependabot desactivado: `.github/dependabot.yml` → `.github/dependabot.yml.disabled`
- Renovate configurado: `renovate.json`
- GitFlow respetado: PRs a `develop`
