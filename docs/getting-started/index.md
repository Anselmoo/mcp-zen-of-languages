---
title: Getting Started
description: Set up MCP Zen of Languages and choose your initial workflow.
icon: material/rocket-launch
tags:
  - CLI
  - MCP
---

# Getting Started

You'll go from zero to your first analysis in under two minutes. The path is simple: install, initialize, analyze.

![Getting Started illustration](../assets/illustration-getting-started.svg)

<div class="grid cards" markdown>

-   :material-download:{ .lg .middle } **Install**

    ---

    Zero-install with `uvx` or one `pip install` command. Python 3.12+ required, no compiled extensions.

    [Installation](installation.md)

-   :material-flash:{ .lg .middle } **Quickstart**

    ---

    Run `zen init` and `zen report` to see your first violations, severities, and remediation prompts.

    [Quickstart](quickstart.md)

-   :material-api:{ .lg .middle } **MCP Integration**

    ---

    Connect to VS Code, Copilot, or any MCP-compatible client for AI-powered analysis workflows.

    [MCP Integration](mcp-integration.md)

</div>

!!! tip "Recommended path"
    Start with [Quickstart](quickstart.md) to understand the CLI output, then add [MCP Integration](mcp-integration.md) when you want AI-assisted remediation in your editor.

!!! info "Supported languages"
    MCP Zen of Languages currently supports :material-language-python: **Python**, :material-language-typescript: **TypeScript**, and :material-language-rust: **Rust**. See the [Language Guides](../user-guide/languages/index.md) for idiomatic rules and configuration per language.

## MCP-first 5-minute workflow

1. Start the server: `uvx --from mcp-zen-of-languages zen-mcp-server`
2. Connect your editor/client using the `zen-of-languages` server key.
3. Run `analyze_zen_violations` on one active file.
4. Generate remediation with `generate_prompts` for the highest-severity findings.
5. Re-run analysis to confirm the score improves.

## See Also

- [User Guide](../user-guide/index.md) — Deep-dive on configuration, languages, and remediation workflows.
- [Security](security.md) — Security posture, data handling expectations, and operational safety.
- [API Reference](../api/index.md) — Programmatic integration points for analyzers and server tools.
