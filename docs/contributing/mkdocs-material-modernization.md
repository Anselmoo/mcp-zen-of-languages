---
title: MkDocs Material Modernization
description: State-of-the-art MkDocs Material theming and API guidance used in this repository.
icon: material/palette
tags:
  - Configuration
  - API
---

# MkDocs Material Modernization

This project uses **MkDocs Material 9.7+** patterns with a Caligo-based design system and explicit theme token mapping.

!!! info "Current baseline"
    We target `mkdocs-material[imaging]>=9.7.1` to pick up recent privacy/security fixes and the latest stable feature set.

!!! warning "Lifecycle note"
    Material for MkDocs entered maintenance mode in 9.7.0. Keep using it confidently for critical fixes, but track long-term ecosystem direction for future migrations.

## State-of-the-art configuration patterns

We follow the current recommended setup for modern Material sites:

- `theme.features` explicitly enables rich UX capabilities (code copy, annotations, tabs, edit/view actions, instant navigation).
- `theme.palette` uses **system preference support** with explicit light/dark toggles.
- `primary: custom` and `accent: custom` are set so design tokens can be controlled in `docs/stylesheets/tokens/*.css` via the `docs/stylesheets/extra.css` manifest.
- `extra_css` + `custom_dir` are used instead of forking the theme.

## Caligo Midnight Atelier Strategy

The Caligo palette is defined as semantic CSS variables and then mapped to Material variables (`--md-*`):

- Background surfaces (`--caligo-bg-*`)
- Foreground/readability (`--caligo-fg-*`)
- **Blue/Purple-centered accents** for icon diversity and visual harmony:
  - Primary: Indigo accent (`#989cff`) - main brand color
  - Cool complement: Azure (`#4ec2ff`) - navigation and header icons
  - Warm complement: Orchid (`#ffadff`) - interactive states and hover
  - Purple bridge: (`#c4abff`) - harmonic connector
- Syntax accents (`--caligo-syntax-*`)
- Semantic feedback (`--caligo-error`, `--caligo-warning`, `--caligo-success`, `--caligo-info`)

### Icon Color Strategy

Icons use a **blue/purple harmony** approach for better visual interest and user experience:

- **Header/Navigation icons (dark scheme)**: Cool azure (`--caligo-icon-secondary`) provides contrast against the dark header
- **Header/Navigation icons (light scheme)**: Inherit `--md-primary-bg-color` (mapped to `--caligo-light-text`) via existing Material header button styling
- **Interactive states**: Bridge purple (`--caligo-icon-interactive`) on hover/focus for clear feedback
- **Content icons**: Primary indigo (`--caligo-icon-primary`) maintains brand consistency
- **Muted icons**: Foreground muted colors for subtle UI elements

This separation keeps branding stable even if Material internals evolve, while providing better accessibility and visual hierarchy.

## API-aware theming decisions

### Palette API

- Use named schemes with `[data-md-color-scheme="..."]` selectors.
- Keep both light and dark schemes defined explicitly.
- Use a system-preference palette entry for better UX on modern OSes.

### Docs deployment API (non-versioned)

- Use classic MkDocs Material deployment without docs-version metadata.
- Do not configure `extra.version.provider` unless versioned docs are intentionally adopted.
- Deploy a single docs site from `main` via GitHub Pages artifact flow.
- Validate release artifacts with SBOM and TestPyPI before production PyPI publish.

### Customization API

- Keep custom styles modular under `docs/stylesheets/` (tokens/theme/components/pages/utilities) and use `docs/stylesheets/extra.css` as the import manifest.
- Keep template overrides minimal (`docs/overrides/main.html`) and focused on metadata/head hooks.
- Re-check overrides on major Material upgrades.
- Prefer Caligo semantic tokens over raw `#fff`/`#000` literals (including print styles) to keep palette cohesion.

## Documentation authoring standard

When documenting configuration or rendering behavior:

1. Start with **what changed**.
2. Add **caveats** with admonitions (`!!! warning`, `!!! note`).
3. Include **version context** (minimum supported version).
4. Prefer practical snippets over abstract prose.

!!! tip "Contributor workflow"
    After any docs theme/config change, run `uv sync --group docs` and `uv run mkdocs build --strict`.

## Hyperlinking policy

To keep docs navigable and verifiable:

- Every major landing page should include a **See Also** section with internal links.
- Language pages should include at least one external authoritative style-guide/spec link.
- Prefer canonical references (official project/spec URLs) over mirrors or blog reposts.
- Use standard Markdown inline links compatible with the [CommonMark links specification](https://spec.commonmark.org/0.31.2/#links).

For implementation details in scripts, prefer explicit, tested regex handling from Python's standard library: [re — Regular expression operations](https://docs.python.org/3/library/re.html).

### GitHub/GitLab shorthand links

This project enables `pymdownx.magiclink`, so docs can use shorthand references:

- `#123` for issues in the default repository
- `!45` for pull/merge requests in the default repository
- `gitlab:group/project#21` for explicit GitLab issue references

These shorthand links improve readability while preserving direct navigation.
