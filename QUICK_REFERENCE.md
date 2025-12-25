# ⚡ QUICK REFERENCE - malpanez.security TOP 0.01%

## 📁 Archivos del Plan

```
/workspace/
├── START_HERE.md               ← EMPEZAR AQUÍ (guía completa)
├── IMPLEMENTATION_PROMPT.md    ← Prompt para LLMs (especificaciones técnicas)
├── IMPLEMENTATION_CHECKLIST.md ← Checklist día a día (78 días)
├── QUICK_REFERENCE.md          ← Este archivo (referencia rápida)
└── AUDIT_REPORT.md            ← Reporte de auditoría original
```

---

## 🎯 SCORE OBJETIVO

| Categoría | Inicial | Objetivo | Gap |
|-----------|---------|----------|-----|
| Security | 7/10 | 10/10 | -3 |
| Testing | 6/10 | 10/10 | -4 |
| Reliability | 6/10 | 10/10 | -4 |
| Observability | 4/10 | 10/10 | -6 ⚠️ |
| Operations | 8/10 | 10/10 | -2 |
| Compliance | 8/10 | 10/10 | -2 |
| Performance | 7/10 | 10/10 | -3 |
| Documentation | 8/10 | 10/10 | -2 |
| **TOTAL** | **7.5/10** | **9.8/10** | **-2.3** |

---

## 🔴 TOP 5 DEFICIENCIAS CRÍTICAS

### 1. NO HAY END-TO-END TESTS
**Impacto**: Riesgo de lockout en producción
**Fix**: `molecule/complete_stack/` con 10 tests críticos
**Tiempo**: 5 días
**Prioridad**: 🔴 P0 BLOQUEANTE

### 2. SECRETOS SIN GESTIÓN
**Impacto**: Credentials en logs, git history
**Fix**: Integración HashiCorp Vault + AWS Secrets Manager
**Tiempo**: 8 días
**Prioridad**: 🔴 P0 BLOQUEANTE

### 3. NO HAY ATOMICIDAD
**Impacto**: Sistema en estado inconsistente si falla mid-deployment
**Fix**: Two-Phase Commit pattern
**Tiempo**: 6 días
**Prioridad**: 🔴 P0 BLOQUEANTE

### 4. ZERO OBSERVABILIDAD
**Impacto**: No sabemos si deployments son exitosos
**Fix**: Prometheus metrics + Grafana dashboards
**Tiempo**: 7 días
**Prioridad**: 🟠 P1 ALTA

### 5. NO HAY DRIFT DETECTION
**Impacto**: Cambios manuales violan compliance
**Fix**: AIDE + continuous compliance checking
**Tiempo**: 4 días
**Prioridad**: 🟠 P1 ALTA

---

## 📅 TIMELINE VISUAL

```
Semana 1-3:  [████████████░░░░░░░░░░░░] Testing Infrastructure
Semana 4-6:  [░░░░░░░░░░░░████████████░░] Seguridad Secretos
Semana 7-8:  [░░░░░░░░░░░░░░░░░░░░████░░] Atomicidad
Semana 9-10: [░░░░░░░░░░░░░░░░░░░░░░████] Observabilidad
Semana 11:   [░░░░░░░░░░░░░░░░░░░░░░░░██] Continuous Compliance
Semana 12:   [░░░░░░░░░░░░░░░░░░░░░░░░░█] Documentación
Semana 13:   [░░░░░░░░░░░░░░░░░░░░░░░░░█] Performance
Semana 14:   [░░░░░░░░░░░░░░░░░░░░░░░░░█] Supply Chain Security
             └──────────────────────────┘
             78 días laborables (12 semanas)
```

---

## 🚀 COMANDOS DE INICIO RÁPIDO

### Setup Inicial
```bash
# 1. Crear branch
git checkout -b feature/top-0.01-percent

# 2. Instalar dependencias
pip install -r requirements.txt
pip install molecule molecule-docker pytest hypothesis

# 3. Validar estado actual
./scripts/validate-all.sh

# 4. Abrir checklist
code IMPLEMENTATION_CHECKLIST.md
```

### Día 1: Primer Test
```bash
# Crear estructura Molecule
mkdir -p molecule/complete_stack

# Usar LLM para generar archivos (copia esto):
cat << 'EOF'
Genera molecule/complete_stack/molecule.yml según especificaciones
en IMPLEMENTATION_PROMPT.md TASK 1.1.

Incluye configuración para:
- 11 plataformas (Ubuntu, Debian, Rocky, Alma)
- Docker driver
- Privileged mode para systemd
- Provisioner Ansible
EOF

# Ejecutar test
molecule test -s complete_stack
```

### Día 6: Quick Win - no_log
```bash
# Copiar script de validación del IMPLEMENTATION_PROMPT.md
# Crear scripts/validate-no-log.py

# Ejecutar
python scripts/validate-no-log.py

# Fix violaciones (probablemente 50-100 tareas)
# Buscar: grep -r "password\|secret\|token" roles/ playbooks/
# Agregar: no_log: true

# Re-validar
python scripts/validate-no-log.py
# ✅ Objetivo: 0 violaciones
```

---

## 💻 PROMPT TEMPLATE PARA LLM

Copia esto y rellena los campos:

```markdown
# PROMPT PARA LLM

Soy desarrollador de malpanez.security, colección Ansible para hardening
de servidores Linux en producción (modifica PAM, SSH, sudo, SELinux, auditd).

## Contexto del Repositorio
- Path: /workspace
- Roles: security_capabilities, sshd_hardening, pam_mfa, sudoers_baseline,
         selinux_enforcement, audit_logging, compliance_evidence, cis_baseline
- Testing: Molecule + pytest
- CI/CD: GitHub Actions
- Plataformas: Ubuntu 18-24, Debian 10-12, Rocky 8-9, Alma 8-9

## Task a Implementar
[TASK_NAME]: _______________________

## Especificaciones
[COPIA SECCIÓN RELEVANTE DE IMPLEMENTATION_PROMPT.md AQUÍ]

## Requerimientos Específicos
1. Código production-ready (manejo de errores, validaciones)
2. Tests comprehensivos (happy path + failure scenarios)
3. Documentación inline (comentarios explicativos)
4. Idempotencia garantizada
5. Compatible con todas las plataformas
6. CRÍTICO: Este código maneja seguridad, un bug causa lockout

## Entregables Esperados
1. Archivos de código con paths absolutos (/workspace/...)
2. Tests de Molecule (verify.yml)
3. Documentación (README.md updates)
4. Validation scripts si aplica

## Acceptance Criteria
[COPIA ACCEPTANCE CRITERIA DE IMPLEMENTATION_PROMPT.md]

Por favor genera implementación completa siguiendo EXACTAMENTE las specs.
```

---

## 🧪 TESTING COMMANDS

```bash
# Molecule - Single role
cd roles/sshd_hardening
molecule test

# Molecule - Scenario específico
molecule test -s complete_stack

# Molecule - Plataforma específica
MOLECULE_DISTRO=ubuntu:22.04 molecule test

# Property tests
pytest tests/property_tests/ -v

# Chaos tests
molecule test -s chaos_network

# Full test suite (toma ~45 min)
./scripts/test-all-platforms.sh

# CI simulation
act -j matrix-test  # Requiere 'act' (GitHub Actions local)
```

---

## 📊 VALIDATION COMMANDS

```bash
# Syntax validation
ansible-playbook playbooks/site.yml --syntax-check

# Linting
ansible-lint --profile production

# YAML validation
yamllint -c .yamllint.yml .

# Secrets scanning
gitleaks detect --no-git

# no_log enforcement
python scripts/validate-no-log.py

# Comprehensive validation
./scripts/validate-all.sh
```

---

## 🎯 GATES DE CALIDAD

### GATE 1: Testing (Después de Semana 3)
```bash
# ¿Pasa todos estos?
molecule test -s complete_stack --all  # 11 plataformas
pytest tests/property_tests/           # 100+ tests
molecule test -s chaos_network         # Chaos tests
molecule test -s rollback_test         # Rollback tests

# Si TODO pasa ✅ → Continúa a GATE 2
# Si ALGO falla ❌ → NO CONTINÚES, fix primero
```

### GATE 2: Security (Después de Semana 6)
```bash
# ¿Pasa todos estos?
gitleaks detect --no-git               # 0 secretos encontrados
python scripts/validate-no-log.py      # 0 violaciones
grep -r "VAULT_TOKEN\|AWS_SECRET" .    # 0 matches (todos en Vault)
git log --show-signature               # 100% commits firmados

# Si TODO pasa ✅ → Continúa a GATE 3
# Si ALGO falla ❌ → NO CONTINÚES, fix primero
```

### GATE 3: Reliability (Después de Semana 8)
```bash
# ¿Pasa todos estos?
# Test: Kill process en cada checkpoint
# Test: Network failure mid-deployment
# Test: Disk full durante staging
# Resultado: 0 lockouts, rollback automático funciona

# Si TODO pasa ✅ → Continúa a FASE 4
# Si ALGO falla ❌ → NO CONTINÚES, fix primero
```

### GATE FINAL: Production Readiness
```bash
# Deploy to staging
ansible-playbook playbooks/enforce-staging.yml

# Monitor 48 horas
# - 0 incidents
# - 0 manual interventions
# - All health checks passing

# Compliance check
ansible-playbook playbooks/generate-compliance-report.yml
# → Todos los scores > 95%

# Si TODO OK ✅ → READY FOR PRODUCTION 🚀
```

---

## 📈 MÉTRICAS DE PROGRESO

### Tracking Semanal
```bash
# Calcular progreso
completed_tasks=$(grep -c "✅" IMPLEMENTATION_CHECKLIST.md)
total_tasks=300
progress=$((completed_tasks * 100 / total_tasks))

echo "Progreso: $progress%"
echo "Completadas: $completed_tasks / $total_tasks tasks"
```

### Tracking de Score
Actualizar semanalmente en IMPLEMENTATION_CHECKLIST.md:

```markdown
| Categoría | Inicial | Semana 3 | Semana 6 | Semana 9 | Semana 12 | Objetivo |
|-----------|---------|----------|----------|----------|-----------|----------|
| Security  | 7/10    | 7.5/10   | 9/10     | 9.5/10   | 10/10     | 10/10    |
| Testing   | 6/10    | 9/10     | 9.5/10   | 10/10    | 10/10     | 10/10    |
| ...       | ...     | ...      | ...      | ...      | ...       | ...      |
```

---

## 🆘 TROUBLESHOOTING RÁPIDO

| Problema | Comando de Debug | Fix Común |
|----------|------------------|-----------|
| Test falla en Ubuntu 24.04 | `molecule login -h ubuntu-2404` → debug manual | Package version mismatch → pin versions |
| Vault connection timeout | `curl -v $VAULT_ADDR/v1/sys/health` | Network/firewall issue → check connectivity |
| Molecule out of memory | `docker stats` | Increase Docker memory limit → 8GB+ |
| Pre-commit hook slow | `pre-commit run --verbose` | Disable offline mode temporarily |
| SSH validation fails | `sshd -t -f /tmp/staging/sshd_config` | Syntax error → check template |

---

## 📞 RECURSOS RÁPIDOS

### Documentación
- [Ansible Docs](https://docs.ansible.com)
- [Molecule Guide](https://molecule.readthedocs.io)
- [Hypothesis Tutorial](https://hypothesis.readthedocs.io)
- [Vault Docs](https://learn.hashicorp.com/vault)

### Templates Útiles
```bash
# Crear nuevo role con testing
molecule init role my_new_role --driver-name docker

# Crear nuevo scenario
molecule init scenario my_scenario --driver-name docker

# Crear ADR
cat > docs/adr/NNN-title.md << 'EOF'
# ADR NNN: Title

## Status: [Proposed|Accepted|Deprecated]

## Context
[Why this decision?]

## Decision
[What are we doing?]

## Consequences
[What are the implications?]

## Alternatives Considered
[What else did we consider?]
EOF
```

---

## 🎓 LEARNING RESOURCES

### Video Tutorials
- Ansible Molecule: https://www.youtube.com/watch?v=... (buscar latest)
- HashiCorp Vault: https://learn.hashicorp.com/tutorials/vault/getting-started-intro
- Property-Based Testing: https://www.youtube.com/watch?v=zi0rHwfiX1Q

### Interactive Labs
- Ansible Playgrounds: https://killercoda.com/ansible
- Vault Playground: https://play.instruqt.com/hashicorp/tracks/vault-basics

---

## 🔥 EMERGENCY CONTACTS

```bash
# Si nada funciona:
# 1. Haz rollback
git checkout main
git branch -D feature/top-0.01-percent

# 2. Restaura backups
# 3. Respira
# 4. Abre Issue en GitHub con:
#    - Qué intentaste
#    - Logs completos
#    - Output de validate-all.sh

# 5. Tag como [BLOCKER] si es crítico
```

---

## ✅ PRE-FLIGHT CHECK

Antes de empezar HOY:

```bash
# Check 1: Dependencies
command -v molecule || echo "❌ Install molecule"
command -v docker || echo "❌ Install docker"
command -v pytest || echo "❌ Install pytest"

# Check 2: Repository clean
git status | grep "nothing to commit" || echo "⚠️ Uncommitted changes"

# Check 3: Tests baseline
./scripts/validate-all.sh && echo "✅ Baseline passes"

# Check 4: Checklist ready
test -f IMPLEMENTATION_CHECKLIST.md && echo "✅ Checklist available"

# Si TODOS ✅ → START!
```

---

## 🚀 START NOW

```bash
# El comando que empieza todo:
git checkout -b feature/top-0.01-percent && \
code IMPLEMENTATION_CHECKLIST.md && \
echo "🚀 ¡Viaje al TOP 0.01% iniciado!" && \
echo "📅 Hoy: $(date)" > JOURNEY_LOG.md

# Ahora: IMPLEMENTATION_CHECKLIST.md → Día 1 → Task 1
```

**¡A por ello!** 💪

---

**Quick Reference v1.0** | **Last Updated**: 2025-12-09 | **License**: MIT
