from mcp_zen_of_languages.analyzers.pipeline import (
    PipelineConfig,
    merge_pipeline_overrides,
)
from mcp_zen_of_languages.analyzers.registry import REGISTRY
from mcp_zen_of_languages.languages.configs import (
    LineLengthConfig,
)
from mcp_zen_of_languages.languages.python.rules import PYTHON_ZEN


def test_registry_configs_from_rules_contains_principle():
    configs = REGISTRY.configs_from_rules(PYTHON_ZEN)
    line_cfg = next(cfg for cfg in configs if cfg.type == "line_length")
    assert line_cfg.principle == "Beautiful is better than ugly"
    assert line_cfg.severity == 4
    assert line_cfg.violation_messages
    missing_cfg = next(cfg for cfg in configs if cfg.type == "sparse_code")
    assert missing_cfg.principle == "Sparse is better than dense"
    assert missing_cfg.severity == 5


def test_registry_configs_from_rules_all_python_rules():
    configs = REGISTRY.configs_from_rules(PYTHON_ZEN)
    types = {cfg.type for cfg in configs}
    assert "sparse_code" in types
    assert "consistency" in types
    assert "explicitness" in types
    assert "namespace_usage" in types


def test_registry_configs_from_rules_all_typescript_rules():
    from mcp_zen_of_languages.languages.typescript.rules import TYPESCRIPT_ZEN

    configs = REGISTRY.configs_from_rules(TYPESCRIPT_ZEN)
    types = {cfg.type for cfg in configs}
    assert "ts_any_usage" in types
    assert "ts_strict_mode" in types
    assert "ts_interface_preference" in types
    assert "ts_return_types" in types
    assert "ts_readonly" in types
    assert "ts_type_guards" in types
    assert "ts_utility_types" in types
    assert "ts_non_null_assertions" in types
    assert "ts_enum_const" in types
    assert "ts_unknown_over_any" in types


def test_merge_pipeline_overrides_applies_value():
    base = PipelineConfig.from_rules("python")
    override = PipelineConfig(
        language="python",
        detectors=[LineLengthConfig(max_line_length=120)],
    )
    merged = merge_pipeline_overrides(base, override)
    merged_line = next(cfg for cfg in merged.detectors if cfg.type == "line_length")
    assert merged_line.max_line_length == 120
