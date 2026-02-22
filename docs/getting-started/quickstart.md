---
title: Quickstart
description: Initialize your project and run your first zen analysis in under two minutes.
icon: material/rocket-launch
tags:
  - MCP
  - CLI
---

# Quickstart

Two minutes to your first analysis — whether you're working through an AI assistant or the CLI.

!!! info "Command naming cheat sheet"
    - Package for install/uvx: `mcp-zen-of-languages`
    - CLI command: `zen`
    - MCP server command: `zen-mcp-server`
    - MCP config server key: `zen-of-languages`

## MCP path (editor + AI agent)

The fastest way to use Zen of Languages is through an MCP-compatible client like VS Code with Copilot, Claude Desktop, or Cursor. Once the server is configured (see [Installation](installation.md)), ask your agent to analyse code directly.

### Example conversation

> **You:** Run zen analysis on `src/auth/login.py`
>
> **Agent:** _(calls `analyze_zen_violations`)_
> Found 3 violations:
>
> - **Severity 8** — Cyclomatic complexity of 14 exceeds threshold of 10 in `authenticate()`
> - **Severity 6** — Function `authenticate()` is 85 lines (max 50)
> - **Severity 5** — Nesting depth of 4 exceeds threshold of 3
>
> **You:** Fix the highest-severity violation
>
> **Agent:** _(calls `generate_prompts`, then applies changes)_
> Extracted the credential-validation logic into a `_validate_credentials()` helper, reducing `authenticate()` complexity from 14 to 7.

No CLI needed — the agent handles analysis and remediation in a single editor session.

### MCP quick-start steps

1. Add the server to your client config (see [Installation](installation.md) or [MCP Integration](mcp-integration.md)).
2. Open a project and ask your agent: _"Run zen analysis on this file."_
3. Review violations and ask: _"Generate remediation for the top finding."_
4. Re-run analysis to confirm the score improves.

## CLI path — first code anamnesis

The CLI is the ideal tool for **first code anamnesis**: an initial diagnostic sweep that reveals the overall health of a codebase before you dive into individual files. Run a single command and get a severity-ranked map of every architectural smell, idiomatic violation, and remediation opportunity across all supported languages.

### 1. Initialize configuration

```bash
zen init  # (1)!
```

1. Creates `zen-config.yaml` with sensible defaults for all 14 languages. Can also bootstrap `.vscode/mcp.json` for MCP integration.

This creates a `zen-config.yaml` in your project root. It enables all languages and sets default thresholds — you can [tune these later](../user-guide/configuration.md).

### 2. Run a report

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

### 3. Generate remediation prompts

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

- [MCP Integration](mcp-integration.md) — Full setup guide for VS Code, Claude Desktop, Cursor, and more
- [Configuration](../user-guide/configuration.md) — Tune thresholds for your codebase
- [Languages](../user-guide/languages/index.md) — See every principle and detector by language
