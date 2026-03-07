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
- Avoid `expand=True` for data panels; reserve it for layout regions — such as the welcome panel — that should fill the terminal like Typer's own help pages.

## Box style hierarchy

| Content type | Constant | Rich box |
| --- | --- | --- |
| Banner / Welcome | `BOX_BANNER` | `box.DOUBLE` |
| Summary / Metrics | `BOX_SUMMARY` | `box.HEAVY` |
| Standard content | `BOX_CONTENT` | `box.ROUNDED` |
| Action lists | `BOX_ACTION` | `box.SIMPLE` |
| Code blocks | `BOX_CODE` | `box.SQUARE` |

## Brand colour palette

All terminal colours are derived from the **Caligo design system** defined in
`docs/stylesheets/tokens/palette.css`. Import constants from
`mcp_zen_of_languages.rendering.themes` — never hard-code hex values.

| Constant | Hex | Caligo token | Role |
| --- | --- | --- | --- |
| `BRAND_PRIMARY` | `#989cff` | `--caligo-accent` | Primary UI — options, paths, usage, banner art |
| `BRAND_ACCENT` | `#c8315a` | `--caligo-cherry` | Vibrant highlight — required markers, high severity, scores |
| `BRAND_COOL` | `#63c8ff` | `--caligo-harmony-cool` | Success / switches / low-severity indicators |
| `BRAND_MUTED` | `#9b95ad` | `--caligo-fg-muted` | Dim text — defaults, env vars, subtle decorations |
| `BORDER_STYLE` | `#767bd8` | `--caligo-accent-muted` | Panel borders — subdued purple coherent with primary |

Semantic Rich theme tokens (applied via `ZEN_THEME`, always prefer these over raw constants):

| Token | Mapped to | Use case |
| --- | --- | --- |
| `banner` | `bold {BRAND_PRIMARY}` | Pyfiglet banner art |
| `severity.high` | `bold {BRAND_ACCENT}` | High-severity violations |
| `severity.medium` | `{BRAND_PRIMARY}` | Medium-severity violations |
| `severity.low` | `{BRAND_COOL}` | Low-severity violations |
| `path` | `bold {BRAND_PRIMARY}` | File and module paths |
| `metric` | `{BRAND_PRIMARY}` | Numeric metrics |
| `score` | `bold {BRAND_ACCENT}` | Quality scores |
| `muted` | `dim {BRAND_MUTED}` | Subdued / secondary text |

!!! note "Backward-compatible aliases"
    The legacy names `BRAND_ORANGE`, `BRAND_BLUE`, `BRAND_GREEN`, and
    `BRAND_GRAY` remain as aliases pointing to their Caligo equivalents so
    existing code continues to compile.  Prefer the semantic names
    (`BRAND_PRIMARY`, `BRAND_ACCENT`, `BRAND_COOL`, `BRAND_MUTED`) in new code.

## Prompt rendering

- Prefer Rich-native renderables (`Panel`, `Group`, `Table`, `Syntax`) over raw markdown text.
- Render code examples with `Syntax(...)` and wrap them in a `BOX_CODE` panel.
- Use panel titles/subtitles for file context instead of markdown headers like `###`.

## Severity and glyph conventions

- Always use `severity_badge(...)` for severity labels.
- Keep severity columns fixed to width 12 (`Sev`).
- Use shared glyph helpers (`file_glyph`, `score_glyph`, `pass_fail_glyph`) to keep fallback behavior consistent.

## Typer + Rich consistency

- `uv run zen` and subcommands should use one visual language (same width cap, same box hierarchy, same Caligo palette).
- Help panels use `BORDER_STYLE` (`--caligo-accent-muted`) for borders and `BRAND_PRIMARY` for option names; switches use `BRAND_COOL`.
- The welcome panel (`_build_welcome_panel`) uses `Panel` directly — matching Typer's own `expand=True`, ROUNDED, left-aligned-title style — rather than the fixed-width `zen_panel` factory.
- Rich and Typer are designed to work together; keep help and command output aligned.
- Pyfiglet banners are allowed, but always keep a plain-text fallback for non-interactive terminals.
