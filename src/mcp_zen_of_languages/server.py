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
async def analyze_zen_violations(code: str, language: str) -> AnalysisResult: ...
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

import base64
import json
import logging
import os

from datetime import timedelta
from pathlib import Path
from typing import Any
from typing import cast

import fastmcp

from fastmcp.server.tasks import TaskConfig
from mcp.types import Icon
from mcp.types import ToolAnnotations
from pydantic import BaseModel
from pydantic import TypeAdapter

from mcp_zen_of_languages import __version__
from mcp_zen_of_languages.analyzers.analyzer_factory import create_analyzer
from mcp_zen_of_languages.analyzers.analyzer_factory import supported_languages
from mcp_zen_of_languages.analyzers.base import AnalyzerConfig
from mcp_zen_of_languages.analyzers.pipeline import PipelineConfig
from mcp_zen_of_languages.config import load_config
from mcp_zen_of_languages.lifespan import zen_server_lifespan
from mcp_zen_of_languages.middleware import build_default_middleware
from mcp_zen_of_languages.models import AnalysisResult
from mcp_zen_of_languages.models import BatchHotspot
from mcp_zen_of_languages.models import BatchPage
from mcp_zen_of_languages.models import BatchSummary
from mcp_zen_of_languages.models import BatchViolation
from mcp_zen_of_languages.models import LanguagesResult
from mcp_zen_of_languages.models import PatternsResult
from mcp_zen_of_languages.models import RepositoryAnalysis
from mcp_zen_of_languages.orchestration import (
    analyze_targets as _shared_analyze_targets,
)
from mcp_zen_of_languages.orchestration import (
    collect_targets as _shared_collect_targets,
)
from mcp_zen_of_languages.reporting.agent_tasks import AgentTaskList
from mcp_zen_of_languages.reporting.agent_tasks import build_agent_tasks
from mcp_zen_of_languages.reporting.models import PromptBundle
from mcp_zen_of_languages.reporting.models import ReportOutput
from mcp_zen_of_languages.reporting.prompts import build_prompt_bundle
from mcp_zen_of_languages.reporting.report import generate_report
from mcp_zen_of_languages.rules import get_all_languages
from mcp_zen_of_languages.rules import get_language_zen
from mcp_zen_of_languages.rules.base_models import LanguageZenPrinciples
from mcp_zen_of_languages.storage import create_cache_backend
from mcp_zen_of_languages.telemetry import analysis_span


SERVER_ICONS = [
    Icon(
        src="https://anselmoo.github.io/mcp-zen-of-languages/assets/icons/zen-icon.svg",
        mimeType="image/svg+xml",
    ),
]
ANALYSIS_TOOL_ICONS = [
    Icon(
        src="https://anselmoo.github.io/mcp-zen-of-languages/assets/icons/tool-analysis.svg",
        mimeType="image/svg+xml",
    ),
]
PROMPT_TOOL_ICONS = [
    Icon(
        src="https://anselmoo.github.io/mcp-zen-of-languages/assets/icons/tool-prompts.svg",
        mimeType="image/svg+xml",
    ),
]
ONBOARDING_TOOL_ICONS = [
    Icon(
        src="https://anselmoo.github.io/mcp-zen-of-languages/assets/icons/tool-onboarding.svg",
        mimeType="image/svg+xml",
    ),
]
RESOURCE_ICONS = [
    Icon(
        src="https://anselmoo.github.io/mcp-zen-of-languages/assets/icons/resource.svg",
        mimeType="image/svg+xml",
    ),
]
PROMPT_RESOURCE_ICONS = [
    Icon(
        src="https://anselmoo.github.io/mcp-zen-of-languages/assets/icons/prompt.svg",
        mimeType="image/svg+xml",
    ),
]
_CACHE_BACKEND = create_cache_backend()

mcp = fastmcp.FastMCP(
    name="zen_of_languages",
    version=__version__,
    instructions=(
        "Multi-language architectural and idiomatic code analysis via MCP and CLI. "
        "In MCP-capable clients, prefer MCP tool invocations over shelling out to CLI commands."
    ),
    website_url="https://anselmoo.github.io/mcp-zen-of-languages/",
    icons=SERVER_ICONS,
    middleware=build_default_middleware(cache_backend=_CACHE_BACKEND),
    lifespan=zen_server_lifespan,
    list_page_size=100,
)
mcp.zen_cache_backend = _CACHE_BACKEND

CONFIG = load_config(path=os.environ.get("ZEN_CONFIG_PATH"))
logger = logging.getLogger(__name__)
logger.setLevel(
    getattr(
        logging,
        os.environ.get("ZEN_LOG_LEVEL", "WARNING").upper(),
        logging.WARNING,
    ),
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
BACKGROUND_TASK = TaskConfig(mode="optional", poll_interval=timedelta(seconds=5))
ANALYZE_ZEN_VIOLATIONS_VERSION = "1.0"
GENERATE_PROMPTS_VERSION = "1.0"
ANALYZE_ZEN_VIOLATIONS_V2_VERSION = "2.0"
GENERATE_PROMPTS_V2_VERSION = "2.0"
# Conservative token overhead reserved for the BatchPage envelope fields
# (cursor, page, has_more, files_processed, files_total, JSON structure).
_BATCH_ENVELOPE_TOKEN_OVERHEAD = 200


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
        "scss": "css",
        "less": "css",
        "yml": "yaml",
        "md": "markdown",
        "mdx": "markdown",
        "github_actions": "github-actions",
        "gha": "github-actions",
        "docker-compose": "docker_compose",
        "ansible-playbook": "ansible",
        "gitlab-ci": "gitlab_ci",
        "gitlabci": "gitlab_ci",
        "tex": "latex",
        "ltx": "latex",
        "sty": "latex",
        "bib": "latex",
        "bibtex": "latex",
        "tf": "terraform",
    }
    return alias_map.get(lang, lang)


def _pipeline_with_runtime_overrides(language: str) -> PipelineConfig:
    """Merge session runtime override values into the effective pipeline config."""
    pipeline_config = CONFIG.pipeline_for(language)
    runtime_override = _runtime_overrides.get(language)
    if runtime_override is None:
        return pipeline_config
    override_values = runtime_override.model_dump(
        exclude_none=True,
        exclude={"language", "severity_threshold"},
    )
    if not override_values:
        return pipeline_config
    runtime_defaults = AnalyzerConfig(**override_values)
    return PipelineConfig(
        language=pipeline_config.language,
        detectors=[*pipeline_config.detectors, runtime_defaults],
    )


def _encode_cursor(file_idx: int, offset: int = 0) -> str:
    """Encode a batch-page cursor as a base-64 JSON string.

    The cursor is a stateless continuation token that records the next
    file index and intra-file violation offset to resume from.  Encoding
    as base-64 JSON keeps the token opaque to callers while remaining
    easy to inspect during debugging.

    Args:
        file_idx: 0-based index of the next file to process.
        offset: 0-based index of the first violation within that file.

    Returns:
        str: Base-64-encoded JSON string, e.g. ``"eyJmaWxlIjogMSwgIm9mZnNldCI6IDB9"``.
    """
    payload = json.dumps({"file": file_idx, "offset": offset})
    return base64.b64encode(payload.encode()).decode()


def _decode_cursor(cursor: str) -> tuple[int, int]:
    """Decode a batch-page cursor back into (file_idx, offset).

    Args:
        cursor: Base-64-encoded JSON cursor previously produced by
            ``_encode_cursor``.

    Returns:
        tuple[int, int]: ``(file_idx, offset)`` pair.

    Raises:
        ValueError: When *cursor* is not valid base-64 JSON.
    """
    try:
        data = json.loads(base64.b64decode(cursor).decode())
        return int(data["file"]), int(data.get("offset", 0))
    except Exception as exc:
        msg = f"Invalid batch cursor: {exc}"
        raise ValueError(msg) from exc


def _estimate_tokens(text: str) -> int:
    """Rough token count estimate for a serialised string.

    Uses a conservative 4-characters-per-token heuristic that errs on
    the side of under-counting to stay safely within LLM context budgets.

    Args:
        text: Any string whose token count should be estimated.

    Returns:
        int: Estimated number of tokens.
    """
    return max(1, len(text) // 4)


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
    icons=RESOURCE_ICONS,
)
def config_resource() -> "ConfigStatus":
    """Return current configuration status as a read-only MCP resource."""
    return _build_config_status()


@mcp.resource(
    "zen://rules/{language}",
    name="zen_rules_resource",
    title="Zen rules resource",
    description="Read-only resource exposing canonical zen principles for a language.",
    icons=RESOURCE_ICONS,
)
def rules_resource(language: str) -> LanguageZenPrinciples:
    """Return canonical zen principles for the requested language key."""
    zen = get_language_zen(_canonical_language(language))
    if zen is None:
        msg = f"Unsupported language '{language}'."
        raise ValueError(msg)
    return zen


@mcp.resource(
    "zen://languages",
    name="zen_languages_resource",
    title="Zen languages resource",
    description="Read-only resource listing language principle and detector coverage counts.",
    icons=RESOURCE_ICONS,
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
            ),
        )
    return LanguagesResource(languages=entries)


@mcp.prompt(
    name="zen_remediation_prompt",
    title="Zen remediation prompt",
    description="Generate a remediation prompt scaffold for violations in a language.",
    icons=PROMPT_RESOURCE_ICONS,
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
        LanguagesResult: LanguagesResult wrapping the list of language strings declared in
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

    _ = repo_path
    return LanguagesResult(languages=CONFIG.languages)


@mcp.tool(
    name="analyze_zen_violations",
    version=ANALYZE_ZEN_VIOLATIONS_VERSION,
    title="Analyze zen violations",
    description="Analyze a code snippet against zen rules and return analysis results.",
    icons=ANALYSIS_TOOL_ICONS,
    tags={"analysis", "zen", "snippet"},
    annotations=READONLY_ANNOTATIONS,
    output_schema=_output_schema(AnalysisResult),
)
async def analyze_zen_violations(
    code: str,
    language: str,
    severity_threshold: int | None = None,
    *,
    enable_external_tools: bool = False,
    allow_temporary_runners: bool = False,
) -> AnalysisResult:
    """Run v1.0 snippet analysis.

    Args:
        code (str): Source code to analyse.
        language (str): Programming language identifier.
        severity_threshold (int | None, optional): Minimum severity to include. Default to None.
        enable_external_tools (bool, optional): Opt-in execution of external linters. Default to False.
        allow_temporary_runners (bool, optional): Allow temporary tool runners (e.g. npx/uvx). Default to False.
    """
    return _analyze_snippet_internal(
        code=code,
        language=language,
        tool_version=ANALYZE_ZEN_VIOLATIONS_VERSION,
        severity_threshold=severity_threshold,
        enable_external_tools=enable_external_tools,
        allow_temporary_runners=allow_temporary_runners,
        reject_empty_code=False,
    )


@mcp.tool(
    name="analyze_zen_violations",
    version=ANALYZE_ZEN_VIOLATIONS_V2_VERSION,
    title="Analyze zen violations (v2)",
    description=(
        "Analyze a code snippet against zen rules with stricter request-quality "
        "guardrails and richer telemetry metadata."
    ),
    icons=ANALYSIS_TOOL_ICONS,
    tags={"analysis", "zen", "snippet", "v2"},
    annotations=READONLY_ANNOTATIONS,
    output_schema=_output_schema(AnalysisResult),
)
async def analyze_zen_violations_v2(
    code: str,
    language: str,
    severity_threshold: int | None = None,
    *,
    enable_external_tools: bool = False,
    allow_temporary_runners: bool = False,
) -> AnalysisResult:
    """Run v2.0 snippet analysis with non-empty code validation.

    Args:
        code (str): Source code to analyse.
        language (str): Programming language identifier.
        severity_threshold (int | None, optional): Severity threshold. Default to None.
        enable_external_tools (bool, optional): Enable external tools. Default to False.
        allow_temporary_runners (bool, optional): Allow temporary runners. Default to False.
    """
    return _analyze_snippet_internal(
        code=code,
        language=language,
        tool_version=ANALYZE_ZEN_VIOLATIONS_V2_VERSION,
        severity_threshold=severity_threshold,
        enable_external_tools=enable_external_tools,
        allow_temporary_runners=allow_temporary_runners,
        reject_empty_code=True,
    )


def _analyze_snippet_internal(  # noqa: PLR0913
    *,
    code: str,
    language: str,
    tool_version: str,
    severity_threshold: int | None,
    enable_external_tools: bool,
    allow_temporary_runners: bool,
    reject_empty_code: bool,
) -> AnalysisResult:
    """Shared analyzer implementation for versioned snippet tools."""
    canonical_language = _canonical_language(language)
    if reject_empty_code and not code.strip():
        msg = (
            "Empty code is not accepted for analyze_zen_violations v2. "
            "Pass a non-empty snippet or use analyze_repository."
        )
        raise ValueError(msg)
    with analysis_span(
        "analyze_zen_violations",
        {
            "language": canonical_language,
            "tool.version": tool_version,
        },
    ):
        supported = sorted(supported_languages())
        if canonical_language not in supported:
            supported_list = ", ".join(supported)
            msg = f"Unsupported language '{language}'. Supported languages: {supported_list}."
            raise ValueError(msg)

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
        analyze_kwargs: dict[str, object] = {}
        if enable_external_tools:
            analyze_kwargs["enable_external_tools"] = True
        if allow_temporary_runners:
            analyze_kwargs["allow_temporary_tools"] = True
        result = analyzer.analyze(code, **analyze_kwargs)
        result.violations = [
            violation
            for violation in result.violations
            if violation.severity >= effective_threshold
        ]
        return result


@mcp.tool(
    name="generate_prompts",
    version=GENERATE_PROMPTS_VERSION,
    title="Generate remediation prompts",
    description="Generate remediation prompts from zen analysis results.",
    icons=PROMPT_TOOL_ICONS,
    tags={"prompts", "remediation"},
    annotations=READONLY_ANNOTATIONS,
    output_schema=_output_schema(PromptBundle),
)
async def generate_prompts_tool(
    code: str,
    language: str,
    *,
    enable_external_tools: bool = False,
    allow_temporary_runners: bool = False,
) -> PromptBundle:
    """Generate remediation prompts for v1.0 prompt generation.

    Args:
        code (str): Source code to analyse.
        language (str): Programming language identifier.
        enable_external_tools (bool, optional): Enable external tools. Default to False.
        allow_temporary_runners (bool, optional): Allow temporary runners. Default to False.
    """
    return _generate_prompts_internal(
        code=code,
        language=language,
        tool_version=GENERATE_PROMPTS_VERSION,
        enable_external_tools=enable_external_tools,
        allow_temporary_runners=allow_temporary_runners,
    )


@mcp.tool(
    name="generate_prompts",
    version=GENERATE_PROMPTS_V2_VERSION,
    title="Generate remediation prompts (v2)",
    description=(
        "Generate remediation prompts with MCP-first guidance metadata and v2 "
        "versioned prompt semantics."
    ),
    icons=PROMPT_TOOL_ICONS,
    tags={"prompts", "remediation", "v2"},
    annotations=READONLY_ANNOTATIONS,
    output_schema=_output_schema(PromptBundle),
)
async def generate_prompts_tool_v2(
    code: str,
    language: str,
    *,
    enable_external_tools: bool = False,
    allow_temporary_runners: bool = False,
) -> PromptBundle:
    """Generate remediation prompts for v2.0 prompt generation.

    Args:
        code (str): Source code to analyse.
        language (str): Programming language identifier.
        enable_external_tools (bool, optional): Enable external tools. Default to False.
        allow_temporary_runners (bool, optional): Allow temporary runners. Default to False.
    """
    return _generate_prompts_internal(
        code=code,
        language=language,
        tool_version=GENERATE_PROMPTS_V2_VERSION,
        enable_external_tools=enable_external_tools,
        allow_temporary_runners=allow_temporary_runners,
    )


def _generate_prompts_internal(
    *,
    code: str,
    language: str,
    tool_version: str,
    enable_external_tools: bool,
    allow_temporary_runners: bool,
) -> PromptBundle:
    """Shared prompt-generation implementation for versioned prompt tools."""
    canonical_language = _canonical_language(language)
    with analysis_span(
        "generate_prompts",
        {"language": canonical_language, "tool.version": tool_version},
    ):
        supported = sorted(supported_languages())
        if canonical_language not in supported:
            supported_list = ", ".join(supported)
            msg = f"Unsupported language '{language}'. Supported languages: {supported_list}."
            raise ValueError(msg)
        analyzer = create_analyzer(
            canonical_language,
            pipeline_config=_pipeline_with_runtime_overrides(canonical_language),
        )
        analyze_kwargs: dict[str, object] = {}
        if enable_external_tools:
            analyze_kwargs["enable_external_tools"] = True
        if allow_temporary_runners:
            analyze_kwargs["allow_temporary_tools"] = True
        result = analyzer.analyze(code, **analyze_kwargs)
        return build_prompt_bundle([result])


async def _analyze_repository_internal(  # noqa: C901, PLR0913
    repo_path: str,
    languages: list[str] | None = None,
    max_files: int = 100,
    ctx: fastmcp.Context | None = None,
    *,
    enable_external_tools: bool = False,
    allow_temporary_runners: bool = False,
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
        languages (list[str] | None, optional): Restrict analysis to these languages.
            Defaults to ``["python"]`` when omitted.
        max_files (int, optional): Cap on files analysed per language, preventing
            runaway analysis on very large repositories. Default to 100.
        ctx (fastmcp.Context | None, optional): Optional FastMCP context used for
            progress updates and per-file log messages. Default to None.
        enable_external_tools (bool, optional): Opt-in execution of allow-listed
            external tools while analyzing files. Default to False.
        allow_temporary_runners (bool, optional): Permit temporary-runner fallback
            strategies for external tools. Default to False.

    Returns:
        list[RepositoryAnalysis]: One entry per analysed file, each
        carrying the file path, detected language, and its
        ``AnalysisResult``.
    """
    with analysis_span(
        "analyze_repository.internal",
        {"repo_path": repo_path, "max_files": max_files},
    ):
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
            enable_external_tools=enable_external_tools,
            allow_temporary_tools=allow_temporary_runners,
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
    task=BACKGROUND_TASK,
)
async def analyze_repository(  # noqa: PLR0913
    repo_path: str,
    languages: list[str] | None = None,
    max_files: int = 100,
    ctx: fastmcp.Context | None = None,
    *,
    enable_external_tools: bool = False,
    allow_temporary_runners: bool = False,
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
        languages (list[str] | None, optional): Restrict analysis to specific
            language identifiers.  Defaults to ``["python"]`` internally.
        max_files (int, optional): Per-language cap on the number of files to
            analyse, protecting against excessive runtime on monorepos. Default to 100.
        ctx (fastmcp.Context | None, optional): Optional FastMCP context for progress
            and log updates during repository analysis. Default to None.
        enable_external_tools (bool, optional): Opt-in execution of allow-listed
            external tools while analyzing files. Default to False.
        allow_temporary_runners (bool, optional): Permit temporary-runner fallback
            strategies for external tools. Default to False.

    Returns:
        list[RepositoryAnalysis]: List of ``RepositoryAnalysis`` entries, each pairing a file path
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
    return await _analyze_repository_internal(
        repo_path,
        languages,
        max_files,
        ctx,
        enable_external_tools=enable_external_tools,
        allow_temporary_runners=allow_temporary_runners,
    )


def _build_batch_violations_list(
    results: list[RepositoryAnalysis],
) -> list[BatchViolation]:
    """Flatten and sort all violations from repository results, worst-first.

    Violations from every file are collected into a single list and sorted
    by descending severity so that the most critical issues appear first
    across all pages, regardless of which file they belong to.

    Args:
        results: Per-file analysis results from ``_analyze_repository_internal``.

    Returns:
        list[BatchViolation]: All violations sorted by severity (highest first).
    """
    all_violations: list[BatchViolation] = []
    for entry in results:
        all_violations.extend(
            BatchViolation(
                file=entry.path,
                language=entry.language,
                principle=v.principle,
                severity=v.severity,
                message=v.message,
                suggestion=v.suggestion,
                location=v.location,
            )
            for v in entry.result.violations
        )
    all_violations.sort(key=lambda bv: bv.severity, reverse=True)
    return all_violations


@mcp.tool(
    name="analyze_batch",
    title="Analyze repository (batch / LLM-safe)",
    description=(
        "Analyse a repository path and return token-budgeted, paginated violations "
        "designed for LLM context windows. Highest-severity violations appear first. "
        "Pass the returned cursor to resume from the next page."
    ),
    tags={"analysis", "batch", "pagination"},
    annotations=READONLY_ANNOTATIONS,
    output_schema=_output_schema(BatchPage),
    task=BACKGROUND_TASK,
)
async def analyze_batch(  # noqa: PLR0913
    path: str,
    language: str,
    cursor: str | None = None,
    max_tokens: int = 8000,
    max_files: int = 100,
    *,
    enable_external_tools: bool = False,
    allow_temporary_runners: bool = False,
) -> BatchPage:
    """Analyse a repository and return one token-budgeted page of violations.

    This tool is explicitly designed for LLM agent workflows where the
    full violation list would exceed the model's context window.  It
    analyses the repository, sorts violations globally by severity
    (highest first), and returns only as many as fit within *max_tokens*.
    The opaque *cursor* field in the response encodes the resume position;
    pass it back unchanged on the next call to advance to the next page.

    Design principles:

    * **Stateless** — the cursor encodes the exact position in the sorted
      violation list; no server-side session state is required.
    * **Token-budget aware** — the response is trimmed so that the
      serialised payload stays within *max_tokens*.
    * **Priority ordering** — highest-severity violations are surfaced
      first across all pages.

    Args:
        path (str): Absolute or relative path to the repository root.
        language (str): Language identifier to restrict analysis (e.g. ``"python"``).
        cursor (str | None, optional): Opaque continuation token from a previous
            call.  Omit or pass ``None`` to start from the first page. Default to None.
        max_tokens (int, optional): Approximate token budget for the ``violations``
            payload.  Violations are added until the budget would be exceeded;
            the envelope overhead is excluded from this count. Default to 8000.
        max_files (int, optional): Cap on the number of files to analyse.
            Default to 100.
        enable_external_tools (bool, optional): Opt-in execution of external linters.
            Default to False.
        allow_temporary_runners (bool, optional): Permit temporary-runner strategies.
            Default to False.

    Returns:
        BatchPage: A page carrying the token-budgeted violations, a continuation
        cursor (``None`` when all violations have been returned), and file
        count metadata.

    Example:
        ```python
        # First page
        page = await analyze_batch("/repo", "python", max_tokens=4000)
        while page.has_more:
            page = await analyze_batch("/repo", "python", cursor=page.cursor)
        ```

    See Also:
        [`analyze_batch_summary`][mcp_zen_of_languages.server.analyze_batch_summary]:
            Returns a compact health-score overview that always fits in one
            context window.
        [`analyze_repository`][mcp_zen_of_languages.server.analyze_repository]:
            Full (unpaginated) repository analysis for non-LLM consumers.
    """
    canonical_language = _canonical_language(language)
    results = await _analyze_repository_internal(
        path,
        [canonical_language],
        max_files,
        None,
        enable_external_tools=enable_external_tools,
        allow_temporary_runners=allow_temporary_runners,
    )
    files_total = len(results)

    all_violations = _build_batch_violations_list(results)

    start_index, _ = _decode_cursor(cursor) if cursor else (0, 0)
    start_index = max(0, min(start_index, len(all_violations)))

    page_violations: list[BatchViolation] = []
    used_tokens = 0
    token_budget = max(1, max_tokens - _BATCH_ENVELOPE_TOKEN_OVERHEAD)

    next_index = start_index
    for bv in all_violations[start_index:]:
        serialised = json.dumps(bv.model_dump())
        cost = _estimate_tokens(serialised)
        if used_tokens + cost > token_budget and page_violations:
            break
        page_violations.append(bv)
        used_tokens += cost
        next_index += 1

    has_more = next_index < len(all_violations)
    next_cursor = _encode_cursor(next_index) if has_more else None

    # files_processed: distinct files represented in this page
    files_in_page = len({bv.file for bv in page_violations})
    # page number: estimate based on cursor position
    page_num = 1
    if start_index > 0 and all_violations:
        page_num = start_index // max(1, len(page_violations)) + 1

    return BatchPage(
        cursor=next_cursor,
        page=page_num,
        has_more=has_more,
        violations=page_violations,
        files_processed=files_in_page,
        files_total=files_total,
    )


@mcp.tool(
    name="analyze_batch_summary",
    title="Analyze repository — batch summary",
    description=(
        "Return a compact project health score and top-5 hotspot files from a "
        "repository scan. Always fits within a single LLM context window. "
        "Use this before analyze_batch to decide whether full pagination is needed."
    ),
    tags={"analysis", "batch", "summary"},
    annotations=READONLY_ANNOTATIONS,
    output_schema=_output_schema(BatchSummary),
    task=BACKGROUND_TASK,
)
async def analyze_batch_summary(
    path: str,
    language: str,
    max_files: int = 100,
    *,
    enable_external_tools: bool = False,
    allow_temporary_runners: bool = False,
) -> BatchSummary:
    """Return a compact health overview for a repository — always one page.

    Unlike ``analyze_batch``, which paginates a potentially large violation
    list, this tool summarises the entire repository in a single response.
    It is designed to fit comfortably inside any LLM context window so that
    an agent can assess project health and identify where to focus before
    deciding whether to call ``analyze_batch`` for deeper detail.

    The returned ``health_score`` is the repository's average ``overall_score``
    expressed on a 0-100 scale (higher is better).  The ``hotspots`` list
    contains the five files with the highest violation count, ordered by
    descending total violations.

    Args:
        path (str): Absolute or relative path to the repository root.
        language (str): Language identifier to restrict analysis (e.g. ``"python"``).
        max_files (int, optional): Cap on the number of files to analyse.
            Default to 100.
        enable_external_tools (bool, optional): Opt-in execution of external linters.
            Default to False.
        allow_temporary_runners (bool, optional): Permit temporary-runner strategies.
            Default to False.

    Returns:
        BatchSummary: Compact summary with ``health_score`` (0-100),
        up to five ``hotspots``, ``total_violations``, and ``total_files``.

    Example:
        ```python
        summary = await analyze_batch_summary("/repo", "python")
        print(summary.health_score, summary.hotspots)
        ```

    See Also:
        [`analyze_batch`][mcp_zen_of_languages.server.analyze_batch]:
            Full paginated violation detail for LLM agents.
        [`analyze_repository`][mcp_zen_of_languages.server.analyze_repository]:
            Complete unpaginated results for non-LLM consumers.
    """
    canonical_language = _canonical_language(language)
    results = await _analyze_repository_internal(
        path,
        [canonical_language],
        max_files,
        None,
        enable_external_tools=enable_external_tools,
        allow_temporary_runners=allow_temporary_runners,
    )

    total_files = len(results)
    total_violations = sum(len(entry.result.violations) for entry in results)

    # Health score: average overall_score (0-10 scale) mapped to 0-100
    if results:
        avg_score = sum(entry.result.overall_score for entry in results) / total_files
    else:
        avg_score = 10.0
    health_score = round(avg_score * 10.0, 1)

    # Top-5 hotspots by violation count, tie-broken by top severity
    sorted_results = sorted(
        results,
        key=lambda e: (
            len(e.result.violations),
            max((v.severity for v in e.result.violations), default=0),
        ),
        reverse=True,
    )
    hotspots = [
        BatchHotspot(
            path=entry.path,
            language=entry.language,
            violations=len(entry.result.violations),
            top_severity=max((v.severity for v in entry.result.violations), default=0),
        )
        for entry in sorted_results[:5]
    ]

    return BatchSummary(
        health_score=health_score,
        hotspots=hotspots,
        total_violations=total_violations,
        total_files=total_files,
    )


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
    task=BACKGROUND_TASK,
)
async def generate_agent_tasks_tool(
    repo_path: str,
    languages: list[str] | None = None,
    min_severity: int = 5,
    *,
    enable_external_tools: bool = False,
    allow_temporary_runners: bool = False,
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
        languages (list[str] | None, optional): Restrict scanning to these
            languages.  Omit to analyse only Python files by default. Default to None.
        min_severity (int, optional): Severity floor (1-10 scale).  Violations
            below this threshold are excluded from the task list. Default to 5.
        enable_external_tools (bool, optional): Opt-in execution of allow-listed
            external tools while gathering repository analysis. Default to False.
        allow_temporary_runners (bool, optional): Permit temporary-runner fallback
            strategies for external tools. Default to False.

    Returns:
        AgentTaskList: AgentTaskList containing prioritised tasks ready for automated
        remediation, sorted from highest to lowest severity.

    See Also:
        [`analyze_repository`][mcp_zen_of_languages.server.analyze_repository]:
            Retrieves the raw per-file results that feed task generation.
        [`generate_prompts_tool`][mcp_zen_of_languages.server.generate_prompts_tool]:
            Provides human-readable remediation text rather than
            structured tasks.

    """
    repo_results = await _analyze_repository_internal(
        repo_path,
        languages=languages,
        enable_external_tools=enable_external_tools,
        allow_temporary_runners=allow_temporary_runners,
    )
    analysis_results = [entry.result for entry in repo_results]
    return build_agent_tasks(
        analysis_results,
        project=repo_path,
        min_severity=min_severity,
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
    msg = (
        "check_architectural_patterns is not implemented yet. "
        "Pattern detection is planned but not available in this release."
    )
    raise NotImplementedError(msg)


@mcp.tool(
    name="generate_report",
    title="Generate report",
    description="Generate a markdown/json report with gap analysis and prompts.",
    tags={"reporting", "analysis"},
    annotations=READONLY_ANNOTATIONS,
    output_schema=_output_schema(ReportOutput),
    task=BACKGROUND_TASK,
)
async def generate_report_tool(  # noqa: PLR0913
    target_path: str,
    language: str | None = None,
    *,
    include_prompts: bool = False,
    include_analysis: bool = True,
    include_gaps: bool = True,
    ctx: fastmcp.Context | None = None,
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
        language (str | None, optional): Explicit language override.  When omitted,
            the language is inferred from file extensions. Default to None.
        include_prompts (bool, optional): Append remediation prompt sections derived
            from ``build_prompt_bundle``. Default to False.
        include_analysis (bool, optional): Include the violation-analysis body
            showing per-rule findings. Default to True.
        include_gaps (bool, optional): Include quality-gap and coverage-gap
            summaries highlighting areas that need attention. Default to True.
        ctx (fastmcp.Context | None, optional): Optional FastMCP context used to emit
            progress and log updates for analyzed targets. Default to None.

    Returns:
        ReportOutput: ReportOutput with ``markdown`` (rendered report text) and ``data``
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
        languages (list[str] | None, optional): Restrict the export to these
            language identifiers.  When omitted, mappings for every
            registered language are returned. Default to None.

    Returns:
        dict: Nested dictionary keyed by language, then by rule ID, with
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
        ConfigStatus: ConfigStatus reflecting the merged view of static configuration
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
        ConfigStatus: ConfigStatus describing active languages, severity threshold,
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
async def set_config_override(  # noqa: PLR0913
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
        max_cyclomatic_complexity (int | None, optional): Override the per-function
            cyclomatic-complexity ceiling. Default to None.
        max_nesting_depth (int | None, optional): Override the maximum allowed
            nesting depth for control-flow blocks. Default to None.
        max_function_length (int | None, optional): Override the maximum lines Default to None.
            permitted in a single function body.
        max_class_length (int | None, optional): Override the maximum lines
            permitted in a single class definition. Default to None.
        max_line_length (int | None, optional): Override the maximum character
            width for a single source line. Default to None.
        severity_threshold (int | None, optional): Override the minimum severity
            at which violations are surfaced in results. Default to None.

    Returns:
        ConfigStatus: ConfigStatus reflecting all overrides after this mutation,
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
        ConfigStatus: ConfigStatus after all override entries have been cleared.

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
    icons=ONBOARDING_TOOL_ICONS,
    tags={"onboarding", "setup"},
    annotations=READONLY_ANNOTATIONS,
    output_schema=_output_schema(OnboardingGuide),
)
async def onboard_project(
    project_path: str,
    primary_language: str = "python",
    team_size: str = "small",
    strictness: str = "moderate",
    ctx: fastmcp.Context | None = None,
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
        primary_language (str, optional): Language used for example snippets and
            default pipeline selection (e.g. ``"python"``). Default to "python".
        team_size (str, optional): Descriptive team-size hint (``"small"``,
            ``"medium"``, ``"large"``), reserved for future adaptive
            threshold scaling. Default to "small".
        strictness (str, optional): Preset name controlling all numeric thresholds
            (``"relaxed"``, ``"moderate"``, or ``"strict"``). Default to "moderate".
        ctx (fastmcp.Context | None, optional): Optional FastMCP context used for
            elicitation when strictness or language values are ambiguous. Default to None.

    Returns:
        OnboardingGuide: OnboardingGuide with ordered steps, each carrying an action key
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
    _ = team_size
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
    strictness_value = strictness
    if strictness_value not in thresholds and ctx is not None:
        response = await ctx.elicit(
            "Strictness is ambiguous. Choose one option:",
            response_type=["relaxed", "moderate", "strict"],
        )
        if response.action == "accept":
            strictness_value = str(response.data)
    if strictness_value not in thresholds:
        strictness_value = "moderate"
    t = thresholds[strictness_value]

    canonical_primary_language = _canonical_language(primary_language)
    supported = sorted(supported_languages())
    if canonical_primary_language not in supported and ctx is not None:
        response = await ctx.elicit(
            (
                f"Primary language '{primary_language}' is unsupported. "
                "Select a supported language:"
            ),
            response_type=supported,
        )
        if response.action == "accept":
            canonical_primary_language = _canonical_language(str(response.data))
    if canonical_primary_language not in supported:
        supported_list = ", ".join(supported)
        msg = (
            f"Unsupported language '{primary_language}'. "
            f"Supported languages: {supported_list}."
        )
        raise ValueError(msg)

    steps = [
        OnboardingStep(
            step=1,
            title="Configure zen-config.yaml",
            description=(
                "Create or update zen-config.yaml in your project root with "
                f"{strictness_value} settings."
            ),
            action="create_config",
            example=f"max_cyclomatic_complexity: {t['complexity']}",
        ),
        OnboardingStep(
            step=2,
            title="Set up VS Code integration",
            description="Add the MCP server configuration to .vscode/mcp.json for VS Code integration.",
            action="setup_vscode",
            example='{"servers":{"zen-of-languages":{"command":"uvx","args":["--from","mcp-zen-of-languages","zen-mcp-server"]}}}',
        ),
        OnboardingStep(
            step=3,
            title="Run initial analysis",
            description="Analyze your codebase to establish a baseline of zen violations.",
            action="analyze",
            example=f"analyze_repository('{project_path}', languages=['{canonical_primary_language}'])",
        ),
        OnboardingStep(
            step=4,
            title="Review and adjust thresholds",
            description="Based on initial results, adjust thresholds using set_config_override if needed.",
            action="tune_config",
            example=f"set_config_override('{canonical_primary_language}', max_cyclomatic_complexity={t['complexity']})",
        ),
        OnboardingStep(
            step=5,
            title="Integrate MCP analysis in CI/CD",
            description=(
                "Use MCP tool calls in CI agents for continuous code quality "
                "monitoring; keep terminal CLI checks as optional fallback."
            ),
            action="ci_integration",
            example=(
                f"generate_agent_tasks('{project_path}', "
                f"languages=['{canonical_primary_language}'], min_severity=7)"
            ),
        ),
    ]

    return OnboardingGuide(
        project_name=project_path.rsplit("/", maxsplit=1)[-1],
        steps=steps,
        recommended_config={
            "language": canonical_primary_language,
            "max_cyclomatic_complexity": t["complexity"],
            "max_nesting_depth": t["nesting"],
            "max_function_length": t["function_length"],
            "max_line_length": t["line_length"],
            "severity_threshold": 5
            if strictness_value == "relaxed"
            else 6
            if strictness_value == "moderate"
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
        dict[str, list[str]]: Dictionary mapping each language identifier (e.g. ``"python"``)
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
    for lang in ZEN_REGISTRY:
        detectors = [
            meta.detector_id
            for meta in REGISTRY.items()
            if meta.language in [lang, "any"]
        ]
        result[lang] = detectors
    return result


class _LegacyResourceManager:
    """Minimal compatibility shim for older tests expecting private managers."""

    def __init__(self) -> None:
        self._resources = {
            "zen://config": config_resource,
            "zen://languages": languages_resource,
        }
        self._templates = {"zen://rules/{language}": rules_resource}


class _LegacyPromptManager:
    """Minimal compatibility shim for older tests expecting private managers."""

    def __init__(self) -> None:
        self._prompts = {"zen_remediation_prompt": remediation_prompt}


def _attach_legacy_tool_annotations(
    tool_fn: object,
    annotations: ToolAnnotations,
) -> None:
    """Attach compatibility attributes expected by older tests."""
    legacy_tool = cast("Any", tool_fn)
    if not hasattr(legacy_tool, "fn"):
        legacy_tool.fn = tool_fn
    if not hasattr(legacy_tool, "annotations"):
        legacy_tool.annotations = annotations


def _attach_legacy_test_compat() -> None:
    """Expose legacy tool attributes used by the repository test suite."""
    tools_with_annotations = [
        (detect_languages, READONLY_ANNOTATIONS),
        (analyze_zen_violations, READONLY_ANNOTATIONS),
        (analyze_zen_violations_v2, READONLY_ANNOTATIONS),
        (generate_prompts_tool, READONLY_ANNOTATIONS),
        (generate_prompts_tool_v2, READONLY_ANNOTATIONS),
        (analyze_repository, READONLY_ANNOTATIONS),
        (analyze_batch, READONLY_ANNOTATIONS),
        (analyze_batch_summary, READONLY_ANNOTATIONS),
        (generate_agent_tasks_tool, READONLY_ANNOTATIONS),
        (check_architectural_patterns, READONLY_ANNOTATIONS),
        (generate_report_tool, READONLY_ANNOTATIONS),
        (export_rule_detector_mapping, READONLY_ANNOTATIONS),
        (get_config, READONLY_ANNOTATIONS),
        (set_config_override, MUTATING_ANNOTATIONS),
        (clear_config_overrides, MUTATING_ANNOTATIONS),
        (onboard_project, READONLY_ANNOTATIONS),
        (get_supported_languages, READONLY_ANNOTATIONS),
    ]

    for tool_fn, annotations in tools_with_annotations:
        _attach_legacy_tool_annotations(tool_fn, annotations)

    resource_manager_attr = "_resource_manager"
    if not hasattr(mcp, resource_manager_attr):
        setattr(mcp, resource_manager_attr, _LegacyResourceManager())
    prompt_manager_attr = "_prompt_manager"
    if not hasattr(mcp, prompt_manager_attr):
        setattr(mcp, prompt_manager_attr, _LegacyPromptManager())


_attach_legacy_test_compat()
