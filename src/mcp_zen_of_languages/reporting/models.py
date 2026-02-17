"""Pydantic models that define the data contracts for the reporting pipeline.

Every stage of the reporting pipeline exchanges data through the models defined
here.  Together they form a strict contract: analysis results flow in via
``ReportContext``, gap and prompt data attach alongside, and the final
``ReportOutput`` carries both a rendered Markdown string and a raw data dict
suitable for JSON serialization.

Model hierarchy (simplified):

    ReportContext
    ├── AnalysisResult[]     (from analyzers)
    ├── GapAnalysis
    │   ├── DetectorCoverageGap[]
    │   └── FeatureGap[]
    └── PromptBundle
        ├── FilePrompt[]
        ├── GenericPrompt[]
        └── BigPictureAnalysis   (from theme_clustering)

    ReportOutput
    ├── markdown: str
    └── data: dict

See Also:
    ``reporting.report.generate_report``: Populates a ``ReportContext`` and
    produces a ``ReportOutput``.
"""

from __future__ import annotations

from pydantic import BaseModel, Field

from mcp_zen_of_languages.models import AnalysisResult
from mcp_zen_of_languages.reporting.theme_clustering import BigPictureAnalysis


class DetectorCoverageGap(BaseModel):
    """A rule that has no registered detector for a specific language.

    The gap analysis module emits one of these for every ``ZenPrinciple`` whose
    ``rule_id`` returns no detector metadata from the registry.  These gaps
    surface in the Markdown report under the *Gap Analysis* section and help
    maintainers prioritise detector development.

    Attributes:
        language: Language identifier (e.g. ``"python"``, ``"typescript"``).
        rule_id: Canonical rule identifier from the language's zen principles.
        principle: Human-readable principle text describing the expected practice.
        severity: Severity level inherited from the zen principle definition.
        reason: Short explanation of why this gap exists.
    """

    language: str
    rule_id: str
    principle: str
    severity: int
    reason: str


class FeatureGap(BaseModel):
    """A product-level capability that is not yet implemented.

    Unlike ``DetectorCoverageGap`` (which tracks missing *detectors*), this
    model tracks missing *features* — entire subsystems or workflows that have
    been identified as desirable but do not exist yet.

    Attributes:
        area: Functional area (e.g. ``"reporting"``, ``"remediation"``).
        description: Concise explanation of what is missing.
        suggested_next_step: Actionable recommendation for closing the gap.
    """

    area: str
    description: str
    suggested_next_step: str


class GapAnalysis(BaseModel):
    """Aggregated gap report covering both detector coverage and product features.

    Produced by ``gaps.build_gap_analysis`` and consumed by the Markdown
    formatter in ``report.py`` to render the *Gap Analysis* section.

    Attributes:
        detector_gaps: Rules that lack a registered violation detector.
        feature_gaps: Product capabilities that have not been implemented.
    """

    detector_gaps: list[DetectorCoverageGap] = Field(default_factory=list)
    feature_gaps: list[FeatureGap] = Field(default_factory=list)


class AnalysisSummary(BaseModel):
    """Aggregate counts derived from a batch of analysis results.

    Used by the Markdown report to render a concise *Summary* table showing
    total files scanned, total violations found, and a breakdown by severity
    bucket (critical ≥ 9, high ≥ 7, medium ≥ 4, low < 4).

    Attributes:
        total_files: Number of distinct source files analysed.
        total_violations: Cumulative violation count across all files.
        severity_counts: Mapping from bucket label to violation count.
    """

    total_files: int
    total_violations: int
    severity_counts: dict[str, int] = Field(default_factory=dict)


class FilePrompt(BaseModel):
    """Remediation prompt scoped to a single analysed file.

    Each ``FilePrompt`` is produced by ``prompts._format_file_prompt`` and
    contains a self-contained Markdown prompt with violation details,
    before/after code patterns, and acceptance criteria.

    Attributes:
        path: Source file path that the prompt targets.
        language: Detected or overridden language for syntax highlighting.
        prompt: Full Markdown-formatted remediation prompt text.
    """

    path: str
    language: str
    prompt: str


class GenericPrompt(BaseModel):
    """Language-level remediation prompt not tied to a specific file.

    Generic prompts cover broad best practices (e.g. *"Harden shell safety"*)
    and are selected based on the languages observed in the analysis batch.

    Attributes:
        title: Short label displayed as a heading in terminal or Markdown output.
        prompt: Descriptive guidance text for the remediation area.
    """

    title: str
    prompt: str


class PromptBundle(BaseModel):
    """Bundle of all remediation prompts produced for a single reporting run.

    Combines per-file prompts (with violation-specific before/after guidance)
    and generic prompts (language-level best practices), plus an optional
    ``BigPictureAnalysis`` that provides roadmap and health-score context.

    Attributes:
        file_prompts: Remediation prompts scoped to individual source files.
        generic_prompts: Language-level best-practice prompts.
        big_picture: Clustered violation analysis with roadmap and health score.
    """

    file_prompts: list[FilePrompt] = Field(default_factory=list)
    generic_prompts: list[GenericPrompt] = Field(default_factory=list)
    big_picture: BigPictureAnalysis | None = None


class ReportOutput(BaseModel):
    """Final output of the reporting pipeline.

    Carries both a human-readable Markdown report and the equivalent machine-
    readable data dict so that consumers (CLI, MCP tools, CI integrations) can
    choose whichever representation fits their needs.

    Attributes:
        markdown: Fully rendered Markdown report text (normalised whitespace).
        data: Serialised dict mirroring the report structure for JSON output.
    """

    markdown: str
    data: dict[str, object]


class ReportContext(BaseModel):
    """Intermediate context assembled during report generation.

    ``generate_report`` populates this model progressively — first with targets
    and analysis results, then with gap analysis and optional prompt bundles —
    before handing it to the Markdown formatters that produce the final output.

    Attributes:
        target_path: Root path (file or directory) that was scanned.
        languages: Sorted list of language identifiers discovered in the target.
        analysis_results: Per-file analysis results with violations and metrics.
        gap_analysis: Detector and feature gap report for the scanned languages.
        prompts: Optional prompt bundle attached when ``include_prompts`` is set.
    """

    target_path: str
    languages: list[str]
    analysis_results: list[AnalysisResult] = Field(default_factory=list)
    gap_analysis: GapAnalysis
    prompts: PromptBundle | None = None
