from __future__ import annotations

from typing import Literal

from pydantic import create_model

from mcp_zen_of_languages.analyzers.base import AnalysisContext
from mcp_zen_of_languages.languages.configs import DetectorConfig
from mcp_zen_of_languages.languages.rule_pattern import RulePatternDetector


def _build_config(name: str, **fields):
    return create_model(
        name,
        __base__=DetectorConfig,
        type=(Literal[name], name),
        **fields,
    )


def test_rule_pattern_detector_matches_patterns():
    RuleConfig = _build_config("pattern_rule")
    config = RuleConfig(
        detectable_patterns=["TODO"],
        recommended_alternative="Fix the TODO.",
    )
    context = AnalysisContext(code="echo TODO", language="bash")
    violations = RulePatternDetector().detect(context, config)
    assert violations
    assert violations[0].suggestion == "Fix the TODO."


def test_rule_pattern_detector_script_length():
    RuleConfig = _build_config(
        "script_rule", max_script_length_without_functions=(int | None, 2)
    )
    config = RuleConfig()
    context = AnalysisContext(code="line1\nline2\nline3", language="bash")
    violations = RulePatternDetector().detect(context, config)
    assert violations


def test_rule_pattern_detector_variable_name_length():
    RuleConfig = _build_config("var_rule", min_variable_name_length=(int | None, 3))
    config = RuleConfig()
    context = AnalysisContext(code="ab=1", language="bash")
    violations = RulePatternDetector().detect(context, config)
    assert violations


def test_rule_pattern_detector_inheritance_depth():
    RuleConfig = _build_config("inherit_rule", max_inheritance_depth=(int | None, 1))
    config = RuleConfig()
    context = AnalysisContext(
        code="class A extends B {}\nclass B extends C {}\n", language="javascript"
    )
    violations = RulePatternDetector().detect(context, config)
    assert violations


def test_rule_pattern_detector_identifier_length():
    RuleConfig = _build_config("ident_rule", min_identifier_length=(int | None, 3))
    config = RuleConfig()
    context = AnalysisContext(code="const x = 1", language="javascript")
    violations = RulePatternDetector().detect(context, config)
    assert violations


def test_rule_pattern_detector_public_naming():
    RuleConfig = _build_config("public_rule", public_naming=(str | None, "PascalCase"))
    config = RuleConfig()
    context = AnalysisContext(code="public class foo {}", language="csharp")
    violations = RulePatternDetector().detect(context, config)
    assert violations


def test_rule_pattern_detector_private_naming():
    RuleConfig = _build_config(
        "private_rule", private_naming=(str | None, "camelCase or _camelCase")
    )
    config = RuleConfig()
    context = AnalysisContext(
        code="public class Foo { private int BadName; }", language="csharp"
    )
    violations = RulePatternDetector().detect(context, config)
    assert violations
