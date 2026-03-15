"""Analyzer that lifts enriched rule violations into universal dogma findings."""

from __future__ import annotations

from typing import TYPE_CHECKING

from mcp_zen_of_languages.core.detectors import ClutterDetector
from mcp_zen_of_languages.core.detectors import ControlFlowDetector
from mcp_zen_of_languages.core.detectors import SignatureDetector
from mcp_zen_of_languages.core.detectors import StateMutationDetector
from mcp_zen_of_languages.dogmas.detectors import DogmaDetector
from mcp_zen_of_languages.dogmas.detectors import build_dogma_detectors
from mcp_zen_of_languages.models import AnalysisResult
from mcp_zen_of_languages.models import DogmaAnalysis
from mcp_zen_of_languages.models import DogmaDomainFinding
from mcp_zen_of_languages.models import DogmaFinding


if TYPE_CHECKING:
    from collections.abc import Iterable


def _dedupe(values: Iterable[str]) -> list[str]:
    """Return values in first-seen order without duplicates."""
    seen: set[str] = set()
    ordered: list[str] = []
    for value in values:
        if not value or value in seen:
            continue
        seen.add(value)
        ordered.append(value)
    return ordered


def _domain_label(detector_name: str) -> str:
    """Convert a universal detector identifier into a human-readable label."""
    return detector_name.removeprefix("universal_").replace("_", " ").title()


def _linked_dogma_ids(violation: object) -> list[str]:
    """Return explicitly linked dogma ids from a violation."""
    linked = getattr(violation, "linked_dogma_ids", None)
    if isinstance(linked, list) and linked:
        return linked
    fallback = getattr(violation, "universal_dogma_ids", None)
    return list(fallback) if isinstance(fallback, list) else []


def _verified_dogma_ids(violation: object) -> list[str]:
    """Return explicitly verified dogma ids from a violation."""
    verified = getattr(violation, "verified_dogma_ids", None)
    return list(verified) if isinstance(verified, list) else []


def _bundle_dogma_ids(
    *,
    language: str,
    violation: object,
    verified: bool = False,
) -> list[str]:
    """Resolve authored dogma ids from the preserved registry bundle seam."""
    detector_id = getattr(violation, "detector_id", None)
    rule_id = getattr(violation, "rule_id", None)
    if not isinstance(detector_id, str) or not detector_id:
        return []
    if not isinstance(rule_id, str) or not rule_id:
        return []

    from mcp_zen_of_languages.analyzers.registry import REGISTRY

    REGISTRY.bootstrap_from_mappings()
    try:
        if verified:
            return REGISTRY.verified_dogma_ids_for(detector_id, language, rule_id)
        return REGISTRY.linked_dogma_ids_for(detector_id, language, rule_id)
    except KeyError:
        return []


class UniversalDogmaAnalyzer:
    """Run universal dogma detectors over an existing ``AnalysisResult``."""

    def __init__(
        self,
        detectors: list[DogmaDetector] | None = None,
        domain_detectors: list[object] | None = None,
    ) -> None:
        """Initialize with the default detector suite unless overridden."""
        self._detectors = detectors or build_dogma_detectors()
        self._domain_detectors = domain_detectors or [
            ControlFlowDetector(),
            SignatureDetector(),
            StateMutationDetector(),
            ClutterDetector(),
        ]

    def analyze(self, result: AnalysisResult) -> DogmaAnalysis:
        """Aggregate dogma findings from one analysis result."""
        findings = [
            finding
            for detector in self._detectors
            if (finding := detector.detect(result)) is not None
        ]
        findings.sort(key=lambda finding: (-finding.severity, finding.dogma_id))
        return DogmaAnalysis(
            findings=findings,
            domains=self._build_domain_findings(findings),
        )

    def enrich_result(self, result: AnalysisResult) -> AnalysisResult:
        """Attach linked and verified dogma ids to violations before analysis."""
        enriched_violations = [
            violation.model_copy(
                update={
                    "linked_dogma_ids": _dedupe(
                        [
                            *_linked_dogma_ids(violation),
                            *_bundle_dogma_ids(
                                language=result.language,
                                violation=violation,
                            ),
                        ]
                    ),
                    "verified_dogma_ids": (
                        _dedupe(
                            [
                                *_verified_dogma_ids(violation),
                                *_bundle_dogma_ids(
                                    language=result.language,
                                    violation=violation,
                                    verified=True,
                                ),
                            ]
                        )
                        if _verified_dogma_ids(violation)
                        else _dedupe(
                            [
                                *_bundle_dogma_ids(
                                    language=result.language,
                                    violation=violation,
                                    verified=True,
                                ),
                                *[
                                    detector.dogma_id
                                    for detector in self._detectors
                                    if detector.is_verified_violation(violation)
                                ],
                            ]
                        )
                    ),
                },
            )
            for violation in result.violations
        ]
        enriched_result = result.model_copy(update={"violations": enriched_violations})
        return enriched_result.model_copy(
            update={"dogma_analysis": self.analyze(enriched_result)}
        )

    def _build_domain_findings(
        self,
        findings: list[DogmaFinding],
    ) -> list[DogmaDomainFinding]:
        """Group concrete dogma findings into shared cross-language domains."""
        findings_by_id = {finding.dogma_id: finding for finding in findings}
        domains: list[DogmaDomainFinding] = []
        for detector in self._domain_detectors:
            detector_name = getattr(detector, "name", "")
            dogma_ids = getattr(detector, "rule_ids", ())
            if not detector_name or not dogma_ids:
                continue
            matched = [
                findings_by_id[dogma_id]
                for dogma_id in dogma_ids
                if dogma_id in findings_by_id
            ]
            if not matched:
                continue
            domains.append(
                DogmaDomainFinding(
                    detector_id=detector_name,
                    label=_domain_label(detector_name),
                    severity=max(finding.severity for finding in matched),
                    dogma_ids=_dedupe(finding.dogma_id for finding in matched),
                    violation_count=sum(finding.violation_count for finding in matched),
                    verified_violation_count=sum(
                        finding.verified_violation_count for finding in matched
                    ),
                    rule_ids=_dedupe(
                        rule_id for finding in matched for rule_id in finding.rule_ids
                    ),
                    verified_rule_ids=_dedupe(
                        rule_id
                        for finding in matched
                        for rule_id in finding.verified_rule_ids
                    ),
                    messages=_dedupe(
                        message for finding in matched for message in finding.messages
                    )[:5],
                    files=_dedupe(
                        file_path for finding in matched for file_path in finding.files
                    ),
                ),
            )
        return sorted(
            domains, key=lambda domain: (-domain.severity, domain.detector_id)
        )


__all__ = ["UniversalDogmaAnalyzer"]
