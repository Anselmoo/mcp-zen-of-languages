---
title: Configuration
description: Configuration is loaded from zen-config.yaml in the current directory or the nearest parent containing pyproject.toml.
icon: material/book-open-page-variant
tags:
  - CLI
  - Configuration
---

# Configuration

Configuration is loaded from `zen-config.yaml` in the current directory or the nearest parent containing `pyproject.toml`. Run `zen init` to generate one interactively.

## How configuration works

The config file controls three things:

1. **Which languages are enabled** — only enabled languages get analyzed
2. **Pipeline overrides** — tune thresholds per detector type
3. **Severity threshold** — set the minimum severity that triggers a non-zero exit code

## Basic example

=== "Python + TypeScript"
    ```yaml
    version: 1
    languages:
      python:
        enabled: true
        pipeline:
          - type: cyclomatic-complexity
            max_cyclomatic_complexity: 10
          - type: nesting-depth
            max_nesting_depth: 4
      typescript:
        enabled: true
        pipeline:
          - type: any-usage
            max_any_count: 0
    ```

=== "Strict CI profile"
    ```yaml
    version: 1
    severity_threshold: 6
    languages:
      python:
        enabled: true
        pipeline:
          - type: cyclomatic-complexity
            max_cyclomatic_complexity: 7
          - type: function-length
            max_function_length: 35
    ```

=== "Relaxed local development"
    ```yaml
    version: 1
    severity_threshold: 8
    languages:
      python:
        enabled: true
      typescript:
        enabled: true
      # All detectors use their default thresholds
    ```

## Choosing thresholds

!!! tip "Start relaxed, tighten over time"
    Begin with default thresholds. Run `zen report .` to see your baseline. Then lower limits on the detectors that matter most to your team.

| Strictness | Cyclomatic complexity | Nesting depth | Function length | Good for |
|-----------|:---------------------:|:-------------:|:---------------:|----------|
| **Relaxed** | 15 | 5 | 80 | Legacy codebases, initial adoption |
| **Moderate** | 10 | 4 | 50 | Active development, PR reviews |
| **Strict** | 7 | 3 | 35 | Greenfield projects, CI gates |

## Override behavior

Pipeline entries override detector defaults **by `type`**. If you list a detector in the pipeline, your values replace its defaults. If you omit a detector, it uses the values derived from the language's zen rules.

```yaml
pipeline:
  - type: cyclomatic-complexity
    max_cyclomatic_complexity: 7  # overrides default of 10
  # nesting-depth not listed → uses rule-derived default
```

## Per-language configuration

Each language has its own set of detector config fields. See the [config reference](../config.md) for all fields, or check the individual language pages:

- [Python detectors](languages/python.md) — 23 detectors with AST-based analysis
- [TypeScript detectors](languages/typescript.md) — 10 type-safety focused detectors
- [Rust detectors](languages/rust.md) — 13 safety and idiom detectors
- [All languages](languages/index.md) — Full comparison table

## Monorepo strategy

For monorepos with multiple languages or packages:

```bash
# Per-package config
zen report packages/frontend --config packages/frontend/zen-config.yaml
zen report packages/backend --config packages/backend/zen-config.yaml
```

Each package can have its own thresholds — strict for new code, relaxed for legacy modules.

## Environment variables

### Configuration

| Variable | Purpose |
|----------|---------|
| `ZEN_CONFIG_PATH` | Override config file location (useful for MCP server) |

### MCP Server (FastMCP)

When running `zen-mcp-server`, these FastMCP environment variables control server behavior:

| Variable | Purpose | Default |
|----------|---------|---------|
| `FASTMCP_DEBUG` | Enable debug mode with verbose logging | `false` |
| `FASTMCP_LOG_LEVEL` | Set logging level: `DEBUG`, `INFO`, `WARNING`, `ERROR` | `INFO` |
| `FASTMCP_SERVER_NAME` | Override server name in MCP protocol | `mcp-zen-of-languages` |

**Example:**
```json
{
  "env": {
    "ZEN_CONFIG_PATH": "${workspaceFolder}/zen-config.yaml",
    "FASTMCP_DEBUG": "true",
    "FASTMCP_LOG_LEVEL": "DEBUG"
  }
}
```

This enables verbose logging useful for troubleshooting MCP integration issues.

## See Also

- [CLI Reference](cli-reference.md) — All command flags
- [Config Reference](../config.md) — Auto-generated list of all config fields
