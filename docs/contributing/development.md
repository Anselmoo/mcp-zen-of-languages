---
title: Development
description: Local development setup, quality gates, pre-commit hooks, and debugging workflows.
icon: material/source-branch
tags:
  - API
  - Configuration
---

# Development

## Setup

```bash
uv sync --group dev --group docs
```

## Project structure

- `src/mcp_zen_of_languages/` core package
- `languages/` per-language analyzers and detectors
- `analyzers/` shared pipeline and registry logic
- `rules/` zen principle models
- `docs/` documentation site

## Checks

```bash
uv run ruff check
uv run ruff format --check
uv run ty check src
uv run pytest
uv run python scripts/check_docs_contrast.py --build --mode check
```

## Developer tasks (Poe)

All `scripts/*.py` helpers are available through Poe tasks in `pyproject.toml`.

```bash
uv run poe check_docs_links
uv run poe check_orphan_docs
uv run poe generate_cli_docs
uv run poe generate_mcp_tools_docs
uv run poe export_svg_assets
```

Use `uv run poe` (without a task) to list all available developer tasks.

## Pre-commit

```bash
pre-commit install --hook-type pre-commit --hook-type pre-push
pre-commit run --all-files
pre-commit run --hook-stage pre-push --all-files
```

## Debugging tips

- Use `uv run pytest -k <pattern> -xvs` for focused tests.
- Run `uv run mkdocs serve` to preview docs locally.

!!! danger "Don't skip pre-commit"
Pushing without running `pre-commit run --all-files` will likely trigger CI failures. The hooks check linting, docs links, orphan pages, Sphinx role leaks, and docs contrast.

## Contrast policy (WCAG AA)

- Documentation styles must satisfy WCAG AA contrast checks for both `caligo-light` and `caligo-dark`.
- The contrast audit runs in pre-commit and CI via `scripts/check_docs_contrast.py`.
- Allowed exceptions must be added to `scripts/docs_contrast_config.json` with explicit selector scope.
- Prefer token updates first in `docs/stylesheets/tokens/palette.css` and `docs/stylesheets/tokens/semantic.css`, then targeted selector overrides in component modules as needed.
