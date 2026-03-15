# Publication and Monetization Strategy Audit

## Goal

Define what should remain private, what should be public, what is suitable for
Ansible Galaxy, and what should be used as authority-building content for
`blog.homelabforge.dev`.

This document is not a code-quality report. It is a product and distribution
audit for the current repository state.

## Executive position

Recommended operating model:

- Keep the current repository private as the main commercial codebase.
- Publish only a smaller, cleaner public subset.
- Use Ansible Galaxy for mature, reusable roles with stable interfaces.
- Use the blog to publish architecture notes, tradeoffs, failure analysis, and
  implementation lessons.

Why:

- The repo contains reusable roles, but also operational runbooks, enterprise
  workflows, compliance delivery material, and implementation detail that is
  more valuable as service IP than as public source.
- Public reputation is better built with fewer high-quality artifacts than with
  one large repo that over-promises support or exposes delivery internals.

## Current blockers before broader public positioning

These issues should be corrected before using the project as a flagship public
product:

1. License inconsistency:
   - `LICENSE` is MIT.
   - `README.md` says MIT.
   - `galaxy.yml` declares `GPL-2.0-or-later`.

2. Support/validation claims are broader than the strongest currently validated
   public CI path.

3. Some public docs contradict each other on behavior and implementation
   details.

4. The repository currently mixes:
   - reusable roles,
   - customer-facing delivery material,
   - internal operational guidance,
   - enterprise CI/CD patterns,
   - compliance/evidence packaging.

## Decision criteria

Use these rules for every asset:

- `Public`: safe to expose without creating disproportionate support burden.
- `Galaxy`: good public API, narrow scope, useful outside your own estate,
  tested, documented, and maintainable.
- `Private`: commercially differentiating, operationally sensitive, or too
  coupled to your delivery model.
- `Blog`: strong material for authority-building, narrative, and case studies.

## Role matrix

| Role | Public | Galaxy | Private | Blog | Recommendation |
|---|---|---|---|---|---|
| `apache_hardening` | Yes | Yes | No | Yes | Good first-wave public role. Clear scope and low commercial leakage. |
| `apparmor` | Yes | Yes | No | Yes | Strong public role. Good authority signal for Linux hardening. |
| `audit_logging` | Limited | Later | Yes | Yes | Valuable, but keep in private stack until docs and support matrix are tighter. |
| `cis_baseline` | Limited | No | Yes | Yes | Better as audit methodology/blog material than as public reusable role. |
| `compliance_evidence` | No | No | Yes | Yes | High commercial value; keep private. Publish concepts, not implementation. |
| `kernel_hardening` | Yes | Yes | No | Yes | Strong Galaxy candidate and good reputation-builder. |
| `mysql_hardening` | Yes | Yes | No | Yes | Good public role if support statements are tightened. |
| `nginx_hardening` | Yes | Yes | No | Yes | Good first-wave public role. |
| `pam_mfa` | Limited | Later | Yes | Yes | High-risk/high-value role. Keep private until you want to support it seriously. |
| `pam_security` | Yes | Later | No | Yes | Public is fine; Galaxy after tightening docs and platform guarantees. |
| `security_capabilities` | No | No | Yes | Yes | Core differentiator; keep private. Explain the approach on the blog. |
| `selinux_enforcement` | Limited | Later | Yes | Yes | Strong role, but platform/behavior guarantees must be very explicit first. |
| `service_accounts_transfer` | No | No | Yes | Yes | Strong commercial differentiator; keep private. |
| `sshd_hardening` | Yes | Later | No | Yes | Public role, but needs documentation and behavior consistency before Galaxy. |
| `sudoers_baseline` | Yes | Later | No | Yes | Public is fine, but make policy contract very explicit first. |
| `system_hardening` | Yes | Yes | No | Yes | Strong Galaxy candidate. Broad but understandable and testable. |
| `tomcat_hardening` | Yes | Yes | No | Yes | Good public/Galaxy role if you want app-server credibility. |

## Recommended Galaxy first wave

Publish first:

- `kernel_hardening`
- `system_hardening`
- `apparmor`
- `apache_hardening`
- `nginx_hardening`
- `mysql_hardening`
- `tomcat_hardening`

Reason:

- Reasonably self-contained.
- Lower lockout risk than authentication stack roles.
- Easier to explain with stable defaults.
- Useful to a broad audience.

## Recommended public but not Galaxy yet

Expose later, once cleaned up and narrowed:

- `sshd_hardening`
- `sudoers_baseline`
- `pam_security`
- `audit_logging`
- `selinux_enforcement`

Gate before Galaxy:

- stable behavior contract,
- sharper platform support statements,
- examples per distro family,
- stronger warnings for risky settings,
- better migration notes.

## Keep private

Keep private in the main commercial repository:

- `pam_mfa`
- `security_capabilities`
- `service_accounts_transfer`
- `compliance_evidence`
- `cis_baseline`
- full-stack playbooks,
- enterprise workflows,
- operational runbooks,
- deployment sequencing,
- customer rollout patterns.

These are your implementation advantage and service leverage.

## Workflow matrix

| Workflow | Public repo | Private repo | Recommendation |
|---|---|---|---|
| `branch-management.yml` | No | Yes | Internal governance only. |
| `ci-cd-enterprise.yml` | No | Yes | Keep private; this exposes delivery model and enterprise process. |
| `ci-uv.yml` | Yes | Yes | Public-safe. Good confidence signal. |
| `ci.yml` | Limited | Yes | Either simplify or remove from public if redundant. |
| `codeql.yml` | Yes | Yes | Public-safe and useful for trust. |
| `docker-test.yml` | Yes | Yes | Public-safe; good signal for portability. |
| `kernel-vm-test.yml` | Yes | Yes | Public-safe once support text is aligned. |
| `molecule-chaos.yml` | Limited | Yes | Optional public. Keep only if it stays understandable. |
| `molecule-complete-stack.yml` | No | Yes | Too tied to private stack and high-complexity delivery path. |
| `molecule-test.yml` | Yes | Yes | Public-safe. |
| `quality-gates.yml` | Yes | Yes | Public-safe. |
| `scorecard.yml` | Yes | Yes | Public-safe. |
| `security-scan.yml` | Yes | Yes | Public-safe. |

## Documentation matrix

| Document area | Public | Private | Blog | Recommendation |
|---|---|---|---|---|
| `README.md` | Yes | No | No | Keep public, but tighten claims and scope. |
| `docs/architecture.md` | Yes | No | Yes | Good public material. |
| `docs/PLATFORM_SUPPORT.md` | Yes | No | Yes | Keep public, but align with actual validation model. |
| `docs/WORKFLOWS.md` | Yes | No | No | Public-safe if kept accurate and concise. |
| `docs/SECURITY_PHILOSOPHY.md` | Yes | No | Yes | Excellent blog/source material. |
| `docs/SECURITY_AND_QUALITY.md` | Yes | No | Yes | Good trust-building material. |
| `docs/controls.md` | Yes | No | Yes | Public-safe with careful wording around compliance claims. |
| `docs/compliance-mapping.md` | Limited | Yes | Yes | Public summary is fine; detailed implementation mapping is more commercial. |
| `docs/compliance-evidence.md` | Limited | Yes | Yes | Publish conceptually, keep implementation detail private. |
| `docs/evidence-pack.md` | No | Yes | Yes | Better private; strong commercial delivery artifact. |
| `docs/runbooks.md` | No | Yes | Limited | Keep private. Publish redacted patterns if useful. |
| `docs/operational_runbooks.md` | No | Yes | Limited | Keep private. |
| `docs/debian13-authentication-runbook.md` | No | Yes | Yes | Better as blog narrative than repo documentation. |
| `docs/BEST_PRACTICES_IMPROVEMENTS.md` | No | Yes | Yes | Mine for blog content, not product docs. |
| `docs/REAL_WORLD_SCENARIOS.md` | Limited | Yes | Yes | Good source for blog case studies. |
| `docs/quickstart.md` | Yes | No | No | Keep public. Essential for adoption. |
| `docs/capabilities-matrix.md` | Limited | Yes | Yes | Public summary only; internal decision logic stays private. |
| `docs/INFISICAL_VS_VAULT.md` | No | Yes | Yes | Strategic content, not core product docs. |
| `docs/SECRETS_BACKEND_AGNOSTIC.md` | Limited | Yes | Yes | Public concept summary is OK; implementation stays private. |
| `docs/GITHUB_BRANCH_PROTECTION.md` | No | Yes | No | Private operational governance. |
| `docs/RENOVATE.md` | Limited | Yes | No | Optional public if you want engineering transparency, otherwise private. |
| `docs/UV_SETUP.md` | Yes | No | No | Public-safe contributor material. |

## Playbook and scenario policy

Keep private:

- `playbooks/review.yml`
- `playbooks/site.yml`
- `playbooks/enforce-*`
- `playbooks/harden-system.yml`
- `playbooks/kernel-vm-test.yml`
- `molecule/complete_stack*`
- enterprise or staged rollout scenarios

Reason:

- These files encode your operational sequencing and delivery model, not just
  reusable building blocks.

Public-safe candidates:

- minimal examples,
- narrow role demo playbooks,
- simplified Molecule scenarios for single roles.

## Recommended repo split

### Private primary repo

Contains:

- full collection,
- complex auth stack,
- compliance evidence implementation,
- rollout playbooks,
- enterprise workflows,
- runbooks,
- customer-specific adaptation patterns.

### Public repo or public collection

Contains:

- mature standalone roles,
- minimal example playbooks,
- clean docs,
- public CI workflows,
- explicit support matrix,
- no operational runbooks,
- no full-stack delivery sequencing.

Recommended naming:

- `malpanez.security-core`
or
- `homelabforge.security_core`

## Commercial positioning

Use public content to prove:

- technical depth,
- discipline in testing,
- practical hardening knowledge,
- cross-distro experience,
- ability to reason about legacy and real environments.

Monetize on:

- security hardening assessments,
- rollout planning,
- exception design and compensating controls,
- legacy platform adaptation,
- implementation reviews,
- compliance-oriented evidence generation,
- remediation programs after audit findings.

## Blog strategy

Best topics to publish:

- containers vs VM validation for hardening roles,
- why `auditd` checks fail in containers,
- how to harden SSH without lockout,
- why MFA automation is hard across distros,
- legacy OS support without lying about CI coverage,
- what compliance evidence should and should not mean,
- using Ansible for hardening reviews before enforcement.

Each article should point to:

- a public Galaxy role,
- a small example repo,
- and a commercial offer for assessment/review work.

## Recommended next actions

1. Fix license inconsistency across `LICENSE`, `README.md`, and `galaxy.yml`.
2. Tighten support claims in public docs.
3. Resolve public documentation contradictions.
4. Move the current repo to private or reduce its public surface sharply.
5. Extract a public subset of roles into a smaller collection.
6. Publish the first Galaxy wave.
7. Build blog articles around the public roles and the CI/testing lessons.

## Suggested launch order

Phase 1:

- `kernel_hardening`
- `system_hardening`
- `apparmor`

Phase 2:

- `nginx_hardening`
- `apache_hardening`
- `mysql_hardening`
- `tomcat_hardening`

Phase 3:

- `sshd_hardening`
- `sudoers_baseline`
- `pam_security`

Phase 4:

- Consider whether `audit_logging`, `selinux_enforcement`, and `pam_mfa` should
  ever be public as code, or stay as private premium capability.
