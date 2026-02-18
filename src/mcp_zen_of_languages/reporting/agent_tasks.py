"""Agent-task generation that converts zen violations into dependency-ordered work items.

This module bridges the gap between *what is wrong* (violations) and *what to
do about it* (tasks).  ``build_agent_tasks`` walks every violation across all
analysis results, resolves a ``RemediationPattern`` for fix guidance, classifies
the violation into a theme via ``theme_clustering``, and emits an ``AgentTask``
with action text, before/after code snippets, effort estimate, and acceptance
criteria.

Tasks are sorted by theme priority (derived from ``BigPictureAnalysis`` cluster
ordering) and descending severity, then chained with intra-theme dependencies
so that an automated agent can execute them in a safe order.  The resulting
``AgentTaskList`` also carries the health score and a numbered refactoring
roadmap for human review.

See Also:
    ``reporting.remediation_patterns.resolve_pattern``: Supplies per-violation guidance.
    ``reporting.theme_clustering.build_big_picture_analysis``: Drives theme ordering.
    ``reporting.terminal.build_agent_tasks_table``: Renders the task list as Rich output.
"""

from __future__ import annotations

from typing import Literal, TypedDict, TYPE_CHECKING

from pydantic import BaseModel, Field

from mcp_zen_of_languages.reporting.remediation_patterns import resolve_pattern
from mcp_zen_of_languages.reporting.theme_clustering import (
    build_big_picture_analysis,
    classify_violation,
)

if TYPE_CHECKING:
    from mcp_zen_of_languages.models import AnalysisResult


class AgentTask(BaseModel):
    """A single actionable remediation task derived from a zen violation.

    Each task carries enough context for an automated agent or a human developer
    to understand, execute, and verify the fix without referring back to the
    original analysis output.

    Attributes:
        task_id: Sequential identifier unique within the parent ``AgentTaskList``.
        file: Source file path where the violation was detected.
        line: 1-based line number of the violation, if available.
        violation: Principle name or message summarising the violation.
        severity: Numeric severity inherited from the original violation.
        action: Imperative description of the remediation to perform.
        idiom_explanation: Why the idiomatic alternative is preferred in this language.
        before_pattern: Example code showing the current anti-pattern.
        after_pattern: Example code showing the desired idiomatic form.
        effort: T-shirt size estimate — ``"S"``, ``"M"``, or ``"L"``.
        acceptance_criteria: Testable statement confirming the fix is complete.
        depends_on: Task IDs that must complete before this task can start.
        theme: Remediation theme from ``theme_clustering`` (e.g. ``"Complexity"``).
    """

    task_id: int
    file: str
    line: int | None = None
    violation: str
    severity: int
    action: str
    idiom_explanation: str
    before_pattern: str | None = None
    after_pattern: str | None = None
    effort: Literal["S", "M", "L"]
    acceptance_criteria: str
    depends_on: list[int] = Field(default_factory=list)
    theme: str


class AgentTaskCluster(BaseModel):
    """A group of agent tasks sharing the same remediation theme.

    Clusters mirror the ``ViolationCluster`` ordering from
    ``theme_clustering`` and allow consumers to process related fixes
    together — for example, addressing all *Complexity* tasks before
    moving on to *Documentation*.

    Attributes:
        theme: Shared remediation theme label.
        priority: 1-based rank derived from cumulative severity weight.
        tasks: Agent tasks belonging to this theme cluster.
    """

    theme: str
    priority: int
    tasks: list[AgentTask] = Field(default_factory=list)


class AgentTaskList(BaseModel):
    """Top-level container for all agent tasks generated from an analysis batch.

    This is the primary output of ``build_agent_tasks`` and the input to
    ``terminal.build_agent_tasks_table``.  Tasks are pre-sorted by theme
    priority and severity, and grouped into clusters for batch execution.

    Attributes:
        project: Project identifier or directory path shown in output headers.
        total_tasks: Total number of tasks generated.
        tasks: Flat list of all agent tasks in recommended execution order.
        health_score: Project health score from 0 (severe issues) to 100 (clean).
        clusters: Tasks grouped by remediation theme with priority ranking.
        roadmap: Numbered refactoring steps derived from cluster analysis.
    """

    project: str
    total_tasks: int
    tasks: list[AgentTask]
    health_score: float
    clusters: list[AgentTaskCluster] = Field(default_factory=list)
    roadmap: list[str] = Field(default_factory=list)


def build_agent_tasks(
    results: list[AnalysisResult],
    project: str = ".",
    min_severity: int = 1,
) -> AgentTaskList:
    """Transform analysis violations into a prioritised, dependency-ordered task list.

    For each violation meeting the severity threshold, a ``RemediationPattern``
    is resolved for fix guidance, a theme is assigned via
    ``classify_violation``, and an ``AgentTask`` is emitted.  Tasks are sorted
    by theme priority (highest-severity clusters first) then by descending
    severity within each theme, and intra-theme dependencies are set so that
    each task depends on the preceding task in its theme.

    Args:
        results: Analysis results containing the violations to convert.
        project: Label identifying the project in output headers.
        min_severity: Violations below this severity are excluded.

    Returns:
        AgentTaskList: Sorted tasks with clusters, health score, and roadmap.
    """

    big_picture = build_big_picture_analysis(results)
    theme_priority = {
        cluster.theme: cluster.suggested_order for cluster in big_picture.clusters
    }

    class _RawTask(TypedDict):
        path: str
        line: int | None
        violation: str
        severity: int
        action: str
        idiom_explanation: str
        before_pattern: str | None
        after_pattern: str | None
        effort: Literal["S", "M", "L"]
        acceptance_criteria: str
        theme: str

    raw_tasks: list[_RawTask] = []
    for result in results:
        for violation in result.violations:
            if violation.severity < min_severity:
                continue
            path = result.path or "<input>"
            pattern = resolve_pattern(violation, result.language)
            theme = classify_violation(violation)
            acceptance = (
                pattern.acceptance_criteria.format(path=path)
                if "{path}" in pattern.acceptance_criteria
                else pattern.acceptance_criteria
            )
            raw_tasks.append(
                _RawTask(
                    path=path,
                    line=violation.location.line if violation.location else None,
                    violation=violation.principle or violation.message,
                    severity=violation.severity,
                    action=pattern.action,
                    idiom_explanation=pattern.idiom_explanation,
                    before_pattern=pattern.before_pattern,
                    after_pattern=pattern.after_pattern,
                    effort=pattern.effort,
                    acceptance_criteria=acceptance,
                    theme=theme,
                )
            )
    raw_tasks.sort(
        key=lambda item: (
            theme_priority.get(str(item["theme"]), 99),
            -int(item["severity"]),
        )
    )

    tasks: list[AgentTask] = []
    last_task_by_theme: dict[str, int] = {}
    for task_id, item in enumerate(raw_tasks, start=1):
        theme = str(item["theme"])
        depends_on = []
        if theme in last_task_by_theme:
            depends_on.append(last_task_by_theme[theme])
        line = item.get("line")
        task = AgentTask(
            task_id=task_id,
            file=str(item["path"]),
            line=line if isinstance(line, int) else None,
            violation=str(item["violation"]),
            severity=item["severity"],
            action=item["action"],
            idiom_explanation=item["idiom_explanation"],
            before_pattern=item["before_pattern"],
            after_pattern=item["after_pattern"],
            effort=item["effort"],
            acceptance_criteria=item["acceptance_criteria"],
            depends_on=depends_on,
            theme=theme,
        )
        tasks.append(task)
        last_task_by_theme[theme] = task.task_id

    clusters = []
    for cluster in big_picture.clusters:
        cluster_tasks = [task for task in tasks if task.theme == cluster.theme]
        clusters.append(
            AgentTaskCluster(
                theme=cluster.theme,
                priority=cluster.suggested_order,
                tasks=cluster_tasks,
            )
        )

    return AgentTaskList(
        project=project,
        total_tasks=len(tasks),
        tasks=tasks,
        health_score=big_picture.health_score,
        clusters=clusters,
        roadmap=big_picture.refactoring_roadmap,
    )
