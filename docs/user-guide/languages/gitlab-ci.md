---
title: GitLab CI
description: Security, maintainability, and idiomatic checks for GitLab CI/CD pipelines.
icon: material/gitlab
tags:
  - GitLab CI
  - CI/CD
  - YAML
---

# GitLab CI

GitLab CI pipeline files named `.gitlab-ci.yml` or `.gitlab-ci.yaml` are auto-detected as `gitlab-ci` and analyzed with workflow-specific zen principles.

## Source Provenance

These pipeline principles are drawn from the [GitLab CI/CD documentation](https://docs.gitlab.com/ee/ci/) and operational hardening guidance in [GitLab CI/CD pipeline configuration reference](https://docs.gitlab.com/ee/ci/yaml/).

## Principles Overview

| Rule ID | Principle | Category | Severity |
|---------|-----------|----------|:--------:|
| `gitlab-ci-001` | Pin container image tags | Security | 8 |
| `gitlab-ci-002` | Avoid exposed variables in repository YAML | Security | 8 |
| `gitlab-ci-003` | Use `allow_failure` only with rules-based context | Security | 6 |
| `gitlab-ci-004` | Avoid god pipelines | Structure | 6 |
| `gitlab-ci-005` | Reduce duplicated `before_script` blocks | Consistency | 5 |
| `gitlab-ci-006` | Use interruptible pipelines | Performance | 5 |
| `gitlab-ci-007` | Model job DAG dependencies with `needs` | Performance | 5 |
| `gitlab-ci-008` | Prefer `rules` over `only`/`except` | Idioms | 6 |
| `gitlab-ci-009` | Cache dependency installs | Performance | 5 |
| `gitlab-ci-010` | Expire artifacts | Configuration | 5 |

## CLI Usage

```bash
zen check .gitlab-ci.yml
```

```bash
zen check .gitlab-ci.yml --format json --out gitlab-ci-report.json
```

You can also force language explicitly:

```bash
zen check .gitlab-ci.yml --language gitlab-ci
```

## MCP Usage

Use `language: "gitlab-ci"` with the `analyze_zen_violations` MCP tool for pipeline snippets.

## Notes

- Pipeline parsing helpers are shared in `utils/ci_yaml.py` for CI analyzers.
- Auto-detection recognises `.gitlab-ci.yml` and `.gitlab-ci.yaml` at the repository root, as well as YAML files inside a `gitlab-ci/` directory.
