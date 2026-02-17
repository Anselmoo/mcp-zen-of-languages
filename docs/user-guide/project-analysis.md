---
title: Project Analysis
description: Run whole-project analysis across directories with aggregated violation reports and JSON export.
icon: material/book-open-page-variant
tags:
  - CLI
  - Configuration
status: new
---

# Project Analysis

Single-file analysis is useful for quick checks, but real insights come from analyzing **entire projects** — where dependency patterns, cross-file violations, and aggregate metrics reveal the true health of a codebase.

## Running a project report

```bash
zen report path/to/project
```

This scans all supported files in the directory (recursively), runs the detection pipeline for each language, and produces:

- **Per-file violation tables** — grouped by language
- **Severity breakdown** — how many violations at each level
- **Project summary** — total violations, top offenders, and dominant issue categories

## Export options

=== "Markdown report"
    ```bash
    zen report path/to/project --out report.md
    ```
    Human-readable report with Rich formatting preserved.

=== "JSON export"
    ```bash
    zen report path/to/project --export-json out/report.json
    ```
    Structured output for CI artifacts, dashboards, or custom tooling.

=== "Full artifact set"
    ```bash
    zen report path/to/project \
      --out report.md \
      --export-json report.json \
      --export-markdown report-export.md \
      --export-log report.log
    ```
    All formats simultaneously.

## CI integration

```bash
zen report . --export-json report.json --quiet
```

- `--quiet` suppresses Rich panels and banners — clean output for CI logs
- Exit code `1` if violations exceed the configured `severity_threshold`
- Attach `report.json` as a build artifact for review

## Including prompts in reports

```bash
zen report path/to/project --include-prompts --out full-report.md
```

Adds remediation prompts inline with each violation — useful for review-ready documents.

## Language filtering

```bash
zen report path/to/project --language python
```

Analyze only files matching a specific language. Useful for focused reviews or when only one language is configured.

## What project analysis reveals

Unlike single-file linting, project-level analysis can detect:

- **Cross-file dependency patterns** (Python only, with AST analysis)
- **Aggregate complexity trends** — which modules are the most complex
- **Systemic issues** — patterns that repeat across many files
- **Coverage gaps** — files or directories with no analysis results

## See Also

- [CLI Reference](cli-reference.md) — Full `zen report` flag reference
- [Configuration](configuration.md) — Set `severity_threshold` for CI gates
- [Prompt Generation](prompt-generation.md) — Generate fix instructions from reports
