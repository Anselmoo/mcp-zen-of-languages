# Dependency Update Design — 2026-09-02

Full dependency refresh across `.pre-commit-config.yaml` and `pyproject.toml`,
including the source-code changes that upgraded tooling forces.

## Problem

This repository carries **three independent sources of dependency truth** that
have drifted apart from each other, not merely from upstream:

1. `pyproject.toml` — declared floors (`>=`) and one exact pin (`==`)
2. `uv.lock` — what actually resolves and runs
3. `.pre-commit-config.yaml` — `rev:` pins for hook repositories

Dependabot only opens a PR when a declared constraint *excludes* the latest
release. Because nearly every dependency uses `>=`, Dependabot stayed silent
while the floors rotted, and `uv lock -U` (wired into `[tool.rrt] lock_command`)
quietly pulled the lock forward. The result is a lock that is **newer than the
declarations it derives from**, and pre-commit revs that match neither.

Two configuration choices amplify any tooling bump into source-code work:

- `select = ["ALL"]` in `[tool.ruff.lint]` auto-enrolls every newly stabilized
  ruff rule.
- `[tool.ty.rules]` carries seven baseline suppressions marked *"fix
  incrementally"*.

Both interact with hard gates: **95% coverage** (`--cov-fail-under=95`) and
**90% docstring coverage** (`interrogate fail-under = 90`).

## Measured state

Versions observed on 2026-09-02.

| Package | Declared | `uv.lock` | Latest | Tier |
| --- | --- | --- | --- | --- |
| fastmcp | `>=3.0.2` | 3.4.2 | 4.0.1 | PR-3 |
| sqlglot | `==29.0.1` | 29.0.1 | 30.17.0 | PR-3 |
| tree-sitter | `>=0.25.2` | 0.25.2 | 0.26.0 | PR-3 |
| pydantic | `>=2.12.5` | 2.13.4 | 2.13.5 | PR-3 |
| ruff | `>=0.14.14` | 0.15.18 | 0.16.5 | PR-2 |
| ty | `>=0.0.16` | 0.0.51 | 0.0.77 | PR-2 |
| uv_build | `>=0.9.26,<0.12.0` | — | 0.12.9 | PR-1 |
| repo-release-tools | `>=1.8.1` | 1.9.0 | 1.17.1 | PR-1 |
| typer | `>=0.12.0` | 0.26.7 | 0.27.2 | PR-1 |
| mkdocstrings | `>=0.26.0` | 1.0.4 | 1.0.6 | PR-1 |
| zensical | `>=0.0.23` | 0.0.46 | 0.0.58 | PR-1 |
| poethepoet | `>=0.33.1` | 0.46.0 | 0.48.0 | PR-1 |
| playwright | `>=1.54.0` | 1.60.0 | 1.62.0 | PR-1 |
| mkdocs-glightbox | `>=0.4.0` | 0.5.2 | 0.5.2 | PR-1 |
| mkdocs-git-revision-date-localized-plugin | `>=1.3.0` | 1.5.3 | 1.5.4 | PR-1 |
| pygments | `>=2.19.2` | 2.20.0 | 2.21.0 | **remove** |
| networkx, radon, pytest, pytest-asyncio, pytest-cov, interrogate, jinja2, cairosvg, pyfiglet, mkdocs-minify-plugin | current | current | current | none |

Pre-commit `rev:` pins:

| Repo | Pinned | Latest |
| --- | --- | --- |
| `pre-commit/pre-commit-hooks` | `v6.0.0` | `v6.0.0` (current) |
| `astral-sh/ruff-pre-commit` | `v0.15.15` | `v0.16.5` |
| `Anselmoo/repo-release-tools` | `v1.16.0` | `v1.17.1` |

`pygments` is declared as a runtime dependency but has **zero imports** across
`src/`, `tests/`, and `scripts/`. Its only references are documentation prose
(`docs/getting-started/security.md:113`, `.github/copilot-instructions.md:142`)
and an unrelated `mkdocs.yml` highlighting setting.

## Probe results

Each risky upgrade was tested against this repository's exact API surface in an
isolated environment rather than inferred from changelogs.

### fastmcp 3.4.2 → 4.0.1 — one-line change

Seven of eight imported symbols resolve unchanged. `FastMCP.__init__` still
accepts every keyword `server.py:144` passes (`name`, `version`, `instructions`,
`website_url`, `icons`, `middleware`, `lifespan`, `list_page_size`), and
`FastMCP.tool()` still accepts `task=`, so all six `task=BACKGROUND_TASK` call
sites are unaffected. The extras `tasks`, `code-mode`, and `apps` all still
exist.

The single break: `fastmcp.server.tasks` was removed. `TaskConfig` now lives at
`fastmcp.utilities.tasks`.

### sqlglot 29.0.1 → 30.17.0 — API-clean

The full surface this repository uses is present and behaviourally correct on
30.17.0: `sqlglot.parse`, `sqlglot.errors.ParseError`, `Expression.find_all`,
and `exp.Column` / `exp.Expression` / `exp.Select` / `exp.Star`. A live
parse-and-traverse round trip returns correct results.

The `==` pin originates from PR #60, where SQL support was introduced. It is a
defensive policy against sqlglot's frequent parser changes, not a record of a
known incompatibility. Residual risk is behavioural (parser output on edge-case
SQL) and is covered by the existing SQL analyzer tests.

### ruff 0.15.18 → 0.16.5 — 508 findings, all from newly stabilized rules

Baseline is clean: ruff 0.15.18 reports zero errors. Every 0.16.5 finding comes
from a rule that graduated out of preview and was auto-enrolled by
`select = ["ALL"]`.

| Rule | Count | Disposition |
| --- | --- | --- |
| `CPY001` missing-copyright-notice | 446 | configure `flake8-copyright` (below) |
| `ISC004` implicit-string-concatenation-in-collection-literal | 45 | `--unsafe-fixes`, then review |
| `PLR0917` too-many-positional-arguments | 13 | hand-review each call site |
| `RUF100` unused-noqa | 4 | auto-fixable |

`CPY001` flags all 446 Python files at the default `min-file-size = 0`. Measured
counts by threshold:

| `min-file-size` | Files flagged |
| --- | --- |
| 0 | 446 |
| 1024 | 330 |
| 2048 | 282 |
| 4096 | 207 |
| 8192 | 107 |
| 16384 | 43 |

### ty 0.0.51 → 0.0.77 — 9 diagnostics, one real bug

Baseline passes cleanly. Version 0.0.77 reports nine diagnostics:

- 7 × `warning[pydantic-discarded-extra-argument]` in
  `src/mcp_zen_of_languages/languages/javascript/rules.py` (constructor starts at
  lines 169, 185, 203, 219, 237, 253, 272)
- 2 × `error[missing-argument]` for a required `type` parameter in
  `tests/registry/test_registry_bootstrap_coverage.py:13-14`

The seven warnings are a latent bug, not noise. `LanguageZenPrinciples` declares
a `source_url` field, which is why line 15 of every language's `rules.py` works.
`ZenPrinciple` does **not** declare one. JavaScript is the only language that
also attaches per-principle deep links — `#destructuring`,
`#properties--eval`, and five others — by passing `source_url=` to
`ZenPrinciple(...)`. Pydantic discards each silently, so those URLs have never
reached any output. No test caught it, because nothing can assert on a field
that does not exist.

## Design

Three tiered pull requests, ordered by blast radius. Each is independently
revertable, so a red CI run isolates its own cause.

### PR-1 — `chore/deps-align`

Mechanical realignment. No behaviour change.

- Raise stale `pyproject.toml` floors to what `uv.lock` already resolves: typer,
  mkdocstrings, ruff, ty, repo-release-tools, poethepoet, playwright, zensical,
  mkdocs-glightbox, mkdocs-git-revision-date-localized-plugin. This closes the
  declaration/lock drift that keeps Dependabot silent.
- Widen the `uv_build` bound from `<0.12.0` to `<0.13.0`, adopting PR #198. The
  current uv 0.12.6 emits a build warning on every invocation today.
- Bump pre-commit revs: `astral-sh/ruff-pre-commit` to `v0.16.5` and
  `Anselmoo/repo-release-tools` to `v1.17.1`. This supersedes PR #207.
- Remove `pygments` from `[project] dependencies` and update the two prose
  references that name it.
- Resolve the 4 `RUF100` findings, which are auto-fixable and must clear for
  this PR to stay green.
- Run `uv lock -U`, then the full CI pipeline.

The ruff rev lands here while the remaining ruff *findings* land in PR-2. To
keep PR-1 green, `CPY001`, `ISC004`, and `PLR0917` are added to `extend-ignore`
in this PR as a temporary measure, each marked as handled in PR-2, and removed
in PR-2 when the real dispositions land.

Note on counting `RUF100`: it must be measured with the project config, never a
bare `--select RUF100`. The rule judges each `noqa` against *currently enabled*
rules, so narrowing the selection reports 10+ sites instead of the real 4 and
would delete legitimate suppressions.

### PR-2 — `chore/deps-tooling`

The tier that touches source code.

Ruff 0.16.5 (`RUF100` already cleared in PR-1):

- `ISC004` (45) — apply `--unsafe-fixes`, then review each hunk; these are
  implicit concatenations inside collection literals, where a missing comma and
  an intentional concatenation look identical.
- `PLR0917` (13) — every site already carries `# noqa: PLR0913`, and every one
  is a function whose arguments are supplied by name: eight are the private
  `_principle` helper in `frameworks/*/rules.py`, three are Typer commands, one
  is an MCP tool, one is an internal script helper. None is callable
  positionally in practice, so each directive is extended to
  `# noqa: PLR0913, PLR0917`.
- `CPY001` (446) — configure `[tool.ruff.lint.flake8-copyright]` with `author`,
  `min-file-size`, and `notice-rgx` so only substantial files require a header,
  then add the header to the files that remain flagged. Threshold selection uses
  the measured table above; `min-file-size = 16384` (43 files) is the default
  unless changed during implementation.

Ty 0.0.77:

- Fix the seven `source_url` discards in `javascript/rules.py` (see Open
  Decision below).
- Fix the two `missing-argument` errors in
  `tests/registry/test_registry_bootstrap_coverage.py`.
- Add regression coverage asserting that a per-principle `source_url` survives
  model construction, so the field cannot silently vanish again.

Then re-run all five documentation generators and their `--check` parity hooks,
and confirm both the 95% coverage gate and the 90% interrogate gate still pass.

### PR-3 — `chore/deps-runtime`

The majors, each with a probed blast radius.

- fastmcp `>=3.0.2` → `>=4.0.1`. Change `server.py:45` to
  `from fastmcp.utilities.tasks import TaskConfig`. Gate on the server,
  middleware, and guardrail test suites.
- sqlglot `==29.0.1` → `==30.17.0`, retaining the exact-pin policy. Supersedes
  PR #201. The SQL analyzer tests are the behavioural gate.
- tree-sitter `>=0.25.2` → `>=0.26.0`; pydantic, networkx, and radon to current.
- `uv lock -U`, full CI including the Docker image check and `.mcpb` build.

## Decision: `ZenPrinciple.source_url`

Two resolutions were available, and the choice changes what the model means:

- **Add the field.** Per-principle deep links start working as the JavaScript
  rules clearly intended, and the other 21 languages gain the capability.
- **Delete the seven kwargs.** Treats the feature as never having existed;
  `source_url` stays a language-level attribute only.

**Resolved: add the field**, as an optional
`source_url: HttpUrl | None = Field(default=None, ...)` mirroring the existing
`LanguageSummary.source_url` pattern at `base_models.py:641`. This is
backward-compatible and unblocks the seven dead links. The consequence to accept
is that a URL can now live in two places, so `LanguageZenPrinciples.source_url`
becomes the fallback and the per-principle value takes precedence — the
docstring records that resolution order.

Implemented by Task 8 of the plan.

## Out of scope

Ten stale GitHub Actions bump PRs — #188, #187, #186, #183, #181, #173, #164,
#162, #160, and the actions half of #207. These belong in a separate `ci/`
batch; mixing them in would obscure which tier broke a run.

## Verification

Every PR runs the full pipeline: `lint` → `rrt-checks` →
`[test, language-tests, visual-regression]` → `docker-image-check` →
`[build, docker-publish]`. Locally, each PR must pass
`uvx pre-commit run --all-files` before it opens.

PR-2 and PR-3 additionally require the coverage gate to hold at 95% and
interrogate at 90%, since both tiers modify source.
