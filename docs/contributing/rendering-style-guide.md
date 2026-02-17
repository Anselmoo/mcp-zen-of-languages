---
title: Rendering Style Guide
description: Use this guide when adding or modifying terminal output in rendering/ and reporting/terminal.py.
icon: material/source-branch
tags:
  - API
  - Configuration
---

# Rendering Style Guide

Use this guide when adding or modifying terminal output in `rendering/` and `reporting/terminal.py`.

## Width conventions

- Always use `get_output_width(console)` for panel and table widths.
- Keep terminal output capped at 88 columns.
- Avoid `expand=True` unless rendering a deliberate layout region.

## Box style hierarchy

| Content type | Constant | Rich box |
| --- | --- | --- |
| Banner / Welcome | `BOX_BANNER` | `box.DOUBLE` |
| Summary / Metrics | `BOX_SUMMARY` | `box.HEAVY` |
| Standard content | `BOX_CONTENT` | `box.ROUNDED` |
| Action lists | `BOX_ACTION` | `box.SIMPLE` |
| Code blocks | `BOX_CODE` | `box.SQUARE` |

## Prompt rendering

- Prefer Rich-native renderables (`Panel`, `Group`, `Table`, `Syntax`) over raw markdown text.
- Render code examples with `Syntax(...)` and wrap them in a `BOX_CODE` panel.
- Use panel titles/subtitles for file context instead of markdown headers like `###`.

## Severity and glyph conventions

- Always use `severity_badge(...)` for severity labels.
- Keep severity columns fixed to width 12 (`Sev`).
- Use shared glyph helpers (`file_glyph`, `score_glyph`, `pass_fail_glyph`) to keep fallback behavior consistent.

## Typer + Rich consistency

- `uv run zen` and subcommands should use one visual language (same width cap, same box hierarchy).
- Rich and Typer are designed to work together; keep help and command output aligned.
- Pyfiglet banners are allowed, but always keep a plain-text fallback for non-interactive terminals.
