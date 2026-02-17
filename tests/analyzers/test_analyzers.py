from __future__ import annotations

from mcp_zen_of_languages.analyzers.analyzer_factory import create_analyzer
from mcp_zen_of_languages.analyzers.base import AnalysisContext
from mcp_zen_of_languages.analyzers.pipeline import PipelineConfig
from mcp_zen_of_languages.analyzers.registry import REGISTRY
from mcp_zen_of_languages.languages.python.rules import PYTHON_ZEN


def test_create_analyzer_invalid_language():
    try:
        create_analyzer("unknown")
    except ValueError as exc:
        assert "Unsupported" in str(exc)
    else:
        raise AssertionError("Expected ValueError")


def test_pipeline_config_from_rules():
    config = PipelineConfig.from_rules("python")
    assert config.detectors


def test_registry_configs_from_rules_contains_detectors():
    configs = REGISTRY.configs_from_rules(PYTHON_ZEN)
    assert configs
    assert all(hasattr(cfg, "type") for cfg in configs)


def test_analysis_context_defaults():
    context = AnalysisContext(code="def foo():\n    pass\n", language="python")
    assert context.code
