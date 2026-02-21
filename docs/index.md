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

Every programming language has a philosophy — a sense of what "good code" looks like. Python has [PEP 20](https://peps.python.org/pep-0020/). Rust has ownership semantics. Go has [proverbs](https://go-proverbs.github.io/). TypeScript has the type system. MCP Zen of Languages **encodes these philosophies into automated analysis** across programming languages, workflow automation, and config formats — exposed as both a CLI and an MCP server.

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

-   :material-translate:{ .lg .middle } **Explore language coverage**

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

## Why MCP

--8<-- "README.md:why-mcp"

## Zen Philosophy

--8<-- "README.md:zen-philosophy"

## Quickstart

```bash
# MCP server (IDE/agent workflows)
uvx --from mcp-zen-of-languages zen-mcp-server

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

## Maturity Tiers

<div class="grid cards" markdown>

-   :material-check-all:{ .lg .middle } **Full Analysis**

    ---

    AST parsing, cyclomatic complexity, dependency graphs, maintainability index. The deepest analysis available.

    **Python**

-   :material-shield-check:{ .lg .middle } **Rule-Driven**

    ---

    Dedicated detectors with regex-based pattern matching. Each rule has its own detector class with configurable thresholds.

    **TypeScript · Rust · Go · JavaScript · CSS · Bash · PowerShell · Ruby · SQL · C++ · C# · Docker Compose · Dockerfile**

-   :material-language-markdown:{ .lg .middle } **Documentation & Markup**

    ---

    Markup-focused detectors for docs and technical writing quality, structure, and maintainability.

    **Markdown / MDX · LaTeX**

-   :material-source-branch:{ .lg .middle } **Workflow Automation**

    ---

    CI/CD-specific security and maintainability checks for pipeline files and reusable workflow patterns.

    **GitHub Actions**

-   :material-file-cog:{ .lg .middle } **Config Validation**

    ---

    Schema and structure-focused detectors for data formats. Checks consistency, naming conventions, and format-specific best practices.

    **JSON · TOML · XML · YAML**

</div>

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

## Choose Your Path

- **New user**: [Quickstart](getting-started/quickstart.md) → [Configuration](user-guide/configuration.md) → [Understanding Violations](user-guide/understanding-violations.md)
- **Maintainer**: [Project Analysis](user-guide/project-analysis.md) → [Prompt Generation](user-guide/prompt-generation.md) → [CLI Reference](user-guide/cli-reference.md)
- **Contributor**: [Contributing](contributing/index.md) → [Development](contributing/development.md) → [Architecture](contributing/architecture.md)
- **AI-agent workflow**: [MCP Integration](getting-started/mcp-integration.md) → [MCP Tools Reference](user-guide/mcp-tools-reference.md) → [Examples](user-guide/examples.md)

## Next Steps

- [Installation](getting-started/installation.md) — Setup options and requirements
- [Configuration](user-guide/configuration.md) — Tune thresholds for your codebase
- [Languages](user-guide/languages/index.md) — See every principle and detector by language
- [Understanding Violations](user-guide/understanding-violations.md) — How to read severity scores
- [Prompt Generation](user-guide/prompt-generation.md) — Generate AI-ready remediation guidance
