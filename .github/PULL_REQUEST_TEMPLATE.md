# Pull request

## What & why

<!-- Describe what this PR changes and the motivation behind it. -->

## Type of change

- [ ] Bug fix (non-breaking change that fixes an issue)
- [ ] New feature / role (non-breaking change that adds functionality)
- [ ] Breaking change (fix or feature that changes existing behaviour)
- [ ] Documentation only
- [ ] CI / tooling / chore
- [ ] Refactor (no functional change)

## Affected roles

<!-- List the role(s) touched, or "N/A" for collection-wide changes. -->

## Verification checklist

- [ ] `ansible-lint` passes on the changed roles/playbooks
- [ ] `yamllint` passes on the changed YAML
- [ ] `molecule test` passes for the relevant scenario(s)
- [ ] `meta/argument_specs.yml` updated (if variables changed)
- [ ] `README.md` updated (if behaviour or variables changed)
- [ ] Changelog fragment added under `changelogs/fragments/`

## Compliance impact

<!--
Note any change to enforcement vs audit behaviour and the compliance
controls affected (CIS, NIST 800-53, NIS2, STIG). State "None" if not
applicable.
-->
