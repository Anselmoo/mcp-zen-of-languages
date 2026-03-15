from __future__ import annotations

from typing import Literal

import pytest

from mcp_zen_of_languages.analyzers.base import ViolationDetector
from mcp_zen_of_languages.analyzers.mapping_models import BindingPerspectiveBundle
from mcp_zen_of_languages.analyzers.mapping_models import ProjectionPerspectiveModel
from mcp_zen_of_languages.analyzers.registry import DetectorMetadata
from mcp_zen_of_languages.analyzers.registry import DetectorRegistry
from mcp_zen_of_languages.languages.configs import DetectorConfig
from mcp_zen_of_languages.models import AnalysisResult
from mcp_zen_of_languages.models import CyclomaticSummary
from mcp_zen_of_languages.models import DogmaAnalysis
from mcp_zen_of_languages.models import DogmaFinding
from mcp_zen_of_languages.models import Metrics
from mcp_zen_of_languages.models import PerspectiveMode
from mcp_zen_of_languages.models import Violation
from mcp_zen_of_languages.reporting.gaps import build_gap_analysis
from mcp_zen_of_languages.reporting.prompts import GENERIC_PROMPTS_BY_LANGUAGE
from mcp_zen_of_languages.reporting.prompts import build_prompt_bundle
from mcp_zen_of_languages.reporting.report import generate_report
from mcp_zen_of_languages.rules import get_all_languages


class DummyConfig(DetectorConfig):
    type: Literal["dummy"] = "dummy"


class DummyDetector(ViolationDetector[DummyConfig]):
    @property
    def name(self) -> str:
        return "dummy"

    def detect(self, context, config):
        return []


def _build_result(path: str, language: str, severity: int) -> AnalysisResult:
    violation = Violation(
        principle="Test",
        severity=severity,
        message="Example violation",
    )
    metrics = Metrics(
        cyclomatic=CyclomaticSummary(blocks=[], average=0.0),
        maintainability_index=0.0,
        lines_of_code=1,
    )
    return AnalysisResult(
        language=language,
        path=path,
        metrics=metrics,
        violations=[violation],
        overall_score=90.0,
    )


def _projection_registry() -> DetectorRegistry:
    registry = DetectorRegistry()
    metadata = DetectorMetadata(
        detector_id="line_length",
        detector_class=DummyDetector,
        config_model=DummyConfig,
        language="python",
        rule_ids=["python-001"],
    )
    bundle = BindingPerspectiveBundle(
        rule_model=metadata,
        projection_model=ProjectionPerspectiveModel(
            detector_id="line_length",
            language="python",
            projection_rule_map={"go": ["python-001"]},
            projection_verified_rule_map={"go": ["python-001"]},
        ),
    )
    registry.register(metadata, bundle=bundle)
    return registry


def _build_projection_result(path: str) -> AnalysisResult:
    return AnalysisResult(
        language="python",
        path=path,
        metrics=Metrics(
            cyclomatic=CyclomaticSummary(blocks=[], average=0.0),
            maintainability_index=100.0,
            lines_of_code=1,
        ),
        violations=[
            Violation(
                principle="line length",
                severity=8,
                message="long line",
                detector_id="line_length",
                rule_id="python-001",
            ),
            Violation(
                principle="docstrings",
                severity=3,
                message="missing docstring",
                detector_id="docstrings",
                rule_id="python-007",
            ),
        ],
        dogma_analysis=DogmaAnalysis(
            findings=[
                DogmaFinding(
                    dogma_id="ZEN-UNAMBIGUOUS-NAME",
                    label="Unambiguous name",
                    severity=3,
                ),
            ],
        ),
        overall_score=95.0,
    )


def test_build_prompt_bundle_includes_file_and_generic():
    results = [
        _build_result("sample.py", "python", 7),
        _build_result("sample.ts", "typescript", 5),
    ]
    prompts = build_prompt_bundle(results)
    assert prompts.file_prompts
    assert prompts.generic_prompts
    assert any(p.language == "python" for p in prompts.file_prompts)


def test_build_prompt_bundle_includes_bash_generic():
    results = [_build_result("sample.sh", "bash", 4)]
    prompts = build_prompt_bundle(results)
    assert any(p.title == "Harden shell safety" for p in prompts.generic_prompts)


def test_generic_prompts_cover_all_languages():
    languages = set(get_all_languages())
    assert languages.issubset(set(GENERIC_PROMPTS_BY_LANGUAGE))
    for language in languages:
        prompts = GENERIC_PROMPTS_BY_LANGUAGE.get(language)
        assert prompts, f"No generic prompts defined for language: {language}"
        for title, prompt in prompts:
            assert title.strip()
            assert prompt.strip()


def test_gap_analysis_no_missing_detectors():
    gaps = build_gap_analysis(["bash"])
    assert gaps.detector_gaps == []


def test_generate_report_includes_sections(tmp_path):
    sample = tmp_path / "sample.py"
    sample.write_text("def foo():\n    pass\n", encoding="utf-8")
    report = generate_report(str(sample), include_prompts=True)
    assert report.markdown.startswith("# Zen of Languages Report")
    assert "Gap Analysis" in report.markdown
    assert report.data["prompts"]


def test_generate_report_zen_perspective_omits_dogma_sections(tmp_path):
    sample = tmp_path / "sample.py"
    sample.write_text("def foo():\n    pass\n", encoding="utf-8")
    report = generate_report(str(sample), perspective=PerspectiveMode.ZEN)
    assert "Universal Dogmas" not in report.markdown
    assert report.data["dogmas"] == []
    assert report.data["dogma_domains"] == []


def test_generate_report_rejects_unimplemented_dogma_perspective(tmp_path):
    sample = tmp_path / "sample.py"
    sample.write_text("def foo():\n    pass\n", encoding="utf-8")
    with pytest.raises(ValueError, match="Perspective 'dogma'"):
        generate_report(str(sample), perspective=PerspectiveMode.DOGMA)


def test_generate_report_testing_perspective_filters_to_testing_rules(tmp_path):
    tests_dir = tmp_path / "tests"
    tests_dir.mkdir()
    sample = tests_dir / "test_sample.py"
    sample.write_text(
        "def test_example():\n"
        '    payload = "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"\n',
        encoding="utf-8",
    )

    report = generate_report(str(sample), perspective=PerspectiveMode.TESTING)

    analysis = report.data["analysis"]
    assert len(analysis) == 1
    assert [violation["rule_id"] for violation in analysis[0]["violations"]] == [
        "python-001",
    ]
    assert "Universal Dogmas" not in report.markdown
    assert report.data["dogmas"] == []
    assert report.data["dogma_domains"] == []


def test_generate_report_projection_perspective_filters_to_requested_family(
    tmp_path,
    monkeypatch: pytest.MonkeyPatch,
):
    from mcp_zen_of_languages.analyzers import registry as registry_module
    from mcp_zen_of_languages.reporting import report as report_module

    sample = tmp_path / "sample.py"
    sample.write_text("def foo():\n    pass\n", encoding="utf-8")
    monkeypatch.setattr(registry_module, "REGISTRY", _projection_registry())
    monkeypatch.setattr(
        report_module,
        "_analyze_targets",
        lambda targets, config_path=None: [_build_projection_result(str(sample))],
    )

    report = generate_report(
        str(sample),
        perspective=PerspectiveMode.PROJECTION,
        project_as="go",
    )

    analysis = report.data["analysis"]
    assert len(analysis) == 1
    assert [violation["rule_id"] for violation in analysis[0]["violations"]] == [
        "python-001",
    ]
    assert "Universal Dogmas" not in report.markdown
    assert report.data["dogmas"] == []
    assert report.data["dogma_domains"] == []
