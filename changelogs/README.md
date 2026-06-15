# Changelog fragments

This directory holds [antsibull-changelog](https://github.com/ansible-community/antsibull-changelog)
fragments. Every user-facing change must ship with a fragment so the
`CHANGELOG.rst` / `CHANGELOG.md` can be regenerated deterministically at
release time.

## Workflow

1. Create one `.yml` file per pull request (or per logical change) in this
   directory. The filename is arbitrary but should be descriptive and unique,
   e.g. `fix-sshd-backup-idempotence.yml` or `v1.3.0-new-roles.yml`.
2. Each fragment is a YAML mapping whose keys are changelog sections and whose
   values are lists of single-line entries written in past tense, reStructured-
   Text-friendly Markdown. End each entry with a period.
3. At release time the maintainer runs `antsibull-changelog release` to fold all
   fragments into the changelog. Because `keep_fragments: true` is set in
   `config.yaml`, fragments are retained after release for traceability.

## Available sections

| Section              | Use for                                                        |
| -------------------- | -------------------------------------------------------------- |
| `release_summary`    | A one-paragraph summary of the release (one fragment per cycle).|
| `major_changes`      | Significant, noteworthy changes that are not breaking.         |
| `minor_changes`      | New features, new roles, or small enhancements.               |
| `breaking_changes`   | Changes that require user action (porting guide material).     |
| `deprecated_features`| Features marked deprecated and scheduled for removal.          |
| `removed_features`   | Previously deprecated features now removed.                    |
| `security_fixes`     | Fixes for security vulnerabilities (with CVE/advisory refs).    |
| `bugfixes`           | Bug fixes that do not change documented behaviour.            |
| `known_issues`       | Documented limitations shipped with the release.              |

## Example fragment

```yaml
---
minor_changes:
  - firewall role - added default-deny host firewall support.
bugfixes:
  - sshd_hardening - fixed unbounded backup file accumulation.
```
