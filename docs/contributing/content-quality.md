---
title: Content Quality Guide
description: Hybrid docs-from-code ownership model, editorial standards, and release quality checks.
icon: material/text-box-check
tags:
  - API
  - Configuration
---

# Content Quality Guide

Use a hybrid source-of-truth model:

- **Code/docstrings own technical truth** (CLI surface, MCP tools, config fields, API signatures).
- **Markdown owns onboarding and narrative** (why/when guidance, philosophy, workflows, contributor context).

## Baseline audit snapshot

High-impact gaps this guide addresses:

1. MCP rationale not consistently visible on high-traffic landing pages.
2. Zen philosophy messaging varied between README and docs home.
3. Workflow pages lacked a short end-to-end MCP remediation loop.
4. Source ownership for generated pages was implicit, not explicit.
5. No dedicated quality gate for required strategic sections.

## Source-of-truth map

| Surface | Source of truth | Generation mechanism |
| --- | --- | --- |
| `docs/user-guide/cli-reference.md` | `src/mcp_zen_of_languages/cli.py` docstrings + command metadata | `uv run python scripts/generate_cli_docs.py` |
| `docs/user-guide/mcp-tools-reference.md` | `src/mcp_zen_of_languages/server.py` tool/resource/prompt metadata | `uv run python scripts/generate_mcp_tools_docs.py` |
| `docs/config.md` | `AnalyzerConfig` model fields | `uv run python scripts/generate_config_docs.py` |
| `docs/api/*.md` | Module/class/function docstrings | `mkdocstrings` via `:::` directives |
| README/docs home philosophy and MCP positioning | Markdown snippets in `README.md` | `--8<--` snippet includes in docs pages |

## Editorial standards

### Voice and structure

- Keep sections concise and actionable.
- Prefer section flow: **problem -> action -> example -> see also**.
- Make MCP guidance explicit: what tool to call, why, and expected outcome.

### Terminology consistency

- Package: `mcp-zen-of-languages`
- CLI command: `zen`
- MCP server command: `zen-mcp-server`
- MCP server key: `zen-of-languages`

### Required strategic sections

- `README.md`: `## Why MCP for Zen Analysis` and `## Zen Philosophy`
- `docs/index.md`: `## Why MCP`, `## Zen Philosophy`, and `## Choose Your Path`

## Release checklist

Before release or major docs updates:

1. Regenerate code-derived docs pages.
2. Run `uvx pre-commit run --all-files`.
3. Run `uv run mkdocs build --strict`.
4. Verify README/docs claim parity for tool counts and language coverage.
5. Spot-check one MCP workflow from setup to remediation output.

## Review cadence

- Review strategic pages at each release.
- Revisit generated docs whenever CLI/server/config surfaces change.
- Treat generated pages as artifacts: edit code/docstrings and generator scripts, not generated markdown directly.
