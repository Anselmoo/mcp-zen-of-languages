from __future__ import annotations

from mcp_zen_of_languages.analyzers.analyzer_factory import create_analyzer
from mcp_zen_of_languages.dogmas.interface import attach_dogma_analysis
from mcp_zen_of_languages.models import AnalysisResult
from mcp_zen_of_languages.models import CyclomaticSummary
from mcp_zen_of_languages.models import Metrics
from mcp_zen_of_languages.models import Violation
from mcp_zen_of_languages.reporting.report import generate_report


def test_attach_dogma_analysis_classifies_violations_without_prelabeled_dogmas() -> (
    None
):
    result = AnalysisResult(
        language="python",
        path="sample.py",
        metrics=Metrics(
            cyclomatic=CyclomaticSummary(blocks=[], average=0.0),
            maintainability_index=80.0,
            lines_of_code=3,
        ),
        violations=[
            Violation(
                principle="Errors should never pass silently.",
                severity=9,
                message="Bare except swallows exception handling.",
                rule_id="python-009",
                detector_id="bare_except",
                files=["sample.py"],
            ),
        ],
        overall_score=9.2,
    )

    enriched = attach_dogma_analysis(result)

    assert enriched.dogma_analysis is not None
    assert [finding.dogma_id for finding in enriched.dogma_analysis.findings] == [
        "ZEN-FAIL-FAST",
    ]


def test_pipeline_enriches_violations_and_attaches_dogma_analysis() -> None:
    analyzer = create_analyzer("python")

    result = analyzer.analyze("from math import *\n", path="sample.py")

    assert result.violations
    violation = result.violations[0]
    assert violation.rule_id == "python-002"
    assert violation.detector_id
    assert violation.universal_dogma_ids
    assert result.dogma_analysis is not None
    assert result.dogma_analysis.findings


def test_generate_report_includes_universal_dogma_section(tmp_path) -> None:
    target = tmp_path / "sample.py"
    target.write_text("from math import *\n", encoding="utf-8")

    report = generate_report(str(target))

    assert "## Universal Dogmas" in report.markdown
    assert report.data["dogmas"]
