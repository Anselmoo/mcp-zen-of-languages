---
title: Quickstart
description: Initialize your project and run your first zen analysis in under two minutes.
icon: material/rocket-launch
tags:
  - CLI
  - MCP
---

# Quickstart

Three commands, two minutes, and you'll have a full analysis with violations, severity scores, and remediation prompts.

## 1. Initialize configuration

```bash
zen init  # (1)!
```

1. Creates `zen-config.yaml` with sensible defaults for all 14 languages. Can also bootstrap `.vscode/mcp.json` for MCP integration.

This creates a `zen-config.yaml` in your project root. It enables all languages and sets default thresholds — you can [tune these later](../user-guide/configuration.md).

## 2. Run a report

=== "Markdown report"
    ```bash
    zen report path/to/project --out report.md  # (1)!
    ```
    1. Scans all supported files, groups violations by language and severity, and outputs a human-readable report.

=== "JSON export"
    ```bash
    zen report path/to/project --export-json out/report.json
    ```
    Structured output for CI artifacts, dashboards, or downstream automation.

The report tells you **what's wrong**, **how severe it is** (1–10), and **which zen principle** was violated.

## 3. Generate remediation prompts

```bash
zen prompts path/to/project --mode both \
  --export-prompts out/prompts.md \
  --export-agent out/prompts.json
```

This produces two outputs:

- **Markdown prompts** — Human-readable remediation guidance you can paste into any AI chat
- **JSON agent tasks** — Structured instructions for MCP-connected AI agents to fix violations automatically

???+ tip "CI integration"
    Export JSON in CI and attach it as a build artifact. Developers can feed the prompts to Copilot or GPT to resolve violations in context.

???+ info "Path strategy"
    Point commands at the repository root so import analysis and dependency detection can see the full project.

## What you'll see

A typical report surfaces violations like:

- **Severity 8**: Cyclomatic complexity exceeding threshold (Python)
- **Severity 7**: Bare `unwrap()` calls without error context (Rust)
- **Severity 6**: Missing error return checks (Go)
- **Severity 5**: Implicit `any` types (TypeScript)

Each violation links to a specific zen principle — not a generic lint rule, but a language-community standard for what "good code" means.

## Next steps

- [Configuration](../user-guide/configuration.md) — Tune thresholds for your codebase
- [Languages](../user-guide/languages/index.md) — See every principle and detector by language
- [MCP Integration](mcp-integration.md) — Connect to VS Code for AI-assisted remediation
