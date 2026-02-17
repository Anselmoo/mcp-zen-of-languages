---
title: User Guide
description: Learn MCP workflows first, then CLI usage, configuration, language support, and violation interpretation.
icon: material/book-open-page-variant
tags:
  - MCP
  - CLI
  - Configuration
---

# User Guide

This guide starts with MCP workflows, then covers CLI usage, configuration, language support, and AI-assisted remediation[^1].

[^1]: Remediation workflows combine violation analysis with AI-generated fix suggestions via the [MCP Tools](mcp-tools-reference.md).

![User guide illustration](../assets/illustration-user-guide.svg)

<div class="grid cards" markdown>

-   :material-api:{ .lg .middle } **MCP Tools Reference**

    ---

    All tools, resources, and prompts available to MCP clients and agents.

    [MCP Tools Reference](mcp-tools-reference.md)

-   :material-console:{ .lg .middle } **CLI Reference**

    ---

    Every command, flag, and exit code — with usage scenarios.

    [CLI Reference](cli-reference.md)

-   :material-cog:{ .lg .middle } **Configuration**

    ---

    Tune thresholds per language, set CI profiles, and manage monorepo configs.

    [Configuration](configuration.md)

-   :material-translate:{ .lg .middle } **Languages**

    ---

    14 languages, 151 principles, 163 detectors — each with its own zen philosophy.

    [Languages](languages/index.md)

-   :material-alert-circle-check:{ .lg .middle } **Understanding Violations**

    ---

    How to read severity scores, what principles mean, and what to fix first.

    [Understanding Violations](understanding-violations.md)

-   :material-lightbulb-on:{ .lg .middle } **Prompt Generation**

    ---

    Generate AI-ready remediation prompts from analysis results.

    [Prompt Generation](prompt-generation.md)

-   :material-flask:{ .lg .middle } **Examples**

    ---

    End-to-end workflows: single file, project report, CI pipeline.

    [Examples](examples.md)

</div>

!!! tip "Recommended learning path"
    **New user?** Start with [MCP Tools Reference](mcp-tools-reference.md) → [CLI Reference](cli-reference.md) → [Configuration](configuration.md).
    **Adding a language?** Go directly to [Languages](languages/index.md) to find your language's principles and detectors.

=== "Single repo"
    Use one `zen-config.yaml` at the repository root and run `zen report .`.

=== "Monorepo"
    Keep one config per package and pass `--config path/to/zen-config.yaml` from each CI job.

## See Also

- [Getting Started](../getting-started/index.md) — Fast path from installation to first report.
- [Languages](languages/index.md) — Per-language principles, detectors, and style-guide provenance.
- [MCP Tools Reference](mcp-tools-reference.md) — All MCP tools, resources, and prompts at a glance.
- [API Reference](../api/index.md) — Python and MCP integration examples.
