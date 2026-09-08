from __future__ import annotations

import ast

from mcp_zen_of_languages.analyzers.base import AnalysisContext
from mcp_zen_of_languages.languages.configs import ConsistencyConfig
from mcp_zen_of_languages.languages.configs import ExplicitnessConfig
from mcp_zen_of_languages.languages.configs import LongFunctionConfig
from mcp_zen_of_languages.languages.configs import NamespaceConfig
from mcp_zen_of_languages.languages.configs import NestingDepthConfig
from mcp_zen_of_languages.languages.configs import UnusedArgumentUtilizationConfig
from mcp_zen_of_languages.languages.python.detectors import ConsistencyDetector
from mcp_zen_of_languages.languages.python.detectors import ExplicitnessDetector
from mcp_zen_of_languages.languages.python.detectors import LongFunctionDetector
from mcp_zen_of_languages.languages.python.detectors import NamespaceUsageDetector
from mcp_zen_of_languages.languages.python.detectors import NestingDepthDetector
from mcp_zen_of_languages.languages.python.detectors import (
    UnusedArgumentUtilizationDetector,
)


def test_consistency_detector_flags_styles():
    code = "def foo():\n    pass\n\ndef Bar():\n    pass\n"
    context = AnalysisContext(code=code, language="python")
    config = ConsistencyConfig().model_copy(update={"max_naming_styles": 1})
    violations = ConsistencyDetector().detect(context, config)
    assert violations


def test_explicitness_detector_requires_hints():
    code = "def foo(x):\n    return x\n"
    context = AnalysisContext(code=code, language="python")
    violations = ExplicitnessDetector().detect(context, ExplicitnessConfig())
    assert violations


def test_namespace_usage_detector_flags_exports():
    code = "a=1\n__all__ = ['a', 'b', 'c', 'd', 'e']\n"
    context = AnalysisContext(code=code, language="python")
    config = NamespaceConfig().model_copy(
        update={"max_top_level_symbols": 0, "max_exports": 1},
    )
    violations = NamespaceUsageDetector().detect(context, config)
    assert violations


def test_nesting_depth_detector_flags():
    code = "if True:\n    if True:\n        pass\n"
    context = AnalysisContext(code=code, language="python")
    config = NestingDepthConfig().model_copy(update={"max_nesting_depth": 0})
    violations = NestingDepthDetector().detect(context, config)
    assert violations


def test_nesting_depth_detector_flags_nested_loops():
    code = "for i in range(3):\n    for j in range(3):\n        pass\n"
    context = AnalysisContext(code=code, language="python")
    config = NestingDepthConfig().model_copy(update={"max_nesting_depth": 5})
    violations = NestingDepthDetector().detect(context, config)
    assert violations


def test_long_function_detector_flags():
    code = "def foo():\n" + "    x=1\n" * 10
    context = AnalysisContext(code=code, language="python")
    config = LongFunctionConfig().model_copy(update={"max_function_length": 1})
    violations = LongFunctionDetector().detect(context, config)
    assert violations


def test_unused_argument_utilization_detector_override_suggests_logging():
    code = (
        "from typing import override\n\n"
        "class Base:\n"
        "    def process(self, context):\n"
        "        raise NotImplementedError\n\n"
        "class Child(Base):\n"
        "    @override\n"
        "    def process(self, context):\n"
        "        return 1\n"
    )
    context = AnalysisContext(code=code, language="python")
    violations = UnusedArgumentUtilizationDetector().detect(
        context,
        UnusedArgumentUtilizationConfig(),
    )
    assert violations
    assert any("inherited" in (v.suggestion or "") for v in violations)


def test_unused_argument_utilization_detector_excludes_abstract_methods():
    code = (
        "from abc import abstractmethod\n\n"
        "class Base:\n"
        "    @abstractmethod\n"
        "    def process(self, context):\n"
        "        ...\n"
    )
    context = AnalysisContext(code=code, language="python")
    violations = UnusedArgumentUtilizationDetector().detect(
        context,
        UnusedArgumentUtilizationConfig(),
    )
    assert violations == []


def test_unused_argument_utilization_detector_excludes_stub_bodies():
    code = "def process(context):\n    ...\n"
    context = AnalysisContext(code=code, language="python")
    violations = UnusedArgumentUtilizationDetector().detect(
        context,
        UnusedArgumentUtilizationConfig(),
    )
    assert violations == []


def test_unused_argument_utilization_detector_excludes_varargs_and_kwargs():
    code = "def process(user_id, *args, **kwargs):\n    return user_id\n"
    context = AnalysisContext(code=code, language="python")
    violations = UnusedArgumentUtilizationDetector().detect(
        context,
        UnusedArgumentUtilizationConfig(),
    )
    assert violations == []


def test_unused_argument_utilization_detector_flags_underscore_prefixed_names():
    code = "def process(_unused):\n    return 1\n"
    context = AnalysisContext(code=code, language="python")
    violations = UnusedArgumentUtilizationDetector().detect(
        context,
        UnusedArgumentUtilizationConfig(),
    )
    assert any("_unused" in v.message for v in violations)


def test_unused_argument_utilization_detector_never_flags_self():
    code = "class Widget:\n    def render(self):\n        return 1\n"
    context = AnalysisContext(code=code, language="python")
    violations = UnusedArgumentUtilizationDetector().detect(
        context,
        UnusedArgumentUtilizationConfig(),
    )
    assert violations == []


def test_unused_argument_utilization_detector_excludes_docstring_stub_bodies():
    """A docstring followed by ``...`` (documented Protocol style) is a stub."""
    code = (
        "class Proto:\n"
        "    def meth(self, value: int) -> int:\n"
        '        """Proto method."""\n'
        "        ...\n"
    )
    context = AnalysisContext(code=code, language="python")
    violations = UnusedArgumentUtilizationDetector().detect(
        context,
        UnusedArgumentUtilizationConfig(),
    )
    assert violations == []


def test_unused_argument_utilization_detector_infers_override_from_base_class():
    """A subclass method without @override still gets the inherited-signature hint."""
    code = (
        "class Base:\n"
        "    def process(self, value):\n"
        "        raise NotImplementedError\n\n"
        "class Child(Base):\n"
        "    def process(self, value):\n"
        "        return 1\n"
    )
    context = AnalysisContext(code=code, language="python")
    violations = UnusedArgumentUtilizationDetector().detect(
        context,
        UnusedArgumentUtilizationConfig(),
    )
    child_violations = [v for v in violations if v.location.line > 4]
    assert child_violations
    assert all("inherited" in (v.suggestion or "") for v in child_violations)


def test_unused_argument_utilization_detector_free_function_keeps_generic_wording():
    """A module-level function (no enclosing class) keeps the generic wording."""
    code = "def process(value):\n    return 1\n"
    context = AnalysisContext(code=code, language="python")
    violations = UnusedArgumentUtilizationDetector().detect(
        context,
        UnusedArgumentUtilizationConfig(),
    )
    assert violations
    assert all(
        "Integrate it into logic or remove the argument" in (v.suggestion or "")
        for v in violations
    )


def test_unused_argument_utilization_detector_base_less_class_keeps_generic_wording():
    """A method on a class with no base classes keeps the generic wording."""
    code = "class Widget:\n    def process(self, value):\n        return 1\n"
    context = AnalysisContext(code=code, language="python")
    violations = UnusedArgumentUtilizationDetector().detect(
        context,
        UnusedArgumentUtilizationConfig(),
    )
    assert violations
    assert all(
        "Integrate it into logic or remove the argument" in (v.suggestion or "")
        for v in violations
    )


def test_unused_argument_utilization_detector_exclude_abstract_methods_flag():
    """exclude_abstract_methods only takes effect on a non-stub abstract body."""
    code = (
        "from abc import abstractmethod\n\n"
        "class Base:\n"
        "    @abstractmethod\n"
        "    def process(self, context):\n"
        "        return None\n"
    )
    context = AnalysisContext(code=code, language="python")

    excluded = UnusedArgumentUtilizationDetector().detect(
        context,
        UnusedArgumentUtilizationConfig(exclude_abstract_methods=True),
    )
    assert excluded == []

    included = UnusedArgumentUtilizationDetector().detect(
        context,
        UnusedArgumentUtilizationConfig(exclude_abstract_methods=False),
    )
    assert any("context" in v.message for v in included)


def test_unused_argument_utilization_detector_suggest_logging_flag():
    """suggest_logging toggles the logging-oriented remediation suggestion."""
    code = (
        "import logging\n\n"
        "logger = logging.getLogger(__name__)\n\n"
        "def process(value):\n"
        "    logger.info('start')\n"
        "    return 1\n"
    )
    context = AnalysisContext(code=code, language="python")

    with_logging = UnusedArgumentUtilizationDetector().detect(
        context,
        UnusedArgumentUtilizationConfig(suggest_logging=True),
    )
    assert with_logging
    assert any("logging" in (v.suggestion or "") for v in with_logging)

    without_logging = UnusedArgumentUtilizationDetector().detect(
        context,
        UnusedArgumentUtilizationConfig(suggest_logging=False),
    )
    assert without_logging
    assert not any("logging" in (v.suggestion or "") for v in without_logging)


def test_unused_argument_utilization_detector_reports_one_based_column():
    """Location.column is 1-based, so a 0-based col_offset must be shifted."""
    code = "def process(context):\n    return 1\n"
    context = AnalysisContext(code=code, language="python")
    violations = UnusedArgumentUtilizationDetector().detect(
        context,
        UnusedArgumentUtilizationConfig(),
    )
    assert violations
    assert violations[0].location.line == 1
    assert violations[0].location.column == code.index("context") + 1


def test_unused_argument_utilization_detector_skips_unparseable_source():
    """Source that cannot be parsed is skipped instead of raising."""
    context = AnalysisContext(code="def process(:\n", language="python")
    violations = UnusedArgumentUtilizationDetector().detect(
        context,
        UnusedArgumentUtilizationConfig(),
    )
    assert violations == []


def test_unused_argument_utilization_detector_excludes_docstring_only_bodies():
    """A body that is nothing but a docstring is a stub, like ... or pass."""
    code = 'def process(context):\n    """Do the thing."""\n'
    analysis_context = AnalysisContext(code=code, language="python")
    violations = UnusedArgumentUtilizationDetector().detect(
        analysis_context,
        UnusedArgumentUtilizationConfig(),
    )
    assert violations == []


def test_unused_argument_utilization_detector_stub_body_handles_empty_body():
    """A function node carrying no body at all is not treated as a stub."""
    node = ast.FunctionDef(
        name="empty",
        args=ast.arguments(
            posonlyargs=[],
            args=[],
            kwonlyargs=[],
            kw_defaults=[],
            defaults=[],
        ),
        body=[],
        decorator_list=[],
        returns=None,
        type_params=[],
        lineno=1,
        col_offset=0,
        end_lineno=1,
        end_col_offset=0,
    )
    assert UnusedArgumentUtilizationDetector._is_stub_body(node) is False
