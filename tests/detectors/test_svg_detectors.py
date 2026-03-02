from __future__ import annotations

from mcp_zen_of_languages.analyzers.base import AnalysisContext
from mcp_zen_of_languages.languages.configs import SvgAbsolutePathOnlyConfig
from mcp_zen_of_languages.languages.configs import SvgDeprecatedXlinkHrefConfig
from mcp_zen_of_languages.languages.configs import SvgDuplicateIdConfig
from mcp_zen_of_languages.languages.configs import SvgMissingTitleConfig
from mcp_zen_of_languages.languages.configs import SvgNestedGroupsConfig
from mcp_zen_of_languages.languages.configs import SvgNodeCountConfig
from mcp_zen_of_languages.languages.configs import SvgUnusedDefsConfig
from mcp_zen_of_languages.languages.configs import SvgXmlnsConfig
from mcp_zen_of_languages.languages.svg.detectors import SvgAbsolutePathOnlyDetector
from mcp_zen_of_languages.languages.svg.detectors import SvgDeprecatedXlinkHrefDetector
from mcp_zen_of_languages.languages.svg.detectors import SvgDuplicateIdDetector
from mcp_zen_of_languages.languages.svg.detectors import SvgMissingTitleDetector
from mcp_zen_of_languages.languages.svg.detectors import SvgNestedGroupsDetector
from mcp_zen_of_languages.languages.svg.detectors import SvgNodeCountDetector
from mcp_zen_of_languages.languages.svg.detectors import SvgUnusedDefsDetector
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


def test_svg_unused_defs_detector_flags_unreferenced_defs_id() -> None:
    code = (
        '<svg xmlns="http://www.w3.org/2000/svg">'
        '<defs><linearGradient id="g1"></linearGradient></defs>'
        '<rect width="10" height="10"/>'
        "</svg>"
    )
    context = AnalysisContext(code=code, language="svg")
    violations = SvgUnusedDefsDetector().detect(context, SvgUnusedDefsConfig())
    assert violations


def test_svg_nested_groups_detector_flags_deep_group_nesting() -> None:
    code = (
        '<svg xmlns="http://www.w3.org/2000/svg">'
        "<g><g><g><g><g><g><rect/></g></g></g></g></g></g>"
        "</svg>"
    )
    context = AnalysisContext(code=code, language="svg")
    violations = SvgNestedGroupsDetector().detect(context, SvgNestedGroupsConfig())
    assert violations


def test_svg_duplicate_id_detector_flags_duplicate_ids() -> None:
    code = (
        '<svg xmlns="http://www.w3.org/2000/svg">'
        '<rect id="dup"/><circle id="dup"/>'
        "</svg>"
    )
    context = AnalysisContext(code=code, language="svg")
    violations = SvgDuplicateIdDetector().detect(context, SvgDuplicateIdConfig())
    assert violations


def test_svg_absolute_path_detector_ignores_exponent_notation() -> None:
    code = '<svg xmlns="http://www.w3.org/2000/svg"><path d="M1e-5 2e-3 l1 1"/></svg>'
    context = AnalysisContext(code=code, language="svg")
    violations = SvgAbsolutePathOnlyDetector().detect(
        context, SvgAbsolutePathOnlyConfig()
    )
    assert not violations


def test_svg_absolute_path_detector_flags_all_absolute_commands() -> None:
    code = (
        '<svg xmlns="http://www.w3.org/2000/svg">'
        '<path d="M10 10 L20 20 C30 30 40 40 50 50 Z"/>'
        "</svg>"
    )
    context = AnalysisContext(code=code, language="svg")
    violations = SvgAbsolutePathOnlyDetector().detect(
        context, SvgAbsolutePathOnlyConfig()
    )
    assert violations


def test_svg_deprecated_xlink_detector_points_to_xlink_href() -> None:
    code = (
        '<svg xmlns="http://www.w3.org/2000/svg" '
        'xmlns:xlink="http://www.w3.org/1999/xlink">'
        '<image xlink:href="foo.png"/>'
        "</svg>"
    )
    context = AnalysisContext(code=code, language="svg")
    violations = SvgDeprecatedXlinkHrefDetector().detect(
        context, SvgDeprecatedXlinkHrefConfig()
    )
    assert violations
    assert violations[0].location is not None
    assert violations[0].location.column == code.find("xlink:href") + 1
