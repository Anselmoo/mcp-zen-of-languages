from __future__ import annotations

from mcp_zen_of_languages.analyzers.pipeline import (
    PipelineConfig,
    merge_pipeline_overrides,
    project_rules_to_configs,
)
from mcp_zen_of_languages.languages.python.rules import PYTHON_ZEN


def test_pipeline_config_from_rules():
    config = PipelineConfig.from_rules("python")
    assert config.detectors


def test_project_rules_to_configs():
    configs = project_rules_to_configs(PYTHON_ZEN)
    assert configs


def test_merge_pipeline_overrides():
    base = PipelineConfig.from_rules("python")
    overrides = PipelineConfig(language="python", detectors=base.detectors[:1])
    merged = merge_pipeline_overrides(base, overrides)
    assert len(merged.detectors) >= 1


def test_merge_pipeline_overrides_language_mismatch():
    base = PipelineConfig.from_rules("python")
    overrides = PipelineConfig(language="rust", detectors=base.detectors[:1])
    try:
        merge_pipeline_overrides(base, overrides)
    except ValueError as exc:
        assert "language" in str(exc)
    else:
        raise AssertionError("Expected ValueError")
