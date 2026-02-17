"""Gap analysis that identifies missing detector coverage and product capabilities.

After analyzers run and violations are collected, the gap analysis stage asks a
different question: *which zen principles could not be checked at all?*  For
each requested language, ``build_gap_analysis`` iterates the canonical zen
principles and queries the detector registry.  Any principle that has zero
registered detectors is surfaced as a ``DetectorCoverageGap``.

In addition to detector gaps, a static list of ``FeatureGap`` entries captures
product-level capabilities (e.g. automated fix suggestions, expanded reporting)
that have been identified but not yet implemented.

The combined ``GapAnalysis`` model feeds into the Markdown report's *Gap
Analysis* section and can also be consumed programmatically via the MCP
``generate_report`` tool.

See Also:
    ``reporting.models.GapAnalysis``: Data model returned by this module.
    ``analyzers.registry.REGISTRY``: Detector registry queried for coverage.
    ``rules.get_language_zen``: Source of canonical zen principles per language.
"""

from __future__ import annotations

from pathlib import Path

from mcp_zen_of_languages.analyzers.analyzer_factory import supported_languages
from mcp_zen_of_languages.analyzers.registry import REGISTRY
from mcp_zen_of_languages.reporting.models import (
    DetectorCoverageGap,
    FeatureGap,
    GapAnalysis,
)
from mcp_zen_of_languages.rules import get_all_languages, get_language_zen

_SERVER_ROUTED_LANGUAGES: tuple[str, ...] = supported_languages()


def _project_root() -> Path:
    current = Path(__file__).resolve()
    for candidate in (current, *current.parents):
        if (candidate / "pyproject.toml").exists():
            return candidate
    return Path.cwd()


def _detectors_without_tests() -> list[str]:
    tests_root = _project_root() / "tests"
    if not tests_root.exists():
        return []
    detector_names = {metadata.detector_class.__name__ for metadata in REGISTRY.items()}
    covered: set[str] = set()
    for path in tests_root.rglob("test_*.py"):
        text = path.read_text(encoding="utf-8", errors="ignore")
        for detector_name in detector_names - covered:
            if detector_name in text:
                covered.add(detector_name)
        if covered == detector_names:
            break
    missing: list[str] = []
    for detector_name in sorted(detector_names):
        if detector_name not in covered:
            missing.append(detector_name)
    return missing


def _build_feature_gaps() -> list[FeatureGap]:
    registry_languages = {meta.language for meta in REGISTRY.items()}
    rules_languages = set(get_all_languages())
    factory_languages = set(supported_languages())
    feature_gaps: list[FeatureGap] = []

    missing_detector_languages = sorted(rules_languages - registry_languages)
    if missing_detector_languages:
        feature_gaps.append(
            FeatureGap(
                area="coverage",
                description=(
                    "Languages with rules but no registered detectors: "
                    + ", ".join(missing_detector_languages)
                ),
                suggested_next_step=(
                    "Add detector mappings for each uncovered language."
                ),
            )
        )

    missing_tests = _detectors_without_tests()
    if missing_tests:
        feature_gaps.append(
            FeatureGap(
                area="testing",
                description=(
                    f"{len(missing_tests)} detector classes have no matching test module."
                ),
                suggested_next_step=(
                    "Add detector-focused tests under tests/detectors."
                ),
            )
        )

    missing_server_routes = sorted(factory_languages - set(_SERVER_ROUTED_LANGUAGES))
    if missing_server_routes:
        feature_gaps.append(
            FeatureGap(
                area="routing",
                description=(
                    "Factory languages missing server routing: "
                    + ", ".join(missing_server_routes)
                ),
                suggested_next_step=(
                    "Route all factory-supported languages through create_analyzer."
                ),
            )
        )

    return feature_gaps


def build_gap_analysis(languages: list[str]) -> GapAnalysis:
    """Build a gap analysis report across one or more languages.

    For every zen principle in each language, the detector registry is queried.
    Principles with no registered detector produce a ``DetectorCoverageGap``.
    The static ``FEATURE_GAPS`` list is appended to capture known product-level
    shortcomings.

    Args:
        languages: Language identifiers to include in the coverage scan.

    Returns:
        GapAnalysis: Combined detector and feature gap report.
    """

    detector_gaps: list[DetectorCoverageGap] = []
    for language in languages:
        lang_zen = get_language_zen(language)
        if lang_zen is None:
            continue
        for principle in lang_zen.principles:
            metas = REGISTRY.detectors_for_rule(principle.id, language)
            if not metas:
                detector_gaps.append(
                    DetectorCoverageGap(
                        language=language,
                        rule_id=principle.id,
                        principle=principle.principle,
                        severity=principle.severity,
                        reason="No detector registered for rule.",
                    )
                )
                continue
    feature_gaps = _build_feature_gaps()
    return GapAnalysis(detector_gaps=detector_gaps, feature_gaps=feature_gaps)
