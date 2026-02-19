---
title: Zensical Migration
description: Documentation migration notes from mkdocs-material to Zensical.
icon: material/theme-light-dark
tags:
  - Configuration
---

# Zensical Migration

This project now uses **Zensical** for documentation builds.

## What changed

- Docs dependency moved from `mkdocs-material` to `zensical`.
- Build command changed from `uv run mkdocs build --strict` to `uv run zensical build -f mkdocs.yml`.
- Local preview command changed to `uv run zensical serve -f mkdocs.yml`.
- Legacy Material-specific migration/reference pages were removed.

## Contributor workflow

```bash
uv sync --group docs
uv run zensical build -f mkdocs.yml
```

For contrast checks (same as CI/pre-commit):

```bash
uv run python scripts/check_docs_contrast.py --build --mode check
```
