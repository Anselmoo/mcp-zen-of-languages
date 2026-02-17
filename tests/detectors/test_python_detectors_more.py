from __future__ import annotations

from mcp_zen_of_languages.analyzers.base import AnalysisContext
from mcp_zen_of_languages.languages.configs import (
    ClassSizeConfig,
    DocstringConfig,
    LineLengthConfig,
    MagicMethodConfig,
    NameStyleConfig,
)
from mcp_zen_of_languages.languages.python.detectors import (
    ClassSizeDetector,
    DocstringDetector,
    LineLengthDetector,
    MagicMethodDetector,
    NameStyleDetector,
)


def test_class_size_detector_handles_parse_error():
    context = AnalysisContext(code="def foo(", language="python")
    violations = ClassSizeDetector().detect(context, ClassSizeConfig())
    assert violations == []


def test_docstring_detector_flags_missing():
    code = "def foo():\n    return 1\n"
    context = AnalysisContext(code=code, language="python")
    violations = DocstringDetector().detect(context, DocstringConfig())
    assert violations


def test_line_length_detector_flags_long():
    code = "a = '" + "x" * 120 + "'\n"
    context = AnalysisContext(code=code, language="python")
    violations = LineLengthDetector().detect(context, LineLengthConfig())
    assert violations


def test_magic_method_detector_flags_overuse():
    code = "def __str__(self):\n    pass\n" * 5
    context = AnalysisContext(code=code, language="python")
    config = MagicMethodConfig().model_copy(update={"max_magic_methods": 1})
    violations = MagicMethodDetector().detect(context, config)
    assert violations


def test_name_style_detector_heuristic():
    code = "def BadName():\n    pass\n"
    context = AnalysisContext(code=code, language="python")
    violations = NameStyleDetector().detect(context, NameStyleConfig())
    assert violations
