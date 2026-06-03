# Claude Code Instructions

## GitHub operations

Use **GitHub MCP tools** (`mcp__github__*`) for all GitHub operations — listing PRs,
reading diffs, viewing issues, creating PRs, etc. Do **not** use the `gh` CLI.
The project uses Keysafe which blocks third-party CLI token consumers, so `gh`
will always return `401 Bad credentials`.

## Package manager

This project uses **uv** exclusively. Never use `pip` or `pip install` directly.

```bash
uv sync --all-groups --all-extras   # install all deps (dev + docs)
uv sync --group dev                 # dev deps only
uv run <command>                    # run any tool in the project venv
uvx <tool>                          # run a one-off tool without installing
```

## Running tests

```bash
uv run pytest -xvs                  # run full suite (stops at first failure)
uv run pytest -x -q --no-cov <path> # fast run without coverage
```

Coverage threshold is **95%** — `pytest` will fail if it drops below.
Coverage is measured over `src/mcp_zen_of_languages/` only; `scripts/` and
`tests/` are excluded.

## Linting and type checking

```bash
uv run ruff check --fix             # lint with auto-fix
uv run ruff format                  # format
uv run ty check --error-on-warning  # strict type checking (ty, not mypy)
uvx pre-commit run --all-files      # run all pre-commit hooks
```

Ruff is configured with `select = ["ALL"]` — all rules enabled, only a handful
explicitly suppressed (see `[tool.ruff.lint.extend-ignore]` in `pyproject.toml`).
`scripts/**` have relaxed rules (`D`, `T201`, `INP001`, `S`, `ANN` ignored).

## Branching and commits (repo-release-tools)

Use **rrt** (repo-release-tools) for branch creation and versioning — never create
branches or bump versions manually.

```bash
uv run poe branch_feat   # create feat/<name> branch
uv run poe branch_fix    # create fix/<name> branch
uv run poe branch_ci     # create ci/<name> branch
uv run poe branch_docs   # create docs/<name> branch
# etc. — see pyproject.toml [tool.poe.tasks] for full list

uv run poe bump_patch    # bump patch version (updates pyproject.toml + __init__.py)
uv run poe bump_minor
uv run poe bump_major
uv run poe changelog_preview  # dry-run: preview changelog without writing
```

Commit messages must follow **Conventional Commits** (`feat:`, `fix:`, `ci:`,
`docs:`, `chore:`, `refactor:`, `test:`, `perf:`, `style:`, `build:`).
The `rrt-commit-subject` pre-commit hook enforces this on every commit.

## Version targets

When `rrt bump` runs it updates versions in two files simultaneously:
- `pyproject.toml` — `[project] version`
- `src/mcp_zen_of_languages/__init__.py` — `__version__`

Never edit these manually when bumping; always use `rrt bump`.

## Release workflow

1. `uv run poe branch_chore` — create a release prep branch
2. `uv run poe bump_patch` (or `bump_minor` / `bump_major`)
3. Review and commit the generated changelog entry
4. Open a PR → merge to `main`
5. Tag `vX.Y.Z` on main → CI publishes to PyPI, GHCR, and GitHub Releases

The CI `github-release` job attaches wheel, sdist, SBOM, and `.mcpb` bundle to
every GitHub Release automatically.

## Building the .mcpb bundle locally

```bash
uv run poe build_mcpb   # outputs dist/mcp-zen-of-languages-{version}.mcpb
```

`dist/` is gitignored, so the bundle is never committed.
The bundle uses `uv tool run` (long form of `uvx`) to install from PyPI at runtime.

## Documentation

Docs are built with **Zensical** (MkDocs wrapper).

```bash
uv run poe run_server   # local dev server with live reload
uv run poe build_docs   # build static site to site/
```

Many doc pages are **auto-generated** from scripts in `scripts/`. If you change
the implementation (new language, new rule, new CLI command), regenerate:

```bash
uv run poe generate_language_docs
uv run poe generate_cli_docs
uv run poe generate_mcp_tools_docs
uv run poe generate_config_docs
uv run poe generate_implementation_counts
```

Run `uv run poe check_orphan_docs` before committing to ensure all new pages
are wired into `mkdocs.yml` navigation.

## Python version

Requires **Python 3.12+**. CI tests against 3.12, 3.13, and 3.14.
The `ty` type checker targets 3.12 (`[tool.ty] environment.python-version = "3.12"`).

## Architecture overview

```
src/mcp_zen_of_languages/
├── server.py          # FastMCP server — all MCP tools defined here
├── cli.py             # Typer CLI (zen / mcp-zen-of-languages-cli)
├── __main__.py        # stdio entry point for MCP
├── analyzers/         # language analysis pipeline (registry + factory)
├── rules/             # zen-principle detectors
├── languages/         # per-language analyzer implementations
├── frameworks/        # framework detection (React, Next.js, …)
├── reporting/         # report generation, prompts, agent tasks
├── dogmas/            # the 10 Zen Dogmas definitions
├── config.py          # configuration management
└── models.py          # Pydantic data models
```

MCP entry points (all equivalent):
- `mcp-zen-of-languages-server` ← preferred
- `mcp-zen-of-languages`
- `zen-mcp-server` (legacy alias)

## Pre-commit hooks

26 hooks run on every commit. Key ones:
- `ruff-check` + `ruff-format` — lint and format
- `rrt-branch-name` — enforces branch naming convention
- `rrt-commit-subject` — enforces Conventional Commits
- `ty` — type checking
- `interrogate` — 90% docstring coverage on `src/`
- Several doc-quality checks (links, contrast, orphans, Sphinx roles)

If a hook auto-fixes files, stage the fixes and re-run `git commit` (do not use
`--no-verify` to bypass).

## CI pipeline

Jobs in order: `lint` → `rrt-checks` → `[test, language-tests, visual-regression]`
→ `docker-image-check` → `[build, docker-publish]` → `[build-mcpb, sbom, attest]`
→ `publish-testpypi` → `verify-testpypi` → `publish-pypi` → `github-release`.

Tag-only jobs (run only on `vX.Y.Z` tags): `docker-publish`, `build-mcpb`,
`publish-testpypi`, `verify-testpypi`, `publish-pypi`, `github-release`.
