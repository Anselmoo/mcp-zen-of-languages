from mcp_zen_of_languages.analyzers.base import AnalysisContext
from mcp_zen_of_languages.analyzers.registry import REGISTRY
from mcp_zen_of_languages.languages.typescript.detectors import (
    TsAnyUsageDetector,
    TsEnumConstDetector,
    TsInterfacePreferenceDetector,
    TsNonNullAssertionDetector,
    TsReadonlyDetector,
    TsReturnTypeDetector,
    TsStrictModeDetector,
    TsTypeGuardDetector,
    TsUnknownOverAnyDetector,
    TsUtilityTypesDetector,
)
from mcp_zen_of_languages.languages.typescript.rules import TYPESCRIPT_ZEN


def config_for(detector_type: str):
    return next(
        cfg
        for cfg in REGISTRY.configs_from_rules(TYPESCRIPT_ZEN)
        if cfg.type == detector_type
    )


def run_detector(detector, code, config):
    ctx = AnalysisContext(code=code, path=None, language="typescript")
    return detector.detect(ctx, config)


def test_ts_any_usage_detector():
    code = "const value: any = 1;"
    violations = run_detector(TsAnyUsageDetector(), code, config_for("ts_any_usage"))
    assert any("any" in v.message for v in violations)


def test_ts_strict_mode_detector():
    violations = run_detector(TsStrictModeDetector(), "", config_for("ts_strict_mode"))
    assert any("strict" in v.message for v in violations)


def test_ts_interface_preference_detector():
    code = "type Foo = { bar: string };"
    violations = run_detector(
        TsInterfacePreferenceDetector(),
        code,
        config_for("ts_interface_preference"),
    )
    assert any("Type aliases" in v.message for v in violations)


def test_ts_return_type_detector():
    code = "export function foo(x: number) { return x; }"
    violations = run_detector(
        TsReturnTypeDetector(),
        code,
        config_for("ts_return_types"),
    )
    assert any("return type" in v.message for v in violations)


def test_ts_readonly_detector():
    code = "interface Foo { bar: string }"
    cfg = config_for("ts_readonly").model_copy(update={"min_readonly_occurrences": 1})
    violations = run_detector(TsReadonlyDetector(), code, cfg)
    assert any("readonly" in v.message for v in violations)


def test_ts_type_guard_detector():
    code = "const x = value as Foo;"
    violations = run_detector(TsTypeGuardDetector(), code, config_for("ts_type_guards"))
    assert any("assertions" in v.message for v in violations)


def test_ts_utility_types_detector():
    code = "type Foo = { bar: string };"
    cfg = config_for("ts_utility_types").model_copy(
        update={"min_utility_type_usage": 1, "min_object_type_aliases": 1},
    )
    violations = run_detector(TsUtilityTypesDetector(), code, cfg)
    assert any("Manual type transformations" in v.message for v in violations)


def test_ts_non_null_assertion_detector():
    code = "const x = foo!;"
    violations = run_detector(
        TsNonNullAssertionDetector(),
        code,
        config_for("ts_non_null_assertions"),
    )
    assert any("Non-null assertions" in v.message for v in violations)


def test_ts_non_null_assertion_detector_chained():
    code = "const x = foo!.bar!;"
    violations = run_detector(
        TsNonNullAssertionDetector(),
        code,
        config_for("ts_non_null_assertions"),
    )
    assert any("Non-null assertions" in v.message for v in violations)


def test_ts_enum_const_detector():
    code = "const Colors = { Red: 'red' };"
    violations = run_detector(TsEnumConstDetector(), code, config_for("ts_enum_const"))
    assert any("Plain objects" in v.message for v in violations)


def test_ts_unknown_over_any_detector():
    code = "let data: any;"
    violations = run_detector(
        TsUnknownOverAnyDetector(),
        code,
        config_for("ts_unknown_over_any"),
    )
    assert any("any" in v.message for v in violations)
