from __future__ import annotations

from mcp_zen_of_languages.analyzers.base import AnalysisContext
from mcp_zen_of_languages.languages.configs import (
    JsonArrayOrderConfig,
    JsonDateFormatConfig,
    JsonKeyCasingConfig,
    JsonNullHandlingConfig,
    JsonNullSprawlConfig,
    JsonSchemaConsistencyConfig,
    JsonStrictnessConfig,
)
from mcp_zen_of_languages.languages.json.detectors import (
    JsonArrayOrderDetector,
    JsonDateFormatDetector,
    JsonKeyCasingDetector,
    JsonNullHandlingDetector,
    JsonNullSprawlDetector,
    JsonSchemaConsistencyDetector,
    JsonStrictnessDetector,
)


def _detect(detector, code: str, config):
    return detector.detect(AnalysisContext(code=code, language="json"), config)


def test_json_trailing_commas_strict_vs_json5():
    code = '{ "name": "demo", }'
    assert _detect(JsonStrictnessDetector(), code, JsonStrictnessConfig())
    assert not _detect(
        JsonStrictnessDetector(),
        code,
        JsonStrictnessConfig(target_format="json5"),
    )


def test_json_deep_nesting_violation():
    code = '{"a":{"b":{"c":{"d":{"e":{"f":1}}}}}}'
    violations = _detect(
        JsonSchemaConsistencyDetector(),
        code,
        JsonSchemaConsistencyConfig(max_depth=5),
    )
    assert violations


def test_json_duplicate_keys_violation():
    violations = _detect(
        JsonDateFormatDetector(),
        '{"a": 1, "a": 2}',
        JsonDateFormatConfig(),
    )
    assert violations


def test_json_magic_string_repetition_violation():
    violations = _detect(
        JsonNullHandlingDetector(),
        '{"status":"active","state":"active","mode":"active"}',
        JsonNullHandlingConfig(min_repetition=3),
    )
    assert violations


def test_json_inconsistent_key_casing_violation():
    violations = _detect(
        JsonKeyCasingDetector(),
        '{"camelCase": 1, "snake_case": 2}',
        JsonKeyCasingConfig(),
    )
    assert violations


def test_json_oversized_inline_array_violation():
    violations = _detect(
        JsonArrayOrderDetector(),
        '{"values":[1,2,3,4,5]}',
        JsonArrayOrderConfig(max_inline_array_size=4),
    )
    assert violations


def test_json_null_sprawl_violation():
    violations = _detect(
        JsonNullSprawlDetector(),
        '{"a":null,"b":null,"c":null,"d":null}',
        JsonNullSprawlConfig(max_null_values=3),
    )
    assert violations
