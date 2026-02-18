"""Typer-based CLI for multi-language zen code analysis.

Exposes ``check``, ``report``, ``prompts``, ``list-rules``, ``init``, and
``export-mapping`` subcommands through a single :pydata:`app` Typer instance.
Terminal output relies on Rich renderables — pyfiglet banners, severity badges,
and structured tables — all capped at :pydata:`MAX_OUTPUT_WIDTH` columns so
panels never blow past a comfortable terminal width.  Typer's own help renderer
is monkey-patched via [`_rich_format_help_with_banner`][_rich_format_help_with_banner] to prepend the
shared Zen banner, and panel/table border styles are forced to ``cyan``
``ROUNDED`` boxes for visual consistency.

Each public Typer command thin-delegates to a private ``_run_*`` orchestrator,
keeping argument parsing separate from business logic and enabling unit testing
of the orchestrators with plain ``SimpleNamespace`` fakes.
"""

from __future__ import annotations

import json
import logging
import os
import sys
from collections import Counter
from pathlib import Path
from types import SimpleNamespace
from typing import Literal, Protocol

import click
import typer
import typer.rich_utils as typer_rich_utils
from rich.console import Group
from rich.table import Table
from rich.text import Text

from mcp_zen_of_languages import __version__
from mcp_zen_of_languages.models import (
    AnalysisResult,
    CyclomaticSummary,
    Metrics,
    ProjectSummary,
    RulesSummary,
    SeverityCounts,
    WorstOffender,
)
from mcp_zen_of_languages.orchestration import (
    analyze_targets as _shared_analyze_targets,
)
from mcp_zen_of_languages.orchestration import (
    build_repository_imports as _shared_build_repository_imports,
)
from mcp_zen_of_languages.orchestration import (
    collect_targets as _shared_collect_targets,
)
from mcp_zen_of_languages.rendering import (
    analysis_progress,
    console,
    file_glyph,
    get_banner_art,
    is_quiet,
    print_banner,
    print_error,
    render_report_terminal,
    set_quiet,
    severity_badge,
)
from mcp_zen_of_languages.rendering.factories import (
    zen_header_panel,
    zen_panel,
    zen_table,
)
from mcp_zen_of_languages.rendering.layout import MAX_OUTPUT_WIDTH
from mcp_zen_of_languages.rendering.sarif import analysis_results_to_sarif
from mcp_zen_of_languages.reporting.agent_tasks import AgentTaskList, build_agent_tasks
from mcp_zen_of_languages.reporting.models import PromptBundle
from mcp_zen_of_languages.reporting.prompts import build_prompt_bundle
from mcp_zen_of_languages.reporting.terminal import (
    build_agent_tasks_table as render_agent_tasks_table,
)
from mcp_zen_of_languages.reporting.terminal import (
    render_prompt_panel,
)
from mcp_zen_of_languages.rules import get_language_zen
from mcp_zen_of_languages.utils.markdown_quality import normalize_markdown

logger = logging.getLogger(__name__)
logger.setLevel(
    getattr(
        logging, os.environ.get("ZEN_LOG_LEVEL", "WARNING").upper(), logging.WARNING
    )
)

_THRESHOLDS = {"relaxed": 5, "moderate": 6, "strict": 7}

# Keep Typer's rich help panels aligned with the CLI rendering width contract.
if typer_rich_utils.MAX_WIDTH is None or typer_rich_utils.MAX_WIDTH > MAX_OUTPUT_WIDTH:
    typer_rich_utils.MAX_WIDTH = MAX_OUTPUT_WIDTH
setattr(typer_rich_utils, "STYLE_OPTIONS_PANEL_BORDER", "cyan")
setattr(typer_rich_utils, "STYLE_COMMANDS_PANEL_BORDER", "cyan")
setattr(typer_rich_utils, "STYLE_OPTIONS_TABLE_BOX", "ROUNDED")
setattr(typer_rich_utils, "STYLE_COMMANDS_TABLE_BOX", "ROUNDED")

_ORIGINAL_RICH_FORMAT_HELP = typer_rich_utils.rich_format_help


def _rich_format_help_with_banner(
    *,
    obj: click.Command | click.Group,
    ctx: click.Context,
    markup_mode: Literal["markdown", "rich"],
) -> None:
    """Prepend the pyfiglet Zen banner before Typer's standard help output.

    Typer delegates help rendering to ``rich_format_help``.  This wrapper
    prints the ASCII art banner first, then forwards to the original renderer,
    so every ``--help`` invocation feels branded without duplicating layout
    logic across subcommands.

    Args:
        obj (click.Command | click.Group): Click command or group whose help text is being rendered.
        ctx (click.Context): Active Click context carrying invocation metadata and parent chain.
        markup_mode (Literal['markdown', 'rich']): Markup dialect Typer selected for panel content.

    See Also:
        ``_build_welcome_panel``: Renders the no-args welcome screen using
        the same banner art but a different Rich layout.
    """

    console.print(Text(get_banner_art(), style="bold cyan"))
    _ORIGINAL_RICH_FORMAT_HELP(obj=obj, ctx=ctx, markup_mode=markup_mode)


setattr(typer_rich_utils, "rich_format_help", _rich_format_help_with_banner)

app = typer.Typer(
    name="mcp-zen-of-languages",
    no_args_is_help=True,
    add_completion=False,
    rich_markup_mode="rich",
    help="Zen of Languages — consistent rich terminal UI for multi-language code analysis (no full-screen TUI).",
)


def _install_rich_traceback() -> None:
    """Activate Rich's pretty-printed traceback handler for the session.

    Called once when ``--verbose`` is passed.  Rich tracebacks surface local
    variable values alongside each stack frame, making it far easier to
    diagnose failures inside detector pipelines or config loading without
    reaching for a debugger.

    See Also:
        [`_configure_app`][_configure_app]: The Typer callback that conditionally invokes
        this helper.
    """

    from rich.traceback import install as install_rich_traceback

    install_rich_traceback(show_locals=True)


@app.callback()
def _configure_app(
    quiet: bool = typer.Option(
        False, "--quiet", "-q", help="Suppress decorative output"
    ),
    verbose: bool = typer.Option(
        False, "--verbose", "-v", help="Show rich tracebacks with local variables"
    ),
) -> None:
    """Apply session-wide quiet/verbose flags before any subcommand runs.

    Typer invokes this callback first on every invocation.  It toggles the
    module-level quiet flag (suppressing banners and decorative output) and
    optionally installs Rich tracebacks.  When neither flag is set the
    pyfiglet banner prints once, giving users a visual anchor.

    Args:
        quiet (bool): Suppress decorative banners, panels, and progress bars.
        verbose (bool): Enable Rich tracebacks with local-variable inspection.

    See Also:
        [`_install_rich_traceback`][_install_rich_traceback]: Activated when *verbose* is ``True``.
    """

    set_quiet(quiet)
    if verbose:
        _install_rich_traceback()
    if not quiet:
        print_banner()


def _ns(**kwargs: object) -> SimpleNamespace:
    """Bundle keyword arguments into a lightweight attribute-access object.

    Typer commands forward their parsed options to ``_run_*`` orchestrators
    as ``SimpleNamespace`` instances, avoiding a hard dependency on the
    Protocol classes while keeping attribute access readable.

    Args:
        **kwargs (object): Arbitrary keyword arguments that become namespace attributes.

    Returns:
        SimpleNamespace: Attribute-access wrapper over the supplied keyword pairs.
    """

    return SimpleNamespace(**kwargs)


def _parse_languages(value: str) -> list[str]:
    """Split a comma-or-space-separated string into individual language tokens.

    The ``--languages`` CLI option accepts ``"python,typescript"`` or
    ``"python typescript"``; this normaliser handles both separators and
    strips surrounding whitespace so downstream code always receives a clean
    list of lowercase identifiers.

    Args:
        value (str): Raw comma-or-space-delimited language string from CLI input.

    Returns:
        list[str]: Deduplicated, whitespace-stripped language identifiers.

    See Also:
        [`_detect_languages`][_detect_languages]: Auto-discovers languages when no explicit
        list is given.
    """

    tokens = [token.strip() for token in value.replace(",", " ").split()]
    return [token for token in tokens if token]


def _detect_languages(target: Path) -> list[str]:
    """Scan a file or directory tree and return the set of languages found.

    Walks *target* with [`_collect_targets`][_collect_targets], extracts the unique language
    identifiers, and falls back to ``["python"]`` when nothing is detected.
    Used by [`_run_init`][_run_init] and the interactive wizard to pre-populate the
    language list for ``zen-config.yaml`` generation.

    Args:
        target (Path): File or directory root to scan for recognized source files.

    Returns:
        list[str]: Sorted language identifiers found under *target*, defaulting
        to ``["python"]`` when the scan yields no matches.

    See Also:
        [`_collect_targets`][_collect_targets]: Performs the underlying recursive file walk.
    """

    languages = {language for _, language in _collect_targets(target, None)}
    return sorted(languages) if languages else ["python"]


def _normalize_strictness(strictness: str) -> str:
    """Clamp a free-form strictness string to one of the recognised presets.

    Accepts any casing of ``relaxed``, ``moderate``, or ``strict`` and
    normalises to lowercase.  Unrecognised values silently fall back to
    ``"moderate"`` so typos never crash the init wizard.

    Args:
        strictness (str): Free-form strictness label entered by the user or CLI default.

    Returns:
        str: One of ``"relaxed"``, ``"moderate"``, or ``"strict"``.
    """

    normalized = strictness.lower()
    return normalized if normalized in _THRESHOLDS else "moderate"


def _build_config_yaml(languages: list[str], strictness: str) -> str:
    """Render a minimal ``zen-config.yaml`` body from language and strictness choices.

    Produces a YAML string with a ``languages:`` list and a
    ``severity_threshold:`` integer derived from :pydata:`_THRESHOLDS`.
    The output is ready to be written directly to disk by [`_run_init`][_run_init].

    Args:
        languages (list[str]): Language identifiers to include in the config stanza.
        strictness (str): Normalised preset name mapped to a numeric severity threshold.

    Returns:
        str: Multi-line YAML text suitable for writing to ``zen-config.yaml``.

    See Also:
        [`_run_init`][_run_init]: Writes the generated YAML to disk.
    """

    unique_languages = list(dict.fromkeys(languages))
    threshold = _THRESHOLDS.get(strictness, _THRESHOLDS["moderate"])
    lines = ["languages:"]
    lines.extend(f"  - {language}" for language in unique_languages)
    lines.extend(["", f"severity_threshold: {threshold}", ""])
    return "\n".join(lines)


def _write_vscode_mcp_config() -> Path:
    """Create ``.vscode/mcp.json`` so VS Code discovers the Zen MCP server.

    Writes a workspace MCP JSON config pointing at ``uv run zen-mcp-server`` with
    workspace-relative ``PYTHONPATH`` and ``ZEN_CONFIG_PATH`` environment
    variables under ``mcp.servers``. The ``.vscode/`` directory is created if
    absent.

    Returns:
        Path: Absolute path to the written ``.vscode/mcp.json`` file.

    See Also:
        [`_run_init`][_run_init]: Optionally calls this helper when the user opts
        into VS Code integration.
    """

    config_path = Path(".vscode") / "mcp.json"
    config_path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "mcp": {
            "servers": {
                "zen-of-languages": {
                    "command": "uv",
                    "args": ["run", "zen-mcp-server"],
                    "cwd": "${workspaceFolder}",
                    "env": {
                        "PYTHONPATH": "${workspaceFolder}/src",
                        "ZEN_CONFIG_PATH": "${workspaceFolder}/zen-config.yaml",
                    },
                }
            }
        }
    }
    config_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return config_path


def _build_welcome_panel() -> None:
    """Display a Rich welcome panel when ``zen`` is invoked with no arguments.

    Combines the pyfiglet banner, version string, and quick-start command
    hints inside a bordered ``zen_panel``, giving first-time users an
    immediate overview without requiring ``--help``.

    See Also:
        [`main`][main]: Calls this helper when *argv* is empty and quiet mode
        is off.
    """

    welcome_group = Group(
        Text(get_banner_art(), style="bold cyan"),
        Text(f"v{__version__}", style="dim"),
        Text(""),
        Text("Welcome to Zen of Languages."),
        Text("Rich CLI output (no full-screen TUI).", style="dim"),
        Text("Run reports to analyze your codebase."),
        Text("Run `zen --help` for the full command reference."),
        Text(""),
        Text("Quick Commands", style="bold"),
        Text("• zen reports <path> — Generate a full report"),
        Text("• zen prompts <path> — Generate remediation guidance"),
        Text("• zen init — Create zen-config.yaml"),
    )
    console.print(zen_panel(welcome_group, title="Welcome"))


class ReportArgs(Protocol):
    """Structural contract for arguments flowing into [`_run_report`][_run_report].

    Each attribute mirrors a Typer option on the [`reports`][reports] command.
    The report workflow reads a file or directory, runs the full analysis
    pipeline, and renders output in one of three formats — ``markdown``,
    ``json``, or ``both``.  Optional export paths let callers siphon the
    JSON payload, rendered markdown, or a compact log summary to separate
    files without replacing the primary output.  Section toggles
    (``skip_analysis``, ``skip_gaps``, ``include_prompts``) control which
    report chapters are generated.

    Attributes:
        path: File or directory to analyse.
        language: Explicit language override bypassing extension-based detection.
        config: Custom ``zen-config.yaml`` path; ``None`` triggers auto-discovery.
        format: Rendering dialect — ``"markdown"``, ``"json"``, or ``"both"``.
        out: Destination file for the rendered report; ``None`` prints to terminal.
        export_json: Sidecar JSON export path, independent of *out*.
        export_markdown: Sidecar markdown export path.
        export_log: Compact log summary export path.
        include_prompts: Append remediation prompts to the report body.
        skip_analysis: Omit the per-file analysis details chapter.
        skip_gaps: Omit the gap-analysis chapter.
    """

    path: str
    language: str | None
    config: str | None
    format: Literal["markdown", "json", "both", "sarif"] | str
    out: str | None
    export_json: str | None
    export_markdown: str | None
    export_log: str | None
    include_prompts: bool
    skip_analysis: bool
    skip_gaps: bool


class ListRulesArgs(Protocol):
    """Structural contract for the ``list-rules`` subcommand arguments.

    Carries the single required language identifier whose zen principles
    will be rendered as a severity-badge table via [`_run_list_rules`][_run_list_rules].

    Attributes:
        language: Language identifier whose zen rules should be listed
            (e.g. ``"python"``, ``"typescript"``).
    """

    language: str


class InitArgs(Protocol):
    """Structural contract for the ``init`` configuration wizard arguments.

    Controls the interactive (or headless ``--yes``) workflow that
    scaffolds a ``zen-config.yaml``.  When running interactively the
    wizard auto-detects project languages, asks the user to confirm or
    override, selects a strictness preset that maps to a severity
    threshold, and optionally writes a ``.vscode/mcp.json`` for editor
    integration.

    Attributes:
        force: Overwrite an existing ``zen-config.yaml`` without prompting.
        yes: Skip all interactive prompts and use detected defaults.
        languages: Pre-selected language list; ``None`` triggers auto-detection.
        strictness: Preset name (``"relaxed"``, ``"moderate"``, ``"strict"``)
            controlling the generated severity threshold.
    """

    force: bool
    yes: bool
    languages: list[str] | None
    strictness: str


class ExportMappingArgs(Protocol):
    """Structural contract for the ``export-mapping`` subcommand arguments.

    Governs how the rule-to-detector mapping is serialised.  The mapping
    shows which ``ViolationDetector`` classes back each zen rule, along
    with coverage status (``full``, ``partial``, ``none``).  Useful for
    debugging pipeline configuration or auditing detector completeness.

    Attributes:
        out: Destination file path; ``None`` prints to stdout.
        languages: Optional language filter; ``None`` includes all registered
            languages.
        format: Output dialect — ``"terminal"`` for Rich tables or ``"json"``
            for machine-readable export.
    """

    out: str | None
    languages: list[str] | None
    format: Literal["terminal", "json"] | str


class PromptsArgs(Protocol):
    """Structural contract for the ``prompts`` subcommand arguments.

    Drives the prompt-generation pipeline that turns analysis results
    into actionable remediation guidance or structured agent task
    payloads.  The ``mode`` selector chooses between human-readable
    markdown prompts (``"remediation"``), machine-oriented agent task
    JSON (``"agent"``), or both.  Export paths allow writing output to
    disk alongside the terminal rendering.

    Attributes:
        path: File or directory whose violations feed prompt generation.
        language: Explicit language override; ``None`` uses extension detection.
        config: Custom ``zen-config.yaml`` path; ``None`` triggers auto-discovery.
        mode: Generation strategy — ``"remediation"``, ``"agent"``, or ``"both"``.
        export_prompts: Markdown export path for remediation prompts.
        export_agent: JSON export path for agent task payloads.
        severity: Minimum severity threshold; violations below are excluded.
    """

    path: str
    language: str | None
    config: str | None
    mode: Literal["remediation", "agent", "both"]
    export_prompts: str | None
    export_agent: str | None
    severity: int | None


class CheckArgs(Protocol):
    """Structural contract for the ``check`` subcommand arguments."""

    path: str
    language: str | None
    config: str | None
    format: Literal["terminal", "json", "sarif"] | str
    out: str | None
    fail_on_severity: int | None


def _summarize_violations(violations: list) -> RulesSummary:
    """Bucket a list of violation objects into severity tiers.

    Iterates violations and increments one of four counters — *critical*
    (≥ 9), *high* (≥ 7), *medium* (≥ 4), or *low* — then wraps them in a
    [`RulesSummary`][RulesSummary].  Used by [`_filter_result`][_filter_result] to recompute the
    summary after severity filtering.

    Args:
        violations (list): Violation model instances with a ``.severity`` attribute.

    Returns:
        RulesSummary: Four-bucket severity tally ready for report rendering.

    See Also:
        [`_summarize_violation_dicts`][_summarize_violation_dicts]: Equivalent logic for raw dict violations.
    """

    summary = {
        "critical": 0,
        "high": 0,
        "medium": 0,
        "low": 0,
    }
    for violation in violations:
        if violation.severity >= 9:
            summary["critical"] += 1
        elif violation.severity >= 7:
            summary["high"] += 1
        elif violation.severity >= 4:
            summary["medium"] += 1
        else:
            summary["low"] += 1
    return RulesSummary(**summary)


def _summarize_violation_dicts(violations: list[dict]) -> RulesSummary:
    """Bucket dict-shaped violations into the same severity tiers as model objects.

    Legacy and JSON-round-tripped violations arrive as plain dictionaries
    with a ``"severity"`` key.  This function mirrors
    [`_summarize_violations`][_summarize_violations] but reads severity via ``dict.get``
    instead of attribute access.

    Args:
        violations (list[dict]): Dictionary violations with a ``"severity"`` key.

    Returns:
        RulesSummary: Four-bucket severity tally matching the model-based summariser.

    See Also:
        [`_summarize_violations`][_summarize_violations]: Equivalent logic for Pydantic violation models.
    """

    summary = {
        "critical": 0,
        "high": 0,
        "medium": 0,
        "low": 0,
    }
    for violation in violations:
        severity = int(violation.get("severity", 0))
        if severity >= 9:
            summary["critical"] += 1
        elif severity >= 7:
            summary["high"] += 1
        elif severity >= 4:
            summary["medium"] += 1
        else:
            summary["low"] += 1
    return RulesSummary(**summary)


def _filter_result(result: AnalysisResult, min_severity: int | None) -> AnalysisResult:
    """Remove violations below a severity floor and recompute the summary.

    Returns the original result untouched when *min_severity* is ``None``
    or no violations are actually removed, avoiding unnecessary copies.
    Otherwise a shallow ``model_copy`` replaces the violations list and
    recalculates the [`RulesSummary`][RulesSummary].

    Args:
        result (AnalysisResult): Complete single-file analysis to narrow.
        min_severity (int | None): Lower severity bound; ``None`` disables filtering.

    Returns:
        AnalysisResult: Filtered copy (or the original when nothing changed).

    See Also:
        [`_summarize_violations`][_summarize_violations]: Recomputes the rules summary after filtering.
    """

    if min_severity is None:
        return result
    filtered = [v for v in result.violations if v.severity >= min_severity]
    if filtered == result.violations:
        return result
    rules_summary = (
        _summarize_violations(filtered) if result.rules_summary is not None else None
    )
    return result.model_copy(
        update={"violations": filtered, "rules_summary": rules_summary}
    )


def _build_repository_imports(files: list[Path]) -> dict[str, list[str]]:
    """Parse top-level ``import`` and ``from … import`` statements from Python files.

    Cross-file analysis needs to know which modules each file imports so
    the dependency-coupling detector can flag feature-envy and excessive
    coupling.  This lightweight line-based scanner avoids a full AST parse
    because only top-level module names are needed.

    Args:
        files (list[Path]): Python source files to scan for import statements.

    Returns:
        dict[str, list[str]]: Mapping from each file's string path to the
        top-level module names it imports.

    See Also:
        [`_analyze_targets`][_analyze_targets]: Passes this mapping as
        ``repository_imports`` to Python analyzers.
    """

    return _shared_build_repository_imports(files, language="python")


def _placeholder_result(language: str, path: str | None) -> AnalysisResult:
    """Construct a zero-violation stub result for languages without an analyser.

    When the factory cannot build an analyser (e.g. an unrecognised language
    in a mixed-language directory scan), the CLI still needs a valid
    [`AnalysisResult`][AnalysisResult] so downstream aggregation and reporting don't
    crash.  The placeholder carries zeroed metrics and a perfect score.

    Args:
        language (str): Identifier for the unsupported language.
        path (str | None): Source file path to embed in the result, or ``None``.

    Returns:
        AnalysisResult: Clean-slate result with no violations and score 100.

    See Also:
        [`_analyze_targets`][_analyze_targets]: Falls back to this helper when
        ``create_analyzer`` raises ``ValueError``.
    """

    cyclomatic = CyclomaticSummary(blocks=[], average=0.0)
    metrics = Metrics(cyclomatic=cyclomatic, maintainability_index=0.0, lines_of_code=0)
    return AnalysisResult(
        language=language,
        path=path,
        metrics=metrics,
        violations=[],
        overall_score=100.0,
    )


def _collect_targets(
    target: Path, language_override: str | None
) -> list[tuple[Path, str]]:
    """Walk a file or directory and pair each source file with its detected language.

    For a single file, the language is either the explicit override or the
    result of extension-based detection (falling back to ``"python"``).
    For directories, every file is inspected; those matching the override
    (when given) or any recognised extension are included.  Files with
    ``"unknown"`` extensions are silently skipped.

    Args:
        target (Path): File or directory root to scan.
        language_override (str | None): Explicit language to use, bypassing detection.

    Returns:
        list[tuple[Path, str]]: ``(file_path, language)`` pairs ready for
        [`_analyze_targets`][_analyze_targets].

    See Also:
        [`_analyze_targets`][_analyze_targets]: Consumes the target list for batch analysis.
        [`_detect_languages`][_detect_languages]: Uses this function to discover available
        languages in a directory tree.
    """

    return _shared_collect_targets(target, language_override)


def _analyze_targets(
    targets: list[tuple[Path, str]],
    config_path: str | None,
) -> list[AnalysisResult]:
    """Run every file through its language-specific analyser and collect results.

    Groups targets by language so each analyser is created once, loads the
    pipeline config from ``zen-config.yaml``, and feeds files through
    ``create_analyzer``.  A Rich progress bar tracks advancement when
    the file count is positive.  Languages without a registered analyser
    receive [`_placeholder_result`][_placeholder_result] stubs.

    Args:
        targets (list[tuple[Path, str]]): ``(file, language)`` pairs produced by [`_collect_targets`][_collect_targets].
        config_path (str | None): Custom ``zen-config.yaml`` path, or ``None`` for auto-discovery.

    Returns:
        list[AnalysisResult]: One result per input file, preserving target order within
        each language group.

    See Also:
        [`_collect_targets`][_collect_targets]: Builds the target list consumed here.
        [`_build_repository_imports`][_build_repository_imports]: Supplies cross-file import context for
        Python analysis.
    """

    total_files = len(targets)
    with analysis_progress(enabled=total_files > 0) as progress:
        task_id: object | None = None
        if progress:
            task_id = progress.add_task("Analyzing files", total=total_files)

        def _advance_progress() -> None:
            if progress and task_id is not None:
                progress.advance(task_id)

        return _shared_analyze_targets(
            targets,
            config_path=config_path,
            unsupported_language="placeholder",
            progress_callback=_advance_progress if total_files > 0 else None,
        )


def _build_log_summary(report: object) -> str:
    """Flatten a report's structured data into a compact key-value log string.

    Extracts the target path, language list, file/violation counts, and
    severity breakdown from the report's ``.data`` dict.  The output is
    designed for ``--export-log`` consumers that want a grep-friendly
    summary rather than full JSON.

    Args:
        report (object): Report object exposing a ``.data`` dict with summary statistics.

    Returns:
        str: Newline-delimited ``key: value`` text ending with a trailing newline.

    See Also:
        [`_run_report`][_run_report]: Writes this string when ``--export-log`` is specified.
    """

    data = getattr(report, "data", {})
    if not isinstance(data, dict):
        return "target: n/a\nlanguages: n/a\n"
    target = data.get("target", "n/a")
    languages = data.get("languages")
    if not isinstance(languages, list):
        languages = []
    lines = [
        f"target: {target}",
        f"languages: {', '.join(languages) if languages else 'n/a'}",
    ]
    summary = data.get("summary")
    if isinstance(summary, dict):
        lines.append(f"total_files: {summary.get('total_files', 0)}")
        lines.append(f"total_violations: {summary.get('total_violations', 0)}")
        counts = summary.get("severity_counts", {})
        if isinstance(counts, dict):
            lines.append(f"critical: {counts.get('critical', 0)}")
            lines.append(f"high: {counts.get('high', 0)}")
            lines.append(f"medium: {counts.get('medium', 0)}")
            lines.append(f"low: {counts.get('low', 0)}")
    return "\n".join(lines) + "\n"


def _aggregate_results(results: list[AnalysisResult]) -> ProjectSummary:
    """Roll up per-file analysis results into a project-wide summary.

    Counts unique file paths, totals violations, buckets severities, and
    ranks the five worst-offender files by violation count.  The resulting
    [`ProjectSummary`][ProjectSummary] feeds both the terminal report header and the
    JSON export's ``summary`` block.

    Args:
        results (list[AnalysisResult]): Per-file results to aggregate across the project.

    Returns:
        ProjectSummary: Totals, severity breakdown, and top-five worst offenders.
    """

    severity_counts = SeverityCounts()
    offenders: list[WorstOffender] = []
    unique_paths: set[str] = set()
    total_violations = 0
    for result in results:
        path = result.path or "<input>"
        unique_paths.add(path)
        violation_count = len(result.violations)
        total_violations += violation_count
        offenders.append(
            WorstOffender(
                path=path,
                violations=violation_count,
                language=result.language,
            )
        )
        for violation in result.violations:
            if violation.severity >= 9:
                severity_counts.critical += 1
            elif violation.severity >= 7:
                severity_counts.high += 1
            elif violation.severity >= 4:
                severity_counts.medium += 1
            else:
                severity_counts.low += 1
    offenders.sort(key=lambda offender: offender.violations, reverse=True)
    return ProjectSummary(
        total_files=len(unique_paths),
        total_violations=total_violations,
        severity_counts=severity_counts,
        worst_offenders=offenders[:5],
    )


def _format_prompt_markdown(bundle: PromptBundle) -> str:
    """Convert a [`PromptBundle`][PromptBundle] into a normalised markdown document.

    Assembles a ``# Remediation Prompts`` document with roadmap steps,
    health-score metadata, per-file prompts, and generic guidance sections.
    The final text is passed through [`normalize_markdown`][normalize_markdown] to ensure
    consistent heading spacing and trailing newlines.

    Args:
        bundle (PromptBundle): Aggregated remediation prompts and big-picture analysis.

    Returns:
        str: Markdown text ready for file export or clipboard.

    See Also:
        [`_run_prompts`][_run_prompts]: Calls this when ``--export-prompts`` is set.
    """

    lines = ["# Remediation Prompts", ""]
    if bundle.big_picture:
        lines.append("## Remediation Roadmap")
        if bundle.big_picture.refactoring_roadmap:
            lines.extend(
                [f"- {step}" for step in bundle.big_picture.refactoring_roadmap]
            )
        else:
            lines.append("- No roadmap available.")
        lines.append("")
        lines.append("## Big Picture")
        lines.append(f"- Health score: {bundle.big_picture.health_score:.1f}/100")
        lines.append(f"- Trajectory: {bundle.big_picture.improvement_trajectory}")
        if bundle.big_picture.systemic_patterns:
            lines.append("- Systemic patterns:")
            lines.extend(
                [f"  - {pattern}" for pattern in bundle.big_picture.systemic_patterns]
            )
        lines.append("")
    if bundle.file_prompts:
        lines.append("## File Prompts")
        for prompt in bundle.file_prompts:
            lines.append(prompt.prompt.strip())
            lines.append("")
    else:
        lines.extend(["## File Prompts", "- No file-specific prompts generated.", ""])
    if bundle.generic_prompts:
        lines.append("## Generic Prompts")
        for prompt in bundle.generic_prompts:
            lines.append(f"### {prompt.title}")
            lines.extend(prompt.prompt.strip().splitlines())
            lines.append("")
    else:
        lines.extend(["## Generic Prompts", "- No generic prompts available."])
    return normalize_markdown("\n".join(lines))


def _render_prompt_panel(bundle: PromptBundle, results: list[AnalysisResult]) -> None:
    """Delegate prompt rendering to the ``reporting.terminal`` module.

    Thin wrapper that keeps the CLI layer decoupled from the rendering
    implementation.  The Rich panel displays the big-picture roadmap and
    per-file prompts side by side with analysis scores.

    Args:
        bundle (PromptBundle): Remediation prompts and big-picture insights to display.
        results (list[AnalysisResult]): Companion analysis results providing score context.

    See Also:
        [`_run_prompts`][_run_prompts]: Invokes this for terminal output in remediation mode.
    """

    render_prompt_panel(bundle, results)


def _build_agent_tasks_table(task_list: AgentTaskList) -> Table:
    """Delegate agent-task table construction to the reporting terminal module.

    Wraps ``render_agent_tasks_table`` so the CLI can build a Rich
    [`Table`][Table] of prioritised agent tasks without importing the
    rendering module at the top level.

    Args:
        task_list (AgentTaskList): Structured list of agent tasks with severity and file context.

    Returns:
        Table: Rich ``Table`` renderable listing tasks by priority.

    See Also:
        [`_run_prompts`][_run_prompts]: Prints this table when running in ``"agent"`` or
        ``"both"`` mode.
    """

    return render_agent_tasks_table(task_list)


def _resolve_prompt_export_path(export: str | None) -> Path | None:
    """Convert an optional export path string into a [`Path`][Path] or ``None``.

    Unlike some export helpers, this function intentionally does **not**
    auto-rename colliding files — the caller is expected to handle
    overwrite semantics.

    Args:
        export (str | None): Raw CLI path string, or ``None`` when export is disabled.

    Returns:
        Path | None: Resolved path, or ``None`` when *export* is falsy.
    """

    if not export:
        return None
    return Path(export)


def _run_prompts(args: PromptsArgs) -> int:
    """Orchestrate prompt generation from file discovery through export.

    Validates the target path, collects analysable files, runs the analysis
    pipeline, and then branches on *mode*: ``"remediation"`` builds a
    [`PromptBundle`][PromptBundle] rendered as a Rich panel and optionally exported
    as markdown; ``"agent"`` builds an [`AgentTaskList`][AgentTaskList] rendered as a
    table and optionally exported as JSON; ``"both"`` does both.

    Args:
        args (PromptsArgs): Parsed CLI options carrying path, mode, and export paths.

    Returns:
        int: Exit code — ``0`` on success, ``2`` when the target is missing or empty.

    See Also:
        [`prompts`][prompts]: Typer command that delegates here.
        [`_collect_targets`][_collect_targets]: Discovers analysable files.
        [`_analyze_targets`][_analyze_targets]: Runs the detector pipeline.
    """

    target = Path(args.path)
    if not target.exists():
        print_error(f"Path not found: {target}")
        return 2
    targets = _collect_targets(target, args.language)
    if not targets:
        print_error("No analyzable files found.")
        return 2
    results = _analyze_targets(targets, args.config)
    if args.severity is not None:
        results = [_filter_result(result, args.severity) for result in results]

    mode = args.mode
    prompt_path = _resolve_prompt_export_path(args.export_prompts)
    agent_path = _resolve_prompt_export_path(args.export_agent)

    if mode in ("remediation", "both"):
        prompt_bundle = build_prompt_bundle(results)
        if not is_quiet():
            _render_prompt_panel(prompt_bundle, results)
        if prompt_path:
            prompt_path.write_text(
                _format_prompt_markdown(prompt_bundle), encoding="utf-8"
            )

    if mode in ("agent", "both"):
        min_severity = args.severity or 1
        task_list = build_agent_tasks(
            results, project=str(target), min_severity=min_severity
        )
        if not is_quiet():
            console.print(_build_agent_tasks_table(task_list))
        if agent_path:
            agent_path.write_text(
                json.dumps(task_list.model_dump(), indent=2), encoding="utf-8"
            )

    return 0


def _run_list_rules(args: ListRulesArgs) -> int:
    """Render a severity-badge table of zen principles for the requested language.

    Loads the zen definition via [`get_language_zen`][get_language_zen], prints a header
    panel with the principle count, and fills a three-column Rich table
    (ID, severity badge, principle text).  Returns exit code ``2`` when the
    language is not recognised.

    Args:
        args (ListRulesArgs): Parsed CLI options carrying the language identifier.

    Returns:
        int: Exit code — ``0`` on success, ``2`` for unsupported languages.

    See Also:
        [`list_rules`][list_rules]: Typer command that delegates here.
    """

    zen = get_language_zen(args.language)
    if not zen:
        print_error(f"Unsupported language: {args.language}")
        return 2
    console.print(
        zen_header_panel(
            f"{file_glyph()} Language: {args.language}",
            f"Principles: {len(zen.principles)}",
            title="Zen Rules",
        )
    )
    table = zen_table(title=f"Rules - {args.language}")
    table.add_column("ID", width=14, no_wrap=True)
    table.add_column("Sev", width=12, justify="center")
    table.add_column("Principle", ratio=1, no_wrap=True, overflow="ellipsis")
    for principle in zen.principles:
        table.add_row(
            principle.id,
            severity_badge(principle.severity),
            principle.principle,
        )
    console.print(table)
    return 0


def _run_init_interactive(args: InitArgs) -> tuple[list[str], str, bool]:
    """Drive the interactive Rich-prompt wizard for ``zen init``.

    Presents detected languages for confirmation, asks the user to pick a
    strictness preset, and offers to generate a ``.vscode/mcp.json``.
    Pre-supplied ``args.languages`` short-circuit the detection question.

    Args:
        args (InitArgs): Parsed CLI options seeding the wizard defaults.

    Returns:
        tuple[list[str], str, bool]: ``(languages, strictness, setup_vscode)``
        triple consumed by [`_run_init`][_run_init].

    See Also:
        [`_run_init`][_run_init]: Calls this helper when stdin is a TTY and
        ``--yes`` was not passed.
    """

    from rich.prompt import Confirm, Prompt

    detected = _detect_languages(Path.cwd())
    languages = args.languages
    if languages is None:
        detected_list = ", ".join(detected)
        use_detected = Confirm.ask(
            f"Detected languages: {detected_list}. Use these?", default=True
        )
        if use_detected:
            languages = detected
        else:
            response = Prompt.ask(
                "Enter languages (comma-separated)", default=detected_list
            )
            languages = _parse_languages(response)
    strictness = Prompt.ask(
        "Select strictness",
        choices=list(_THRESHOLDS.keys()),
        default=_normalize_strictness(args.strictness),
    )
    setup_vscode = Confirm.ask(
        "Create .vscode/mcp.json for VS Code integration?", default=True
    )
    return (languages or detected), strictness, setup_vscode


def _run_init(args: InitArgs) -> int:
    """Scaffold a ``zen-config.yaml`` (and optional VS Code config) to disk.

    Refuses to overwrite an existing config unless ``--force`` is set.
    In headless mode (``--yes`` or non-TTY stdin) detected defaults are
    used directly; otherwise the interactive wizard collects preferences.
    A summary panel is printed to confirm what was written.

    Args:
        args (InitArgs): Parsed CLI options controlling overwrite, headless, language, and strictness.

    Returns:
        int: Exit code — ``0`` on success, ``2`` when a config already exists.

    See Also:
        [`init`][init]: Typer command that delegates here.
        [`_run_init_interactive`][_run_init_interactive]: Collects user preferences interactively.
        [`_build_config_yaml`][_build_config_yaml]: Generates the YAML body.
    """

    target = Path("zen-config.yaml")
    if target.exists() and not args.force:
        print_error("zen-config.yaml already exists (use --force to overwrite).")
        return 2
    if args.yes or not sys.stdin.isatty():
        languages = args.languages or _detect_languages(Path.cwd())
        strictness = _normalize_strictness(args.strictness)
        setup_vscode = False
    else:
        languages, strictness, setup_vscode = _run_init_interactive(args)

    config_text = _build_config_yaml(languages, _normalize_strictness(strictness))
    target.write_text(config_text, encoding="utf-8")
    if setup_vscode:
        _write_vscode_mcp_config()
    if not is_quiet():
        details = [
            f"{file_glyph()} Config: {target}",
            f"Languages: {', '.join(languages)}",
            f"Strictness: {strictness}",
        ]
        if setup_vscode:
            details.append("VS Code MCP config: .vscode/mcp.json")
        console.print(zen_header_panel(*details, title="Zen Init"))
    return 0


def _render_report_output(report, fmt: str) -> str:
    """Serialise a report object into the format selected by ``--format``.

    ``"json"`` returns indented JSON of the report's ``.data`` dict,
    ``"markdown"`` returns the pre-rendered ``.markdown`` text, and
    ``"both"`` wraps both into a single JSON envelope.

    Args:
        report (object): Report object exposing ``.data`` and ``.markdown`` attributes.
        fmt (str): Format selector — ``"json"``, ``"markdown"``, or ``"both"``.

    Returns:
        str: Rendered report body ready for file or terminal output.

    See Also:
        [`_run_report`][_run_report]: Uses this when ``--out`` is specified.
    """

    if fmt == "json":
        return json.dumps(report.data, indent=2)
    if fmt == "sarif":
        analysis = report.data.get("analysis", [])
        if not isinstance(analysis, list):
            raise ValueError("Report analysis payload must be a list for SARIF output.")
        if any(not isinstance(item, dict) for item in analysis):
            raise ValueError(
                "Report analysis entries must be objects for SARIF output."
            )
        analysis_results = [AnalysisResult.model_validate(item) for item in analysis]
        return json.dumps(analysis_results_to_sarif(analysis_results), indent=2)
    if fmt == "markdown":
        return report.markdown
    payload = {"markdown": report.markdown, "data": report.data}
    return json.dumps(payload, indent=2)


def _run_check(args: CheckArgs) -> int:
    """Analyze target files and optionally fail CI based on severity threshold.

    Returns:
        int: Exit code ``0`` on success, ``1`` when violations exceed
        ``--fail-on-severity``, and ``2`` for input errors.
    """

    target = Path(args.path)
    if not target.exists():
        print_error(f"Path not found: {target}")
        return 2

    targets = _collect_targets(target, args.language)
    if not targets:
        print_error("No analyzable files found.")
        return 2

    results = _analyze_targets(targets, args.config)
    rendered: str | None = None
    if args.format == "json":
        rendered = json.dumps([result.model_dump() for result in results], indent=2)
    elif args.format == "sarif":
        rendered = json.dumps(analysis_results_to_sarif(results), indent=2)

    if args.out and rendered is not None:
        Path(args.out).write_text(rendered, encoding="utf-8")
    elif rendered is not None:
        print(rendered)

    if args.fail_on_severity is not None:
        has_blocking = any(
            violation.severity >= args.fail_on_severity
            for result in results
            for violation in result.violations
        )
        if has_blocking:
            if args.format == "terminal":
                print_error(
                    "Analysis failed: found violations meeting "
                    f"--fail-on-severity={args.fail_on_severity}. "
                    "Use --format json or --format sarif for detailed output."
                )
            return 1
    return 0


def _run_report(args: ReportArgs) -> int:
    """Execute the full report pipeline from target validation to output.

    Validates the target path, delegates to ``generate_report`` for the
    heavy lifting, then dispatches exports (JSON, markdown, log) and
    renders the final output to a file or the terminal depending on
    ``--out``.

    Args:
        args (ReportArgs): Parsed CLI options carrying path, format, and export toggles.

    Returns:
        int: Exit code — ``0`` on success, ``2`` for missing paths or no files.

    See Also:
        [`reports`][reports]: Typer command that delegates here.
        [`_render_report_output`][_render_report_output]: Serialises the report for ``--out``.
        [`_build_log_summary`][_build_log_summary]: Generates compact log text for ``--export-log``.
    """

    from mcp_zen_of_languages.reporting.report import generate_report

    target = Path(args.path)
    if not target.exists():
        print_error(f"Path not found: {target}")
        return 2
    if not _collect_targets(target, args.language):
        print_error("No analyzable files found.")
        return 2

    report = generate_report(
        str(target),
        config_path=args.config,
        language=args.language,
        include_prompts=args.include_prompts,
        include_analysis=not args.skip_analysis,
        include_gaps=not args.skip_gaps,
    )

    export_json = getattr(args, "export_json", None)
    export_markdown = getattr(args, "export_markdown", None)
    export_log = getattr(args, "export_log", None)

    if export_json:
        Path(export_json).write_text(
            json.dumps(report.data, indent=2), encoding="utf-8"
        )
    if export_markdown:
        Path(export_markdown).write_text(report.markdown, encoding="utf-8")
    if export_log:
        Path(export_log).write_text(_build_log_summary(report), encoding="utf-8")

    if args.out:
        output = _render_report_output(report, args.format)
        Path(args.out).write_text(output, encoding="utf-8")
    else:
        render_report_terminal(report)
    return 0


def _run_export_mapping(args: ExportMappingArgs) -> int:
    """Build and display the rule-to-detector mapping for registered languages.

    When ``--out`` is set, the mapping is written as JSON and the function
    returns immediately.  ``--format json`` prints JSON to stdout.  The
    default ``terminal`` mode renders a Rich header panel with aggregate
    counts and a per-language coverage table showing full/partial/none
    detector coverage for each rule.

    Args:
        args (ExportMappingArgs): Parsed CLI options with output path, language filter, and format.

    Returns:
        int: Exit code — always ``0``.

    See Also:
        [`export_mapping`][export_mapping]: Typer command that delegates here.
    """

    from mcp_zen_of_languages.rules.mapping_export import (
        build_rule_detector_mapping,
        export_mapping_json,
    )

    payload = build_rule_detector_mapping(args.languages)
    if args.out:
        export_mapping_json(args.out, args.languages)
        return 0
    if args.format == "json":
        print(json.dumps(payload, indent=2))
        return 0
    languages_payload = payload.get("languages", {})
    if not isinstance(languages_payload, dict):
        languages_payload = {}
    total_rules = 0
    total_detectors = 0
    coverage_totals: Counter[str] = Counter()
    for language_data in languages_payload.values():
        if not isinstance(language_data, dict):
            continue
        total_rules += int(language_data.get("rules_count", 0))
        total_detectors += int(language_data.get("detectors_count", 0))
        mapping = language_data.get("mapping", {})
        if isinstance(mapping, dict):
            for rule_meta in mapping.values():
                if isinstance(rule_meta, dict):
                    coverage = str(rule_meta.get("coverage", "unknown"))
                    coverage_totals[coverage] += 1
    console.print(
        zen_header_panel(
            f"Languages: {len(languages_payload)}",
            f"Rules: {total_rules}",
            f"Detectors: {total_detectors}",
            (
                f"Coverage buckets: full={coverage_totals.get('full', 0)}, "
                f"partial={coverage_totals.get('partial', 0)}, "
                f"none={coverage_totals.get('none', 0)}"
            ),
            title="Rule Detector Mapping",
        )
    )
    table = zen_table(title="Language Coverage")
    table.add_column("Language", style="metric", no_wrap=True)
    table.add_column("Counts", ratio=1)
    table.add_column("Coverage", ratio=1)
    for language in sorted(languages_payload):
        language_data = languages_payload.get(language, {})
        if not isinstance(language_data, dict):
            language_data = {}
        mapping = (
            language_data.get("mapping", {}) if isinstance(language_data, dict) else {}
        )
        coverage_counts: Counter[str] = Counter()
        if isinstance(mapping, dict):
            for rule_meta in mapping.values():
                if isinstance(rule_meta, dict):
                    coverage_counts[str(rule_meta.get("coverage", "unknown"))] += 1
        table.add_row(
            language,
            (
                f"rules={int(language_data.get('rules_count', 0))}, "
                f"detectors={int(language_data.get('detectors_count', 0))}"
            ),
            (
                f"full={coverage_counts.get('full', 0)}, "
                f"partial={coverage_counts.get('partial', 0)}, "
                f"none={coverage_counts.get('none', 0)}"
            ),
        )
    console.print(table)
    return 0


@app.command("reports", rich_help_panel="Analysis")
def reports(
    path: str = typer.Argument(..., help="File or directory to analyze"),
    language: str | None = typer.Option(None, help="Override language detection"),
    config: str | None = typer.Option(None, help="Path to zen-config.yaml"),
    format: Literal["markdown", "json", "both", "sarif"] = typer.Option(
        "markdown", help="Output format", show_choices=True
    ),
    out: str | None = typer.Option(None, help="Write output to file"),
    export_json: str | None = typer.Option(
        None, "--export-json", help="Write report JSON to file"
    ),
    export_markdown: str | None = typer.Option(
        None, "--export-markdown", help="Write report markdown to file"
    ),
    export_log: str | None = typer.Option(
        None, "--export-log", help="Write log summary to file"
    ),
    include_prompts: bool = typer.Option(
        False, "--include-prompts", help="Include remediation prompts"
    ),
    skip_analysis: bool = typer.Option(
        False, "--skip-analysis", help="Skip analysis details in report"
    ),
    skip_gaps: bool = typer.Option(False, "--skip-gaps", help="Skip gap analysis"),
) -> int:
    """Generate a comprehensive analysis report for a file or directory.

    Analyses every recognised source file under *path*, groups violations
    by severity, and renders the output as markdown, JSON, or both.
    Sidecar exports (``--export-json``, ``--export-markdown``,
    ``--export-log``) can be written independently of the primary output.
    Section toggles let callers skip analysis details or gap analysis to
    keep reports compact.

    Args:
        path (str): File or directory to analyse — directories are walked recursively.
        language (str | None): Override extension-based language detection.
        config (str | None): Path to a custom ``zen-config.yaml``; auto-discovered when omitted.
        format (Literal['markdown', 'json', 'both']): Primary output serialisation format.
        out (str | None): Write the rendered report to this file instead of stdout.
        export_json (str | None): Sidecar path for the raw JSON data export.
        export_markdown (str | None): Sidecar path for the rendered markdown export.
        export_log (str | None): Sidecar path for a compact key-value log summary.
        include_prompts (bool): Append remediation prompt text to the report body.
        skip_analysis (bool): Omit the per-file analysis details chapter.
        skip_gaps (bool): Omit the gap-analysis chapter.

    Returns:
        int: Process exit code — ``0`` on success, ``2`` on input errors.

    See Also:
        [`_run_report`][_run_report]: Contains the actual report orchestration logic.
    """

    args = _ns(
        path=path,
        language=language,
        config=config,
        format=format,
        out=out,
        export_json=export_json,
        export_markdown=export_markdown,
        export_log=export_log,
        include_prompts=include_prompts,
        skip_analysis=skip_analysis,
        skip_gaps=skip_gaps,
    )
    return _run_report(args)


app.command("report", hidden=True, rich_help_panel="Analysis")(reports)


@app.command("check", rich_help_panel="Analysis")
def check(
    path: str = typer.Argument(..., help="File or directory to analyze"),
    language: str | None = typer.Option(None, help="Override language detection"),
    config: str | None = typer.Option(None, help="Path to zen-config.yaml"),
    format: Literal["terminal", "json", "sarif"] = typer.Option(
        "terminal", help="Output format", show_choices=True
    ),
    out: str | None = typer.Option(None, help="Write output to file"),
    fail_on_severity: int | None = typer.Option(
        None,
        "--fail-on-severity",
        min=1,
        max=10,
        help="Exit with code 1 when any violation has severity >= this threshold",
    ),
) -> int:
    """Run zen analysis for a path with optional CI gating and machine output.

    Args:
        path (str): File or directory to analyze.
        language (str | None): Optional language override.
        config (str | None): Optional path to ``zen-config.yaml``.
        format (Literal["terminal", "json", "sarif"]): Output format.
        out (str | None): Optional file path for output payload.
        fail_on_severity (int | None): Exit with code ``1`` when any
            violation has severity greater than or equal to this threshold.

    Returns:
        int: Exit code ``0`` on success, ``1`` for severity-gated failure,
        and ``2`` for input/target errors.
    """

    args = _ns(
        path=path,
        language=language,
        config=config,
        format=format,
        out=out,
        fail_on_severity=fail_on_severity,
    )
    return _run_check(args)


@app.command("prompts", rich_help_panel="Analysis")
def prompts(
    path: str = typer.Argument(..., help="File or directory to analyze"),
    language: str | None = typer.Option(None, help="Override language detection"),
    config: str | None = typer.Option(None, help="Path to zen-config.yaml"),
    mode: Literal["remediation", "agent", "both"] = typer.Option(
        "remediation", help="Prompt generation mode", show_choices=True
    ),
    export_prompts: str | None = typer.Option(
        None, "--export-prompts", help="Write prompts markdown to file"
    ),
    export_agent: str | None = typer.Option(
        None, "--export-agent", help="Write agent JSON to file"
    ),
    severity: int | None = typer.Option(None, help="Minimum severity threshold"),
) -> int:
    """Turn analysis violations into actionable remediation prompts or agent tasks.

    Runs the full analysis pipeline on *path*, then generates either
    human-readable remediation markdown, structured agent-task JSON, or
    both.  Results can be rendered to the terminal, exported to disk, or
    both — depending on the mode and export flags.

    Args:
        path (str): File or directory whose violations drive prompt generation.
        language (str | None): Override extension-based language detection.
        config (str | None): Path to a custom ``zen-config.yaml``; auto-discovered when omitted.
        mode (Literal['remediation', 'agent', 'both']): Which prompt artefact to produce.
        export_prompts (str | None): Write remediation markdown to this path.
        export_agent (str | None): Write agent-task JSON to this path.
        severity (int | None): Exclude violations below this severity threshold.

    Returns:
        int: Process exit code — ``0`` on success, ``2`` on input errors.

    See Also:
        [`_run_prompts`][_run_prompts]: Contains the actual prompt orchestration logic.
    """

    args = _ns(
        path=path,
        language=language,
        config=config,
        mode=mode,
        export_prompts=export_prompts,
        export_agent=export_agent,
        severity=severity,
    )
    return _run_prompts(args)


app.command("prompt", hidden=True, rich_help_panel="Analysis")(prompts)


@app.command("list-rules", rich_help_panel="Configuration")
def list_rules(language: str = typer.Argument(..., help="Language identifier")) -> int:
    """Display a table of zen rule IDs, severities, and principle texts.

    Loads the canonical zen definition for *language* and renders each
    principle as a row with a colour-coded severity badge, making it
    easy to audit which rules are active and how severe they are.

    Args:
        language (str): Language whose zen principles should be listed (e.g. ``"python"``).

    Returns:
        int: Process exit code — ``0`` on success, ``2`` if the language is unknown.

    See Also:
        [`_run_list_rules`][_run_list_rules]: Contains the table-building logic.
    """

    args = _ns(language=language)
    return _run_list_rules(args)


@app.command(rich_help_panel="Configuration")
def init(
    force: bool = typer.Option(False, "--force", help="Overwrite existing config"),
    yes: bool = typer.Option(False, "--yes", help="Skip prompts and use defaults"),
    languages: list[str] | None = typer.Option(
        None, "--languages", help="Languages to include (repeatable)"
    ),
    strictness: Literal["relaxed", "moderate", "strict"] = typer.Option(
        "moderate",
        help="Strictness: relaxed|moderate|strict",
        show_choices=True,
    ),
) -> int:
    """Interactively scaffold a ``zen-config.yaml`` and optional VS Code integration.

    Walks the user through language selection, strictness presets, and
    editor integration choices.  With ``--yes`` or in non-interactive
    terminals the wizard is skipped and detected defaults are used.  Pass
    ``--force`` to overwrite an existing config file.

    Args:
        force (bool): Allow overwriting an existing ``zen-config.yaml``.
        yes (bool): Accept all defaults without interactive prompts.
        languages (list[str] | None): Pre-selected languages; ``None`` triggers auto-detection.
        strictness (Literal['relaxed', 'moderate', 'strict']): Severity threshold preset.

    Returns:
        int: Process exit code — ``0`` on success, ``2`` if the file exists without ``--force``.

    See Also:
        [`_run_init`][_run_init]: Contains the file-writing orchestration.
    """

    args = _ns(
        force=force,
        yes=yes,
        languages=languages,
        strictness=strictness,
    )
    return _run_init(args)


@app.command("export-mapping", rich_help_panel="Configuration")
def export_mapping(
    out: str | None = typer.Option(None, help="Write output to file"),
    languages: list[str] | None = typer.Option(
        None, "--languages", help="Filter by languages"
    ),
    format: Literal["terminal", "json"] = typer.Option(
        "terminal", help="Output format", show_choices=True
    ),
) -> int:
    """Export rule-to-detector mappings as a Rich table or JSON payload.

    Shows which ``ViolationDetector`` backs each zen rule and the
    coverage level (``full``, ``partial``, ``none``).  Useful for
    pipeline debugging and verifying that new detectors are correctly
    registered.

    Args:
        out (str | None): Write JSON mapping to this file and exit.
        languages (list[str] | None): Restrict output to these languages; ``None`` includes all.
        format (Literal['terminal', 'json']): Output style — Rich table or raw JSON.

    Returns:
        int: Process exit code — always ``0``.

    See Also:
        [`_run_export_mapping`][_run_export_mapping]: Contains the mapping-build and rendering logic.
    """

    args = _ns(out=out, languages=languages, format=format)
    return _run_export_mapping(args)


def main(argv: list[str] | None = None) -> int:
    """Top-level CLI entry point invoked by the ``zen`` console script.

    With no arguments the welcome panel is displayed and the process exits
    cleanly.  Otherwise *argv* is forwarded to the Typer :pydata:`app`
    instance.  All Typer and Click exceptions are caught so the function
    always returns a numeric exit code rather than raising.

    Args:
        argv (list[str] | None): Command-line tokens; defaults to ``sys.argv[1:]``.

    Returns:
        int: Process exit code — ``0`` for success, non-zero on errors.

    See Also:
        ``_build_welcome_panel``: Rendered when no arguments are supplied.
    """

    if argv is None:
        argv = sys.argv[1:]
    if not argv:
        if not is_quiet():
            _build_welcome_panel()
        return 0
    try:
        result = app(args=argv, prog_name="zen", standalone_mode=False)
    except typer.Exit as exc:
        return exc.exit_code
    except click.ClickException as exc:
        exc.show()
        raise SystemExit(exc.exit_code) from exc
    except SystemExit as exc:
        return int(exc.code) if isinstance(exc.code, int) else 1
    return result if isinstance(result, int) else 0


if __name__ == "__main__":
    raise SystemExit(main())
