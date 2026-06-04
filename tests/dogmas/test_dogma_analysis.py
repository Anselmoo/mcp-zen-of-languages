from __future__ import annotations

from mcp_zen_of_languages.analyzers.analyzer_factory import create_analyzer
from mcp_zen_of_languages.analyzers.registry import REGISTRY
from mcp_zen_of_languages.core.universal_dogmas import UniversalDogmaID
from mcp_zen_of_languages.dogmas.interface import attach_dogma_analysis
from mcp_zen_of_languages.dogmas.mapping import DOGMA_DETECTOR_MAP
from mcp_zen_of_languages.models import AnalysisResult
from mcp_zen_of_languages.models import CyclomaticSummary
from mcp_zen_of_languages.models import Metrics
from mcp_zen_of_languages.models import Violation
from mcp_zen_of_languages.reporting.report import generate_report
from mcp_zen_of_languages.transport.reporters import CliReporter
from mcp_zen_of_languages.transport.reporters import McpReporter


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
    assert enriched.violations[0].linked_dogma_ids == [
        "ZEN-FAIL-FAST",
        "ZEN-EXPLICIT-INTENT",
    ]
    assert enriched.violations[0].verified_dogma_ids == ["ZEN-FAIL-FAST"]
    assert [finding.dogma_id for finding in enriched.dogma_analysis.findings] == [
        "ZEN-EXPLICIT-INTENT",
        "ZEN-FAIL-FAST",
    ]
    finding_by_id = {
        finding.dogma_id: finding for finding in enriched.dogma_analysis.findings
    }
    assert finding_by_id["ZEN-FAIL-FAST"].verified_violation_count == 1
    assert finding_by_id["ZEN-EXPLICIT-INTENT"].verified_violation_count == 0
    assert {domain.detector_id for domain in enriched.dogma_analysis.domains} == {
        "universal_signature",
        "universal_control_flow",
    }


def test_pipeline_enriches_violations_and_attaches_dogma_analysis() -> None:
    analyzer = create_analyzer("python")

    result = analyzer.analyze("from math import *\n", path="sample.py")

    assert result.violations
    violation = result.violations[0]
    assert violation.rule_id == "python-002"
    assert violation.detector_id
    assert violation.linked_dogma_ids == ["ZEN-EXPLICIT-INTENT"]
    assert violation.verified_dogma_ids == ["ZEN-EXPLICIT-INTENT"]
    assert result.dogma_analysis is not None
    assert result.dogma_analysis.findings
    assert result.dogma_analysis.domains


def test_generate_report_includes_universal_dogma_section(tmp_path) -> None:
    target = tmp_path / "sample.py"
    target.write_text("from math import *\n", encoding="utf-8")

    report = generate_report(str(target))

    assert "## Universal Dogmas" in report.markdown
    assert "## Universal Dogma Domains" in report.markdown
    assert "Linked dogmas" in report.markdown
    assert "Verified dogmas" in report.markdown
    assert report.data["dogmas"]
    assert report.data["dogma_domains"]


def test_dogma_detector_map_covers_all_universal_dogmas() -> None:
    dogma_ids = [binding.dogma_id for binding in DOGMA_DETECTOR_MAP.bindings]

    assert dogma_ids == [dogma.value for dogma in UniversalDogmaID]
    assert [
        detector.dogma_id for detector in DOGMA_DETECTOR_MAP.build_detectors()
    ] == dogma_ids


def test_attach_dogma_analysis_groups_findings_into_shared_domains() -> None:
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
                principle="Use clear naming.",
                severity=6,
                message="Identifier should be descriptive.",
                rule_id="python-001",
                detector_id="naming",
                files=["sample.py"],
                linked_dogma_ids=["ZEN-UNAMBIGUOUS-NAME"],
                universal_dogma_ids=["ZEN-UNAMBIGUOUS-NAME"],
                verified_dogma_ids=["ZEN-UNAMBIGUOUS-NAME"],
            ),
            Violation(
                principle="Avoid dead code.",
                severity=5,
                message="Dead code should be removed.",
                rule_id="python-999",
                detector_id="deletion",
                files=["sample.py"],
                linked_dogma_ids=["ZEN-RUTHLESS-DELETION"],
                universal_dogma_ids=["ZEN-RUTHLESS-DELETION"],
            ),
        ],
        overall_score=9.2,
    )

    enriched = attach_dogma_analysis(result)

    assert enriched.dogma_analysis is not None
    assert [domain.detector_id for domain in enriched.dogma_analysis.domains] == [
        "universal_clutter",
    ]
    assert enriched.dogma_analysis.domains[0].dogma_ids == [
        "ZEN-UNAMBIGUOUS-NAME",
        "ZEN-RUTHLESS-DELETION",
    ]


def test_attach_dogma_analysis_preserves_existing_verified_subset() -> None:
    result = AnalysisResult(
        language="ruby",
        path="sample.rb",
        metrics=Metrics(
            cyclomatic=CyclomaticSummary(blocks=[], average=0.0),
            maintainability_index=80.0,
            lines_of_code=3,
        ),
        violations=[
            Violation(
                principle="Prefer symbols over strings for keys.",
                severity=6,
                message="Prefer symbols over strings for keys",
                rule_id="ruby-007",
                detector_id="ruby_symbol_keys",
                files=["sample.rb"],
                linked_dogma_ids=[
                    "ZEN-RIGHT-ABSTRACTION",
                    "ZEN-UNAMBIGUOUS-NAME",
                ],
                verified_dogma_ids=["ZEN-RIGHT-ABSTRACTION"],
            ),
        ],
        overall_score=9.2,
    )

    enriched = attach_dogma_analysis(result)

    assert enriched.violations[0].linked_dogma_ids == [
        "ZEN-RIGHT-ABSTRACTION",
        "ZEN-UNAMBIGUOUS-NAME",
    ]
    assert enriched.violations[0].verified_dogma_ids == ["ZEN-RIGHT-ABSTRACTION"]
    assert enriched.dogma_analysis is not None
    assert {finding.dogma_id for finding in enriched.dogma_analysis.findings} >= {
        "ZEN-RIGHT-ABSTRACTION",
        "ZEN-UNAMBIGUOUS-NAME",
    }


def test_attach_dogma_analysis_enriches_detectorless_composite_violation_from_dogma_rule_indexes() -> (
    None
):
    result = AnalysisResult(
        language="ruby",
        path="sample.rb",
        metrics=Metrics(
            cyclomatic=CyclomaticSummary(blocks=[], average=0.0),
            maintainability_index=80.0,
            lines_of_code=3,
        ),
        violations=[
            Violation(
                principle="Prefer symbols over strings for keys.",
                severity=6,
                message="Prefer symbols over strings for keys",
                rule_id="ruby-007",
                files=["sample.rb"],
            ),
        ],
        overall_score=9.2,
    )

    enriched = attach_dogma_analysis(result)

    assert enriched.violations[0].linked_dogma_ids == [
        "ZEN-RIGHT-ABSTRACTION",
        "ZEN-UNAMBIGUOUS-NAME",
    ]
    assert enriched.violations[0].verified_dogma_ids == ["ZEN-RIGHT-ABSTRACTION"]
    assert enriched.dogma_analysis is not None
    assert {finding.dogma_id for finding in enriched.dogma_analysis.findings} >= {
        "ZEN-RIGHT-ABSTRACTION",
        "ZEN-UNAMBIGUOUS-NAME",
    }


def test_attach_dogma_analysis_uses_dogma_rule_and_family_indexes(monkeypatch) -> None:
    REGISTRY.bootstrap_from_mappings()
    rule_calls: list[tuple[str, str]] = []
    family_calls: list[tuple[str, str]] = []
    original_dogma_models_for_rule = REGISTRY.dogma_models_for_rule
    original_dogma_models_for_family = REGISTRY.dogma_models_for_family

    def spy_dogma_models_for_rule(rule_id: str, language: str):
        rule_calls.append((rule_id, language))
        return original_dogma_models_for_rule(rule_id, language)

    def spy_dogma_models_for_family(dogma_id: str, language: str):
        family_calls.append((dogma_id, language))
        return original_dogma_models_for_family(dogma_id, language)

    monkeypatch.setattr(REGISTRY, "dogma_models_for_rule", spy_dogma_models_for_rule)
    monkeypatch.setattr(
        REGISTRY, "dogma_models_for_family", spy_dogma_models_for_family
    )

    result = AnalysisResult(
        language="ruby",
        path="sample.rb",
        metrics=Metrics(
            cyclomatic=CyclomaticSummary(blocks=[], average=0.0),
            maintainability_index=80.0,
            lines_of_code=3,
        ),
        violations=[
            Violation(
                principle="Prefer symbols over strings for keys.",
                severity=6,
                message="Prefer symbols over strings for keys",
                rule_id="ruby-007",
                linked_dogma_ids=[
                    "ZEN-RIGHT-ABSTRACTION",
                    "ZEN-UNAMBIGUOUS-NAME",
                ],
                files=["sample.rb"],
            ),
        ],
        overall_score=9.2,
    )

    enriched = attach_dogma_analysis(result)

    assert ("ruby-007", "ruby") in rule_calls
    assert ("ZEN-RIGHT-ABSTRACTION", "ruby") in family_calls
    assert ("ZEN-UNAMBIGUOUS-NAME", "ruby") in family_calls
    assert enriched.violations[0].verified_dogma_ids == ["ZEN-RIGHT-ABSTRACTION"]


def test_ruby_multi_dogma_rule_flows_to_mcp_cli_and_report(tmp_path) -> None:
    code = "payload = { 'name' => 'Copilot' }\n"
    result = create_analyzer("ruby").analyze(code, path="sample.rb")

    ruby_violation = next(
        violation for violation in result.violations if violation.rule_id == "ruby-007"
    )
    assert ruby_violation.linked_dogma_ids == [
        "ZEN-RIGHT-ABSTRACTION",
        "ZEN-UNAMBIGUOUS-NAME",
    ]
    assert ruby_violation.verified_dogma_ids == ["ZEN-RIGHT-ABSTRACTION"]
    assert {finding.dogma_id for finding in result.dogma_analysis.findings} >= {
        "ZEN-RIGHT-ABSTRACTION",
        "ZEN-UNAMBIGUOUS-NAME",
    }
    right_abstraction = next(
        finding
        for finding in result.dogma_analysis.findings
        if finding.dogma_id == "ZEN-RIGHT-ABSTRACTION"
    )
    unambiguous_name = next(
        finding
        for finding in result.dogma_analysis.findings
        if finding.dogma_id == "ZEN-UNAMBIGUOUS-NAME"
    )
    assert right_abstraction.verified_violation_count == 1
    assert unambiguous_name.verified_violation_count == 0

    cli_output = CliReporter().report(result)
    mcp_output = McpReporter().report(result)
    violations_payload = mcp_output["violations"]
    assert isinstance(violations_payload, list)
    ruby_payload = next(
        violation
        for violation in violations_payload
        if violation["rule_id"] == "ruby-007"
    )
    assert "linked_dogmas=2" in cli_output
    assert "verified_dogmas=1" in cli_output
    assert "linked_domains=2" in cli_output
    assert "verified_domains=1" in cli_output
    assert ruby_payload["linked_dogma_ids"] == [
        "ZEN-RIGHT-ABSTRACTION",
        "ZEN-UNAMBIGUOUS-NAME",
    ]
    assert ruby_payload["verified_dogma_ids"] == ["ZEN-RIGHT-ABSTRACTION"]

    target = tmp_path / "sample.rb"
    target.write_text(code, encoding="utf-8")
    report = generate_report(str(target))
    assert "ZEN-RIGHT-ABSTRACTION, ZEN-UNAMBIGUOUS-NAME" in report.markdown
    assert "Linked dogmas" in report.markdown
    assert "Verified dogmas" in report.markdown
    assert "Prefer symbols over strings for keys" in report.markdown


def test_framework_multi_dogma_rule_tracks_linked_and_verified_dogmas() -> None:
    code = "export default function Page() { document.getElementById('x'); return <div /> }\n"
    result = create_analyzer("react").analyze(code, path="Page.tsx")

    framework_violation = next(
        violation for violation in result.violations if violation.rule_id == "react-003"
    )
    assert framework_violation.linked_dogma_ids == [
        "ZEN-RIGHT-ABSTRACTION",
        "ZEN-STRICT-FENCES",
    ]
    assert framework_violation.verified_dogma_ids == ["ZEN-RIGHT-ABSTRACTION"]
    assert {finding.dogma_id for finding in result.dogma_analysis.findings} >= {
        "ZEN-RIGHT-ABSTRACTION",
        "ZEN-STRICT-FENCES",
        "ZEN-VISIBLE-STATE",
    }
    assert {domain.detector_id for domain in result.dogma_analysis.domains} >= {
        "universal_signature",
        "universal_state_mutation",
    }


# ---------------------------------------------------------------------------
# dogmas/rules.py — compatibility wrappers
# ---------------------------------------------------------------------------


def test_resolved_rule_dogmas_returns_dogma_tuple() -> None:
    from mcp_zen_of_languages.dogmas.rules import resolved_rule_dogmas

    result = resolved_rule_dogmas("python", "python-009")
    assert isinstance(result, tuple)
    assert len(result) >= 1


def test_resolved_rule_dogmas_ignores_language_arg() -> None:
    from mcp_zen_of_languages.dogmas.rules import resolved_rule_dogmas

    result_a = resolved_rule_dogmas("python", "python-009")
    result_b = resolved_rule_dogmas("rust", "python-009")
    assert result_a == result_b


def test_resolved_rule_dogmas_for_rule_ids_aggregates() -> None:
    from mcp_zen_of_languages.dogmas.rules import resolved_rule_dogmas_for_rule_ids

    result = resolved_rule_dogmas_for_rule_ids("python", ["python-009", "python-001"])
    assert isinstance(result, tuple)


# ---------------------------------------------------------------------------
# dogmas/mapping_models.py — ValueError on dogma_id mismatch
# ---------------------------------------------------------------------------


def test_dogma_detector_binding_raises_on_mismatched_dogma_id() -> None:
    import pytest

    from mcp_zen_of_languages.dogmas.detectors import DogmaDetector
    from mcp_zen_of_languages.dogmas.mapping_models import DogmaDetectorBinding

    class _WrongDogma(DogmaDetector):
        dogma_id = "ZEN-WRONG"

        def analyze(self, context):  # type: ignore[override]
            return []

    binding = DogmaDetectorBinding(
        dogma_id="ZEN-EXPLICIT-INTENT",
        detector_class=_WrongDogma,
    )
    with pytest.raises(ValueError, match="binding mismatch"):
        binding.build_detector()
