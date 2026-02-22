# MCP Zen of Languages - AI Agent Instructions

> Use regularly `Serena` in the MCP Zen of Languages repository for code analysis, following the architecture and patterns established in the codebase. `Serena` allows saving tokens by writing, fetching, deleting, and reading memories which should be synchronized with plans.
Always ensure that any code changes pass the pre-commit checks before claiming completion.

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
- Pre-commit (all, mandatory before completion): `uvx pre-commit run --all-files`
- Pre-push docs gate: `uvx pre-commit run --hook-stage pre-push --all-files`

## Completion Gate (Required)

- Do not claim work is complete until `uvx pre-commit run --all-files` passes.
- If pre-commit fails, fix issues and re-run until all hooks pass.
- In final responses, explicitly confirm pre-commit status.

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
6. Implement `_build_dependency_analysis()` with regex-based import extraction (see below)
7. Override `capabilities()` to declare `supports_ast` / `supports_dependency_analysis`

## Dependency Analysis Pattern

Every language analyzer should extract imports/includes/requires via regex and feed them into `build_import_graph()`:

```python
import re
from mcp_zen_of_languages.analyzers.base import AnalysisContext, AnalyzerCapabilities

_IMPORT_RE = re.compile(r"^import\s+(.+)")  # language-specific regex

class MyAnalyzer(BaseAnalyzer):
    def capabilities(self) -> AnalyzerCapabilities:
        return AnalyzerCapabilities(supports_dependency_analysis=True)

    def _build_dependency_analysis(self, context: AnalysisContext) -> object | None:
        imports = []
        for line in context.code.splitlines():
            m = _IMPORT_RE.match(line.strip())
            if m:
                imports.append(m.group(1))
        if not imports:
            return None
        from mcp_zen_of_languages.metrics.dependency_graph import build_import_graph
        return build_import_graph({(context.path or "<current>"): imports})
```

Key conventions:
- Module-level compiled regex constants (e.g. `_IMPORT_RE`)
- Rename `_context` → `context` when activating the method
- Skip comment lines before matching
- Return `None` (not empty `DependencyAnalysis`) when no imports found

## Subprocess Integration

`utils/subprocess_runner.py` provides `SubprocessToolRunner` for external tool integration:

```python
from mcp_zen_of_languages.utils.subprocess_runner import SubprocessToolRunner

runner = SubprocessToolRunner()
if runner.is_available("shellcheck"):
    result = runner.run("shellcheck", ["-"], code=script_code)
```

- Security: allowlist of known tools (`KNOWN_TOOLS` mapping), no `shell=True`
- Supported tools are language-scoped and extensible (for example `ruff`, `eslint`, `biome`, `prettier`, `hadolint`, `chktex`, `markdownlint`)
- Individual analyzers opt-in; this is infrastructure only
- **No hard installs**: analysis paths must never auto-install missing runtimes/linters
- Missing-tool behavior: return clear info + recommendation (e.g., install command), then continue best-effort analysis
- Consent-first UX: CLI/MCP should keep external tools disabled by default and advertise opt-in quality enhancement
- Temporary runner mode (`npx`/`uvx`) must be a separate explicit opt-in, never enabled implicitly

## Agent & Prompt Strategy

Existing `generate_agent_tasks` and `generate_prompts` MCP tools consume `AnalysisResult` objects. When analyzers produce richer results (real AST, dependency graphs, more violations), those automatically flow into agent tasks and remediation prompts—no new agent infrastructure is needed.

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
