from __future__ import annotations

import types

import pytest

from mcp_zen_of_languages.analyzers.base import LocationHelperMixin
from mcp_zen_of_languages.analyzers.pipeline import PipelineConfig
from mcp_zen_of_languages.languages.placeholder import PlaceholderDetector
from mcp_zen_of_languages.models import (
    AnalysisResult,
    CyclomaticSummary,
    Metrics,
    Violation,
)
from mcp_zen_of_languages.reporting.gaps import build_gap_analysis
from mcp_zen_of_languages.reporting.prompts import build_prompt_bundle
from mcp_zen_of_languages.reporting.report import _format_prompts_markdown
from mcp_zen_of_languages.rules.base_models import (
    LanguageZenPrinciples,
    PrincipleCategory,
    ZenPrinciple,
)


class DummyLocation(LocationHelperMixin):
    pass


def test_location_helper_paths():
    helper = DummyLocation()
    loc = helper.find_location_by_substring("abc", "z")
    assert loc.line == 1
    assert helper.ast_node_to_location(None, None) is None


def test_placeholder_detector():
    detector = PlaceholderDetector()
    assert detector.name == "placeholder_detector"


def test_pipeline_validator_type_error():
    with pytest.raises(TypeError):
        PipelineConfig.model_validate({"language": "python", "detectors": "bad"})


def test_models_getitem_access():
    cyclomatic = CyclomaticSummary(blocks=[], average=0.0)
    metrics = Metrics(cyclomatic=cyclomatic, maintainability_index=0.0, lines_of_code=1)
    result = AnalysisResult(
        language="python",
        path="file.py",
        metrics=metrics,
        violations=[Violation(principle="p", severity=3, message="m")],
        overall_score=97.0,
    )
    assert result["language"] == "python"


def test_gap_analysis_unknown_language():
    gaps = build_gap_analysis(["unknown"])
    assert gaps.detector_gaps == []


def test_prompt_bundle_generic_prompts():
    violation = Violation(principle="p", severity=4, message="m")
    cyclomatic = CyclomaticSummary(blocks=[], average=0.0)
    metrics = Metrics(cyclomatic=cyclomatic, maintainability_index=0.0, lines_of_code=1)
    result = AnalysisResult(
        language="python",
        path="file.py",
        metrics=metrics,
        violations=[violation],
        overall_score=90.0,
    )
    prompts = build_prompt_bundle([result])
    assert prompts.file_prompts


def test_language_zen_helpers():
    zen = LanguageZenPrinciples(
        language="demo",
        name="Demo",
        philosophy="Testing",
        source_text="none",
        source_url="https://example.com/none",
        principles=[
            ZenPrinciple(
                id="demo-1",
                principle="One",
                category=PrincipleCategory.CORRECTNESS,
                severity=7,
                description="desc",
                violations=[],
            )
        ],
    )
    assert zen.principle_count == 1
    assert zen.get_by_id("demo-1") is not None
    assert zen.get_by_category(PrincipleCategory.CORRECTNESS)
    assert zen.get_by_severity(7)


def test_format_prompts_markdown_empty():
    context = types.SimpleNamespace(prompts=None)
    assert _format_prompts_markdown(context) == []
