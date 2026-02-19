from __future__ import annotations

from mcp_zen_of_languages.analyzers.base import AnalysisContext
from mcp_zen_of_languages.languages.configs import (
    BareExceptConfig,
    CircularDependencyConfig,
    ClassSizeConfig,
    ConsistencyConfig,
    ContextManagerConfig,
    CyclomaticComplexityConfig,
    DocstringConfig,
    ExplicitnessConfig,
    GodClassConfig,
    LineLengthConfig,
    LongFunctionConfig,
    MagicMethodConfig,
    NamespaceConfig,
    NestingDepthConfig,
    SparseCodeConfig,
)
from mcp_zen_of_languages.languages.python.detectors import (
    BareExceptDetector,
    CircularDependencyDetector,
    ClassSizeDetector,
    ConsistencyDetector,
    ContextManagerDetector,
    CyclomaticComplexityDetector,
    DocstringDetector,
    ExplicitnessDetector,
    GodClassDetector,
    LineLengthDetector,
    LongFunctionDetector,
    MagicMethodDetector,
    NamespaceUsageDetector,
    NestingDepthDetector,
    SparseCodeDetector,
)
from mcp_zen_of_languages.models import (
    CyclomaticBlock,
    CyclomaticSummary,
    DependencyAnalysis,
    DependencyCycle,
)


def test_python_detector_coverage_paths():
    code = """
class BigClass:
    def a(self):
        pass
    def b(self):
        pass
    def c(self):
        pass
    def d(self):
        pass
    def e(self):
        pass

def foo():
    return 1

x = 1; y = 2
"""
    context = AnalysisContext(code=code, language="python")
    assert LineLengthDetector().detect(context, LineLengthConfig()) == []
    assert SparseCodeDetector().detect(context, SparseCodeConfig())

    bare = "try:\n    pass\nexcept:\n    pass\n"
    bare_context = AnalysisContext(code=bare, language="python")
    assert BareExceptDetector().detect(bare_context, BareExceptConfig())

    doc_context = AnalysisContext(code="def foo():\n    pass\n", language="python")
    assert DocstringDetector().detect(doc_context, DocstringConfig())

    class_context = AnalysisContext(code=code, language="python")
    class_cfg = ClassSizeConfig().model_copy(update={"max_class_length": 3})
    assert ClassSizeDetector().detect(class_context, class_cfg)

    long_cfg = LongFunctionConfig().model_copy(update={"max_function_length": 1})
    assert LongFunctionDetector().detect(doc_context, long_cfg)

    magic_cfg = MagicMethodConfig().model_copy(update={"max_magic_methods": 0})
    magic_context = AnalysisContext(
        code="def __str__(self):\n    return 'x'\n",
        language="python",
    )
    assert MagicMethodDetector().detect(magic_context, magic_cfg)

    nest_cfg = NestingDepthConfig().model_copy(update={"max_nesting_depth": 0})
    nested_context = AnalysisContext(
        code="if True:\n    if True:\n        pass\n",
        language="python",
    )
    assert NestingDepthDetector().detect(nested_context, nest_cfg)

    cc_summary = CyclomaticSummary(
        blocks=[CyclomaticBlock(name="foo", complexity=12, lineno=1)],
        average=12.0,
    )
    cc_context = AnalysisContext(code="def foo():\n    return 1\n", language="python")
    cc_context.cyclomatic_summary = cc_summary
    cc_cfg = CyclomaticComplexityConfig().model_copy(
        update={"max_cyclomatic_complexity": 5},
    )
    assert CyclomaticComplexityDetector().detect(cc_context, cc_cfg)

    consistency_context = AnalysisContext(
        code="def foo():\n    pass\n\ndef FooBar():\n    pass\n",
        language="python",
    )
    assert ConsistencyDetector().detect(consistency_context, ConsistencyConfig())

    explicit_context = AnalysisContext(
        code="def foo(x, y):\n    return x\n",
        language="python",
    )
    assert ExplicitnessDetector().detect(explicit_context, ExplicitnessConfig())

    namespace_context = AnalysisContext(
        code="def a():\n    pass\n\ndef b():\n    pass\n\n__all__ = ['a', 'b']\n",
        language="python",
    )
    ns_cfg = NamespaceConfig().model_copy(
        update={"max_top_level_symbols": 1, "max_exports": 0},
    )
    assert NamespaceUsageDetector().detect(namespace_context, ns_cfg)

    dep_context = AnalysisContext(code="", language="python")
    dep_context.dependency_analysis = DependencyAnalysis(
        nodes=["a", "b"],
        edges=[("a", "b"), ("b", "a")],
        cycles=[DependencyCycle(cycle=["a", "b", "a"])],
    )
    assert CircularDependencyDetector().detect(dep_context, CircularDependencyConfig())

    ctx_context = AnalysisContext(code="open('a')\n", language="python")
    assert ContextManagerDetector().detect(ctx_context, ContextManagerConfig())

    god_code = "class Huge:\n    def a(self):\n        pass\n    def b(self):\n        pass\n    def c(self):\n        pass\n    def d(self):\n        pass\n"
    god_context = AnalysisContext(code=god_code, language="python")
    god_cfg = GodClassConfig().model_copy(update={"max_methods": 1})
    assert GodClassDetector().detect(god_context, god_cfg)
