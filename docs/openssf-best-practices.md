# OpenSSF Best Practices — Self-Assessment

Self-assessment against the [OpenSSF Best Practices Badge](https://www.bestpractices.dev)
*passing* criteria. To claim the live badge, register the repository at
bestpractices.dev (requires a maintainer GitHub login), record the project ID,
and add the badge to `README.md`.

| Criterion | Status | Evidence |
|-----------|--------|----------|
| **Basics** | | |
| Project description / homepage | ✅ | `README.md`, `galaxy.yml` |
| FLOSS license (OSI-approved) | ✅ | Apache-2.0 — `LICENSE`, `galaxy.yml` |
| Documentation (user + API) | ✅ | per-role `README.md` + `meta/argument_specs.yml`; `docs/`; antsibull-docs site (`docs.yml`) |
| English communication | ✅ | repo docs in English |
| **Change Control** | | |
| Public version-controlled source | ✅ | GitHub, GitFlow (develop/main) |
| Unique version numbering (semver) | ✅ | `galaxy.yml` version; `docs/RELEASING.md` |
| Release notes / changelog | ✅ | `CHANGELOG.md` + `changelogs/fragments/` (antsibull-changelog) |
| **Reporting** | | |
| Bug-reporting process | ✅ | `.github/ISSUE_TEMPLATE/` |
| Vulnerability-reporting process | ✅ | `SECURITY.md` (private disclosure) |
| **Quality** | | |
| Working build system | ✅ | `ansible-galaxy collection build`; CI |
| Automated test suite | ✅ | Molecule (per-role + complete_stack), `ansible-test sanity`, property tests |
| Tests run on new contributions (CI) | ✅ | `ci-uv.yml`, `quality-gates.yml`, `ansible-test.yml` on push/PR |
| New-functionality testing policy | ✅ | `CONTRIBUTING.md`, PR template checklist |
| Static analysis | ✅ | ansible-lint (production), yamllint, CodeQL, Grype, Gitleaks |
| **Security** | | |
| Secure development knowledge | ✅ | hardening-focused collection; `SECURITY.md` |
| Good cryptographic practices | ✅ | no hardcoded secrets (Gitleaks-gated); TLS/crypto-policy roles |
| Secured delivery against MITM | ✅ | HTTPS; pinned dependencies; signed + attested artifacts |
| Vulnerabilities fixed / patched | ✅ | Grype gate on criticals; Renovate; SBOM |
| **Analysis** | | |
| Supply-chain hardening | ✅ | all actions/images/hooks SHA-pinned; harden-runner; SLSA provenance; cosign signing — see `docs/RELEASING.md` |
| Dependency monitoring | ✅ | Renovate + Dependency Review + Grype |

**Beyond passing (silver/gold signals already met):** SHA-pinned dependencies,
SLSA build provenance, keyless artifact signing, least-privilege CI tokens,
CODEOWNERS-enforced review, and an OpenSSF Scorecard workflow.
