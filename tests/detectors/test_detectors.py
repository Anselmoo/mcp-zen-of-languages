from mcp_zen_of_languages.analyzers.base import AnalysisContext
from mcp_zen_of_languages.analyzers.registry import REGISTRY
from mcp_zen_of_languages.languages.python.detectors import (
    BareExceptDetector,
    ComplexOneLinersDetector,
    ConsistencyDetector,
    CyclomaticComplexityDetector,
    ExplicitnessDetector,
    LineLengthDetector,
    MagicNumberDetector,
    NamespaceUsageDetector,
    NameStyleDetector,
    ShortVariableNamesDetector,
    SparseCodeDetector,
    StarImportDetector,
)
from mcp_zen_of_languages.languages.python.rules import PYTHON_ZEN


def run_detector(detector, code, config):
    ctx = AnalysisContext(code=code, path=None, language="python")
    return detector.detect(ctx, config)


def config_for(detector_type: str):
    return next(
        cfg
        for cfg in REGISTRY.configs_from_rules(PYTHON_ZEN)
        if cfg.type == detector_type
    )


def test_name_style_detector():
    code = """
def BadName():
    pass

FOO = 1
barBaz = 2
    """
    detector = NameStyleDetector()
    violations = run_detector(detector, code, config_for("name_style"))
    assert any("Poor naming conventions" in v.message for v in violations)


def test_star_import_detector():
    code = "from module import *\nprint('hi')\n"
    detector = StarImportDetector()
    violations = run_detector(detector, code, config_for("star_imports"))
    assert any("Overuse of * imports" in v.message for v in violations)


def test_bare_except_detector():
    code = "try:\n    x=1\nexcept:\n    pass\n"
    detector = BareExceptDetector()
    violations = run_detector(detector, code, config_for("bare_except"))
    assert any("Bare except clauses" in v.message for v in violations)


def test_empty_except_detector():
    code = "try:\n    x=1\nexcept Exception:\n    pass\n"
    detector = BareExceptDetector()
    violations = run_detector(detector, code, config_for("bare_except"))
    assert any("Empty except blocks" in v.message for v in violations)


def test_magic_number_detector():
    code = "answer = 42\n"
    detector = MagicNumberDetector()
    violations = run_detector(detector, code, config_for("magic_number"))
    assert any("Magic numbers" in v.message for v in violations)


def test_magic_number_detector_skips_constants():
    code = "MAX_COUNT = 42\n"
    detector = MagicNumberDetector()
    violations = run_detector(detector, code, config_for("magic_number"))
    assert not violations


def test_magic_number_detector_ignores_comments():
    code = "# magic number 42\n"
    detector = MagicNumberDetector()
    violations = run_detector(detector, code, config_for("magic_number"))
    assert not violations


def test_complex_one_liners_detector():
    code = "values = [x for x in items for y in items]\n"
    detector = ComplexOneLinersDetector()
    violations = run_detector(detector, code, config_for("complex_one_liners"))
    assert any("comprehensions" in v.message for v in violations)


def test_complex_one_liners_detector_ternary():
    code = "value = 1 if condition else 2\n"
    detector = ComplexOneLinersDetector()
    config = config_for("complex_one_liners").model_copy(update={"max_line_length": 10})
    violations = run_detector(detector, code, config)
    assert violations


def test_short_variable_names_detector():
    code = "a = 1\nvalue = 2\n"
    detector = ShortVariableNamesDetector()
    violations = run_detector(detector, code, config_for("short_variable_names"))
    assert any("variable names" in v.suggestion for v in violations)


def test_short_variable_names_detector_loop():
    code = "for a in items:\n    pass\n"
    detector = ShortVariableNamesDetector()
    violations = run_detector(detector, code, config_for("short_variable_names"))
    assert violations


def test_short_variable_names_detector_allows_loop_short_names():
    code = "for i in items:\n    pass\n"
    detector = ShortVariableNamesDetector()
    violations = run_detector(detector, code, config_for("short_variable_names"))
    assert not violations


def test_short_variable_names_detector_heuristic():
    code = "a = 1\nif"
    detector = ShortVariableNamesDetector()
    violations = run_detector(detector, code, config_for("short_variable_names"))
    assert violations


def test_short_variable_names_detector_heuristic_skips_long():
    code = "long_name = 1\nif"
    detector = ShortVariableNamesDetector()
    violations = run_detector(detector, code, config_for("short_variable_names"))
    assert not violations


def test_short_variable_names_detector_ann_assign():
    code = "a: int = 1\n"
    detector = ShortVariableNamesDetector()
    violations = run_detector(detector, code, config_for("short_variable_names"))
    assert violations


def test_short_variable_names_detector_skips_constants():
    code = "MAX = 1\n"
    detector = ShortVariableNamesDetector()
    violations = run_detector(detector, code, config_for("short_variable_names"))
    assert not violations


def test_short_variable_names_detector_tuple_assignment():
    code = "a, bb = (1, 2)\n"
    detector = ShortVariableNamesDetector()
    violations = run_detector(detector, code, config_for("short_variable_names"))
    assert violations


def test_cyclomatic_complexity_detector_name():
    assert CyclomaticComplexityDetector().name == "cyclomatic_complexity"


def test_line_length_detector():
    code = "a = '" + "x" * 120 + "'\n"
    detector = LineLengthDetector()
    violations = run_detector(detector, code, config_for("line_length"))
    assert any("whitespace" in v.message for v in violations)


def test_sparse_code_detector():
    code = "a = 1; b = 2\n"
    detector = SparseCodeDetector()
    base_cfg = config_for("sparse_code")
    cfg = base_cfg.model_copy(update={"max_statements_per_line": 1})
    violations = run_detector(detector, code, cfg)
    assert any("Multiple statements on one line" in v.message for v in violations)


def test_consistency_detector():
    code = "def foo():\n    pass\n\ndef Bar():\n    pass\n"
    detector = ConsistencyDetector()
    base_cfg = config_for("consistency")
    cfg = base_cfg.model_copy(update={"max_naming_styles": 1})
    violations = run_detector(detector, code, cfg)
    assert any(
        "Different naming conventions within same module" in v.message
        for v in violations
    )


def test_explicitness_detector():
    code = "def foo(x, y: int):\n    return x + y\n"
    detector = ExplicitnessDetector()
    base_cfg = config_for("explicitness")
    cfg = base_cfg.model_copy(update={"require_type_hints": True})
    violations = run_detector(detector, code, cfg)
    assert any("Missing input validation" in v.message for v in violations)


def test_namespace_usage_detector():
    code = "a = 1\nb = 2\nc = 3\nd = 4\n__all__ = ['a', 'b', 'c', 'd', 'e']\n"
    detector = NamespaceUsageDetector()
    base_cfg = config_for("namespace_usage")
    cfg = base_cfg.model_copy(update={"max_top_level_symbols": 3, "max_exports": 4})
    violations = run_detector(detector, code, cfg)
    assert any(
        "Polluting global namespace" in v.message
        or "Too many items in __all__" in v.message
        for v in violations
    )


def test_js_detectors_smoke():
    from mcp_zen_of_languages.languages.configs import (
        JsCallbackNestingConfig,
        JsNoVarConfig,
        JsStrictEqualityConfig,
    )
    from mcp_zen_of_languages.languages.javascript.detectors import (
        JsCallbackNestingDetector,
        JsNoVarDetector,
        JsStrictEqualityDetector,
    )

    code = (
        "function foo() {\n  function bar() {\n    if (a == b) { var x = 1; }\n  }\n}\n"
    )
    context = AnalysisContext(code=code, language="javascript")
    nesting_config = JsCallbackNestingConfig().model_copy(
        update={"max_callback_nesting": 1},
    )
    assert JsCallbackNestingDetector().detect(context, nesting_config)
    assert JsNoVarDetector().detect(context, JsNoVarConfig())
    assert JsStrictEqualityDetector().detect(context, JsStrictEqualityConfig())


def test_powershell_detectors_smoke():
    from mcp_zen_of_languages.languages.configs import (
        PowerShellApprovedVerbConfig,
        PowerShellErrorHandlingConfig,
        PowerShellPascalCaseConfig,
    )
    from mcp_zen_of_languages.languages.powershell.detectors import (
        PowerShellApprovedVerbDetector,
        PowerShellErrorHandlingDetector,
        PowerShellPascalCaseDetector,
    )

    code = "function customThing-Thing { }\n"
    context = AnalysisContext(code=code, language="powershell")
    assert PowerShellApprovedVerbDetector().detect(
        context,
        PowerShellApprovedVerbConfig(),
    )
    assert PowerShellErrorHandlingDetector().detect(
        context,
        PowerShellErrorHandlingConfig(),
    )
    assert PowerShellPascalCaseDetector().detect(context, PowerShellPascalCaseConfig())


def test_ruby_detectors_smoke():
    from mcp_zen_of_languages.languages.configs import (
        RubyMethodChainConfig,
        RubyNamingConventionConfig,
    )
    from mcp_zen_of_languages.languages.ruby.detectors import (
        RubyMethodChainDetector,
        RubyNamingConventionDetector,
    )

    code = "def BadName\n  foo.bar.baz.qux.quux.quuz\nend\n"
    context = AnalysisContext(code=code, language="ruby")
    assert RubyNamingConventionDetector().detect(context, RubyNamingConventionConfig())
    assert RubyMethodChainDetector().detect(context, RubyMethodChainConfig())
