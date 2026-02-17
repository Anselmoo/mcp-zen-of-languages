---
title: MCP Zen of Languages
description: Multi-language code analysis with calm, high-signal remediation workflows for CLI and MCP.
icon: material/home
template: home.html
tags:
  - MCP
  - CLI
  - API
---

# MCP Zen of Languages

Every programming language has a philosophy — a sense of what "good code" looks like. Python has [PEP 20](https://peps.python.org/pep-0020/). Rust has ownership semantics. Go has [proverbs](https://go-proverbs.github.io/). TypeScript has the type system. MCP Zen of Languages **encodes these philosophies into automated analysis** — 151 zen principles across 14 languages, enforced by 163 detectors, exposed as both a CLI and an MCP server.

<div class="grid cards" markdown>

-   :material-rocket-launch:{ .lg .middle } **Start fast**

    ---

    Install, initialize, and run your first analysis in under two minutes.

    [Quickstart](getting-started/quickstart.md)

-   :material-console:{ .lg .middle } **Use the CLI**

    ---

    Run `zen` for local checks, exports, and CI automation with JSON/Markdown outputs.

    [CLI Reference](user-guide/cli-reference.md)

-   :material-api:{ .lg .middle } **Integrate via MCP**

    ---

    Connect to VS Code, Copilot, and other MCP-compatible clients for AI-assisted analysis.

    [MCP Integration](getting-started/mcp-integration.md)

-   :material-translate:{ .lg .middle } **Explore 14 languages**

    ---

    From Python's PEP 20 to Rust's ownership idioms — each language has its own zen.

    [Languages](user-guide/languages/index.md)

-   :material-wrench-cog:{ .lg .middle } **Solution workflow**

    ---

    Analyze code, generate remediation prompts, and turn findings into actionable fixes.

    [Project Analysis](user-guide/project-analysis.md)

</div>

!!! tip "Why zen?"
    Most linters focus on formatting. Zen analysis goes deeper — it detects **architectural** and **idiomatic** issues: god classes, circular dependencies, callback hell, unsafe blocks, monkey-patching. The goal isn't nitpicking commas; it's surfacing the structural problems that slow teams down.

## Quickstart

```bash
# Run without installing (recommended)
uvx --from mcp-zen-of-languages zen init
uvx --from mcp-zen-of-languages zen report path/to/project

# Or install globally
pip install mcp-zen-of-languages
zen init
zen report path/to/project
```

## What You Get

--8<-- "README.md:what-you-get"

## MCP Tools at a Glance

![MCP tools workflow illustration](assets/illustration-mcp-tools.svg)

The MCP server exposes **13 tools** across five families, plus **3 resources** and **1 prompt**.

<div class="grid cards" markdown>

-   :material-magnify:{ .lg .middle } **Analysis** (3 tools)

    ---

    `analyze_zen_violations` · `analyze_repository` · `check_architectural_patterns`

-   :material-file-document-outline:{ .lg .middle } **Reporting** (3 tools)

    ---

    `generate_prompts` · `generate_agent_tasks` · `generate_report`

-   :material-cog-outline:{ .lg .middle } **Configuration** (3 tools)

    ---

    `get_config` · `set_config_override` · `clear_config_overrides`

-   :material-tag-text-outline:{ .lg .middle } **Metadata** (3 tools)

    ---

    `detect_languages` · `get_supported_languages` · `export_rule_detector_mapping`

-   :material-rocket-launch-outline:{ .lg .middle } **Onboarding** (1 tool)

    ---

    `onboard_project` — initialise `zen-config.yaml` for any repository

</div>

[:octicons-arrow-right-24: Full MCP Tools Reference](user-guide/mcp-tools-reference.md)

## Next Steps

- [Installation](getting-started/installation.md) — Setup options and requirements
- [Configuration](user-guide/configuration.md) — Tune thresholds for your codebase
- [Languages](user-guide/languages/index.md) — See every principle and detector by language
- [Understanding Violations](user-guide/understanding-violations.md) — How to read severity scores
- [Prompt Generation](user-guide/prompt-generation.md) — Generate AI-ready remediation guidance
