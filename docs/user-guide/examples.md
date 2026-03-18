---
title: Examples
description: End-to-end workflow examples covering initialization, reporting, prompt generation, and MCP requests.
icon: material/book-open-page-variant
tags:
  - CLI
  - Configuration
---

# Examples

Practical workflows from initialization through analysis and remediation.

## Initialize a project

=== "Interactive"
    ```bash
    zen init
    ```
    The wizard detects languages in your project, asks for a strictness level, and writes `zen-config.yaml`.

=== "CI-friendly (non-interactive)"
    ```bash
    zen init --yes --languages python --languages typescript --strictness strict
    ```
    Skips all prompts and writes config with specified settings.

## Single-file analysis

```bash
zen check src/orders.py
```

Quick check on one file — useful during development before committing.

## Project report

=== "Terminal output"
    ```bash
    zen reports src
    ```
    Rich-formatted terminal output with severity badges and grouped violations.

=== "Markdown export"
    ```bash
    zen reports src --out report.md
    ```

=== "Full artifact set"
    ```bash
    zen reports src \
      --out report.md \
      --export-json report.json \
      --export-markdown report-export.md \
      --export-log report.log
    ```

## Perspective-aware workflows

### Rule-first default (`all`)

```bash
zen check src/orders.py --perspective all
```

This is the full runtime view: standard rule analysis, summaries, and any
additional perspective metadata the selected surface includes.

### Zen-only report

```bash
zen reports src --perspective zen --out zen-report.md
```

Use `zen` when you want the rule-level findings only. This keeps the report
focused on the current language or framework rules and omits dogma-analysis
payloads from the rendered result.

### Testing-family report

```bash
zen reports tests --perspective testing --out testing-report.md
```

The `testing` perspective works on recognised test-file paths and surfaces only
violations explicitly bound to the detected testing family, such as `pytest`,
`gotest`, `jest`, or `rspec`.

### Projection-family report

```bash
zen reports src/frontend --language react --perspective projection --as nextjs
```

Use `projection` when you want to view the subset of rule bindings that were
authored for another family target. The `--as` value is required because
projection is driven by explicit family bindings, not by file-path detection.

!!! info "Standalone dogma is runnable"
    `dogma` is now a first-class perspective. Use it when you want a
    dogma-focused result that keeps universal dogma analysis and filters out
    non-dogma violations.

## Prompt generation

```bash
zen prompts src --mode both \
  --export-prompts out/prompts.md \
  --export-agent out/prompts.json
```

This produces:

- `out/prompts.md` — Human-readable remediation prompts, organized by file and severity
- `out/prompts.json` — Structured agent tasks for MCP-connected AI agents

## List rules for a language

```bash
zen list-rules python
zen list-rules rust
```

Displays all zen principles with severity badges — useful for understanding what the analyzer checks.

## MCP server request

When running as an MCP server, tools accept JSON requests:

```json
{
  "tool": "analyze_zen_violations",
  "arguments": {
    "language": "python",
    "code": "def foo():\n    return 1\n"
  }
}
```

The response includes violations, severity scores, and remediation context.

For perspective-aware MCP workflows, prefer a file or directory target:

```json
{
  "tool": "generate_report",
  "arguments": {
    "target_path": "tests",
    "perspective": "testing",
    "include_prompts": true
  }
}
```

Snippet tools like `analyze_zen_violations` can use `all`, `zen`, or
`projection`, but `testing` requires a real file path so the runtime can detect
the test-family overlay.

## CI pipeline example

```bash
#!/bin/bash
set -e

# Initialize with strict settings
zen init --yes --strictness strict

# Run report — exits 1 if violations exceed threshold
zen reports . --export-json report.json --quiet

# Generate remediation prompts for the team
zen prompts . --mode remediation --export-prompts remediation.md --severity 6
```

## See Also

- [Quickstart](../getting-started/quickstart.md) — First-time setup
- [CLI Reference](cli-reference.md) — Full command reference
- [Configuration](configuration.md) — Tune thresholds and pipelines
