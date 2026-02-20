---
title: GitHub Actions
description: Security, maintainability, and idiomatic checks for GitHub Actions workflows.
icon: material/github
tags:
  - GitHub Actions
  - CI/CD
  - YAML
---

# GitHub Actions

GitHub Actions workflow files in `.github/workflows/*.yml` and `.github/workflows/*.yaml` are auto-detected as `github-actions` and analyzed with workflow-specific zen principles.

## Principles Overview

| Rule ID | Principle | Category | Severity |
|---------|-----------|----------|:--------:|
| `gha-001` | Pin third-party actions by full commit SHA | Security | 9 |
| `gha-002` | Avoid `pull_request_target` checkout of untrusted head SHA | Security | 10 |
| `gha-003` | Do not expose secrets in run blocks | Security | 10 |
| `gha-004` | Avoid over-permissive or missing workflow permissions | Security | 8 |
| `gha-005` | Restrict `GITHUB_TOKEN` permissions per job | Security | 7 |
| `gha-006` | Split oversized workflows | Organization | 5 |
| `gha-007` | Avoid duplicated step sequences across jobs | Consistency | 5 |
| `gha-008` | Set `timeout-minutes` on jobs | Robustness | 6 |
| `gha-009` | Use `concurrency` to cancel stale runs | Performance | 5 |
| `gha-010` | Avoid rigid, hardcoded matrix values | Consistency | 4 |
| `gha-011` | Use `$GITHUB_OUTPUT` instead of `::set-output` | Idioms | 7 |
| `gha-012` | Use `$GITHUB_STATE` / `$GITHUB_ENV` instead of deprecated commands | Idioms | 7 |
| `gha-013` | Set explicit `shell` for `run` steps | Consistency | 4 |
| `gha-014` | Cache dependency installation steps | Performance | 4 |
| `gha-015` | Set artifact `retention-days` explicitly | Organization | 4 |

## CLI Usage

```bash
zen check .github/workflows/ci.yml
```

```bash
zen check .github/workflows/ci.yml --format json --out gha-report.json
```

You can also force language explicitly:

```bash
zen check .github/workflows/ci.yml --language github-actions
```

## MCP Usage

Use `language: "github-actions"` with the `analyze_zen_violations` MCP tool for workflow snippets.

## Notes

- Workflow parsing helpers are shared in `languages/ci_yaml_utils.py` for CI analyzers.
- Workflow path auto-detection is intentionally scoped to `.github/workflows/`.
