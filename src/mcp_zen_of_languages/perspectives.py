"""Shared perspective helpers for CLI, reporting, and MCP surfaces.

The rule-first runtime remains the source of truth for every analysis result,
but selected public perspectives can safely project that result into narrower
views without changing the transport schema.
"""

from __future__ import annotations

from mcp_zen_of_languages.models import AnalysisResult
from mcp_zen_of_languages.models import PerspectiveMode
from mcp_zen_of_languages.models import RulesSummary
from mcp_zen_of_languages.models import Violation
from mcp_zen_of_languages.utils.language_detection import detect_testing_family_overlay


SEVERITY_CRITICAL = 9
SEVERITY_HIGH = 7
SEVERITY_MEDIUM = 4


def validate_perspective(
    perspective: PerspectiveMode,
    *,
    project_as: str | None = None,
) -> None:
    """Reject perspective values that do not have explicit behavior yet."""
    if perspective == PerspectiveMode.PROJECTION and (
        project_as is None or not project_as.strip()
    ):
        msg = (
            "Perspective 'projection' requires a non-empty 'project_as' "
            "request value (CLI: --as)."
        )
        raise ValueError(msg)


def _summarize_violations(result: AnalysisResult) -> RulesSummary | None:
    """Recompute summary buckets when a perspective filters violations."""
    if result.rules_summary is None:
        return None

    summary = {
        "critical": 0,
        "high": 0,
        "medium": 0,
        "low": 0,
    }
    for violation in result.violations:
        if violation.severity >= SEVERITY_CRITICAL:
            summary["critical"] += 1
        elif violation.severity >= SEVERITY_HIGH:
            summary["high"] += 1
        elif violation.severity >= SEVERITY_MEDIUM:
            summary["medium"] += 1
        else:
            summary["low"] += 1
    return RulesSummary(**summary)


def _dedupe_ids(values: list[str]) -> list[str]:
    """Preserve first-seen order while removing duplicate ids."""
    return list(dict.fromkeys(values))


def _registry_dogma_ids_for_violation(
    result: AnalysisResult,
    violation: Violation,
) -> tuple[list[str], list[str]]:
    """Resolve dogma ids for one violation directly from the authored registry seam."""
    from mcp_zen_of_languages.analyzers.registry import REGISTRY

    if violation.rule_id is None:
        return [], []

    linked_ids: list[str] = []
    verified_ids: list[str] = []
    for dogma_model in REGISTRY.dogma_models_for_rule(
        violation.rule_id, result.language
    ):
        linked_ids.extend(dogma_model.dogma_ids_for_rule(violation.rule_id))
        verified_ids.extend(dogma_model.verified_dogma_ids_for_rule(violation.rule_id))
    return _dedupe_ids(linked_ids), _dedupe_ids(verified_ids)


def resolve_linked_dogma_ids(
    result: AnalysisResult,
    violation: Violation,
) -> list[str]:
    """Return linked dogma ids using enriched fields first and registry metadata as a seam."""
    registry_linked_ids, _ = _registry_dogma_ids_for_violation(result, violation)
    linked_ids = list(violation.linked_dogma_ids or violation.universal_dogma_ids)
    return _dedupe_ids([*linked_ids, *registry_linked_ids])


def resolve_verified_dogma_ids(
    result: AnalysisResult,
    violation: Violation,
) -> list[str]:
    """Return verified dogma ids using enriched fields first and registry metadata as a seam."""
    _, registry_verified_ids = _registry_dogma_ids_for_violation(result, violation)
    return _dedupe_ids([*violation.verified_dogma_ids, *registry_verified_ids])


def _resolve_testing_family(result: AnalysisResult) -> str:
    """Resolve the configured testing-family overlay for one analysis result."""
    from mcp_zen_of_languages.analyzers.registry import REGISTRY

    if result.path is None:
        msg = (
            "Perspective 'testing' requires a file path; snippet analysis does "
            "not expose testing-family routing."
        )
        raise ValueError(msg)

    family = detect_testing_family_overlay(result.language, result.path)
    if family is None:
        msg = (
            "Perspective 'testing' requires a recognized test-file path for "
            f"language '{result.language}'."
        )
        raise ValueError(msg)
    if not REGISTRY.testing_models_for_family(family, result.language):
        msg = (
            "Perspective 'testing' is not configured for "
            f"language='{result.language}' family='{family}' yet."
        )
        raise ValueError(msg)
    return family


def _matches_testing_family(
    result: AnalysisResult,
    family: str,
) -> list:
    """Return violations explicitly linked to one configured testing family."""
    from mcp_zen_of_languages.analyzers.registry import REGISTRY

    matched = []
    for violation in result.violations:
        detector_id = violation.detector_id
        if detector_id is None:
            continue
        rule_id = violation.rule_id
        linked_ids = REGISTRY.testing_ids_for(detector_id, result.language, rule_id)
        verified_ids = REGISTRY.verified_testing_ids_for(
            detector_id,
            result.language,
            rule_id,
        )
        if family in {*linked_ids, *verified_ids}:
            matched.append(violation)
    return matched


def _resolve_projection_family(
    result: AnalysisResult,
    project_as: str | None,
) -> str:
    """Resolve one requested projection family for a result language."""
    from mcp_zen_of_languages.analyzers.registry import REGISTRY

    if project_as is None or not project_as.strip():
        msg = (
            "Perspective 'projection' requires a non-empty 'project_as' request "
            "value (CLI: --as)."
        )
        raise ValueError(msg)

    family = project_as.strip()
    if not REGISTRY.projection_models_for_family(family, result.language):
        msg = (
            "Perspective 'projection' is not configured for "
            f"language='{result.language}' project_as='{family}' yet."
        )
        raise ValueError(msg)
    return family


def _matches_projection_family(
    result: AnalysisResult,
    family: str,
) -> list:
    """Return violations explicitly linked to one configured projection family."""
    from mcp_zen_of_languages.analyzers.registry import REGISTRY

    matched = []
    for violation in result.violations:
        detector_id = violation.detector_id
        if detector_id is None:
            continue
        rule_id = violation.rule_id
        linked_ids = REGISTRY.projection_ids_for(detector_id, result.language, rule_id)
        verified_ids = REGISTRY.verified_projection_ids_for(
            detector_id,
            result.language,
            rule_id,
        )
        if family in {*linked_ids, *verified_ids}:
            matched.append(violation)
    return matched


def _apply_dogma_perspective(result: AnalysisResult) -> AnalysisResult:
    """Project one result into the dogma-focused view."""
    from mcp_zen_of_languages.dogmas.interface import attach_dogma_analysis

    enriched = attach_dogma_analysis(result.model_copy(update={"dogma_analysis": None}))
    filtered = enriched.model_copy(
        update={
            "violations": [
                violation
                for violation in enriched.violations
                if resolve_linked_dogma_ids(enriched, violation)
                or resolve_verified_dogma_ids(enriched, violation)
            ],
            "dogma_analysis": None,
        }
    )
    projected = attach_dogma_analysis(filtered)
    return projected.model_copy(
        update={"rules_summary": _summarize_violations(projected)}
    )


def apply_perspective_to_result(
    result: AnalysisResult,
    perspective: PerspectiveMode,
    *,
    project_as: str | None = None,
) -> AnalysisResult:
    """Return the analysis result filtered for the selected perspective."""
    if perspective == PerspectiveMode.DOGMA:
        return _apply_dogma_perspective(result)
    if perspective == PerspectiveMode.ZEN:
        return result.model_copy(update={"dogma_analysis": None})
    if perspective == PerspectiveMode.TESTING:
        family = _resolve_testing_family(result)
        filtered = result.model_copy(
            update={
                "violations": _matches_testing_family(result, family),
                "dogma_analysis": None,
            },
        )
        return filtered.model_copy(
            update={"rules_summary": _summarize_violations(filtered)}
        )
    if perspective == PerspectiveMode.PROJECTION:
        family = _resolve_projection_family(result, project_as)
        filtered = result.model_copy(
            update={
                "violations": _matches_projection_family(result, family),
                "dogma_analysis": None,
            },
        )
        return filtered.model_copy(
            update={"rules_summary": _summarize_violations(filtered)}
        )
    return result
