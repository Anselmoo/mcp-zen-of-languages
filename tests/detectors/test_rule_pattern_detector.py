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
    rule_config = _build_config("pattern_rule")
    config = rule_config(
        detectable_patterns=["TODO"],
        recommended_alternative="Fix the TODO.",
    )
    context = AnalysisContext(code="echo TODO", language="bash")
    violations = RulePatternDetector().detect(context, config)
    assert violations
    assert violations[0].suggestion == "Fix the TODO."


def test_rule_pattern_detector_script_length():
    rule_config = _build_config(
        "script_rule",
        max_script_length_without_functions=(int | None, 2),
    )
    config = rule_config()
    context = AnalysisContext(code="line1\nline2\nline3", language="bash")
    violations = RulePatternDetector().detect(context, config)
    assert violations


def test_rule_pattern_detector_variable_name_length():
    rule_config = _build_config("var_rule", min_variable_name_length=(int | None, 3))
    config = rule_config()
    context = AnalysisContext(code="ab=1", language="bash")
    violations = RulePatternDetector().detect(context, config)
    assert violations


def test_rule_pattern_detector_inheritance_depth():
    rule_config = _build_config("inherit_rule", max_inheritance_depth=(int | None, 1))
    config = rule_config()
    context = AnalysisContext(
        code="class A extends B {}\nclass B extends C {}\n",
        language="javascript",
    )
    violations = RulePatternDetector().detect(context, config)
    assert violations


def test_rule_pattern_detector_identifier_length():
    rule_config = _build_config("ident_rule", min_identifier_length=(int | None, 3))
    config = rule_config()
    context = AnalysisContext(code="const x = 1", language="javascript")
    violations = RulePatternDetector().detect(context, config)
    assert violations


def test_rule_pattern_detector_public_naming():
    rule_config = _build_config("public_rule", public_naming=(str | None, "PascalCase"))
    config = rule_config()
    context = AnalysisContext(code="public class foo {}", language="csharp")
    violations = RulePatternDetector().detect(context, config)
    assert violations


def test_rule_pattern_detector_private_naming():
    rule_config = _build_config(
        "private_rule",
        private_naming=(str | None, "camelCase or _camelCase"),
    )
    config = rule_config()
    context = AnalysisContext(
        code="public class Foo { private int BadName; }",
        language="csharp",
    )
    violations = RulePatternDetector().detect(context, config)
    assert violations


def test_rule_pattern_detector_name_and_required_pattern_branches():
    rule_config = _build_config("required_rule")
    config = rule_config(
        detectable_patterns=["", "!", "!MUST_HAVE"],
        recommended_alternative="Add required marker.",
    )
    context = AnalysisContext(code="echo ok", language="bash")
    detector = RulePatternDetector()

    assert detector.name == "rule_pattern"
    violations = detector.detect(context, config)

    assert len(violations) == 1
    assert violations[0].principle == "required_rule"


def test_rule_pattern_detector_no_violation_return_paths():
    rule_config = _build_config(
        "no_violation_rule",
        max_script_length_without_functions=(int | None, 10),
        min_variable_name_length=(int | None, 3),
        max_inheritance_depth=(int | None, 5),
        min_identifier_length=(int | None, 1),
        public_naming=(str | None, "UnknownStyle"),
        private_naming=(str | None, "UnknownStyle"),
    )
    config = rule_config()
    context = AnalysisContext(
        code=(
            "class Child extends Parent {}\n"
            "echo ok\n"
            "abc=1\n"
            "const goodName = 1\n"
            "public int Name;\n"
            "private int Other;\n"
        ),
        language="javascript",
    )
    violations = RulePatternDetector().detect(context, config)
    assert violations == []


def test_rule_pattern_detector_matches_regex_patterns():
    rule_config = _build_config("regex_rule")
    config = rule_config(
        detectable_patterns=[r"re:key=\{(?:index|itemIndex)\}"],
        recommended_alternative="Use a stable key instead of an array index.",
    )
    context = AnalysisContext(
        code="items.map((item, index) => <li key={index}>{item}</li>)",
        language="react",
    )

    violations = RulePatternDetector().detect(context, config)

    assert len(violations) == 1
    assert violations[0].location.line == 1
    assert violations[0].location.column > 0


def test_rule_pattern_detector_required_regex_patterns():
    rule_config = _build_config("required_regex_rule")
    config = rule_config(
        detectable_patterns=[r"!re:export const metadata"],
        recommended_alternative="Define metadata for the route.",
    )
    context = AnalysisContext(
        code="export default function Page() {}", language="nextjs"
    )

    violations = RulePatternDetector().detect(context, config)

    assert len(violations) == 1
    assert violations[0].principle == "required_regex_rule"
