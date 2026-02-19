"""Theme clustering that groups related violations into higher-level remediation narratives.

Violations produced by detectors are granular — a single file may trigger dozens
of individual findings.  This module classifies each violation into a broader
*theme* (e.g. ``Complexity``, ``Safety & Error Handling``) using keyword matching
against ``THEME_TAGS``, then aggregates those classifications into
``ViolationCluster`` objects ranked by cumulative severity weight.

The resulting ``BigPictureAnalysis`` provides:

* **Clusters** — ordered groups with severity totals and suggested fix order.
* **Systemic patterns** — natural-language descriptions of dominant problem areas.
* **Refactoring roadmap** — numbered action items derived from cluster ranking.
* **Health score** — a 0–100 metric penalized by total violation severity.
* **Improvement trajectory** — guidance on which theme to tackle first.

Downstream consumers include ``prompts.build_prompt_bundle`` (attaches big-picture
context to remediation prompts), ``agent_tasks.build_agent_tasks`` (uses cluster
ordering to set task priorities), and ``terminal.render_prompt_panel`` (renders
the roadmap and health score in Rich panels).

See Also:
    ``reporting.prompts``: Consumes ``BigPictureAnalysis`` for prompt enrichment.
    ``reporting.agent_tasks``: Uses cluster ordering for task dependency graphs.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from pydantic import BaseModel, Field

from mcp_zen_of_languages.models import Violation  # noqa: TC001

if TYPE_CHECKING:
    from mcp_zen_of_languages.models import AnalysisResult

THEME_TAGS: dict[str, list[str]] = {
    "Complexity": ["cyclomatic", "nesting", "long-function", "complexity", "god class"],
    "Naming & Style": ["naming", "magic-number", "magic number", "style", "formatting"],
    "Safety & Error Handling": ["error-handling", "bare except", "unsafe", "unwrap"],
    "Architecture": [
        "coupling",
        "feature envy",
        "duplication",
        "imports",
        "dependency",
    ],
    "Documentation": ["docstring", "comment", "type hints", "type-hints"],
}


class ViolationCluster(BaseModel):
    """A cluster of violations unified under a single remediation theme.

    Each cluster aggregates violations whose keyword footprint matches one of
    the entries in ``THEME_TAGS``.  The ``suggested_order`` field indicates the
    recommended fix sequence — clusters with the highest cumulative severity
    weight are addressed first to maximise the health-score improvement per
    engineering effort.

    Attributes:
        theme: Human-readable theme label such as ``"Complexity"`` or ``"Architecture"``.
        violations: Individual violation records belonging to this cluster.
        total_severity_weight: Sum of severity scores across all clustered violations.
        suggested_order: 1-based rank indicating the recommended remediation sequence.
    """

    theme: str
    violations: list[Violation] = Field(default_factory=list)
    total_severity_weight: int
    suggested_order: int


class BigPictureAnalysis(BaseModel):
    """High-level remediation intelligence synthesised from all violation clusters.

    This model is the primary output of ``build_big_picture_analysis`` and feeds
    into both the prompt bundle (where it enriches remediation guidance) and the
    terminal renderer (where it powers the roadmap and health-score panels).

    Attributes:
        clusters: Theme clusters sorted by descending severity weight.
        systemic_patterns: Natural-language observations about dominant problem areas.
        refactoring_roadmap: Numbered action items derived from cluster ordering.
        health_score: Project quality score from 0 (severe issues) to 100 (clean).
        improvement_trajectory: One-line guidance on the highest-impact next step.
    """

    clusters: list[ViolationCluster] = Field(default_factory=list)
    systemic_patterns: list[str] = Field(default_factory=list)
    refactoring_roadmap: list[str] = Field(default_factory=list)
    health_score: float
    improvement_trajectory: str


def classify_violation(violation: Violation) -> str:
    """Classify a single violation into a remediation theme using keyword matching.

    The violation's ``principle`` and ``message`` are lower-cased and scanned
    against ``THEME_TAGS``.  The first theme whose tag list produces a substring
    match wins; if nothing matches, the violation falls into the ``"Other"`` bucket.

    Args:
        violation: Violation record whose principle and message text drive classification.

    Returns:
        str: Theme label (e.g. ``"Complexity"``, ``"Documentation"``, ``"Other"``).
    """
    text = f"{violation.principle} {violation.message}".lower()
    return next(
        (
            theme
            for theme, tags in THEME_TAGS.items()
            if any(tag in text for tag in tags)
        ),
        "Other",
    )


def build_big_picture_analysis(results: list[AnalysisResult]) -> BigPictureAnalysis:
    """Synthesise a big-picture remediation overview from one or more analysis runs.

    All violations across every ``AnalysisResult`` are classified by theme,
    aggregated into severity-weighted clusters, and ranked to produce a
    refactoring roadmap.  A health score (0–100) is derived by penalising
    total severity weight, and an improvement trajectory string highlights
    the single theme whose resolution would yield the largest score lift.

    Args:
        results: Analysis results spanning one or more files and languages.

    Returns:
        BigPictureAnalysis: Clusters, roadmap, health score, and trajectory guidance.
    """
    clusters_map: dict[str, list[Violation]] = {}
    total_weight = 0
    for result in results:
        for violation in result.violations:
            theme = classify_violation(violation)
            clusters_map.setdefault(theme, []).append(violation)
            total_weight += violation.severity

    clusters: list[ViolationCluster] = [
        ViolationCluster(
            theme=theme,
            violations=violations,
            total_severity_weight=sum(v.severity for v in violations),
            suggested_order=0,
        )
        for theme, violations in clusters_map.items()
    ]
    clusters.sort(key=lambda cluster: cluster.total_severity_weight, reverse=True)
    for idx, cluster in enumerate(clusters, start=1):
        cluster.suggested_order = idx

    systemic_patterns = []
    if clusters:
        top_cluster = clusters[0]
        systemic_patterns.append(
            f"High concentration of {top_cluster.theme} violations "
            f"({len(top_cluster.violations)} findings)."
        )
    systemic_patterns.extend(
        [
            f"Secondary pressure in {cluster.theme} "
            f"({len(cluster.violations)} findings)."
            for cluster in clusters[1:3]
        ]
    )

    refactoring_roadmap = [
        f"{cluster.suggested_order}. Address {cluster.theme} issues "
        f"({len(cluster.violations)} violations)."
        for cluster in clusters
    ]

    health_score = max(0.0, 100.0 - total_weight * 2.5)
    if clusters:
        improvement_trajectory = (
            f"Prioritize {clusters[0].theme} fixes first for the fastest score lift."
        )
    else:
        improvement_trajectory = "No violations detected; maintain current quality."

    return BigPictureAnalysis(
        clusters=clusters,
        systemic_patterns=systemic_patterns,
        refactoring_roadmap=refactoring_roadmap,
        health_score=health_score,
        improvement_trajectory=improvement_trajectory,
    )
