# Dependency Update Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Refresh every dependency in `.pre-commit-config.yaml` and `pyproject.toml` across three tiered pull requests, absorbing the source-code changes that upgraded tooling forces.

**Architecture:** Three sequential PRs ordered by blast radius. PR-1 is mechanical realignment that closes the drift between declared floors, `uv.lock`, and pre-commit revs. PR-2 absorbs the source-code churn from ruff 0.16 and ty 0.0.77, including one latent bug the type checker exposed. PR-3 lands the two runtime majors, each with a pre-probed blast radius. Each PR is independently revertable so a red CI run isolates its own cause.

**Tech Stack:** Python 3.12+, uv (package manager, exclusively — never `pip`), ruff (lint + format), ty (type checking), pytest, pre-commit, repo-release-tools (`rrt`) for branches and versioning, zensical for docs.

**Spec:** [`specs/2026-09-02-dependency-update-design.md`](../specs/2026-09-02-dependency-update-design.md)

## Global Constraints

- **Package manager is `uv`, exclusively.** Never run `pip` or `pip install`. Use `uv sync --all-groups --all-extras`, `uv run <cmd>`, `uvx <tool>`.
- **Branches are created with `rrt`, never manually.** Use `uv run poe branch_chore` for all three PRs in this plan.
- **Commit subjects must follow Conventional Commits.** The `rrt-commit-subject` pre-commit hook enforces this on every commit.
- **Never bypass hooks with `--no-verify`.** If a hook auto-fixes files, stage the fixes and re-run `git commit`.
- **Coverage gate: 95%**, measured over `src/mcp_zen_of_languages/` only (`--cov-fail-under=95` in `[tool.pytest.ini_options]`).
- **Docstring coverage gate: 90%** (`interrogate` `fail-under = 90`, excluding `tests` and `scripts`).
- **Ruff runs with `select = ["ALL"]`.** Any newly stabilized rule is auto-enrolled. Only three suppressions are permanent: `COM812`, `E501`, `PLC0415`.
- **Always run ruff with the project config.** Never use a bare `--select <RULE>` to count findings: `RUF100` judges `noqa` directives against *currently enabled* rules, so narrowing the selection inflates the count from 4 to 10+ and would delete legitimate suppressions.
- **Plans and specs live outside `docs/`.** The `check-orphan-docs` hook does `Path("docs").rglob("*.md")` and fails any page missing from `mkdocs.yml` nav.
- **Python version targets:** `requires-python = ">=3.12"`; CI matrix is 3.12, 3.13, 3.14; `ty` targets 3.12.

---

## File Structure

**PR-1 — `chore/deps-align`**

| File | Responsibility |
| --- | --- |
| `pyproject.toml` | Raise stale floors to locked versions; widen `uv_build` bound; drop `pygments`; add three temporary `extend-ignore` entries |
| `.pre-commit-config.yaml` | Bump `ruff-pre-commit` and `repo-release-tools` revs |
| `tests/test_declared_dependencies.py` | **New.** Guard that every declared runtime dependency is actually imported by `src/` |
| `src/mcp_zen_of_languages/adapters/rules_adapter.py` | Remove 3 unused `# noqa: BLE001` |
| `src/mcp_zen_of_languages/analyzers/base.py` | Remove 1 unused `# noqa: BLE001` |
| `docs/getting-started/security.md`, `.github/copilot-instructions.md` | Drop `pygments` from prose dependency lists |
| `uv.lock` | Regenerated |

**PR-2 — `chore/deps-tooling`**

| File | Responsibility |
| --- | --- |
| `pyproject.toml` | Remove the three temporary suppressions; add `[tool.ruff.lint.flake8-copyright]` |
| `src/mcp_zen_of_languages/reporting/prompts.py` | 31 `ISC004` fixes |
| `scripts/generate_dogma_mapping.py`, `scripts/generate_config_docs.py` | 13 `ISC004` fixes |
| `src/mcp_zen_of_languages/languages/go/rules.py` | 1 `ISC004` fix |
| `src/mcp_zen_of_languages/frameworks/{angular,django,fastapi,nextjs,pydantic,react,sqlalchemy,vue}/rules.py` | 8 identical `PLR0917` sites on `_principle` |
| `src/mcp_zen_of_languages/cli.py`, `src/mcp_zen_of_languages/server.py`, `scripts/check_docs_contrast.py` | 5 remaining `PLR0917` sites |
| `src/mcp_zen_of_languages/rules/base_models.py` | Add `ZenPrinciple.source_url` — the latent-bug fix |
| `tests/rules/test_rules_base_models.py` | Regression test for per-principle `source_url` |
| `tests/registry/test_registry_bootstrap_coverage.py` | Fix 2 `missing-argument` errors |

**PR-3 — `chore/deps-runtime`**

| File | Responsibility |
| --- | --- |
| `pyproject.toml` | fastmcp, sqlglot, tree-sitter, pydantic floors |
| `src/mcp_zen_of_languages/server.py:45` | `TaskConfig` import path |
| `uv.lock` | Regenerated |

---

# PR-1 — `chore/deps-align`

Mechanical realignment. No behaviour change.

### Task 1: Guard against undeclared-but-unused runtime dependencies

`pygments` is declared in `[project] dependencies` but has zero imports anywhere in `src/`, `tests/`, or `scripts/`. Rather than just deleting it, add a test that would have caught it, then delete it.

**Files:**
- Create: `tests/test_declared_dependencies.py`
- Modify: `pyproject.toml` (the `dependencies` list), `docs/getting-started/security.md:113`, `.github/copilot-instructions.md:142`

**Interfaces:**
- Consumes: nothing
- Produces: nothing consumed by later tasks

- [ ] **Step 1: Create the branch**

```bash
uv run poe branch_chore
```

Name it `deps-align` when prompted. Confirm with `git branch --show-current`.

- [ ] **Step 2: Write the failing test**

Create `tests/test_declared_dependencies.py`:

```python
from __future__ import annotations

import re
import tomllib

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"

# Import name differs from the distribution name for these packages.
IMPORT_ALIASES = {
    "tree-sitter": "tree_sitter",
}


def _declared_runtime_packages() -> set[str]:
    data = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    names = set()
    for spec in data["project"]["dependencies"]:
        name = re.split(r"[<>=!\[ ]", spec, maxsplit=1)[0].strip()
        names.add(name.lower())
    return names


def _imported_modules() -> set[str]:
    pattern = re.compile(r"^\s*(?:from|import)\s+([A-Za-z_][A-Za-z0-9_]*)", re.MULTILINE)
    modules = set()
    for path in SRC.rglob("*.py"):
        modules.update(pattern.findall(path.read_text(encoding="utf-8")))
    return modules


def test_every_declared_runtime_dependency_is_imported():
    imported = _imported_modules()
    unused = sorted(
        name
        for name in _declared_runtime_packages()
        if IMPORT_ALIASES.get(name, name.replace("-", "_")) not in imported
    )
    assert not unused, f"declared but never imported by src/: {unused}"
```

- [ ] **Step 3: Run the test to verify it fails**

```bash
uv run pytest tests/test_declared_dependencies.py -v --no-cov
```

Expected: FAIL with `declared but never imported by src/: ['pygments']`

- [ ] **Step 4: Remove the dependency**

In `pyproject.toml`, delete the line `    "pygments>=2.19.2",` from `[project] dependencies`.

- [ ] **Step 5: Run the test to verify it passes**

```bash
uv run pytest tests/test_declared_dependencies.py -v --no-cov
```

Expected: PASS

- [ ] **Step 6: Update the two prose references**

In `docs/getting-started/security.md`, delete line 113:

```markdown
- **pygments** — Syntax highlighting (mature, stable)
```

In `.github/copilot-instructions.md` line 142, change:

```markdown
- External: fastmcp, networkx, pydantic, pygments, radon, tree-sitter
```

to:

```markdown
- External: fastmcp, networkx, pydantic, radon, tree-sitter
```

Note: `mkdocs.yml:162`'s `pygments_lang_class: true` is a docs-theme highlighting setting, not a reference to the runtime dependency. **Leave it alone.**

- [ ] **Step 7: Re-sync and run the full suite**

```bash
uv sync --all-groups --all-extras
uv run pytest -x -q
```

Expected: all tests pass, coverage ≥ 95%.

- [ ] **Step 8: Commit**

```bash
git add tests/test_declared_dependencies.py pyproject.toml docs/getting-started/security.md .github/copilot-instructions.md uv.lock
git commit -m "chore: drop unused pygments runtime dependency"
```

---

### Task 2: Realign stale version floors to the locked versions

The declared floors sit below what `uv.lock` already resolves, which is why Dependabot stays silent while the floors rot. Raise each floor to the locked version.

**Files:**
- Modify: `pyproject.toml`

**Interfaces:**
- Consumes: Task 1's branch
- Produces: nothing consumed by later tasks

- [ ] **Step 1: Apply the floor changes**

In `[project] dependencies`:

```toml
    "typer>=0.26.7",        # was >=0.12.0
```

In `[build-system]`:

```toml
requires = ["uv_build>=0.9.26,<0.13.0"]   # was <0.12.0
```

The `<0.12.0` bound currently excludes the installed uv 0.12.6, producing this warning on every build:
`warning: build_system.requires = ["uv-build>=0.9.26,<0.12.0"] does not contain the current uv version 0.12.6`

In `[dependency-groups] docs`:

```toml
    "zensical>=0.0.46",                                  # was >=0.0.23
    "mkdocstrings[python]>=1.0.4",                       # was >=0.26.0
    "mkdocs-git-revision-date-localized-plugin>=1.5.3",  # was >=1.3.0
    "mkdocs-glightbox>=0.5.2",                           # was >=0.4.0
```

In `[dependency-groups] dev`:

```toml
    "poethepoet>=0.46.0",       # was >=0.33.1
    "playwright>=1.60.0",       # was >=1.54.0
    "ruff>=0.16.5",             # was >=0.14.14 — must match the pre-commit rev, see Task 3
    "ty>=0.0.51",               # was >=0.0.16 — PR-2 raises this to 0.0.77
    "repo-release-tools>=1.9.0",# was >=1.8.1
```

**The ruff floor must equal the pre-commit rev Task 3 sets.** CI's `lint` job runs
`uv run ruff check` (the *locked* ruff) **and** `uvx pre-commit run --all-files`
(the *pinned rev*). Leaving the lock behind the rev makes the two disagree —
which is the same three-way drift PR-1 exists to eliminate. Task 3's `RUF100`
fix is the concrete case: ruff 0.16 narrowed `BLE001` so it no longer fires when
the caught exception is logged, so 0.16.5 calls those four `# noqa: BLE001`
unused while 0.15.18 still requires them. Mutually exclusive; only matching
versions resolves it.

Leave `mkdocs-minify-plugin`, `cairosvg`, `jinja2`, `pytest`, `pytest-asyncio`, `pytest-cov`, `interrogate` unchanged — their floors already match the locked versions.

- [ ] **Step 2: Verify resolution does not move**

```bash
uv lock --check
```

Expected: exits 0. Raising a floor to a version already in the lock must not force a re-resolve. If it reports the lock is stale, run `uv lock` and inspect `git diff uv.lock` — any version *change* here means a floor was raised too far; back it off to the locked value.

- [ ] **Step 3: Run the full suite**

```bash
uv sync --all-groups --all-extras
uv run pytest -x -q
```

Expected: all tests pass.

- [ ] **Step 4: Commit**

```bash
git add pyproject.toml uv.lock
git commit -m "chore: align dependency floors with locked versions"
```

---

### Task 3: Bump pre-commit revs and absorb `RUF100`

Bumping `ruff-pre-commit` to `v0.16.5` enrolls four newly stabilized rules. `RUF100` (4 findings) is auto-fixable and lands here. `CPY001`, `ISC004`, and `PLR0917` are suppressed **temporarily** so PR-1 stays green; PR-2 removes the suppressions and handles them properly.

**Files:**
- Modify: `.pre-commit-config.yaml:14` and `:23`, `pyproject.toml` (`extend-ignore`), `src/mcp_zen_of_languages/adapters/rules_adapter.py:405,470,512`, `src/mcp_zen_of_languages/analyzers/base.py:1030`

**Interfaces:**
- Consumes: Task 2's branch
- Produces: three temporary `extend-ignore` entries that Task 5, Task 6, and Task 7 each remove

- [ ] **Step 1: Bump the two revs**

In `.pre-commit-config.yaml`, change `rev: v0.15.15` to `rev: v0.16.5` under `https://github.com/astral-sh/ruff-pre-commit`, and `rev: v1.16.0` to `rev: v1.17.1` under `https://github.com/Anselmoo/repo-release-tools`.

Leave `pre-commit/pre-commit-hooks` at `v6.0.0` — it is already current.

- [ ] **Step 2: Add the temporary suppressions**

In `pyproject.toml`, `[tool.ruff.lint].extend-ignore`, append below the three permanent entries:

```toml
    # Temporary — newly stabilised in ruff 0.16, handled in PR-2 (chore/deps-tooling).
    "CPY001",  # missing-copyright-notice (446) — flake8-copyright config pending
    "ISC004",  # implicit-string-concatenation-in-collection-literal (45)
    "PLR0917", # too-many-positional-arguments (13)
```

- [ ] **Step 3: Confirm only `RUF100` remains**

```bash
uvx ruff@0.16.5 check src tests scripts --output-format concise
```

Expected: exactly 4 errors, all `RUF100`, at
`src/mcp_zen_of_languages/adapters/rules_adapter.py:405:43`, `:470:39`, `:512:39`, and
`src/mcp_zen_of_languages/analyzers/base.py:1030:39` — each `Unused 'noqa' directive (unused: BLE001)`.

- [ ] **Step 4: Auto-fix them**

```bash
uvx ruff@0.16.5 check src tests scripts --fix
```

This strips the four `# noqa: BLE001` comments. Read each hunk in `git diff` and confirm only a trailing `# noqa: BLE001` was removed — no code change.

- [ ] **Step 5: Verify the tree is clean under 0.16.5**

```bash
uvx ruff@0.16.5 check src tests scripts
uvx ruff@0.16.5 format --check src tests scripts
```

Expected: `All checks passed!` and no format diff.

- [ ] **Step 6: Run all hooks**

```bash
uvx pre-commit run --all-files
```

Expected: all pass. The `ty` hook still runs the locked 0.0.51, which passes cleanly.

- [ ] **Step 7: Run the full suite**

```bash
uv run pytest -x -q
```

Expected: all tests pass.

- [ ] **Step 8: Commit**

```bash
git add .pre-commit-config.yaml pyproject.toml src/mcp_zen_of_languages/adapters/rules_adapter.py src/mcp_zen_of_languages/analyzers/base.py
git commit -m "chore: bump pre-commit revs to ruff 0.16.5 and rrt 1.17.1"
```

---

### Task 4: Refresh the lock and open PR-1

**Files:**
- Modify: `uv.lock`

**Interfaces:**
- Consumes: Tasks 1-3
- Produces: merged `chore/deps-align` branch that PR-2 builds on

- [ ] **Step 1: Upgrade the lock**

```bash
uv lock -U
uv sync --all-groups --all-extras
```

- [ ] **Step 2: Review what moved**

```bash
git diff --stat uv.lock
```

Any package jumping a major version here is unexpected in PR-1 — the runtime majors belong in PR-3. If `fastmcp` moves to 4.x or `sqlglot` moves to 30.x, stop and check that the floors from Task 2 were applied as written.

- [ ] **Step 3: Full verification**

```bash
uvx pre-commit run --all-files
uv run pytest -x -q
uv run poe build_docs
```

Expected: all pass.

- [ ] **Step 4: Commit and open the PR**

```bash
git add uv.lock
git commit -m "chore: refresh lockfile after floor realignment"
git push -u origin HEAD
```

Open the PR with the GitHub MCP tools (`mcp__github__create_pull_request`) — **not** the `gh` CLI, which always returns `401 Bad credentials` in this repo. Title: `chore: align dependency declarations with lockfile`. In the body, note that this supersedes PR #207 and adopts PR #198.

---

# PR-2 — `chore/deps-tooling`

The tier that touches source code. Branch from `main` after PR-1 merges.

### Task 5: Fix the 45 `ISC004` findings

`ISC004` flags implicit string concatenation inside a collection literal — where a missing comma and a deliberate multi-line string look identical. The fix is mechanical but each hunk needs an eye, because "wrap this long string" and "I forgot a comma" produce the same lint.

**Files:**
- Modify: `pyproject.toml` (drop the `ISC004` suppression), `src/mcp_zen_of_languages/reporting/prompts.py` (31), `scripts/generate_dogma_mapping.py` (10), `scripts/generate_config_docs.py` (3), `src/mcp_zen_of_languages/languages/go/rules.py` (1)

**Interfaces:**
- Consumes: PR-1 merged
- Produces: nothing consumed by later tasks

- [ ] **Step 1: Create the branch and raise the tool floors**

```bash
uv run poe branch_chore
```

Name it `deps-tooling`. Then in `pyproject.toml` `[dependency-groups] dev`, set `"ty>=0.0.77"` (the ruff floor already reached 0.16.5 in PR-1 Task 2), and run:

```bash
uv lock -U && uv sync --all-groups --all-extras
```

- [ ] **Step 2: Remove the `ISC004` suppression**

Delete the `"ISC004",` line added in Task 3 Step 2 from `[tool.ruff.lint].extend-ignore`.

- [ ] **Step 3: Confirm the 45 findings reappear**

```bash
uv run ruff check src tests scripts --output-format concise | grep -c ISC004
```

Expected: `45`.

- [ ] **Step 4: Apply the fixes**

```bash
uv run ruff check src tests scripts --fix --unsafe-fixes
```

`ISC004` fixes are marked unsafe because ruff cannot know whether you meant a comma. That is why the next step is mandatory.

- [ ] **Step 5: Review every hunk**

```bash
git diff
```

For each change, confirm the two adjacent string literals were genuinely one logical string. If any pair reads as two separate list items with a missing comma, **that is a real bug** — add the comma instead of merging, and note it in the commit body.

- [ ] **Step 6: Verify and run affected tests**

```bash
uv run ruff check src tests scripts
uv run pytest tests/reporting -q --no-cov
uv run pytest -x -q
```

Expected: `All checks passed!` and all tests pass. `reporting/prompts.py` holds 31 of the 45 changes, so `tests/reporting` is the sharpest signal.

- [ ] **Step 7: Regenerate docs touched by the changed scripts**

```bash
uv run poe generate_config_docs
uv run poe generate_implementation_counts
git status --short
```

`generate_dogma_mapping.py` and `generate_config_docs.py` were modified, so confirm their output is unchanged. If any generated doc changed, the string merge altered emitted text — revert that hunk and add the comma instead.

- [ ] **Step 8: Commit**

```bash
git add pyproject.toml src scripts uv.lock
git commit -m "style: resolve ISC004 implicit string concatenation in collections"
```

---

### Task 6: Fix the 13 `PLR0917` findings

`PLR0917` (too many *positional* arguments) is distinct from `PLR0913` (too many arguments), which the codebase already suppresses at several of these exact sites. Eight of the thirteen are the identical `_principle` helper repeated across framework rule modules.

**Files:**
- Modify: `pyproject.toml` (drop the `PLR0917` suppression); `src/mcp_zen_of_languages/frameworks/{angular,django,fastapi,nextjs,pydantic,react,sqlalchemy,vue}/rules.py:12`; `src/mcp_zen_of_languages/cli.py:1792,1865,1933`; `src/mcp_zen_of_languages/server.py:1743`; `scripts/check_docs_contrast.py:345`

**Interfaces:**
- Consumes: Task 5's branch
- Produces: nothing consumed by later tasks

- [ ] **Step 1: Remove the `PLR0917` suppression**

Delete the `"PLR0917",` line from `[tool.ruff.lint].extend-ignore`.

- [ ] **Step 2: Confirm the 13 findings reappear**

```bash
uv run ruff check src tests scripts --output-format concise | grep PLR0917
```

Expected: 13 lines matching the file list above.

- [ ] **Step 3: Extend the existing suppression at all 13 sites**

Every one of the 13 sites already carries `# noqa: PLR0913`, and every one is a function whose arguments are supplied by name rather than positionally — eight are the private `_principle` helper, three are Typer commands (dispatched from parsed CLI options), one is an MCP tool (dispatched by FastMCP from a named payload), and one is an internal script helper. None can be called positionally in practice, so `PLR0917` is the same call shape `PLR0913` already recorded a judgement on, seen through a narrower lens.

The change is identical at every site: extend the directive from one rule to two.

In each of the eight framework files — `src/mcp_zen_of_languages/frameworks/{angular,django,fastapi,nextjs,pydantic,react,sqlalchemy,vue}/rules.py` at line 12:

```python
def _principle(  # noqa: PLR0913, PLR0917
```

In `src/mcp_zen_of_languages/cli.py` at lines 1792, 1865, and 1933 respectively:

```python
def reports(  # noqa: PLR0913, PLR0917
def check(  # noqa: PLR0913, PLR0917
def prompts(  # noqa: PLR0913, PLR0917
```

In `src/mcp_zen_of_languages/server.py` at line 1743:

```python
async def set_config_override(  # noqa: PLR0913, PLR0917
```

In `scripts/check_docs_contrast.py` at line 345:

```python
def run_audit(  # noqa: PLR0913, PLR0917
```

- [ ] **Step 4: Confirm no `RUF100` regression**

```bash
uv run ruff check src tests scripts --output-format concise | grep -c RUF100
```

Expected: `0`. This guards the change from the opposite direction — if a `PLR0913` suppression at any of these sites had become unnecessary, adding `PLR0917` beside it would leave a half-unused directive, and `RUF100` is the rule that catches it.

- [ ] **Step 5: Verify**

```bash
uv run ruff check src tests scripts
uv run pytest -x -q
```

Expected: `All checks passed!` and all tests pass.

- [ ] **Step 6: Commit**

```bash
git add pyproject.toml src scripts
git commit -m "refactor: resolve PLR0917 too-many-positional-arguments findings"
```

---

### Task 7: Configure `flake8-copyright` and add headers to substantial files

`CPY001` flags all 446 Python files at the default `min-file-size = 0`. The chosen policy is to require headers only on substantial files.

Measured counts by threshold: `0` → 446, `1024` → 330, `2048` → 282, `4096` → 207, `8192` → 107, `16384` → 43.

**Files:**
- Modify: `pyproject.toml` (drop the `CPY001` suppression; add `[tool.ruff.lint.flake8-copyright]`), plus the 43 files the threshold leaves flagged

**Interfaces:**
- Consumes: Task 6's branch
- Produces: nothing consumed by later tasks

- [ ] **Step 1: Remove the `CPY001` suppression**

Delete the `"CPY001",` line and the `# Temporary — newly stabilised in ruff 0.16...` comment block from `[tool.ruff.lint].extend-ignore`. Only the three permanent entries (`COM812`, `E501`, `PLC0415`) should remain.

- [ ] **Step 2: Add the copyright configuration**

In `pyproject.toml`, after the `[tool.ruff.lint.pydocstyle]` block, add:

```toml
[tool.ruff.lint.flake8-copyright]
# Headers are required only on substantial modules; the repo-level MIT LICENSE
# covers the rest. 16384 bytes leaves 43 files in scope (446 at the default 0).
author = "Anselm Hahn"
min-file-size = 16384
notice-rgx = "(?i)Copyright \\(C\\) \\d{4}"
```

- [ ] **Step 3: List the files still flagged**

```bash
uv run ruff check src tests scripts --output-format concise | grep CPY001 | cut -d: -f1 | sort -u
```

Expected: 43 paths. Record this list — it is the exact work for Step 4.

- [ ] **Step 4: Add the header to each flagged file**

For each path from Step 3, insert this as the very first line, above the module docstring:

```python
# Copyright (C) 2026 Anselm Hahn. Licensed under the MIT License.
```

The header must precede the docstring. Placing it after would leave the docstring no longer first in the module, which changes `__doc__` and breaks `interrogate`'s module-docstring detection (`ignore-module = false`).

- [ ] **Step 5: Verify all four gates**

```bash
uv run ruff check src tests scripts
uv run ruff format --check src tests scripts
uv run pytest -x -q
uvx --from interrogate interrogate -c pyproject.toml src
```

Expected: ruff clean, no format diff, tests pass with coverage ≥ 95%, interrogate ≥ 90%. Interrogate is the one most at risk here — if it drops, a header landed below a docstring.

- [ ] **Step 6: Commit**

```bash
git add pyproject.toml src tests scripts
git commit -m "chore: configure flake8-copyright and add headers to substantial modules"
```

---

### Task 8: Fix the silently discarded `source_url` kwargs

This is a real latent bug, not lint noise. `LanguageZenPrinciples` declares `source_url` (`base_models.py:305`), which is why line 15 of every language's `rules.py` works. `ZenPrinciple` does **not** declare one. JavaScript is the only language that also attaches *per-principle* deep links — `#destructuring`, `#properties--eval`, and five others — by passing `source_url=` to `ZenPrinciple(...)`. Pydantic discards each silently, so those URLs have never reached any output, and no test caught it because nothing can assert on a field that does not exist.

This task implements the spec's Open Decision as **add the field**, which makes the seven existing deep links work and gives the other 21 languages the same capability. The alternative — deleting the seven `source_url=` kwargs from `javascript/rules.py` — is a one-step change if you prefer to treat the feature as never having existed.

**Files:**
- Modify: `src/mcp_zen_of_languages/rules/base_models.py` (`ZenPrinciple`, ~lines 153 and 195)
- Test: `tests/rules/test_rules_base_models.py`

**Interfaces:**
- Consumes: Task 7's branch
- Produces: `ZenPrinciple.source_url: HttpUrl | None` — an optional field defaulting to `None`, readable as `principle.source_url`

- [ ] **Step 1: Write the failing test**

Append to `tests/rules/test_rules_base_models.py`:

```python
def test_zen_principle_retains_per_principle_source_url():
    from pydantic import HttpUrl

    from mcp_zen_of_languages.rules.base_models import PrincipleCategory
    from mcp_zen_of_languages.rules.base_models import ZenPrinciple

    principle = ZenPrinciple(
        id="js-012",
        principle="Use destructuring for assignment",
        category=PrincipleCategory.IDIOMS,
        severity=5,
        description="Prefer destructuring over manual extraction",
        source_url=HttpUrl("https://github.com/airbnb/javascript#destructuring"),
    )

    assert principle.source_url is not None
    assert str(principle.source_url).endswith("#destructuring")


def test_zen_principle_source_url_defaults_to_none():
    from mcp_zen_of_languages.rules.base_models import PrincipleCategory
    from mcp_zen_of_languages.rules.base_models import ZenPrinciple

    principle = ZenPrinciple(
        id="python-001",
        principle="Explicit is better than implicit",
        category=PrincipleCategory.IDIOMS,
        severity=5,
        description="Say what you mean",
    )

    assert principle.source_url is None
```

- [ ] **Step 2: Run the test to verify it fails**

```bash
uv run pytest tests/rules/test_rules_base_models.py::test_zen_principle_retains_per_principle_source_url -v --no-cov
```

Expected: FAIL on `assert principle.source_url is not None` — Pydantic discards the unknown kwarg, so the attribute does not exist and the assertion raises `AttributeError`.

- [ ] **Step 3: Add the field**

In `src/mcp_zen_of_languages/rules/base_models.py`, inside `class ZenPrinciple`, add the field immediately after `required_config` and before `model_config = ConfigDict(use_enum_values=True)`:

```python
    source_url: HttpUrl | None = Field(
        default=None,
        description="URL to the upstream guidance for this specific principle",
    )
```

`HttpUrl` is already imported in this module (used by `LanguageZenPrinciples.source_url` at line 305). This mirrors `LanguageSummary.source_url` at line 641, which is the established optional-URL pattern in this file.

- [ ] **Step 4: Add the docstring entry**

In the same class's `Attributes:` block, immediately after the `required_config:` entry, add:

```
        source_url: URL to the upstream guidance for this specific principle,
            overriding the language-level ``LanguageZenPrinciples.source_url``
            when present.
```

`interrogate` requires this — the class docstring documents every field, and a `ruff` `D` rule under `select = ["ALL"]` will flag the omission.

- [ ] **Step 5: Run the tests to verify they pass**

```bash
uv run pytest tests/rules/test_rules_base_models.py -v --no-cov
```

Expected: both new tests PASS.

- [ ] **Step 6: Confirm the ty warnings are gone**

```bash
uv run ty check src tests --error-on-warning
```

Expected: the 7 `pydantic-discarded-extra-argument` warnings in `languages/javascript/rules.py` are gone. Two `missing-argument` errors in `tests/registry/test_registry_bootstrap_coverage.py` remain — Task 9 handles those.

- [ ] **Step 7: Regenerate the language docs**

```bash
uv run poe generate_language_docs
uv run poe check_orphan_docs
git status --short
```

A new serialized field can change generated per-language pages. If pages changed, that is expected and correct — the seven JavaScript deep links now appear. Stage the regenerated output.

- [ ] **Step 8: Run the full suite**

```bash
uv run pytest -x -q
```

Expected: all tests pass, coverage ≥ 95%.

- [ ] **Step 9: Commit**

```bash
git add src/mcp_zen_of_languages/rules/base_models.py tests/rules/test_rules_base_models.py docs
git commit -m "fix: add ZenPrinciple.source_url so per-principle links are not discarded"
```

---

### Task 9: Fix the two `missing-argument` errors and close out PR-2

`ty` 0.0.77 now resolves the dynamically built config models from `_build_rule_configs` and sees that `type` is required. The test calls the factories with no arguments.

**Files:**
- Modify: `tests/registry/test_registry_bootstrap_coverage.py:13-14`

**Interfaces:**
- Consumes: Task 8's branch
- Produces: merged `chore/deps-tooling` branch that PR-3 builds on

- [ ] **Step 1: Reproduce the errors**

```bash
uv run ty check src tests --error-on-warning
```

Expected: 2 × `error[missing-argument]: No argument provided for required parameter 'type'` at `tests/registry/test_registry_bootstrap_coverage.py:13:12` and `:14:12`.

- [ ] **Step 2: Read the current assertions**

Lines 12-14 currently read:

```python
    configs = _build_rule_configs(["bash-006", "custom-001"])
    assert configs["bash-006"]().type == "bash-006"
    assert configs["custom-001"]().type == "custom-001"
```

The test asserts the factory *defaults* `type` to the rule ID. `ty` reads the generated model signature and sees `type` as required, so it cannot know a default was supplied at model-creation time.

- [ ] **Step 3: Determine which side is wrong**

```bash
uv run pytest tests/registry/test_registry_bootstrap_coverage.py -v --no-cov
```

If the test **passes**, the runtime default is real and `ty` is over-strict about a `pydantic.create_model`-generated signature. Fix by making the intent explicit at the call:

```python
    assert configs["bash-006"](type="bash-006").type == "bash-006"
    assert configs["custom-001"](type="custom-001").type == "custom-001"
```

Then add a second assertion that still pins the defaulting behaviour the original test cared about:

```python
    assert configs["bash-006"]().type == "bash-006"  # ty: ignore[missing-argument]
```

If the test **fails**, `ty` found a second real bug — `_build_rule_configs` is not defaulting `type` as `registry_bootstrap.py:126-133` intends. Fix the factory, not the test.

- [ ] **Step 4: Verify ty is clean**

```bash
uv run ty check src tests --error-on-warning
```

Expected: `All checks passed!`

- [ ] **Step 5: Full verification**

```bash
uvx pre-commit run --all-files
uv run pytest -x -q
uvx --from interrogate interrogate -c pyproject.toml src
uv run poe build_docs
uv run poe check_implementation_counts
```

Expected: all pass; coverage ≥ 95%; interrogate ≥ 90%.

- [ ] **Step 6: Commit and open the PR**

```bash
git add tests/registry/test_registry_bootstrap_coverage.py
git commit -m "test: satisfy ty missing-argument on generated rule configs"
git push -u origin HEAD
```

Open the PR with `mcp__github__create_pull_request`. Title: `chore: upgrade ruff to 0.16.5 and ty to 0.0.77`. In the body, call out that the ty upgrade exposed a real bug — seven per-principle `source_url` deep links silently discarded since they were written — and that Task 8 fixed it.

---

# PR-3 — `chore/deps-runtime`

The two runtime majors. Branch from `main` after PR-2 merges.

### Task 10: Upgrade fastmcp 3.4.2 → 4.0.1

Probed against this repo's exact import list: 7 of 8 symbols resolve unchanged, `FastMCP.__init__` still accepts all 8 keywords `server.py:144` passes, `FastMCP.tool()` still accepts `task=`, and the `tasks` / `code-mode` / `apps` extras all still exist. The single break is that `fastmcp.server.tasks` was removed; `TaskConfig` now lives at `fastmcp.utilities.tasks`.

**Files:**
- Modify: `pyproject.toml` (`[project] dependencies`), `src/mcp_zen_of_languages/server.py:45`

**Interfaces:**
- Consumes: PR-2 merged
- Produces: nothing consumed by later tasks

- [ ] **Step 1: Create the branch**

```bash
uv run poe branch_chore
```

Name it `deps-runtime`.

- [ ] **Step 2: Raise the floor**

In `pyproject.toml`, change:

```toml
    "fastmcp[tasks, code-mode, apps]>=4.0.1",
```

The extras list is unchanged — all three still exist on fastmcp 4.

- [ ] **Step 3: Sync and confirm the expected failure**

```bash
uv lock -U && uv sync --all-groups --all-extras
uv run python -c "import mcp_zen_of_languages.server"
```

Expected: `ModuleNotFoundError: No module named 'fastmcp.server.tasks'`

- [ ] **Step 4: Fix the import**

In `src/mcp_zen_of_languages/server.py`, change line 45 from:

```python
from fastmcp.server.tasks import TaskConfig
```

to:

```python
from fastmcp.utilities.tasks import TaskConfig
```

Change nothing else. `BACKGROUND_TASK = TaskConfig(mode="optional", poll_interval=timedelta(seconds=5))` at line 186 and all six `task=BACKGROUND_TASK` sites (lines 878, 1050, 1180, 1283, 1423, 1521) are unaffected.

- [ ] **Step 5: Confirm the import resolves**

```bash
uv run python -c "import mcp_zen_of_languages.server; print('ok')"
```

Expected: `ok`

- [ ] **Step 6: Run the server-facing suites**

```bash
uv run pytest tests/server tests/entrypoint tests/e2e -q --no-cov
```

These cover `FastMCP` construction, the middleware chain (`CallNext`, `Middleware`, `MiddlewareContext`), the lifespan hook, and the guardrails. Expected: all pass.

- [ ] **Step 7: Run the full suite**

```bash
uv run pytest -x -q
```

Expected: all tests pass, coverage ≥ 95%.

- [ ] **Step 8: Regenerate the MCP tools reference**

```bash
uv run poe generate_mcp_tools_docs
uv run poe check_orphan_docs
git status --short
```

Stage any regenerated output.

- [ ] **Step 9: Commit**

```bash
git add pyproject.toml src/mcp_zen_of_languages/server.py uv.lock docs
git commit -m "feat: upgrade fastmcp to 4.0.1"
```

---

### Task 11: Upgrade sqlglot 29.0.1 → 30.17.0

The `==` pin dates to PR #60 and is a defensive policy against sqlglot's frequent parser changes, not a record of a known incompatibility. The full surface this repo uses — `sqlglot.parse`, `sqlglot.errors.ParseError`, `Expression.find_all`, and `exp.Column` / `exp.Expression` / `exp.Select` / `exp.Star` — is present and behaviourally correct on 30.17.0. Residual risk is behavioural: parser output on edge-case SQL.

**Files:**
- Modify: `pyproject.toml` (`[project] dependencies`)

**Interfaces:**
- Consumes: Task 10's branch
- Produces: nothing consumed by later tasks

- [ ] **Step 1: Capture the current SQL baseline**

```bash
uv run pytest tests -q --no-cov -k sql > /tmp/sql-baseline.txt 2>&1; tail -3 /tmp/sql-baseline.txt
```

Record the pass count. This is what must still hold after the bump.

- [ ] **Step 2: Bump the pin**

In `pyproject.toml`, change `"sqlglot==29.0.1",` to `"sqlglot==30.17.0",`.

Keep the `==`. The exact-pin policy is deliberate; this task bumps the pin, it does not relax it.

- [ ] **Step 3: Sync**

```bash
uv lock -U && uv sync --all-groups --all-extras
```

- [ ] **Step 4: Run the SQL suites**

```bash
uv run pytest tests -q --no-cov -k sql
```

Expected: the same pass count as Step 1. The nine detectors in `src/mcp_zen_of_languages/languages/sql/detectors.py` — `sql-001` through the transaction-boundary rule — all depend on sqlglot's AST shape, so a behavioural change surfaces here first.

If a detector test fails, the cause is a parser output change, not an API break. Read the failing assertion, print the parsed AST with `sqlglot.parse(<the test's SQL>)`, and adapt the detector's traversal. Do **not** loosen the test.

- [ ] **Step 5: Run the full suite**

```bash
uv run pytest -x -q
```

Expected: all tests pass, coverage ≥ 95%.

- [ ] **Step 6: Commit**

```bash
git add pyproject.toml uv.lock
git commit -m "chore: bump sqlglot pin to 30.17.0"
```

---

### Task 12: Bump the remaining runtime floors and close out PR-3

**Files:**
- Modify: `pyproject.toml` (`[project] dependencies`), `uv.lock`

**Interfaces:**
- Consumes: Task 11's branch
- Produces: merged `chore/deps-runtime` branch — the plan's final state

- [ ] **Step 1: Raise the remaining floors**

In `[project] dependencies`:

```toml
    "networkx>=3.6.1",     # unchanged, already current
    "pydantic>=2.13.5",    # was >=2.12.5
    "radon>=6.0.1",        # unchanged, already current
    "tree-sitter>=0.26.0", # was >=0.25.2
```

`tree-sitter` is a 0.x package, so 0.25 → 0.26 may carry breaking changes. This repo's usage is narrow: a single `from tree_sitter import Parser` inside a `try` block in `src/mcp_zen_of_languages/utils/parsers.py:45`, whose documented contract is to fall back to the stdlib `ast` module when tree-sitter is unavailable.

- [ ] **Step 2: Sync and verify the parser path**

```bash
uv lock -U && uv sync --all-groups --all-extras
uv run pytest tests/utils -q --no-cov
```

Expected: all pass. If the tree-sitter path now silently falls back to `ast`, `ParserResult.type` will read `"ast"` where a test expects `"tree-sitter"` — that is a real regression, not an acceptable fallback. Fix the call to match the 0.26 `Parser` API rather than accepting the degraded path.

- [ ] **Step 3: Confirm the declared-dependency guard still holds**

```bash
uv run pytest tests/test_declared_dependencies.py -v --no-cov
```

Expected: PASS. This is the test from Task 1; it catches any dependency that became unused during this plan.

- [ ] **Step 4: Full verification**

```bash
uvx pre-commit run --all-files
uv run pytest -x -q
uvx --from interrogate interrogate -c pyproject.toml src
uv run poe build_docs
uv run poe build_mcpb
```

Expected: all pass; coverage ≥ 95%; interrogate ≥ 90%; the `.mcpb` bundle builds into the gitignored `dist/`.

- [ ] **Step 5: Confirm no drift remains**

```bash
uv lock --check
uv run ruff check src tests scripts
uv run ty check src tests --error-on-warning
```

Expected: all clean. At this point the three sources of truth — declared floors, `uv.lock`, and pre-commit revs — agree.

- [ ] **Step 6: Commit and open the PR**

```bash
git add pyproject.toml uv.lock
git commit -m "chore: bump pydantic and tree-sitter to current"
git push -u origin HEAD
```

Open the PR with `mcp__github__create_pull_request`. Title: `chore: upgrade fastmcp to 4.x and sqlglot to 30.x`. In the body, note that this supersedes PR #201.

- [ ] **Step 7: Close the superseded Dependabot PRs**

After all three PRs merge, close #207, #201, and #198 with a comment pointing at the PR that superseded each. Use `mcp__github__issue_write` or `mcp__github__update_pull_request` — not the `gh` CLI.

---

## Out of Scope

Ten stale GitHub Actions bump PRs — #188, #187, #186, #183, #181, #173, #164, #162, #160, and the actions half of #207. These belong in a separate `ci/` batch; mixing them in would obscure which tier broke a run.
