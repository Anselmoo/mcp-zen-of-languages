from mcp_zen_of_languages.analyzers.base import AnalysisContext
from mcp_zen_of_languages.analyzers.registry import REGISTRY
from mcp_zen_of_languages.languages.python.detectors import (
    ContextManagerDetector,
    DocstringDetector,
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


def test_docstring_detector():
    code = """
class X:
    def method(self):
        pass

def foo():
    pass
    """
    det = DocstringDetector()
    violations = run_detector(det, code, config_for("docstrings"))
    assert any("Missing docstrings" in v.message for v in violations)


def test_context_manager_detector():
    code = """
with open('a.txt') as f:
    data = f.read()

f = open('b.txt')
    """
    det = ContextManagerDetector()
    violations = run_detector(det, code, config_for("context_manager"))
    assert any("context managers" in v.message for v in violations)
