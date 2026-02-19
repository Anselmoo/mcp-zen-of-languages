---
title: Installation
description: Install MCP Zen of Languages from PyPI, Docker, or source with Python 3.12+ and uv.
icon: material/rocket-launch
tags:
  - CLI
  - MCP
---

# Installation

## Prerequisites

| Requirement | Notes |
|-------------|-------|
| **Python 3.12+** | Union-type syntax and modern typing features are required |
| **uvx** or **pip** | `uvx` is recommended for zero-install usage; `pip` for global install |
| **Docker (optional)** | Useful when you want to run the CLI without a local Python environment |

## Run without installing (recommended)

The recommended approach is to use `uvx` which runs the tool in an isolated environment without installation:

```bash
# Run the CLI directly
uvx --from mcp-zen-of-languages zen --help
uvx --from mcp-zen-of-languages zen init
uvx --from mcp-zen-of-languages zen report path/to/project

# Start the MCP server
uvx --from mcp-zen-of-languages zen-mcp-server
```

This is the standard approach for MCP tools and requires no setup beyond having `uv` installed.

## Install from PyPI

For persistent installation:

```bash
pip install mcp-zen-of-languages
```

After install, two commands are available:

- `zen` — CLI for analysis, reports, and prompt generation
- `zen-mcp-server` — MCP server for AI agent integration

## Install from source (development)

```bash
git clone https://github.com/Anselmoo/mcp-zen-of-languages.git
cd mcp-zen-of-languages
uv sync --group dev --group docs
```

This installs all development dependencies (pytest, ruff, ty) and documentation tooling (Zensical).

## Install with Docker (no local Python)

```bash
docker run --rm ghcr.io/anselmoo/mcp-zen-of-languages:latest zen --help
```

Run the MCP server entrypoint:

```bash
docker run --rm -i ghcr.io/anselmoo/mcp-zen-of-languages:latest
```

This image defaults to `zen-mcp-server`.

## Official Docker image policy

1. Publish a GHCR image on each `vX.Y.Z` release tag.
2. Keep Docker tags as `latest` and `<major>.<minor>` channels only.
3. Patch releases overwrite the same `<major>.<minor>` image channel.
4. Add CI smoke checks for CLI and MCP server startup in the image pipeline.

## Verify installation

```bash
zen --version
zen --help
```

You should see the CLI help output listing `init`, `check`, `report`, and `prompts` subcommands.

## What's next

Run [Quickstart](quickstart.md) to initialize a project and see your first analysis results.

## Theme customization references

- https://www.mkdocs.org/user-guide/customizing-your-theme/
- https://zensical.org/docs/
- https://github.com/zensical/zensical
