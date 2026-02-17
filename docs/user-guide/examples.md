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
    zen report src
    ```
    Rich-formatted terminal output with severity badges and grouped violations.

=== "Markdown export"
    ```bash
    zen report src --out report.md
    ```

=== "Full artifact set"
    ```bash
    zen report src \
      --out report.md \
      --export-json report.json \
      --export-markdown report-export.md \
      --export-log report.log
    ```

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

## CI pipeline example

```bash
#!/bin/bash
set -e

# Initialize with strict settings
zen init --yes --strictness strict

# Run report — exits 1 if violations exceed threshold
zen report . --export-json report.json --quiet

# Generate remediation prompts for the team
zen prompts . --mode remediation --export-prompts remediation.md --severity 6
```

## See Also

- [Quickstart](../getting-started/quickstart.md) — First-time setup
- [CLI Reference](cli-reference.md) — Full command reference
- [Configuration](configuration.md) — Tune thresholds and pipelines
```
