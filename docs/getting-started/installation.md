---
title: Installation
description: Install MCP Zen of Languages from PyPI, Docker, or source with Python 3.12+ and uv.
icon: material/rocket-launch
tags:
  - MCP
  - CLI
---

# Installation

## Prerequisites

| Requirement | Notes |
|-------------|-------|
| **Python 3.12+** | Union-type syntax and modern typing features are required |
| **uvx** or **pip** | `uvx` is recommended for zero-install usage; `pip` for global install |
| **Docker (optional)** | Useful when you want to run the server or CLI without a local Python environment |

## MCP server setup (recommended)

The fastest way to start using Zen of Languages is to add the MCP server to your editor or AI assistant. No global install required — `uvx` runs the server in an isolated environment.

### Claude Desktop

Add to `claude_desktop_config.json` (usually `~/Library/Application Support/Claude/` on macOS or `%APPDATA%\Claude\` on Windows):

```json
{
  "mcpServers": {
    "zen-of-languages": {
      "command": "uvx",
      "args": ["--from", "mcp-zen-of-languages", "mcp-zen-of-languages-server"]
    }
  }
}
```

### VS Code

Add to `.vscode/mcp.json` in your workspace, or use one of the one-click install badges below:

```json
{
  "servers": {
    "zen-of-languages": {
      "command": "uvx",
      "args": ["--from", "mcp-zen-of-languages", "mcp-zen-of-languages-server"]
    }
  }
}
```

| Method                | VS Code                                                                                                                                                                                                                                                                                                                                 | VS Code Insiders                                                                                                                                                                                                                                                                                                                                         |
| --------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **UVX** (native)      | [![Install](https://img.shields.io/badge/Install-007ACC?style=flat-square&logo=python&logoColor=white)](https://insiders.vscode.dev/redirect/mcp/install?name=zen-of-languages&config=%7B%22command%22%3A%22uvx%22%2C%22args%22%3A%5B%22--from%22%2C%22mcp-zen-of-languages%22%2C%22mcp-zen-of-languages-server%22%5D%7D)                            | [![Install](https://img.shields.io/badge/Install-24bfa5?style=flat-square&logo=python&logoColor=white)](https://insiders.vscode.dev/redirect/mcp/install?name=zen-of-languages&config=%7B%22command%22%3A%22uvx%22%2C%22args%22%3A%5B%22--from%22%2C%22mcp-zen-of-languages%22%2C%22mcp-zen-of-languages-server%22%5D%7D&quality=insiders)                            |
| **Docker** (isolated) | [![Install](https://img.shields.io/badge/Install-007ACC?style=flat-square&logo=docker&logoColor=white)](https://insiders.vscode.dev/redirect/mcp/install?name=zen-of-languages&config=%7B%22command%22%3A%22docker%22%2C%22args%22%3A%5B%22run%22%2C%22--rm%22%2C%22-i%22%2C%22ghcr.io/anselmoo/mcp-zen-of-languages%3Alatest%22%5D%7D) | [![Install](https://img.shields.io/badge/Install-24bfa5?style=flat-square&logo=docker&logoColor=white)](https://insiders.vscode.dev/redirect/mcp/install?name=zen-of-languages&config=%7B%22command%22%3A%22docker%22%2C%22args%22%3A%5B%22run%22%2C%22--rm%22%2C%22-i%22%2C%22ghcr.io/anselmoo/mcp-zen-of-languages%3Alatest%22%5D%7D&quality=insiders) |

### Cursor / Windsurf

Add to `.cursor/mcp.json` or `.windsurf/mcp.json` in your project root:

```json
{
  "mcpServers": {
    "zen-of-languages": {
      "command": "uvx",
      "args": ["--from", "mcp-zen-of-languages", "mcp-zen-of-languages-server"]
    }
  }
}
```

### Codex

Add to `~/.codex/config.toml`:

```toml
[mcp_servers."zen-of-languages"]
command = "uvx"
args = ["--from", "mcp-zen-of-languages", "mcp-zen-of-languages-server"]
enabled = true
```

Codex reads MCP servers from the global `~/.codex/config.toml` file rather than a workspace `.json` file. If you want to pin a config file, add `env = { ZEN_CONFIG_PATH = "/absolute/path/to/zen-config.yaml" }` under the same table.

### Claude Code

Install via the CLI:

```bash
claude mcp add zen-of-languages -- uvx --from mcp-zen-of-languages mcp-zen-of-languages-server
```

For the full integration guide — including environment variables, debugging, and troubleshooting — see [MCP Integration](mcp-integration.md).

## Install with Docker (no local Python)

```bash
# MCP server via Docker (default entrypoint)
docker run --rm -i ghcr.io/anselmoo/mcp-zen-of-languages:latest

# CLI via Docker
docker run --rm ghcr.io/anselmoo/mcp-zen-of-languages:latest mcp-zen-of-languages-cli --help
```

This image defaults to `mcp-zen-of-languages-server`.

## Official Docker image policy

1. Publish a GHCR image on each `vX.Y.Z` release tag.
2. Keep Docker tags as `latest` and `<major>.<minor>` channels only.
3. Patch releases overwrite the same `<major>.<minor>` image channel.
4. Add CI smoke checks for CLI and MCP server startup in the image pipeline.

## CLI — First Code Anamnesis & Local Development

The CLI is a powerful tool for **first code anamnesis** — an initial diagnostic sweep of any codebase. Use it to get a full-project health picture before wiring up MCP, or for local analysis, CI pipelines, and contributing to the project.

### Run without installing

```bash
# Run the CLI directly
uvx --from mcp-zen-of-languages mcp-zen-of-languages-cli --help
uvx --from mcp-zen-of-languages mcp-zen-of-languages-cli init
uvx --from mcp-zen-of-languages mcp-zen-of-languages-cli reports path/to/project

# Start the MCP server
uvx --from mcp-zen-of-languages mcp-zen-of-languages-server
```

This is the standard approach for MCP tools and requires no setup beyond having `uv` installed.

### Install from PyPI

For persistent installation:

```bash
pip install mcp-zen-of-languages
```

After install, the package-style commands are:

- `mcp-zen-of-languages-cli` — CLI for analysis, reports, and prompt generation
- `mcp-zen-of-languages` / `mcp-zen-of-languages-server` — MCP server entry points for AI agent integration

Legacy aliases remain available: `zen` and `zen-mcp-server`.

### Install from source (development)

```bash
git clone https://github.com/Anselmoo/mcp-zen-of-languages.git
cd mcp-zen-of-languages
uv sync --group dev --group docs
```

This installs all development dependencies (pytest, ruff, ty) and documentation tooling (Zensical).

## Verify installation

```bash
mcp-zen-of-languages-cli --version
mcp-zen-of-languages-cli --help
```

You should see the CLI help output listing `init`, `check`, `report`, and `prompts` subcommands.

## What's next

- [MCP Integration](mcp-integration.md) — Full setup guide with environment variables, debugging, and troubleshooting
- [Quickstart](quickstart.md) — Initialize a project and see your first analysis results

## Theme customization references

- https://www.mkdocs.org/user-guide/customizing-your-theme/
- https://zensical.org/docs/
- https://github.com/zensical/zensical
