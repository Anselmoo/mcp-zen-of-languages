from mcp_zen_of_languages.analyzers.base import AnalysisContext
from mcp_zen_of_languages.analyzers.registry import REGISTRY
from mcp_zen_of_languages.languages.configs import ClassSizeConfig
from mcp_zen_of_languages.languages.python.detectors import (
    ClassSizeDetector,
    NameStyleDetector,
)
from mcp_zen_of_languages.languages.python.rules import PYTHON_ZEN


# Minimal fixture-like helper
class SimpleContext:
    def __init__(self, code: str):
        self.code = code
        self.path = None
        self.ast_tree = None
        self.other_files = None
        self.repository_imports = None
        self.language = "python"


def test_class_size_detector_respects_rules():
    # Create a code sample with a large class
    code = (
        """
class Big:
"""
        + "\n".join(["    def m{}(self):\n        pass".format(i) for i in range(20)])
        + "\n"
    )

    detector = ClassSizeDetector()
    cfg = ClassSizeConfig(max_class_length=300)
    ctx = AnalysisContext(code=code, path=None, language="python")

    # Default analyzer config may have max_class_length=300 so no violation normally
    violations_default = detector.detect(ctx, cfg)
    assert len(violations_default) == 0

    # Run detector again with stricter config - it should now detect the class as too large
    strict_cfg = ClassSizeConfig(max_class_length=10)
    violations_rules = detector.detect(ctx, strict_cfg)
    assert len(violations_rules) >= 1
    rule_cfg = next(
        cfg
        for cfg in REGISTRY.configs_from_rules(PYTHON_ZEN)
        if cfg.type == "class_size"
    )
    rule_violations = detector.detect(
        ctx, rule_cfg.model_copy(update={"max_class_length": 10})
    )
    assert any("Classes longer than 300 lines" in v.message for v in rule_violations)


def test_name_style_detector_ast():
    code = """
def BadName():
    pass

fooBar = 1
"""
    detector = NameStyleDetector()
    cfg = next(
        cfg
        for cfg in REGISTRY.configs_from_rules(PYTHON_ZEN)
        if cfg.type == "name_style"
    )
    ctx = AnalysisContext(code=code, path=None, language="python")
    violations = detector.detect(ctx, cfg)
    assert any("Poor naming conventions" in v.message for v in violations)


def test_pipeline_detectors_have_rule_ids():
    pipeline = REGISTRY.create_pipeline_from_rules(PYTHON_ZEN)
    assert pipeline.detectors
    for detector in pipeline.detectors:
        assert detector.rule_ids
        meta = REGISTRY.get(detector.config.type)
        assert detector.rule_ids == meta.rule_ids
