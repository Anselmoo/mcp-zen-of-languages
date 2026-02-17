---
title: CLI Reference
description: The CLI is available as zen (short alias) or mcp-zen-of-languages.
icon: material/book-open-page-variant
tags:
  - CLI
  - Configuration
---

# CLI Reference

![CLI workflow illustration](../assets/illustration-cli.svg)

The CLI is available as `zen` (short alias) or `mcp-zen-of-languages`. It is the local/CI interface for the same analysis capabilities exposed through MCP tools. All commands support `--quiet` to suppress Rich panels and banners.

!!! info "MCP-first workflow"
    If you're using an MCP-capable editor or agent, start with [MCP Tools Reference](mcp-tools-reference.md). Use the CLI when you need local checks, export artifacts, or CI automation.

## Commands at a glance

| Command | Purpose |
|---------|---------|
| `zen init` | Initialize `zen-config.yaml` for your project |
| `zen report` | Analyze a directory and produce violation reports |
| `zen prompts` | Generate AI-ready remediation prompts |
| `zen list-rules` | Show all principles and severities for a language |
| `zen export-mapping` | Export rule-to-detector mapping as JSON |

## zen init

```bash
zen init [--force] [--yes] [--languages <lang>...] [--strictness relaxed|moderate|strict]
```

Interactive wizard that:

1. Detects languages in your project
2. Lets you choose a strictness level (affects thresholds)
3. Writes `zen-config.yaml`
4. Optionally creates `.vscode/mcp.json` for MCP integration

Use `--yes` in CI to skip interactive prompts and accept defaults.

**When to use**: First time setting up zen in a repository, or after adding a new language to your project.

## zen report

```bash
zen report <path> [--language <lang>] [--config <path>] \
  [--format markdown|json|both] [--out <file>] \
  [--export-json <file>] [--export-markdown <file>] [--export-log <file>] \
  [--include-prompts] [--skip-analysis] [--skip-gaps]
```

The primary analysis command. Scans all supported files in `<path>`, runs the detection pipeline, and outputs violations grouped by language and severity.

**Common workflows**:

=== "Local review"
    ```bash
    zen report . --out report.md
    ```
    Quick check before committing — scan the whole repo, write results to markdown.

=== "CI gate"
    ```bash
    zen report . --export-json report.json --format json
    # Exit code 1 if violations exceed severity_threshold
    ```
    Attach `report.json` as a build artifact for review.

=== "With prompts"
    ```bash
    zen report . --include-prompts --out full-report.md
    ```
    Include remediation prompts inline with each violation.

## zen prompts

```bash
zen prompts <path> [--language <lang>] [--config <path>] \
  [--mode remediation|agent|both] \
  [--export-prompts <file>] [--export-agent <file>] [--severity <n>]
```

Generate remediation prompts from analysis results. Two modes:

- **remediation** — Human-readable markdown prompts you can paste into AI chat
- **agent** — Structured JSON tasks for MCP agents to execute automatically
- **both** — Both outputs

Use `--severity` to filter: only violations at or above this severity get prompts.

## zen list-rules

```bash
zen list-rules <language>
```

Displays all zen principles for a language as a Rich table with severity badges. Useful for understanding what the analyzer checks before running it.

## zen export-mapping

```bash
zen export-mapping [--out <file>] [--languages <lang>...]
```

Exports the complete rule-to-detector mapping as JSON. Useful for auditing which detectors implement which principles, or for building custom tooling.

## Global options

| Flag | Description |
|------|-------------|
| `--quiet`, `-q` | Suppress banner, Rich panels, and decorative output |
| `--help` | Show help for any command |
| `--version` | Print version number |

## Exit codes

| Code | Meaning |
|------|---------|
| `0` | Success — no violations above the configured threshold |
| `1` | Violations found above the severity threshold |
| `2` | Invalid configuration or arguments |
