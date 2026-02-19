from __future__ import annotations

from mcp_zen_of_languages.analyzers.base import AnalysisContext
from mcp_zen_of_languages.languages.configs import (
    ConsistencyConfig,
    ExplicitnessConfig,
    LongFunctionConfig,
    NamespaceConfig,
    NestingDepthConfig,
)
from mcp_zen_of_languages.languages.python.detectors import (
    ConsistencyDetector,
    ExplicitnessDetector,
    LongFunctionDetector,
    NamespaceUsageDetector,
    NestingDepthDetector,
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
