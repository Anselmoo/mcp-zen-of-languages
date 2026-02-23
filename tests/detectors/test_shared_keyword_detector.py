from __future__ import annotations

from mcp_zen_of_languages.analyzers.base import AnalysisContext
from mcp_zen_of_languages.core.detectors.shared_keyword import (
    SharedDogmaKeywordDetector,
)
from mcp_zen_of_languages.languages.configs import DetectorConfig


def test_shared_keyword_detector_finds_configured_patterns() -> None:
    detector = SharedDogmaKeywordDetector()
    config = DetectorConfig(
        type="shared-test",
        principle="Dogma keyword match",
        detectable_patterns=["TODO", "FIXME"],
    )
    context = AnalysisContext(code="print('x')\n# TODO: refactor\n", language="python")

    violations = detector.detect(context, config)

    assert len(violations) == 1
    assert violations[0].message == "Dogma keyword match"
    assert violations[0].location is not None
    assert violations[0].location.line == 2


def test_shared_keyword_detector_returns_empty_without_matches() -> None:
    detector = SharedDogmaKeywordDetector()
    config = DetectorConfig(type="shared-test", detectable_patterns=["TODO"])
    context = AnalysisContext(code="print('clean')\n", language="python")

    assert detector.detect(context, config) == []
