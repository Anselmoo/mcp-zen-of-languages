# Contributing

<!-- --8<-- [start:dev-workflow] -->
## Setup

```bash
uv sync --group dev --all-extras
```

This is enough for tests, linting and type checking. The `docs` group is only
needed for documentation work (see [Docs work](#docs-work)).

## Run Checks

```bash
uv run pytest -xvs
uv run ty check
uv run ruff check
```

## Docs work

```bash
uv sync --group dev --group docs
uv run zensical build -f mkdocs.yml
uv run python scripts/check_docs_contrast.py --build --mode check
```

`zensical` is a Rust-built package. It ships prebuilt wheels for macOS
(x86_64, arm64), Linux (manylinux x86_64, aarch64, armv7l; musllinux x86_64,
aarch64) and Windows (amd64, arm64). On other platforms (32-bit Linux, musl
armv7, 32-bit Windows) `--group docs` falls back to building from source, which
needs a Rust toolchain. If you do not need to touch the docs, skip the group and
let CI run the docs build; the `docs-build-strict` pre-push hook can be skipped
with `SKIP=docs-build-strict git push`.

## Pre-commit

```bash
pre-commit install
pre-commit run --all-files
```

## Notes

- Use Python 3.12+ typing (`str | None`, `list[str]`).
- Pydantic v2 only (use `ConfigDict`, avoid `class Config`).
- Rule metrics must match detector config field names.
- Language modules must include `__init__.py`, `analyzer.py`, `detectors.py`, and `rules.py`.
- Follow the rendering conventions in `docs/contributing/rendering-style-guide.md` for all terminal UX changes.
<!-- --8<-- [end:dev-workflow] -->

## Docstring quality checklist

- Start each module/class/function docstring with a domain-specific summary line.
- Document argument and return semantics (not placeholder text like `Value for ...`).
- Use realistic examples when examples are included.
- Keep `See Also` references symbol-relevant; omit the section when no useful cross-reference exists.
- `Raises:` should be included only when callers need to handle concrete exception behavior.
- Template-like boilerplate is disallowed, even when the docstring is syntactically valid.

### Quality examples (Google style)

Bad `Args`:

```python
Args:
    language (str): The language input value.
```

Good `Args`:

```python
Args:
    language (str): Language key used to select zen rules and analyzer pipeline overrides.
```

Bad `Returns`:

```python
Returns:
    AnalysisResult: Computed return value.
```

Good `Returns`:

```python
Returns:
    AnalysisResult: Analysis payload containing metrics, violations, and aggregate score.
```

When to include `Examples`:
- Include examples only for non-obvious call patterns, CLI flows, or tricky edge cases.
- Skip examples when they would only restate the signature.

When to include `See Also`:
- Include only symbol-relevant references that help navigation.
- Omit the section when no direct related symbol adds value.
