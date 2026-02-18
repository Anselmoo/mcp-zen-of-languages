"""Report generation orchestrator that drives the full analysis-to-Markdown pipeline.

``generate_report`` is the primary entry point.  It accepts a filesystem path
(file or directory), discovers analysable targets by extension, runs the
appropriate language analyzers, and assembles the results into a ``ReportOutput``
containing both a normalised Markdown document and a serialised data dict.

Orchestration stages:

1. **Target collection** — ``_collect_targets`` recursively discovers source
   files and detects their languages, optionally filtered by a language override.
2. **Batch analysis** — ``_analyze_targets`` groups files by language, creates
   analyzers via the factory, and collects ``AnalysisResult`` objects.  For
   Python targets, repository-level import maps are built to enable cross-file
   dependency analysis.
3. **Summarisation** — ``_summarize_results`` computes aggregate violation
   counts bucketed by severity.
4. **Gap analysis** — ``gaps.build_gap_analysis`` identifies missing detector
   coverage (optional, controlled by ``include_gaps``).
5. **Prompt generation** — ``prompts.build_prompt_bundle`` produces remediation
   prompts (optional, controlled by ``include_prompts``).
6. **Markdown rendering** — A series of ``_format_*_markdown`` helpers convert
   each section into Markdown table fragments, which are joined and normalised.

See Also:
    ``reporting.terminal``: Alternative Rich-based rendering for interactive use.
    ``reporting.models.ReportOutput``: Final output model carrying Markdown and data.
"""

from __future__ import annotations

from pathlib import Path

from mcp_zen_of_languages.models import AnalysisResult
from mcp_zen_of_languages.orchestration import (
    analyze_targets as _shared_analyze_targets,
)
from mcp_zen_of_languages.orchestration import (
    build_repository_imports as _shared_build_repository_imports,
)
from mcp_zen_of_languages.orchestration import (
    collect_targets as _shared_collect_targets,
)
from mcp_zen_of_languages.reporting.gaps import build_gap_analysis
from mcp_zen_of_languages.reporting.models import (
    AnalysisSummary,
    GapAnalysis,
    ReportContext,
    ReportOutput,
)
from mcp_zen_of_languages.reporting.prompts import build_prompt_bundle
from mcp_zen_of_languages.utils.markdown_quality import normalize_markdown


def _collect_targets(
    target: Path, language_override: str | None
) -> list[tuple[Path, str]]:
    """Discover analysable source files under a target path.

    For a single file, the language is either overridden explicitly or detected
    by extension.  For a directory, all files are recursively scanned; unknown
    extensions are skipped unless a language override is active.

    Args:
        target: Filesystem path (file or directory) to scan.
        language_override: When set, only files matching this language are collected.

    Returns:
        list[tuple[Path, str]]: Pairs of ``(file_path, language)`` ready for analysis.
    """

    return _shared_collect_targets(target, language_override)


def _analyze_targets(
    targets: list[tuple[Path, str]],
    config_path: str | None,
) -> list[AnalysisResult]:
    """Run language-specific analyzers across a batch of file targets.

    Files are grouped by language so that each analyzer is instantiated once.
    For Python targets, a repository-level import map is computed to support
    cross-file dependency detectors.  Languages with no registered analyzer
    are silently skipped.

    Args:
        targets: ``(path, language)`` pairs produced by ``_collect_targets``.
        config_path: Optional path to a ``zen-config.yaml`` override.

    Returns:
        list[AnalysisResult]: Per-file analysis results with violations and metrics.
    """

    return _shared_analyze_targets(targets, config_path=config_path)


def _build_repository_imports(files: list[Path]) -> dict[str, list[str]]:
    """Build a mapping from Python file paths to their top-level import roots.

    This lightweight import scanner extracts the first dotted component of
    every ``import`` and ``from … import`` statement, giving cross-file
    dependency detectors a repository-level view of module usage.

    Args:
        files: Python source files to scan for import statements.

    Returns:
        dict[str, list[str]]: Mapping from file path string to imported root module names.
    """

    return _shared_build_repository_imports(files, language="python")


def _summarize_results(results: list[AnalysisResult]) -> AnalysisSummary:
    """Compute aggregate violation counts from a batch of analysis results.

    Violations are bucketed into four severity tiers: *critical* (≥ 9),
    *high* (≥ 7), *medium* (≥ 4), and *low* (< 4).  The total file count
    is derived from unique ``path`` values across all results.

    Args:
        results: Analysis results spanning one or more files and languages.

    Returns:
        AnalysisSummary: Total files, total violations, and severity bucket counts.
    """

    severity_counts = {"critical": 0, "high": 0, "medium": 0, "low": 0}
    total_violations = 0
    for result in results:
        for violation in result.violations:
            total_violations += 1
            if violation.severity >= 9:
                severity_counts["critical"] += 1
            elif violation.severity >= 7:
                severity_counts["high"] += 1
            elif violation.severity >= 4:
                severity_counts["medium"] += 1
            else:
                severity_counts["low"] += 1
    unique_paths = {r.path or f"<input:{idx}>" for idx, r in enumerate(results)}
    return AnalysisSummary(
        total_files=len(unique_paths),
        total_violations=total_violations,
        severity_counts=severity_counts,
    )


def _markdown_table(headers: list[str], rows: list[list[str]]) -> list[str]:
    """Render a pipe-delimited Markdown table from headers and row data.

    Args:
        headers: Column header labels for the table.
        rows: List of row values, each list matching the header count.

    Returns:
        list[str]: Markdown lines including the header, separator, and data rows.
    """

    header = "| " + " | ".join(headers) + " |"
    separator = "| " + " | ".join(["---"] * len(headers)) + " |"
    lines = [header, separator]
    lines.extend("| " + " | ".join(row) + " |" for row in rows)
    return lines


def _format_summary_markdown(summary: AnalysisSummary) -> list[str]:
    """Format the analysis summary as a Markdown table under a ``## Summary`` heading.

    Args:
        summary: Aggregated violation counts to render.

    Returns:
        list[str]: Markdown lines for the summary section.
    """

    counts = summary.severity_counts
    rows = [
        ["Total files", str(summary.total_files)],
        ["Total violations", str(summary.total_violations)],
        ["Critical", str(counts.get("critical", 0))],
        ["High", str(counts.get("high", 0))],
        ["Medium", str(counts.get("medium", 0))],
        ["Low", str(counts.get("low", 0))],
    ]
    lines = ["## Summary"]
    lines.extend(_markdown_table(["Metric", "Value"], rows))
    return lines


def _format_gap_markdown(gaps: GapAnalysis) -> list[str]:
    """Format detector and feature gaps as a Markdown table under ``## Gap Analysis``.

    Each detector gap shows the language, rule ID, severity, principle text, and
    reason.  Each feature gap shows the functional area, description, and
    suggested next step.

    Args:
        gaps: Combined gap analysis to render.

    Returns:
        list[str]: Markdown lines for the gap analysis section.
    """

    rows: list[list[str]] = []
    if gaps.detector_gaps:
        rows.extend(
            [
                "Detector",
                (
                    f"{gap.language} {gap.rule_id} ({gap.severity}): "
                    f"{gap.principle} — {gap.reason}"
                ),
            ]
            for gap in gaps.detector_gaps
        )
    if gaps.feature_gaps:
        rows.extend(
            [
                "Feature",
                f"{gap.area}: {gap.description} (Next: {gap.suggested_next_step})",
            ]
            for gap in gaps.feature_gaps
        )
    if not rows:
        rows.append(["None", "No gaps reported."])
    lines = ["## Gap Analysis"]
    lines.extend(_markdown_table(["Area", "Detail"], rows))
    return lines


def _format_analysis_markdown(results: list[AnalysisResult]) -> list[str]:
    """Format per-file analysis results as Markdown sub-sections under ``## Analysis``.

    Each file gets a ``### path (language)`` heading followed by a violations
    table (capped at 10 rows) showing severity, principle, message, and
    suggestion.

    Args:
        results: Analysis results to render, one sub-section per file.

    Returns:
        list[str]: Markdown lines for the analysis section.
    """

    lines = ["## Analysis"]
    for result in results:
        lines.append(f"### {result.path or '<input>'} ({result.language})")
        if not result.violations:
            lines.append("No violations detected.")
            continue
        rows: list[list[str]] = [
            [
                str(violation.severity),
                violation.principle,
                violation.message,
                violation.suggestion or "-",
            ]
            for violation in result.violations[:10]
        ]
        lines.extend(
            _markdown_table(["Severity", "Principle", "Message", "Suggestion"], rows)
        )
        if len(result.violations) > 10:
            lines.append(f"- ...and {len(result.violations) - 10} more violations.")
    return lines


def _format_prompts_markdown(context: ReportContext) -> list[str]:
    """Format remediation prompts as Markdown under ``## Remediation Prompts``.

    Renders a count table, then expands each file-specific prompt and lists
    each generic prompt as a bullet.

    Args:
        context: Report context carrying the optional prompt bundle.

    Returns:
        list[str]: Markdown lines for the remediation prompts section (empty if no prompts).
    """

    if not context.prompts:
        return []
    file_count = len(context.prompts.file_prompts)
    generic_count = len(context.prompts.generic_prompts)
    lines = ["## Remediation Prompts"]
    lines.extend(
        _markdown_table(
            ["Type", "Count"],
            [
                ["File prompts", str(file_count)],
                ["Generic prompts", str(generic_count)],
            ],
        )
    )
    lines.append("### File-Specific Prompts")
    if context.prompts.file_prompts:
        for prompt in context.prompts.file_prompts:
            lines.extend([prompt.prompt, ""])
    else:
        lines.append("- No file-specific prompts generated.")
    lines.append("### Generic Prompts")
    if context.prompts.generic_prompts:
        lines.extend(
            [
                f"- {prompt.title}: {prompt.prompt}"
                for prompt in context.prompts.generic_prompts
            ]
        )
    else:
        lines.append("- No generic prompts available.")
    return lines


def generate_report(
    target_path: str,
    *,
    config_path: str | None = None,
    language: str | None = None,
    include_prompts: bool = False,
    include_analysis: bool = True,
    include_gaps: bool = True,
) -> ReportOutput:
    """Orchestrate the full analysis-to-report pipeline for a target path.

    Discovers files, runs analyzers, computes summaries, performs gap analysis,
    optionally generates remediation prompts, and renders everything into a
    normalised Markdown document alongside a serialised data dict.

    Args:
        target_path: File or directory to analyse.
        config_path: Optional path to a ``zen-config.yaml`` override file.
        language: When set, restricts analysis to this single language.
        include_prompts: Attach per-file and generic remediation prompts.
        include_analysis: Run analyzers and include a violation summary.
        include_gaps: Perform detector coverage gap analysis.

    Returns:
        ReportOutput: Markdown report text and equivalent machine-readable data dict.
    """

    path = Path(target_path)
    targets = _collect_targets(path, language)
    results = _analyze_targets(targets, config_path) if include_analysis else []
    languages = sorted({lang for _, lang in targets})
    gaps = build_gap_analysis(languages) if include_gaps else GapAnalysis()
    prompts = build_prompt_bundle(results) if include_prompts else None

    summary = _summarize_results(results) if include_analysis else None
    context = ReportContext(
        target_path=str(path),
        languages=languages,
        analysis_results=results,
        gap_analysis=gaps,
        prompts=prompts,
    )
    markdown_sections = [
        "# Zen of Languages Report",
        f"- Target: {context.target_path}",
        f"- Languages: {', '.join(context.languages) if context.languages else 'n/a'}",
    ]
    if summary:
        markdown_sections.extend(_format_summary_markdown(summary))
    if include_analysis:
        markdown_sections.extend(_format_analysis_markdown(results))
    if include_gaps:
        markdown_sections.extend(_format_gap_markdown(gaps))
    markdown_sections.extend(_format_prompts_markdown(context))

    data = {
        "target": context.target_path,
        "languages": context.languages,
        "summary": summary.model_dump() if summary else None,
        "analysis": [result.model_dump() for result in results],
        "gaps": gaps.model_dump(),
        "prompts": prompts.model_dump() if prompts else None,
    }
    return ReportOutput(
        markdown=normalize_markdown("\n".join(markdown_sections)), data=data
    )
