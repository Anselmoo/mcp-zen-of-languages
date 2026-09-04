# Dependency reconciliation: `.pre-commit-config.yaml`, `.serena/project.yml`, and `uv.lock`

**Date:** 2026-09-04
**Branch:** `claude/dependency-update-plan-e7326c`
**Status:** implemented, then partly superseded — see Outcome below

## Superseded in part by #214

While this branch was executing, [#214](https://github.com/Anselmoo/mcp-zen-of-languages/pull/214)
(`chore: resolve ruff 0.16 findings and upgrade ty to 0.0.78`) landed on `main` and
independently did most of the same work. `main` was merged into this branch afterwards, and
on every point of overlap **`main`'s resolution was kept**. Three decisions recorded below
are therefore historical rather than current:

- **`CPY001` — reversed.** This spec suppressed the rule in `extend-ignore`, reasoning that
  the project ships a single MIT `LICENSE` at the repo root and does not use per-file
  headers. `#214` took the opposite route and added a
  `# Copyright (C) 2026 Anselm Hahn. Licensed under the MIT License.` header to every source
  file. That is the policy in effect; the suppression was removed during the merge.
- **`ty` — no longer blocked.** `#214` upgraded `ty` and fixed
  `tests/registry/test_registry_bootstrap_coverage.py`, removing the `error[missing-argument]`
  findings that triggered this branch's drop. `ty` now carries a `>=0.0.77` floor.
- **The `source_url` defect — fixed upstream.** `#214` added
  `source_url: HttpUrl | None` to `ZenPrinciple`, so the 7 silently-discarded values
  described below are resolved. No follow-up issue is needed.

## The Serena migration was dropped from this branch

This branch originally carried a Serena v1.7 schema migration for
`.serena/project.yml` (see Task 1 of the implementation plan). **It is no longer part of
this branch.** Serena is being removed from the repository entirely — it consumed context
on every session without being used, and its two `.serena/memories/*.md` files were tracked
in git, so they loaded as project context for everyone.

The removal is [#219](https://github.com/Anselmoo/mcp-zen-of-languages/pull/219). Migrating
a file that is about to be deleted served no purpose and would have forced a modify/delete
conflict between the two PRs, so `.serena/project.yml` was restored to its `main` state
here. This branch no longer touches it.

References to the Serena migration in the Outcome section below and throughout the
implementation plan describe what was executed at the time, and are kept as the record.

What remains uniquely this branch's contribution: the tool-version-agreement guard and the
`repo-release-tools` pin reconciliation it forced, the `CLAUDE.md` Markdown-formatting note,
`zensical` `0.0.46` -> `0.0.59`, and the `ruff` patch bump `v0.16.5` -> `v0.16.6` on both
axes.

## Outcome (as executed, before the merge with `main`)

Eight commits shipped on this branch (`b116149..c745801`): the rrt hook bump and Serena
schema migration, the `ruff` bump to `0.16.6` on both axes plus its rule-surface absorption
(`CPY001` suppression, `ISC004` fixes, `PLR0917`/`RUF100` cleanup), the `CLAUDE.md`
Markdown-formatting note, and the `zensical` bump to `0.0.59`. All of these landed as
planned.

**`ty` did not move.** It was held at `0.0.51`; the planned `0.0.78` bump (Commit 3 below)
was attempted and dropped at its designed drop point (Task 6, Step 3 of the implementation
plan). `pyproject.toml` still reads `"ty>=0.0.16"` and `uv.lock` still resolves `ty` at
`0.0.51`.

The gate command was `uv run ty check --error-on-warning` with `ty` temporarily bumped to
`0.0.78`. It reported 9 diagnostics (exit code 1):

- 7 new `warning[pydantic-discarded-extra-argument]` findings, all in
  `src/mcp_zen_of_languages/languages/javascript/rules.py` (lines 169, 185, 203, 219, 237,
  253, 272) — `ty` 0.0.78 gained the ability to detect that a `ZenPrinciple(...)` call's
  `source_url=...` keyword argument is silently discarded by Pydantic, because `ZenPrinciple`
  does not declare that field (it belongs to `LanguageZenPrinciples`). `ty` 0.0.51 did not
  catch this.
- 2 pre-existing `error[missing-argument]` findings in
  `tests/registry/test_registry_bootstrap_coverage.py` (lines 13-14) — a required `type`
  parameter that `ty` 0.0.78 now flags more strictly for a factory-defaulted call pattern.

Per this spec's explicit rule (see "Commit 3" below and Task 6, Step 3 of the implementation
plan), `[tool.ty.rules]`'s seven baseline suppressions were **deliberately not widened** to
force the bump through — that trade was rejected as unacceptable inside a dependency PR.
The `ty` change was reverted with `git checkout -- pyproject.toml uv.lock`, confirmed back
to `ty 0.0.51`, and left no trace in the shipped commits.

Both diagnostics categories are pre-existing code issues, unrelated to this branch's other
changes, that only became visible because `ty` 0.0.78 checks more strictly. Neither is fixed
here — fixing the Pydantic one is a behaviour change to shipped data needing a human call on
whether the discarded `source_url` values should be persisted or dropped; fixing the test one
is unrelated to dependency reconciliation. **The `ty` `0.0.51` -> `0.0.78` bump remains open
work**, blocked on resolving both findings first.

## Problem

Update the pinned dependencies in `.pre-commit-config.yaml` and `.serena/project.yml`. The
request is not a mechanical version bump: this repository lints under
`select = ["ALL"]`, so every Ruff minor release changes the rule surface and therefore the
source code.

## Context discovered during exploration

### Two independent version axes, already skewed

The repository pins tool versions in two unrelated places, and CI runs both:

- **Axis A** — `rev:` pins in `.pre-commit-config.yaml`. Pins `ruff-pre-commit` at `v0.15.15`.
- **Axis B** — resolutions in `uv.lock`, which drive the three `local` `language: system`
  hooks (`ty`, `interrogate`, `zensical`). Resolves `ruff` at `0.15.18`.

`.github/workflows/cicd.yml:60` runs `uv run ruff check` (Axis B's binary) and
`.github/workflows/cicd.yml:66` runs `uvx pre-commit run --all-files` (Axis A's binary).
Two different Ruff versions therefore lint the same 446 files / ~85k lines today. Bumping
one axis without the other widens this gap.

This branch closes the Axis A/B gap **for `ruff` only**. `repo-release-tools` (rrt) turns
out to have the same two-axis structure, pinned in three places at three different
versions, only one of which this plan touches:

- `.pre-commit-config.yaml:23` — `rev: v1.16.0` (this branch bumps to `v1.17.1`)
- `.github/workflows/cicd.yml:88` — `uses: Anselmoo/repo-release-tools@v1.8.1` (untouched
  by this branch; CI's `rrt-checks` job runs `check-branch-name` / `check-commit-subject`
  at this pinned Action version)
- `uv.lock` / `pyproject.toml` `[dependency-groups] dev` — floor `>=1.8.1`, resolving to
  `repo-release-tools 1.9.0` (untouched by this branch; this is what `uv run poe branch_*`
  and `uv run poe bump_*` invoke locally)

So after this branch merges, the local pre-commit hook validates branch names and commit
subjects at rrt v1.17.1 while the CI Action that gates the same checks in `rrt-checks` still
runs v1.8.1 — structurally the same defect this plan exists to close, just for a different
tool. This gap is **pre-existing** (not introduced by this branch) and **knowingly out of
scope** here: closing it means deciding whether to bump the CI Action pin, the `uv.lock`
floor, or both, which is a separate, unmeasured change or PR.

### `.serena/project.yml` is a schema, not a dependency

Serena appears nowhere in `pyproject.toml`. The file in the working tree has already been
auto-migrated by a newer Serena (v1.7.x) and sits uncommitted. Renames applied:

- `languages:` -> `language_servers:`
- `additional_workspace_folders:` -> `ls_additional_workspace_folders:`
- new keys: `ls_workspace_folders`, `activation_command`, `activation_command_timeout`

The five configured language servers (python, toml, yaml, markdown, bash) survive intact.

### Measured baseline

`uv run ruff check` and `uv run ty check --error-on-warning` both report clean today.

## Version moves

| Axis | Package | Current | Target | Notes |
| --- | --- | --- | --- | --- |
| A | `pre-commit/pre-commit-hooks` | `v6.0.0` | `v6.0.0` | already current, no change |
| A | `astral-sh/ruff-pre-commit` | `v0.15.15` | `v0.16.6` | new rule surface |
| A | `Anselmoo/repo-release-tools` | `v1.16.0` | `v1.17.1` | no validator changes |
| B | `ruff` | `0.15.18` | `0.16.6` | must match Axis A |
| B | `ty` | `0.0.51` | `0.0.78` attempted, **held at `0.0.51`** | dropped at its designed drop point — see Outcome below |
| B | `zensical` | `0.0.46` | `0.0.59` | drives strict docs build |
| B | `interrogate` | `1.7.0` | `1.7.0` | already current, no change |

`repo-release-tools` v1.17.0 adds MCP-registry registration and an `mcp_server_json`
version target; v1.17.1 fixes namespace casing. Neither touches the `rrt-branch-name` or
`rrt-commit-subject` validators this repository depends on.

## Ruff 0.16.6 rule fallout (measured, baseline 0)

| Rule | Hits | Disposition | Rationale |
| --- | --- | --- | --- |
| `CPY001` missing-copyright-notice | 446 | add to `extend-ignore` | MIT `LICENSE` at repo root, zero files carry headers, no `flake8-copyright` config. Per-file headers are not this project's convention. |
| `ISC004` implicit-str-concat-in-collection | 45 | apply `--unsafe-fixes`, review diff | Approved 2026-09-04. |
| `PLR0917` too-many-positional-arguments | 13 | extend existing `noqa` to `PLR0913, PLR0917` | All 13 sites already carry `# noqa: PLR0913`. |
| `RUF100` unused-noqa | 4 | `--fix` | Safe autofix, removes dead suppressions. |

### `ISC004` detail

Affects 4 files: `scripts/generate_config_docs.py`, `scripts/generate_dogma_mapping.py`,
`src/mcp_zen_of_languages/languages/go/rules.py`,
`src/mcp_zen_of_languages/reporting/prompts.py`.

The flagged pattern is intentional line-wrapping inside collection literals; the code is
correct today. The rule fires because inside a list or tuple an intentional wrap and a
missing comma are visually identical. Ruff's fix adds explicit parentheses and preserves
semantics; it is classed unsafe only because Ruff cannot prove a comma was not intended.

The diff must be read site by site. Any site where the parenthesised result changes the
number of collection elements is a pre-existing bug, not a formatting change, and must be
reported rather than silently fixed.

### `PLR0917` detail

All 13 sites already declare `# noqa: PLR0913`:

- `src/mcp_zen_of_languages/frameworks/{angular,django,fastapi,nextjs,pydantic,react,sqlalchemy,vue}/rules.py:12`
  — the same `_principle()` helper replicated 8 times
- `src/mcp_zen_of_languages/cli.py:1792,1865,1933`
- `src/mcp_zen_of_languages/server.py:1743`
- `scripts/check_docs_contrast.py:345`

Converting `_principle()` to keyword-only arguments would be a genuine improvement but
rewrites 54 call sites. That is a refactor, out of scope here.

## New behaviour: Ruff formats Markdown code blocks

Ruff 0.16 formats Python code inside fenced Markdown blocks. `ruff format` reformats 7
files (4 under `.github/`, 3 under `docs/contributing/`).

The pre-commit hook is gated `types_or: ["python", "pyi"]`, so **the hook will not do
this**. A bare `uv run ruff format` will. Two contributors running "the formatter" would
get different results depending on whether they went through pre-commit.

**Decision:** do not opt in. Leave `types_or` unchanged and keep this change out of scope.
Mitigate by documenting the discrepancy in `CLAUDE.md` under the linting section. Opting in
properly is a separate `docs:` change.

## Implementation plan

Four commits on `claude/dependency-update-plan-e7326c`, ordered so each is independently
revertible and risk increases monotonically.

### Commit 1 — `build(deps): bump rrt hook and accept serena schema migration`

- `.pre-commit-config.yaml`: `repo-release-tools` `v1.16.0` -> `v1.17.1`
- `.serena/project.yml`: commit the migrated file as-is, without hand-editing, so it stays
  byte-compatible with what Serena regenerates

Risk: none. No source-code effect.

### Commit 2 — `build(deps): bump ruff to 0.16.6 across pre-commit and uv.lock`

- `.pre-commit-config.yaml`: `ruff-pre-commit` `v0.15.15` -> `v0.16.6`
- `pyproject.toml`: `ruff>=0.14.14` -> `ruff>=0.16.6` in `[dependency-groups] dev`
- `uv lock`
- `pyproject.toml`: add `"CPY001"` to `[tool.ruff.lint] extend-ignore` with a comment
  recording the reason (MIT `LICENSE` at root; no per-file headers)
- Apply `ruff check --fix` (clears `RUF100`)
- Apply `ruff check --select ISC004 --fix --unsafe-fixes`, then read the full 45-site diff
- Extend the 13 `# noqa: PLR0913` comments to `# noqa: PLR0913, PLR0917`
- Add the Markdown-formatting note to `CLAUDE.md`

Risk: high. This is the only commit with source-code churn.

### Commit 3 — `build(deps): bump ty to 0.0.78` (DROPPED — see Outcome above)

- `pyproject.toml`: `ty>=0.0.16` -> `ty>=0.0.78`, then `uv lock`

Unmeasured: `uvx ty@0.0.78` runs outside the project venv and yields only
import-resolution noise, so the only real probe is moving the lock. If the bump produces
diagnostics, **drop this commit** rather than widening the seven existing baseline
suppressions in `[tool.ty.rules]`.

This is what happened: moving the lock surfaced 9 diagnostics under
`--error-on-warning` (7 new Pydantic warnings, 2 pre-existing test errors — see Outcome
above for detail), so this commit was dropped and never shipped. `ty` remains at `0.0.51`.

### Commit 4 — `build(deps): bump zensical to 0.0.59`

- `pyproject.toml`: `zensical>=0.0.23` -> `zensical>=0.0.59`, then `uv lock`

Verify with `uv run poe build_docs`. If the strict build fails, drop this commit.

## Verification

Per commit:

1. `uv run ruff check`
2. `uv run ty check --error-on-warning`
3. `uvx pre-commit run --all-files`
4. `uv run pytest -x -q` (95% coverage floor)

After commit 2, additionally regenerate docs, since several `always_run` hooks rewrite
files: `generate_config_docs`, `generate_implementation_counts`, `generate_dogma_mapping`.

After commit 4, additionally run `uv run poe build_docs`.

The 95% coverage floor must not move. No change in this plan alters a branch — only
formatting, `noqa` comments, and string parenthesisation.

## Out of scope

- Converting `_principle()` to keyword-only arguments (54 call sites)
- Opting Ruff's Markdown formatting into the pre-commit hook
- Adopting `repo-release-tools` v1.17's `mcp_server_json` version target, which overlaps
  the registry work done by hand in commit `b116149`

## Note on spec location

The Superpowers default location is `docs/superpowers/specs/`. This repository's
`scripts/check_orphan_docs.py` hook runs `always_run` and rglobs every `.md` under `docs/`,
excluding only `docs/overrides`, `docs/stylesheets`, `docs/assets`, `docs/includes`, and
`docs/404.md`. A spec written under `docs/` would fail the commit as an orphan page, so
specs live at `.superpowers/specs/` instead.
