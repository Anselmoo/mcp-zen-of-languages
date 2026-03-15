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
from mcp_zen_of_languages.perspectives import apply_perspective_to_result
from mcp_zen_of_languages.perspectives import validate_perspective


class DummyConfig(DetectorConfig):
    type: Literal["dummy"] = "dummy"


class DummyDetector(ViolationDetector[DummyConfig]):
    @property
    def name(self) -> str:
        return "dummy"

    def detect(self, context, config):
        return []


def _build_result(*, path: str | None, language: str) -> AnalysisResult:
    return AnalysisResult(
        language=language,
        path=path,
        metrics=Metrics(
            cyclomatic=CyclomaticSummary(blocks=[], average=0.0),
            maintainability_index=100.0,
            lines_of_code=1,
        ),
        violations=[
            Violation(
                principle="Line length",
                severity=3,
                message="line too long",
                detector_id="line_length",
                rule_id="python-001",
            ),
            Violation(
                principle="Docstrings",
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


def test_validate_perspective_accepts_testing() -> None:
    validate_perspective(PerspectiveMode.TESTING)


def test_validate_perspective_accepts_projection_with_target() -> None:
    validate_perspective(PerspectiveMode.PROJECTION, project_as="go")


def test_validate_perspective_rejects_projection_without_target() -> None:
    with pytest.raises(ValueError, match="requires a non-empty 'project_as'"):
        validate_perspective(PerspectiveMode.PROJECTION)


def test_apply_testing_perspective_filters_to_pytest_rules() -> None:
    result = _build_result(path="tests/test_sample.py", language="python")

    filtered = apply_perspective_to_result(result, PerspectiveMode.TESTING)

    assert [violation.rule_id for violation in filtered.violations] == ["python-001"]
    assert filtered.dogma_analysis is None


def test_apply_testing_perspective_rejects_non_test_file() -> None:
    result = _build_result(path="src/sample.py", language="python")

    with pytest.raises(ValueError, match="recognized test-file path"):
        apply_perspective_to_result(result, PerspectiveMode.TESTING)


def test_apply_testing_perspective_rejects_unconfigured_family() -> None:
    result = _build_result(path="foo_test.go", language="go")

    with pytest.raises(ValueError, match="not configured for language='go'"):
        apply_perspective_to_result(result, PerspectiveMode.TESTING)


def test_apply_projection_perspective_filters_to_requested_family(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from mcp_zen_of_languages.analyzers import registry as registry_module

    monkeypatch.setattr(registry_module, "REGISTRY", _projection_registry())
    result = _build_result(path="src/sample.py", language="python")

    filtered = apply_perspective_to_result(
        result,
        PerspectiveMode.PROJECTION,
        project_as="go",
    )

    assert [violation.rule_id for violation in filtered.violations] == ["python-001"]
    assert filtered.dogma_analysis is None


def test_apply_projection_perspective_rejects_unconfigured_family(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from mcp_zen_of_languages.analyzers import registry as registry_module

    monkeypatch.setattr(registry_module, "REGISTRY", _projection_registry())
    result = _build_result(path="src/sample.py", language="python")

    with pytest.raises(
        ValueError,
        match="not configured for language='python' project_as='typescript'",
    ):
        apply_perspective_to_result(
            result,
            PerspectiveMode.PROJECTION,
            project_as="typescript",
        )
