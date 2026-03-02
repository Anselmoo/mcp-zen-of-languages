from __future__ import annotations

from mcp_zen_of_languages.analyzers.base import AnalysisContext
from mcp_zen_of_languages.languages.configs import SvgMissingTitleConfig
from mcp_zen_of_languages.languages.configs import SvgNodeCountConfig
from mcp_zen_of_languages.languages.configs import SvgXmlnsConfig
from mcp_zen_of_languages.languages.svg.detectors import SvgMissingTitleDetector
from mcp_zen_of_languages.languages.svg.detectors import SvgNodeCountDetector
from mcp_zen_of_languages.languages.svg.detectors import SvgXmlnsDetector


def test_svg_missing_title_detector_flags_svg_without_title() -> None:
    code = '<svg xmlns="http://www.w3.org/2000/svg"></svg>'
    context = AnalysisContext(code=code, language="svg")
    violations = SvgMissingTitleDetector().detect(context, SvgMissingTitleConfig())
    assert violations


def test_svg_xmlns_detector_flags_missing_namespace() -> None:
    code = "<svg><title>Icon</title></svg>"
    context = AnalysisContext(code=code, language="svg")
    violations = SvgXmlnsDetector().detect(context, SvgXmlnsConfig())
    assert violations


def test_svg_node_count_detector_uses_configurable_threshold() -> None:
    code = '<svg xmlns="http://www.w3.org/2000/svg">' + ("<g></g>" * 4) + "</svg>"
    context = AnalysisContext(code=code, language="svg")
    config = SvgNodeCountConfig(max_node_count=3)
    violations = SvgNodeCountDetector().detect(context, config)
    assert violations
