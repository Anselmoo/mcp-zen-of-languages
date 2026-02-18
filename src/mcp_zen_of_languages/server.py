"""MCP server exposing zen-of-languages analysis tools over the Model Context Protocol.

This module is the public surface of the zen analysis server.  Every function
decorated with ``@mcp.tool`` becomes an MCP tool that IDE assistants and
automation agents can invoke.  The module-level ``CONFIG`` singleton, loaded
once from ``zen-config.yaml`` via
[`load_config`][mcp_zen_of_languages.config.load_config], governs default
thresholds, language lists, and pipeline overrides for the entire session.

Tool registration follows the FastMCP decorator pattern:

```python
@mcp.tool(name="analyze_zen_violations", tags={"analysis", "zen", "snippet"})
async def analyze_zen_violations(code: str, language: str) -> AnalysisResult:
    ...
```

The tools are grouped into four families:

* **Analysis** — snippet and repository-level violation detection.
* **Reporting** — prompt generation, agent task lists, and markdown reports.
* **Configuration** — runtime override management and introspection.
* **Onboarding** — guided setup for new projects adopting zen analysis.

Note:
    Runtime overrides set via ``set_config_override`` are stored in the
    module-level ``_runtime_overrides`` dict and persist only for the
    current server session.
"""

import logging
import os
from pathlib import Path

import fastmcp as MCP
from mcp.types import ToolAnnotations
from pydantic import BaseModel, TypeAdapter

from mcp_zen_of_languages import __version__
from mcp_zen_of_languages.analyzers.analyzer_factory import (
    create_analyzer,
    supported_languages,
)
from mcp_zen_of_languages.analyzers.base import AnalyzerConfig
from mcp_zen_of_languages.analyzers.pipeline import PipelineConfig
from mcp_zen_of_languages.config import load_config
from mcp_zen_of_languages.models import (
    AnalysisResult,
    LanguagesResult,
    PatternsResult,
    RepositoryAnalysis,
)
from mcp_zen_of_languages.orchestration import (
    analyze_targets as _shared_analyze_targets,
)
from mcp_zen_of_languages.orchestration import (
    collect_targets as _shared_collect_targets,
)
from mcp_zen_of_languages.reporting.agent_tasks import (
    AgentTaskList,
    build_agent_tasks,
)
from mcp_zen_of_languages.reporting.models import PromptBundle, ReportOutput
from mcp_zen_of_languages.reporting.prompts import build_prompt_bundle
from mcp_zen_of_languages.reporting.report import generate_report
from mcp_zen_of_languages.rules import get_all_languages, get_language_zen
from mcp_zen_of_languages.rules.base_models import LanguageZenPrinciples

mcp = MCP.FastMCP(name="zen_of_languages", version=__version__)
CONFIG = load_config(path=os.environ.get("ZEN_CONFIG_PATH"))
logger = logging.getLogger(__name__)
logger.setLevel(
    getattr(
        logging, os.environ.get("ZEN_LOG_LEVEL", "WARNING").upper(), logging.WARNING
    )
)

READONLY_ANNOTATIONS = ToolAnnotations(
    readOnlyHint=True,
    idempotentHint=True,
    destructiveHint=False,
)
MUTATING_ANNOTATIONS = ToolAnnotations(
    readOnlyHint=False,
    idempotentHint=False,
    destructiveHint=True,
)


def _output_schema(annotation: object) -> dict[str, object]:
    """Convert a return annotation into MCP-compatible JSON Schema."""

    return TypeAdapter(annotation).json_schema()


def _canonical_language(language: str) -> str:
    """Normalize aliases to canonical analyzer language keys."""
    lang = language.lower()
    alias_map = {
        "py": "python",
        "ts": "typescript",
        "tsx": "typescript",
        "js": "javascript",
        "jsx": "javascript",
        "rs": "rust",
        "sh": "bash",
        "shell": "bash",
        "ps": "powershell",
        "pwsh": "powershell",
        "rb": "ruby",
        "c++": "cpp",
        "cc": "cpp",
        "cxx": "cpp",
        "cs": "csharp",
        "yml": "yaml",
    }
    return alias_map.get(lang, lang)


def _pipeline_with_runtime_overrides(language: str) -> PipelineConfig:
    """Merge session runtime override values into the effective pipeline config."""
    pipeline_config = CONFIG.pipeline_for(language)
    runtime_override = _runtime_overrides.get(language)
    if runtime_override is None:
        return pipeline_config
    override_values = runtime_override.model_dump(
        exclude_none=True, exclude={"language", "severity_threshold"}
    )
    if not override_values:
        return pipeline_config
    runtime_defaults = AnalyzerConfig(**override_values)
    return PipelineConfig(
        language=pipeline_config.language,
        detectors=[*pipeline_config.detectors, runtime_defaults],
    )


class LanguageCoverage(BaseModel):
    """Per-language counts exposed by ``zen://languages`` resource."""

    language: str
    principles: int
    detectors: int


class LanguagesResource(BaseModel):
    """Container model for the ``zen://languages`` MCP resource."""

    languages: list[LanguageCoverage]


@mcp.resource(
    "zen://config",
    name="zen_config_resource",
    title="Zen config resource",
    description="Read-only resource exposing current configuration and active overrides.",
)
def config_resource() -> "ConfigStatus":
    """Return current configuration status as a read-only MCP resource."""

    return _build_config_status()


@mcp.resource(
    "zen://rules/{language}",
    name="zen_rules_resource",
    title="Zen rules resource",
    description="Read-only resource exposing canonical zen principles for a language.",
)
def rules_resource(language: str) -> LanguageZenPrinciples:
    """Return canonical zen principles for the requested language key."""

    zen = get_language_zen(_canonical_language(language))
    if zen is None:
        raise ValueError(f"Unsupported language '{language}'.")
    return zen


@mcp.resource(
    "zen://languages",
    name="zen_languages_resource",
    title="Zen languages resource",
    description="Read-only resource listing language principle and detector coverage counts.",
)
def languages_resource() -> LanguagesResource:
    """Return supported languages with principle and detector counts."""

    from mcp_zen_of_languages.analyzers.registry import REGISTRY

    entries: list[LanguageCoverage] = []
    for language in get_all_languages():
        detectors = [
            meta.detector_id
            for meta in REGISTRY.items()
            if meta.language in [language, "any"]
        ]
        zen = get_language_zen(language)
        entries.append(
            LanguageCoverage(
                language=language,
                principles=len(zen.principles) if zen else 0,
                detectors=len(detectors),
            )
        )
    return LanguagesResource(languages=entries)


@mcp.prompt(
    name="zen_remediation_prompt",
    title="Zen remediation prompt",
    description="Generate a remediation prompt scaffold for violations in a language.",
    tags={"prompts", "remediation"},
)
def remediation_prompt(language: str, violations: str) -> str:
    """Build a typed remediation prompt template for MCP clients."""

    return (
        "Context: Remediate zen violations in a codebase.\n"
        f"Language: {language}\n"
        "Goal: Produce precise, testable fixes aligned with zen principles.\n"
        f"Violations:\n{violations}\n"
        "Requirements:\n"
        "1. Prioritize highest severity findings first.\n"
        "2. Provide before/after guidance for each fix.\n"
        "3. Include verification steps for each remediation."
    )


@mcp.tool(
    name="detect_languages",
    title="Detect languages",
    description="Return supported language list for analysis.",
    tags={"languages", "metadata"},
    annotations=READONLY_ANNOTATIONS,
    output_schema=_output_schema(LanguagesResult),
)
async def detect_languages(repo_path: str) -> LanguagesResult:
    """Return the language identifiers listed in the active ``zen-config.yaml``.

    Unlike heuristic language-detection libraries, this tool does **not**
    scan file extensions or parse shebangs.  It simply reflects the
    ``languages`` key from the configuration that ``CONFIG`` loaded at
    server startup, giving callers a predictable, deterministic list they
    can iterate over when orchestrating multi-language analysis runs.

    Args:
        repo_path (str): Workspace root passed by the MCP client — reserved
            for future per-repo config resolution but currently unused.

    Returns:
        LanguagesResult wrapping the list of language strings declared in
        ``zen-config.yaml`` (e.g. ``["python", "typescript", "go"]``).

    Example:
        ```python
        result = await detect_languages("/home/dev/myproject")
        for lang in result.languages:
            await analyze_zen_violations(code, lang)
        ```

    See Also:
        [`get_supported_languages`][mcp_zen_of_languages.server.get_supported_languages]:
            Lists languages that have registered detectors, rather than
            configured languages.

    """

    from mcp_zen_of_languages.models import LanguagesResult

    return LanguagesResult(languages=CONFIG.languages)


@mcp.tool(
    name="analyze_zen_violations",
    title="Analyze zen violations",
    description="Analyze a code snippet against zen rules and return analysis results.",
    tags={"analysis", "zen", "snippet"},
    annotations=READONLY_ANNOTATIONS,
    output_schema=_output_schema(AnalysisResult),
)
async def analyze_zen_violations(
    code: str, language: str, severity_threshold: int | None = None
) -> AnalysisResult:
    r"""Run the full zen analysis pipeline on a single code snippet.

    This is the primary analysis entry-point.  The call progresses through
    three stages:

    1. **Language routing** — ``language`` is normalised and validated against
       all analyzers supported by ``create_analyzer``.
    2. **Analyzer creation** — ``create_analyzer`` builds a language-specific
       analyzer wired with the pipeline configuration from ``CONFIG``.
    3. **Pipeline execution** — the analyzer parses the source, computes
       metrics, runs every registered detector, and returns an
       ``AnalysisResult`` containing violations, metrics, and an overall
       quality score.

    Unsupported languages fail fast with a validation error that includes
    the list of supported language identifiers.

    Args:
        code (str): Raw source code to analyse — typically the full contents
            of a single file read by the MCP client.
        language (str): Target language identifier such as ``"python"`` or
            ``"tsx"``.  Aliases like ``"ts"`` and ``"rs"`` are accepted.
        severity_threshold (int | None): Floor severity that downstream
            consumers (reports, task generators) should honour.  Falls back
            to ``CONFIG.severity_threshold`` when omitted.

    Returns:
        AnalysisResult carrying metrics, a scored violation list, and the
        computed ``overall_score`` (0–100 scale, higher is better).

    Example:
        ```python
        result = await analyze_zen_violations(
            code="def f(x):\\n  if x:\\n    if x > 1:\\n      pass",
            language="python",
        )
        for v in result.violations:
            print(v.rule_id, v.severity, v.message)
        ```

    See Also:
        [`generate_prompts_tool`][mcp_zen_of_languages.server.generate_prompts_tool]:
            Feeds an ``AnalysisResult`` into the prompt builder for
            remediation guidance.
        [`generate_report_tool`][mcp_zen_of_languages.server.generate_report_tool]:
            Produces a full markdown report from file-level analysis.

    """
    canonical_language = _canonical_language(language)
    supported = sorted(supported_languages())
    if canonical_language not in supported:
        supported_list = ", ".join(supported)
        raise ValueError(
            f"Unsupported language '{language}'. Supported languages: {supported_list}."
        )

    runtime_override = _runtime_overrides.get(canonical_language)
    effective_threshold = severity_threshold
    if effective_threshold is None and runtime_override is not None:
        effective_threshold = runtime_override.severity_threshold
    if effective_threshold is None:
        effective_threshold = CONFIG.severity_threshold

    analyzer = create_analyzer(
        canonical_language,
        pipeline_config=_pipeline_with_runtime_overrides(canonical_language),
    )
    result = analyzer.analyze(code)
    result.violations = [
        violation
        for violation in result.violations
        if violation.severity >= effective_threshold
    ]
    return result


@mcp.tool(
    name="generate_prompts",
    title="Generate remediation prompts",
    description="Generate remediation prompts from zen analysis results.",
    tags={"prompts", "remediation"},
    annotations=READONLY_ANNOTATIONS,
    output_schema=_output_schema(PromptBundle),
)
async def generate_prompts_tool(code: str, language: str) -> PromptBundle:
    """Analyse code and synthesise remediation prompts for each detected violation.

    Prompt generation is a two-phase process: the code is first analysed
    exactly as ``analyze_zen_violations`` would, and the resulting
    ``AnalysisResult`` is then fed into ``build_prompt_bundle`` which
    produces both **file-specific** prompts (anchored to a particular
    violation) and **generic** prompts (language-wide best-practice nudges).

    MCP clients typically call this tool right after reviewing an
    ``AnalysisResult`` to obtain copy-pasteable refactoring instructions
    they can present to the developer or inject into an agent workflow.

    Args:
        code (str): Source code whose violations will drive prompt
            generation — should match the snippet passed to analysis.
        language (str): Language identifier used to select the correct
            analyzer and prompt templates (e.g. ``"python"``).

    Returns:
        PromptBundle holding ``file_prompts`` with per-violation
        remediation text and ``generic_prompts`` for broader guidance.

    See Also:
        [`analyze_zen_violations`][mcp_zen_of_languages.server.analyze_zen_violations]:
            Produces the raw violations that drive prompt content.
        [`generate_report_tool`][mcp_zen_of_languages.server.generate_report_tool]:
            Embeds prompts alongside gap analysis in a full report.

    """

    canonical_language = _canonical_language(language)
    supported = sorted(supported_languages())
    if canonical_language not in supported:
        supported_list = ", ".join(supported)
        raise ValueError(
            f"Unsupported language '{language}'. Supported languages: {supported_list}."
        )
    analyzer = create_analyzer(
        canonical_language,
        pipeline_config=_pipeline_with_runtime_overrides(canonical_language),
    )
    result = analyzer.analyze(code)
    return build_prompt_bundle([result])


async def _analyze_repository_internal(
    repo_path: str,
    languages: list[str] | None = None,
    max_files: int = 100,
    ctx: MCP.Context | None = None,
) -> list[RepositoryAnalysis]:
    """Orchestrate multi-file analysis across a repository tree.

    This internal helper handles the heavy lifting behind
    ``analyze_repository`` and ``generate_agent_tasks_tool``.  It walks
    the directory tree rooted at *repo_path*, groups files by detected
    language, then analyses each file with its language-specific analyzer.

    A two-pass strategy is used for every target language:

    1. **Import harvesting** — a lightweight scan collects top-level import
       names from every file, building a ``repository_imports`` mapping that
       gives each analyzer cross-file dependency context.
    2. **Full analysis** — each file is analysed individually with the
       harvested import context attached, so detectors like
       *circular-dependency* can reason about project-wide coupling.

    Args:
        repo_path (str): Absolute or relative path to the repository root
            whose source files will be discovered recursively.
        languages (list[str] | None): Restrict analysis to these languages.
            Defaults to ``["python"]`` when omitted.
        max_files (int): Cap on files analysed per language, preventing
            runaway analysis on very large repositories.
        ctx (MCP.Context | None): Optional FastMCP context used for
            progress updates and per-file log messages.

    Returns:
        list[RepositoryAnalysis]: One entry per analysed file, each
        carrying the file path, detected language, and its
        ``AnalysisResult``.
    """

    repo = Path(repo_path)
    if languages:
        targets: list[tuple[Path, str]] = []
        for language in languages:
            canonical_language = _canonical_language(language)
            targets.extend(_shared_collect_targets(repo, canonical_language))
    else:
        targets = _shared_collect_targets(repo, None)

    deduped_targets: list[tuple[Path, str]] = []
    seen: set[tuple[str, str]] = set()
    for path, language in targets:
        key = (str(path), language)
        if key in seen:
            continue
        seen.add(key)
        deduped_targets.append((path, language))

    counts: dict[str, int] = {}
    limited_targets: list[tuple[Path, str]] = []
    for path, language in deduped_targets:
        current = counts.get(language, 0)
        if current >= max_files:
            continue
        counts[language] = current + 1
        limited_targets.append((path, language))

    total_targets = len(limited_targets)
    ordered_paths: list[Path] = []
    if ctx is not None and total_targets:
        ctx.report_progress(0, total_targets)
        grouped_targets: dict[str, list[Path]] = {}
        for path, language in limited_targets:
            grouped_targets.setdefault(language, []).append(path)
        for files in grouped_targets.values():
            ordered_paths.extend(files)
    progress_count = 0

    def _progress_callback() -> None:
        nonlocal progress_count
        if ctx is None or total_targets == 0:
            return
        progress_count += 1
        if progress_count <= len(ordered_paths):
            ctx.log(f"Analyzing {ordered_paths[progress_count - 1]}")
        ctx.report_progress(progress_count, total_targets)

    analysis_results = _shared_analyze_targets(
        limited_targets,
        pipeline_resolver=_pipeline_with_runtime_overrides,
        unsupported_language="placeholder",
        include_read_errors=True,
        progress_callback=_progress_callback if total_targets > 0 else None,
    )
    return [
        RepositoryAnalysis(
            path=result.path or "",
            language=result.language,
            result=result,
        )
        for result in analysis_results
    ]


@mcp.tool(
    name="analyze_repository",
    title="Analyze repository",
    description="Analyze a repository path and return per-file analysis results.",
    tags={"analysis", "repository"},
    annotations=READONLY_ANNOTATIONS,
)
async def analyze_repository(
    repo_path: str,
    languages: list[str] | None = None,
    max_files: int = 100,
    ctx: MCP.Context | None = None,
) -> list[RepositoryAnalysis]:
    """Analyse every eligible file in a repository and return per-file results.

    This is the public MCP tool that wraps
    ``_analyze_repository_internal``.  It exists as a thin async façade so
    that the internal helper can also be called from non-tool code paths
    (such as ``generate_agent_tasks_tool``) without duplicating parameter
    validation or the ``@mcp.tool`` decorator.

    Args:
        repo_path (str): Absolute path to the repository root.  The MCP
            client typically resolves this from the active workspace.
        languages (list[str] | None): Restrict analysis to specific
            language identifiers.  Defaults to ``["python"]`` internally.
        max_files (int): Per-language cap on the number of files to
            analyse, protecting against excessive runtime on monorepos.
        ctx (MCP.Context | None): Optional FastMCP context for progress
            and log updates during repository analysis.

    Returns:
        List of ``RepositoryAnalysis`` entries, each pairing a file path
        and language with its ``AnalysisResult``.

    Example:
        ```python
        entries = await analyze_repository(
            "/home/dev/myproject", languages=["python", "go"], max_files=50
        )
        for entry in entries:
            print(entry.path, entry.result.overall_score)
        ```

    See Also:
        [`generate_agent_tasks_tool`][mcp_zen_of_languages.server.generate_agent_tasks_tool]:
            Builds actionable remediation tasks from repository analysis.

    """

    return await _analyze_repository_internal(repo_path, languages, max_files, ctx)


@mcp.tool(
    name="generate_agent_tasks",
    title="Generate agent tasks",
    description=(
        "Convert zen violations into structured agent task lists for automated "
        "remediation."
    ),
    tags={"agent", "tasks", "automation"},
    annotations=READONLY_ANNOTATIONS,
    output_schema=_output_schema(AgentTaskList),
)
async def generate_agent_tasks_tool(
    repo_path: str,
    languages: list[str] | None = None,
    min_severity: int = 5,
) -> AgentTaskList:
    """Convert repository-level violations into prioritised remediation tasks.

    Agent workflows need structured, machine-readable work items — not
    prose reports.  This tool analyses the repository via
    ``_analyze_repository_internal``, extracts every violation whose
    severity meets *min_severity*, and transforms them into an
    ``AgentTaskList`` ordered by priority.  Each task carries the file
    path, rule identifier, and a concise action description an automated
    agent can execute without further context.

    Args:
        repo_path (str): Absolute path to the repository to scan.  All
            eligible source files are discovered recursively.
        languages (list[str] | None): Restrict scanning to these
            languages.  Omit to analyse only Python files by default.
        min_severity (int): Severity floor (1–10 scale).  Violations
            below this threshold are excluded from the task list.

    Returns:
        AgentTaskList containing prioritised tasks ready for automated
        remediation, sorted from highest to lowest severity.

    See Also:
        [`analyze_repository`][mcp_zen_of_languages.server.analyze_repository]:
            Retrieves the raw per-file results that feed task generation.
        [`generate_prompts_tool`][mcp_zen_of_languages.server.generate_prompts_tool]:
            Provides human-readable remediation text rather than
            structured tasks.

    """

    repo_results = await _analyze_repository_internal(repo_path, languages=languages)
    analysis_results = [entry.result for entry in repo_results]
    return build_agent_tasks(
        analysis_results, project=repo_path, min_severity=min_severity
    )


@mcp.tool(
    name="check_architectural_patterns",
    title="Check architectural patterns",
    description="Return detected architectural patterns for a code snippet.",
    tags={"analysis", "patterns"},
    annotations=READONLY_ANNOTATIONS,
    output_schema=_output_schema(PatternsResult),
)
async def check_architectural_patterns(code: str, language: str) -> PatternsResult:
    """Scan a code snippet for recognised architectural patterns.

    Architectural pattern detection is not implemented yet.

    Args:
        code (str): Source fragment to inspect for structural patterns.
        language (str): Language identifier guiding which pattern
            recognisers to apply (e.g. ``"python"``, ``"go"``).

    Raises:
        NotImplementedError: Always raised until pattern detection support
            is implemented.

    """

    raise NotImplementedError(
        "check_architectural_patterns is not implemented yet. "
        "Pattern detection is planned but not available in this release."
    )


@mcp.tool(
    name="generate_report",
    title="Generate report",
    description="Generate a markdown/json report with gap analysis and prompts.",
    tags={"reporting", "analysis"},
    annotations=READONLY_ANNOTATIONS,
    output_schema=_output_schema(ReportOutput),
)
async def generate_report_tool(
    target_path: str,
    language: str | None = None,
    include_prompts: bool = False,
    include_analysis: bool = True,
    include_gaps: bool = True,
    ctx: MCP.Context | None = None,
) -> ReportOutput:
    """Produce a structured markdown report combining analysis, gaps, and prompts.

    Reports are the highest-level output the server offers.  They stitch
    together violation analysis, coverage-gap summaries, and optional
    remediation prompts into a single ``ReportOutput`` whose ``markdown``
    field is ready for rendering and whose ``data`` field carries the
    machine-readable payload.

    Callers control which sections appear through the three boolean flags,
    making it easy to request a lightweight analysis-only snapshot or a
    full diagnostic document.

    Args:
        target_path (str): Path to a single file or a directory.  When a
            directory is given, all eligible files inside are analysed.
        language (str | None): Explicit language override.  When omitted,
            the language is inferred from file extensions.
        include_prompts (bool): Append remediation prompt sections derived
            from ``build_prompt_bundle``.
        include_analysis (bool): Include the violation-analysis body
            showing per-rule findings.
        include_gaps (bool): Include quality-gap and coverage-gap
            summaries highlighting areas that need attention.
        ctx (MCP.Context | None): Optional FastMCP context used to emit
            progress and log updates for analyzed targets.

    Returns:
        ReportOutput with ``markdown`` (rendered report text) and ``data``
        (structured dict) ready for MCP client consumption.

    See Also:
        [`analyze_zen_violations`][mcp_zen_of_languages.server.analyze_zen_violations]:
            Underlying snippet analysis powering the report body.
        [`generate_prompts_tool`][mcp_zen_of_languages.server.generate_prompts_tool]:
            Standalone prompt generation when a full report is not needed.

    """

    if ctx is not None:
        ctx.log(f"Generating zen-of-languages report for {target_path}")
        ctx.report_progress(0, 1)

    report = generate_report(
        target_path,
        language=language,
        include_prompts=include_prompts,
        include_analysis=include_analysis,
        include_gaps=include_gaps,
    )
    if ctx is not None:
        ctx.report_progress(1, 1)
    return ReportOutput(markdown=report.markdown, data=report.data)


@mcp.tool(
    name="export_rule_detector_mapping",
    title="Export rule detector mapping",
    description="Generate rule-detector mapping JSON from the live registry.",
    tags={"metadata", "mapping"},
    annotations=READONLY_ANNOTATIONS,
    output_schema=_output_schema(dict[str, object]),
)
async def export_rule_detector_mapping(
    languages: list[str] | None = None,
) -> dict:
    """Export the live rule-to-detector wiring from the detector registry.

    The registry maps each zen rule (e.g. ``PY-R001``) to the detector
    class responsible for finding its violations.  Exporting this mapping
    is useful for introspection dashboards, CI tooling that needs to know
    which rules are actively enforced, and documentation generators that
    want to list coverage per language.

    Args:
        languages (list[str] | None): Restrict the export to these
            language identifiers.  When omitted, mappings for every
            registered language are returned.

    Returns:
        Nested dictionary keyed by language, then by rule ID, with
        detector metadata (class name, config schema) as values.

    See Also:
        [`get_supported_languages`][mcp_zen_of_languages.server.get_supported_languages]:
            Returns the same language keys but paired with detector IDs
            rather than full mapping metadata.

    """

    from mcp_zen_of_languages.rules.mapping_export import build_rule_detector_mapping

    return build_rule_detector_mapping(languages)


# ============================================================================
# Configuration Management Tools
# ============================================================================


class ConfigOverride(BaseModel):
    """Session-scoped override for a single language's analysis thresholds.

    When an MCP client calls ``set_config_override``, the supplied values
    are captured in a ``ConfigOverride`` instance and stored in the
    module-level ``_runtime_overrides`` dict, keyed by language.  Only
    non-``None`` fields are considered active — omitted fields leave the
    corresponding ``zen-config.yaml`` default in effect.

    Note:
        Overrides do **not** persist across server restarts.  Call
        ``clear_config_overrides`` to reset mid-session.
    """

    language: str
    max_cyclomatic_complexity: int | None = None
    max_nesting_depth: int | None = None
    max_function_length: int | None = None
    max_class_length: int | None = None
    max_line_length: int | None = None
    severity_threshold: int | None = None


class ConfigStatus(BaseModel):
    """Read-only snapshot of the server's current configuration state.

    Returned by ``get_config``, ``set_config_override``, and
    ``clear_config_overrides`` so callers can confirm the effective
    settings after every mutation.  The ``overrides_applied`` field
    shows only the non-default values injected during the current session.
    """

    languages: list[str]
    severity_threshold: int
    config_path: str | None
    overrides_applied: dict[str, dict[str, int | bool]]


# Runtime config overrides storage
_runtime_overrides: dict[str, ConfigOverride] = {}


def _build_config_status() -> ConfigStatus:
    """Assemble a ``ConfigStatus`` snapshot from ``CONFIG`` and active overrides.

    Reads the module-level ``_runtime_overrides`` dict, serialises each
    ``ConfigOverride`` with ``exclude_none=True`` so only explicitly set
    fields appear, and combines them with the base ``CONFIG`` values.

    Returns:
        ConfigStatus reflecting the merged view of static configuration
        and any session-scoped overrides currently in effect.
    """
    import os

    overrides_dict = {
        lang: override.model_dump(exclude_none=True, exclude={"language"})
        for lang, override in _runtime_overrides.items()
    }
    return ConfigStatus(
        languages=CONFIG.languages,
        severity_threshold=CONFIG.severity_threshold,
        config_path=os.environ.get("ZEN_CONFIG_PATH"),
        overrides_applied=overrides_dict,
    )


@mcp.tool(
    name="get_config",
    title="Get current configuration",
    description="Return the current server configuration including any runtime overrides.",
    tags={"config", "metadata"},
    annotations=READONLY_ANNOTATIONS,
    output_schema=_output_schema(ConfigStatus),
)
async def get_config() -> ConfigStatus:
    """Return a snapshot of the running server's configuration.

    Combines the static values loaded from ``zen-config.yaml`` with any
    session-scoped overrides applied via ``set_config_override``.  Useful
    for MCP clients that need to display current thresholds or verify
    that an override took effect before launching an analysis run.

    Returns:
        ConfigStatus describing active languages, severity threshold,
        resolved config file path, and a per-language map of overrides.

    See Also:
        [`set_config_override`][mcp_zen_of_languages.server.set_config_override]:
            Mutates the runtime overrides reflected in this snapshot.
        [`clear_config_overrides`][mcp_zen_of_languages.server.clear_config_overrides]:
            Resets all overrides so the snapshot matches ``zen-config.yaml``.

    """
    return _build_config_status()


@mcp.tool(
    name="set_config_override",
    title="Set configuration override",
    description="Override configuration values for a specific language at runtime. Overrides persist for the session.",
    tags={"config", "settings"},
    annotations=MUTATING_ANNOTATIONS,
    output_schema=_output_schema(ConfigStatus),
)
async def set_config_override(
    language: str,
    max_cyclomatic_complexity: int | None = None,
    max_nesting_depth: int | None = None,
    max_function_length: int | None = None,
    max_class_length: int | None = None,
    max_line_length: int | None = None,
    severity_threshold: int | None = None,
) -> ConfigStatus:
    """Apply session-scoped threshold overrides for a specific language.

    Overrides are stored in memory and survive until the server process
    exits or ``clear_config_overrides`` is called.  Only the fields
    explicitly set are overridden — omitted fields retain their
    ``zen-config.yaml`` defaults.  Calling this tool a second time for
    the same language **replaces** the previous override entirely.

    Args:
        language (str): Language whose thresholds should be adjusted
            (e.g. ``"python"``).
        max_cyclomatic_complexity (int | None): Override the per-function
            cyclomatic-complexity ceiling.
        max_nesting_depth (int | None): Override the maximum allowed
            nesting depth for control-flow blocks.
        max_function_length (int | None): Override the maximum lines
            permitted in a single function body.
        max_class_length (int | None): Override the maximum lines
            permitted in a single class definition.
        max_line_length (int | None): Override the maximum character
            width for a single source line.
        severity_threshold (int | None): Override the minimum severity
            at which violations are surfaced in results.

    Returns:
        ConfigStatus reflecting all overrides after this mutation,
        confirming the change took effect.

    See Also:
        [`get_config`][mcp_zen_of_languages.server.get_config]:
            Inspect the full configuration without mutating it.

    """
    language = _canonical_language(language)
    override = ConfigOverride(
        language=language,
        max_cyclomatic_complexity=max_cyclomatic_complexity,
        max_nesting_depth=max_nesting_depth,
        max_function_length=max_function_length,
        max_class_length=max_class_length,
        max_line_length=max_line_length,
        severity_threshold=severity_threshold,
    )
    _runtime_overrides[language] = override
    return _build_config_status()


@mcp.tool(
    name="clear_config_overrides",
    title="Clear configuration overrides",
    description="Clear all runtime configuration overrides, reverting to zen-config.yaml defaults.",
    tags={"config", "settings"},
    annotations=MUTATING_ANNOTATIONS,
    output_schema=_output_schema(ConfigStatus),
)
async def clear_config_overrides() -> ConfigStatus:
    """Remove every session-scoped override, reverting to ``zen-config.yaml`` defaults.

    After this call, ``get_config().overrides_applied`` will be empty
    and all subsequent analyses will use the thresholds defined in the
    static configuration file.

    Returns:
        ConfigStatus after all override entries have been cleared.

    """
    _runtime_overrides.clear()
    return _build_config_status()


# ============================================================================
# Onboarding Tools
# ============================================================================


class OnboardingStep(BaseModel):
    """A single instruction in the guided onboarding sequence.

    Each step pairs a human-readable title and description with an
    ``action`` key that MCP clients can use to trigger the corresponding
    operation programmatically, and an optional ``example`` showing
    concrete invocation syntax.
    """

    step: int
    title: str
    description: str
    action: str
    example: str | None = None


class OnboardingGuide(BaseModel):
    """Complete onboarding payload returned by ``onboard_project``.

    Bundles an ordered list of ``OnboardingStep`` entries with a
    ``recommended_config`` dict that reflects the thresholds appropriate
    for the caller's chosen strictness profile.  MCP clients can render
    the steps as an interactive wizard or apply ``recommended_config``
    directly to ``zen-config.yaml``.
    """

    project_name: str
    steps: list[OnboardingStep]
    recommended_config: dict[str, int | str | bool]


@mcp.tool(
    name="onboard_project",
    title="Onboard a new project",
    description="Get interactive onboarding guidance for setting up zen analysis on a project. Returns recommended configuration based on project characteristics.",
    tags={"onboarding", "setup"},
    annotations=READONLY_ANNOTATIONS,
    output_schema=_output_schema(OnboardingGuide),
)
async def onboard_project(
    project_path: str,
    primary_language: str = "python",
    team_size: str = "small",
    strictness: str = "moderate",
) -> OnboardingGuide:
    """Generate a step-by-step onboarding guide tailored to a project's profile.

    The guide walks a new user through five stages — configuration file
    creation, IDE integration, baseline analysis, threshold tuning, and
    CI/CD wiring — with concrete examples customised for the selected
    *primary_language* and *strictness* level.

    Three strictness presets are available:

    * **relaxed** — generous thresholds suited to legacy codebases.
    * **moderate** — balanced defaults for active development.
    * **strict** — tight limits for greenfield or high-quality projects.

    Args:
        project_path (str): Absolute path to the project root, used to
            derive the project name and populate example commands.
        primary_language (str): Language used for example snippets and
            default pipeline selection (e.g. ``"python"``).
        team_size (str): Descriptive team-size hint (``"small"``,
            ``"medium"``, ``"large"``), reserved for future adaptive
            threshold scaling.
        strictness (str): Preset name controlling all numeric thresholds
            (``"relaxed"``, ``"moderate"``, or ``"strict"``).

    Returns:
        OnboardingGuide with ordered steps, each carrying an action key
        and example, plus a ``recommended_config`` dict ready to write
        into ``zen-config.yaml``.

    Example:
        ```python
        guide = await onboard_project(
            "/home/dev/webapp", primary_language="typescript", strictness="strict"
        )
        for step in guide.steps:
            print(f"Step {step.step}: {step.title}")
        ```

    See Also:
        [`set_config_override`][mcp_zen_of_languages.server.set_config_override]:
            Apply recommended thresholds at runtime without editing
            ``zen-config.yaml``.

    """
    # Determine thresholds based on strictness
    thresholds = {
        "relaxed": {
            "complexity": 15,
            "nesting": 5,
            "function_length": 100,
            "line_length": 120,
        },
        "moderate": {
            "complexity": 10,
            "nesting": 3,
            "function_length": 50,
            "line_length": 88,
        },
        "strict": {
            "complexity": 7,
            "nesting": 2,
            "function_length": 30,
            "line_length": 79,
        },
    }
    t = thresholds.get(strictness, thresholds["moderate"])

    steps = [
        OnboardingStep(
            step=1,
            title="Configure zen-config.yaml",
            description=f"Create or update zen-config.yaml in your project root with {strictness} settings.",
            action="create_config",
            example=f"max_cyclomatic_complexity: {t['complexity']}",
        ),
        OnboardingStep(
            step=2,
            title="Set up VS Code integration",
            description="Add the MCP server configuration to .vscode/mcp.json for VS Code integration.",
            action="setup_vscode",
            example='{"mcp": {"servers": {"zen-of-languages": {"command": "uv", "args": ["run", "zen-mcp-server"]}}}}',
        ),
        OnboardingStep(
            step=3,
            title="Run initial analysis",
            description="Analyze your codebase to establish a baseline of zen violations.",
            action="analyze",
            example=f"analyze_repository('{project_path}', languages=['{primary_language}'])",
        ),
        OnboardingStep(
            step=4,
            title="Review and adjust thresholds",
            description="Based on initial results, adjust thresholds using set_config_override if needed.",
            action="tune_config",
            example=f"set_config_override('{primary_language}', max_cyclomatic_complexity={t['complexity']})",
        ),
        OnboardingStep(
            step=5,
            title="Integrate with CI/CD",
            description="Add zen analysis to your CI pipeline for continuous code quality monitoring.",
            action="ci_integration",
            example="mcp-zen-of-languages check src/ --severity-threshold 7",
        ),
    ]

    return OnboardingGuide(
        project_name=project_path.rsplit("/", maxsplit=1)[-1],
        steps=steps,
        recommended_config={
            "language": primary_language,
            "max_cyclomatic_complexity": t["complexity"],
            "max_nesting_depth": t["nesting"],
            "max_function_length": t["function_length"],
            "max_line_length": t["line_length"],
            "severity_threshold": 5
            if strictness == "relaxed"
            else 6
            if strictness == "moderate"
            else 7,
        },
    )


@mcp.tool(
    name="get_supported_languages",
    title="Get supported languages",
    description="Return list of all languages with zen rules and their detector coverage.",
    tags={"metadata", "languages"},
    annotations=READONLY_ANNOTATIONS,
    output_schema=_output_schema(dict[str, list[str]]),
)
async def get_supported_languages() -> dict[str, list[str]]:
    """List every language that has zen rules alongside its registered detector IDs.

    This tool queries two registries at once: ``ZEN_REGISTRY`` (which
    holds the canonical zen principles per language) and the detector
    ``REGISTRY`` (which maps rule IDs to detector implementations).
    The result tells callers not just *which* languages are known, but
    *how much* detector coverage each language currently has.

    Returns:
        Dictionary mapping each language identifier (e.g. ``"python"``)
        to the list of detector IDs wired up for that language.

    See Also:
        [`detect_languages`][mcp_zen_of_languages.server.detect_languages]:
            Returns the *configured* language list from ``zen-config.yaml``
            rather than the full set of languages with rules.
        [`export_rule_detector_mapping`][mcp_zen_of_languages.server.export_rule_detector_mapping]:
            Provides deeper mapping metadata including config schemas.

    """
    from mcp_zen_of_languages.analyzers.registry import REGISTRY
    from mcp_zen_of_languages.rules import ZEN_REGISTRY

    result = {}
    for lang in ZEN_REGISTRY.keys():
        detectors = [
            meta.detector_id
            for meta in REGISTRY.items()
            if meta.language in [lang, "any"]
        ]
        result[lang] = detectors
    return result
