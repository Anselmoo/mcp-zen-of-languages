"""Analyzer that lifts enriched rule violations into universal dogma findings."""

from __future__ import annotations

from mcp_zen_of_languages.dogmas.detectors import DogmaDetector
from mcp_zen_of_languages.dogmas.detectors import build_dogma_detectors
from mcp_zen_of_languages.models import AnalysisResult
from mcp_zen_of_languages.models import DogmaAnalysis


class UniversalDogmaAnalyzer:
    """Run universal dogma detectors over an existing ``AnalysisResult``."""

    def __init__(self, detectors: list[DogmaDetector] | None = None) -> None:
        """Initialize with the default detector suite unless overridden."""
        self._detectors = detectors or build_dogma_detectors()

    def analyze(self, result: AnalysisResult) -> DogmaAnalysis:
        """Aggregate dogma findings from one analysis result."""
        findings = [
            finding
            for detector in self._detectors
            if (finding := detector.detect(result)) is not None
        ]
        findings.sort(key=lambda finding: (-finding.severity, finding.dogma_id))
        return DogmaAnalysis(findings=findings)


__all__ = ["UniversalDogmaAnalyzer"]
