# MCP Zen of Languages - AI Agent Instructions

## Architecture Overview

This is an MCP server for multi-language code analysis against "zen principles" (idiomatic best practices). Core components:

- **server.py**: FastMCP server exposing analysis tools via `@mcp.tool` decorators
- **__main__.py**: Entry point for `python -m mcp_zen_of_languages` or `zen-mcp-server`
- **config.py**: Auto-loads `zen-config.yaml` (CWD or parent until `pyproject.toml`)
- **languages/*/rules.py**: Canonical Pydantic models defining zen principles per language
- **analyzers/**: Language-specific analyzers using Template Method pattern (see `base.py`)
- **analyzers/pipeline.py**: Builds detector configs from rules and merges overrides
- **analyzers/detectors/**: Individual violation detectors (Strategy pattern)
- **models.py**: Analysis results with dict-like access for legacy compatibility
- **cli.py**: Local analysis wrapper (`zen check file.py`)

Data flow: `server`/`cli` -> `create_analyzer()` -> `BaseAnalyzer.analyze()` (parse/metrics) -> `DetectionPipeline` detectors -> `AnalysisResult`.

## Running the Server

```bash
# Via module
python -m mcp_zen_of_languages

# Via entry point (after uv sync)
zen-mcp-server

# For local CLI analysis
zen check myfile.py
```

## Build, Test, Lint

- Setup: `uv sync --all-groups --all-extras`
- Build: `uv build`
- Tests: `uv run pytest`
- Single test: `uv run pytest tests/test_server_routing.py::test_analyze_zen_violations_python`
- Type check: `uv run ty check` (preferred over mypy)
- Lint: `uv run ruff check`
- Pre-commit (all): `uvx pre-commit run --all-files`
- Pre-push docs gate: `uvx pre-commit run --hook-stage pre-push --all-files`

## Key Patterns & Conventions

- **Pydantic v2 everywhere**: Use models with `ConfigDict`, avoid raw dict/list returns
- **Modern typing**: `str | None` not `Optional[str]`, `list[str]` not `List[str]` (Python 3.12+)
- **Config access**: Direct attribute `config.max_nesting_depth`, never `.get()`
- **Rule projection is strict**: rule `metrics` keys must match detector config fields exactly
- **Pipeline overrides**: `zen-config.yaml` pipelines merge over rule-derived defaults by detector `type`
- **Rules canonical**: `src/mcp_zen_of_languages/languages/*/rules.py` only
- **MCP imports**: `import fastmcp as MCP` then `mcp = MCP.FastMCP(...)`
- **Analyzer pattern**: Template Method in `base.py` - subclasses override `parse_code()` and `compute_metrics()`
- **Detector pattern**: Strategy in `languages/*/detectors*` - each detector implements `ViolationDetector.detect()`
- **Config auto-load**: `zen-config.yaml` discovered from CWD automatically

## Adding a New Detector

1. Create detector class in `languages/{lang}/detectors.py` or `languages/python/detectors/*` implementing `ViolationDetector`
2. Add config model in `languages/configs.py` extending `DetectorConfig`
3. Register in `registry_bootstrap.py` with rule_id mapping
4. Add tests in `tests/`

## Adding a New Language

1. Define zen principles in `languages/{lang}/rules.py`
2. Create `languages/{lang}/analyzer.py` subclassing `BaseAnalyzer`
3. Register language-specific detectors
4. Add to `analyzer_factory.py`
5. Update `zen-config.yaml` example

## Integration Points

- External: fastmcp, networkx, pydantic, pygments, radon, tree-sitter
- Config: `zen-config.yaml` with language-specific pipeline overrides
- CLI: Wraps MCP tools for local `zen check file.py` usage

## Terminal UX Guidelines

- Rich and Typer should produce a consistent layout style across `zen`, `zen --help`, and subcommands.
- Pyfiglet output can be used, but combine it with Rich renderables (`Panel`, `Group`, `Table.grid`) and keep fallback text for non-interactive terminals.
- Prefer structured Rich layouts over raw string formatting for complex terminal sections.

## Examples

- Rule definition: `ZenPrinciple` in `rules/base_models.py` with severity/violations
- Analyzer extension: Subclass `BaseAnalyzer`, implement abstract methods
- Result compatibility: `violation.get('severity')` works for legacy tests
