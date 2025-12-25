# Workflow Map

```mermaid
flowchart TD
  classDef trigger fill:#f6f6f6,stroke:#555,color:#111
  classDef wf fill:#e8f0fe,stroke:#1a73e8,color:#0b1f3a
  classDef job fill:#fff3e0,stroke:#ef6c00,color:#4a2c00

  subgraph Triggers
    P[push to develop]:::trigger
    PR[pull_request to develop]:::trigger
    S[schedule]:::trigger
    M[workflow_dispatch]:::trigger
    BP[branch_protection_rule]:::trigger
  end

  CIUV[ci-uv.yml]:::wf
  CI[ci.yml (manual)]:::wf
  CIENT[ci-cd-enterprise.yml (manual)]:::wf
  QG[quality-gates.yml]:::wf
  SEC[security-scan.yml]:::wf
  DT[docker-test.yml]:::wf
  MOL[molecule-test.yml]:::wf
  MCS[molecule-complete-stack.yml]:::wf
  CHAOS[molecule-chaos.yml]:::wf
  SCORE[scorecard.yml]:::wf
  BM[branch-management.yml]:::wf
  CODEQL[codeql.yml]:::wf

  P --> CIUV
  PR --> CIUV

  M --> CI
  M --> CIENT

  P --> QG
  PR --> QG

  P --> SEC
  PR --> SEC
  S --> SEC

  P --> DT
  PR --> DT
  M --> DT

  P --> MOL
  PR --> MOL
  M --> MOL

  S --> MCS
  M --> MCS

  M --> CHAOS

  BP --> SCORE
  S --> SCORE
  P --> SCORE
  M --> SCORE

  P --> BM
  PR --> BM

  P --> CODEQL
  PR --> CODEQL
  M --> CODEQL

  subgraph "ci-uv.yml jobs"
    CIUV_lint[lint]:::job --> CIUV_test[test-roles]:::job --> CIUV_build[build]:::job
  end
  CIUV --> CIUV_lint

  subgraph "ci.yml jobs"
    CI_lint[lint]:::job --> CI_test[test-roles]:::job --> CI_build[build-collection]:::job --> CI_install[test-install]:::job
  end
  CI --> CI_lint

  subgraph "security-scan.yml jobs"
    SEC_trivy[trivy-scan]:::job
    SEC_lint[ansible-lint-security]:::job
    SEC_secret[secret-scanning]:::job
    SEC_sbom[sbom-generation]:::job
    SEC_ansible[ansible-security-check]:::job
    SEC_summary[security-summary]:::job
    SEC_trivy --> SEC_summary
    SEC_lint --> SEC_summary
    SEC_secret --> SEC_summary
    SEC_sbom --> SEC_summary
    SEC_ansible --> SEC_summary
  end
  SEC --> SEC_trivy

  subgraph "docker-test.yml jobs"
    DT_platforms[test-platforms]:::job --> DT_compliance[test-compliance-report]:::job
    DT_scan[security-scan]:::job
  end
  DT --> DT_platforms

  subgraph "quality-gates.yml jobs"
    QG_pre[pre-commit-checks]:::job
    QG_ansible[ansible-best-practices]:::job
    QG_docs[documentation-quality]:::job
    QG_playbooks[playbook-syntax]:::job
    QG_security[security-hardening-checks]:::job
    QG_idem[idempotency-check]:::job
    QG_vars[variable-naming]:::job
  end
  QG --> QG_pre

  subgraph "codeql.yml jobs"
    CODEQL_analyze[analyze]:::job
  end
  CODEQL --> CODEQL_analyze
```

## Runbook

- Trigger chaos tests: Actions → `molecule-chaos` → Run workflow → verify `chaos` job passes.
- Trigger Docker platform tests: Actions → `docker-test` → Run workflow → review matrix failures by platform.
- Trigger security scans: Actions → `security-scan` → Run workflow → confirm SARIF uploads appear in Code scanning.
- Trigger quality gates: Actions → `quality-gates` → Run workflow → ensure lint/docs/idempotency checks pass.
- Trigger full CI: push/PR to `develop` runs `ci-uv`, `molecule-test`, `docker-test`, `security-scan`, `quality-gates`, and `codeql`.

## CI Strategy (Why This Split)

We keep high-signal checks on every push/PR and move long-running suites to scheduled/manual runs to avoid blocking delivery while still catching regressions.

- Always on push/PR: `ci-uv`, `molecule-test`, `docker-test`, `security-scan`, `quality-gates`, `codeql`.
- Scheduled/manual: `molecule-complete-stack` (expensive, long runtime).
- Manual only: `ci` and `ci-cd-enterprise` for deep audits or release gates.
