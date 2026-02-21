<p align="center">
  <img src="https://github.com/Anselmoo/mcp-zen-of-languages/blob/59dcb31c4c3f38547f4a212be58704825177df19/docs/assets/logo.png" alt="MCP Zen of Languages" width="460" />
</p>

<h1 align="center">Zen of Languages</h1>

<p align="center">
  <em>🖌️ Write code the way the language intended.</em>
</p>

<p align="center">
  <a href="https://pypi.org/project/mcp-zen-of-languages"><img src="https://img.shields.io/pypi/v/mcp-zen-of-languages?style=flat-square&color=989cff" alt="PyPI"></a>
  <a href="https://pypi.org/project/mcp-zen-of-languages"><img src="https://img.shields.io/pypi/pyversions/mcp-zen-of-languages?style=flat-square" alt="Python"></a>
  <a href="https://github.com/Anselmoo/mcp-zen-of-languages/blob/main/LICENSE"><img src="https://img.shields.io/github/license/Anselmoo/mcp-zen-of-languages?style=flat-square" alt="License"></a>
  <a href="https://github.com/Anselmoo/mcp-zen-of-languages/actions"><img src="https://img.shields.io/github/actions/workflow/status/Anselmoo/mcp-zen-of-languages/cicd.yml?style=flat-square&label=CI" alt="CI"></a>
  <a href="https://anselmoo.github.io/mcp-zen-of-languages/"><img src="https://img.shields.io/badge/docs-mkdocs-c9b3ff?style=flat-square" alt="Docs"></a>
</p>

<p align="center">
  <a href="https://insiders.vscode.dev/redirect/mcp/install?name=zen-of-languages&config=%7B%22command%22%3A%22uvx%22%2C%22args%22%3A%5B%22--from%22%2C%22mcp-zen-of-languages%22%2C%22zen-mcp-server%22%5D%7D"><img src="https://img.shields.io/badge/VS_Code-Install_MCP-007ACC?style=flat-square&logo=visualstudiocode&logoColor=white" alt="Install in VS Code"></a>
  <a href="https://insiders.vscode.dev/redirect/mcp/install?name=zen-of-languages&config=%7B%22command%22%3A%22uvx%22%2C%22args%22%3A%5B%22--from%22%2C%22mcp-zen-of-languages%22%2C%22zen-mcp-server%22%5D%7D&quality=insiders"><img src="https://img.shields.io/badge/VS_Code_Insiders-Install_MCP-24bfa5?style=flat-square&logo=visualstudiocode&logoColor=white" alt="Install in VS Code Insiders"></a>
  <a href="https://github.com/Anselmoo/mcp-zen-of-languages/pkgs/container/mcp-zen-of-languages"><img src="https://img.shields.io/badge/Docker-GHCR-2496ED?style=flat-square&logo=docker&logoColor=white" alt="Docker"></a>
</p>

---

Multi-language architectural and idiomatic code analysis, exposed as an **MCP server** and a **CLI**. Zen of Languages codifies idiomatic best practices ("zen principles") into machine-readable rules and workflow checks across programming languages, CI automation, and configuration formats — so AI agents and developers get actionable, language-aware feedback in every review.

<!-- --8<-- [start:what-you-get] -->

- **215 zen principles** across programming, markup, workflow, and config domains
- **227 detector/check coverage points** with severity scoring
- **MCP server** for IDE and agent workflows (13 tools, 3 resources, 1 prompt)
- **CLI reports** with remediation prompts and JSON / Markdown export
- **Rule-driven pipelines** configurable per language and project
<!-- --8<-- [end:what-you-get] -->

## Why MCP for Zen Analysis

<!-- --8<-- [start:why-mcp] -->

MCP turns zen analysis from a standalone report into an interactive engineering loop. Instead of copying output between tools, your editor/agent can call zen tools directly, inspect violations in context, generate remediation prompts, and apply fixes in one flow.

- **Less context switching**: analyze, explain, and remediate without leaving your coding session.
- **Higher-fidelity fixes**: prompts are generated from structured violations, not ad-hoc lint text.
- **Team consistency**: MCP workflows make review behavior repeatable across IDEs and agents.

<!-- --8<-- [end:why-mcp] -->

## Zen Philosophy

<!-- --8<-- [start:zen-philosophy] -->

Zen of Languages treats idioms as engineering constraints, not style preferences. Every language guide encodes the practices that make code maintainable in that ecosystem, then scores violations by risk so teams can fix what matters first.

- **Language-native quality** over one-size-fits-all linting.
- **Architectural feedback** beyond formatting checks.
- **Actionable prioritization** through severity-guided remediation.

<!-- --8<-- [end:zen-philosophy] -->

## Quickstart

<!-- --8<-- [start:quickstart] -->

```bash
# MCP server (IDE/agent workflows)
uvx --from mcp-zen-of-languages zen-mcp-server

# CLI without installing (recommended)
uvx --from mcp-zen-of-languages zen --help

# Or install globally
pip install mcp-zen-of-languages

# Analyze a file (CLI)
zen report path/to/file.py

# Analyze a project with remediation prompts (CLI)
zen report path/to/project --include-prompts
```

<!-- --8<-- [end:quickstart] -->

## Naming Guide

Keep these names distinct to avoid setup confusion:

- **Package name**: `mcp-zen-of-languages` (for `pip install` and `uvx --from`)
- **CLI command**: `zen`
- **MCP server command**: `zen-mcp-server`
- **MCP client server key**: `zen-of-languages` (JSON config label in VS Code/Claude/Cursor)

## Installation

### One-Click (VS Code)

<!-- --8<-- [start:vscode-integration] -->

| Method                | VS Code                                                                                                                                                                                                                                                                                                                                 | VS Code Insiders                                                                                                                                                                                                                                                                                                                                         |
| --------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **UVX** (native)      | [![Install](https://img.shields.io/badge/Install-007ACC?style=flat-square&logo=python&logoColor=white)](https://insiders.vscode.dev/redirect/mcp/install?name=zen-of-languages&config=%7B%22command%22%3A%22uvx%22%2C%22args%22%3A%5B%22--from%22%2C%22mcp-zen-of-languages%22%2C%22zen-mcp-server%22%5D%7D)                            | [![Install](https://img.shields.io/badge/Install-24bfa5?style=flat-square&logo=python&logoColor=white)](https://insiders.vscode.dev/redirect/mcp/install?name=zen-of-languages&config=%7B%22command%22%3A%22uvx%22%2C%22args%22%3A%5B%22--from%22%2C%22mcp-zen-of-languages%22%2C%22zen-mcp-server%22%5D%7D&quality=insiders)                            |
| **Docker** (isolated) | [![Install](https://img.shields.io/badge/Install-007ACC?style=flat-square&logo=docker&logoColor=white)](https://insiders.vscode.dev/redirect/mcp/install?name=zen-of-languages&config=%7B%22command%22%3A%22docker%22%2C%22args%22%3A%5B%22run%22%2C%22--rm%22%2C%22-i%22%2C%22ghcr.io/anselmoo/mcp-zen-of-languages%3Alatest%22%5D%7D) | [![Install](https://img.shields.io/badge/Install-24bfa5?style=flat-square&logo=docker&logoColor=white)](https://insiders.vscode.dev/redirect/mcp/install?name=zen-of-languages&config=%7B%22command%22%3A%22docker%22%2C%22args%22%3A%5B%22run%22%2C%22--rm%22%2C%22-i%22%2C%22ghcr.io/anselmoo/mcp-zen-of-languages%3Alatest%22%5D%7D&quality=insiders) |

<!-- --8<-- [end:vscode-integration] -->

### Docker

```bash
# CLI via Docker
docker run --rm ghcr.io/anselmoo/mcp-zen-of-languages:latest zen --help

# MCP server via Docker
docker run --rm -i ghcr.io/anselmoo/mcp-zen-of-languages:latest
```

### From Source

```bash
git clone https://github.com/Anselmoo/mcp-zen-of-languages.git
cd mcp-zen-of-languages
uv sync --all-groups --all-extras

# Start the MCP server
zen-mcp-server

# Run a CLI report
zen report path/to/file.py
```

## MCP Tools

The server exposes **13 tools**, **3 resources**, and **1 prompt** for AI-assisted code analysis.

| Family            | Tools                                                                          | Purpose                                       |
| ----------------- | ------------------------------------------------------------------------------ | --------------------------------------------- |
| **Analysis**      | `analyze_zen_violations`, `analyze_repository`, `check_architectural_patterns` | Idiomatic and structural analysis             |
| **Reporting**     | `generate_prompts`, `generate_agent_tasks`, `generate_report`                  | Remediation guidance, task lists, gap reports |
| **Configuration** | `get_config`, `set_config_override`, `clear_config_overrides`                  | Read and tune thresholds at runtime           |
| **Metadata**      | `detect_languages`, `get_supported_languages`, `export_rule_detector_mapping`  | Discover languages, rules, detector coverage  |
| **Onboarding**    | `onboard_project`                                                              | Initialize `zen-config.yaml` for a project    |

See the full [MCP Tools Reference](https://anselmoo.github.io/mcp-zen-of-languages/user-guide/mcp-tools-reference/) for parameters, return types, and workflow diagrams.

### Use Cases

1. **AI Code Review** — Call `analyze_zen_violations` on a file, then `generate_prompts` for remediation instructions in a single editor round-trip.
2. **Project-Wide Gap Analysis** — `analyze_repository` scans a codebase, `generate_report` produces a Markdown/JSON report, and `generate_agent_tasks` creates a prioritised fix list.
3. **One-Click Onboarding** — `onboard_project` detects languages and writes a tuned `zen-config.yaml`, making analysis immediately project-aware.

## Supported Languages

| Tier             | Languages                        | Notes                                   |
| ---------------- | -------------------------------- | --------------------------------------- |
| **Stable**       | Python                           | Full parser + richest detector coverage |
| **Beta**         | TypeScript, Go, Rust, JavaScript | Rule-driven pipelines, partial parsing  |
| **Experimental** | Bash, PowerShell, Ruby, C++, C#  | Heuristic detectors                     |
| **Data/Config**  | YAML, TOML, JSON/JSON5, XML, GitHub Actions | Structure, schema, and workflow checks  |


## Configuration

Analysis pipelines are derived from language zen rules and merged with project overrides in `zen-config.yaml`. See the [Configuration Guide](https://anselmoo.github.io/mcp-zen-of-languages/user-guide/configuration/) for the full reference.

```bash
# Generate reports in multiple formats
zen report path/to/project --export-json report.json --export-markdown report.md
```

## Documentation

Full documentation is available at **[anselmoo.github.io/mcp-zen-of-languages](https://anselmoo.github.io/mcp-zen-of-languages/)**.

## Contributing

See [Adding a Language](https://anselmoo.github.io/mcp-zen-of-languages/contributing/adding-language/) and [Development Guide](https://anselmoo.github.io/mcp-zen-of-languages/contributing/development/) to get started.

## License

[MIT](https://github.com/Anselmoo/mcp-zen-of-languages/blob/main/LICENSE)

---

<p align="center">
  <img src="https://github.com/Anselmoo/mcp-zen-of-languages/blob/59dcb31c4c3f38547f4a212be58704825177df19/docs/assets/social-card-github.png" alt="Zen garden — sumi-e landscape" width="100%" />
</p>
