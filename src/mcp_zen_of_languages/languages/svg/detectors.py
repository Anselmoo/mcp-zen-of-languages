"""Detectors for SVG accessibility, idioms, and performance."""
# ruff: noqa: D102

from __future__ import annotations

import re
import xml.etree.ElementTree as ET

from mcp_zen_of_languages.analyzers.base import AnalysisContext
from mcp_zen_of_languages.analyzers.base import LocationHelperMixin
from mcp_zen_of_languages.analyzers.base import ViolationDetector
from mcp_zen_of_languages.languages.configs import DetectorConfig
from mcp_zen_of_languages.languages.configs import SvgNodeCountConfig
from mcp_zen_of_languages.models import Location
from mcp_zen_of_languages.models import ParserResult
from mcp_zen_of_languages.models import Violation


_SVG_NS = "http://www.w3.org/2000/svg"
_XLINK_NS = "http://www.w3.org/1999/xlink"
_REF_RE = re.compile(r"#([A-Za-z_][\w\-.]*)")
_PATH_CMD_RE = re.compile(r"[MmZzLlHhVvCcSsQqTtAa]")
_RELATIVE_CMD_RE = re.compile(r"[mlhvcsqtaz]")
_BASE64_IMAGE_RE = re.compile(r"data:image/[^;]+;base64,", re.IGNORECASE)
_UNSAFE_XML_DIRECTIVE_RE = re.compile(r"<!\s*(DOCTYPE|ENTITY)\b", re.IGNORECASE)
_PREFIXED_HREF_RE = re.compile(r"\b\w+:href\b")
_COMPLEX_NODE_THRESHOLD = 20
_GROUP_DEPTH_LIMIT = 5


def _local_name(tag: str) -> str:
    return tag.split("}", 1)[-1] if "}" in tag else tag


def _root_from_context(context: AnalysisContext) -> ET.Element | None:
    ast_tree = context.ast_tree
    if isinstance(ast_tree, ParserResult) and isinstance(ast_tree.tree, ET.Element):
        return ast_tree.tree
    if _UNSAFE_XML_DIRECTIVE_RE.search(context.code):
        return None
    try:
        return ET.fromstring(context.code)  # noqa: S314
    except ET.ParseError:
        return None


class SvgMissingTitleDetector(ViolationDetector[DetectorConfig], LocationHelperMixin):
    """Detects root SVG elements that omit an accessible title child."""

    @property
    def name(self) -> str:
        return "svg-001"

    def detect(
        self, context: AnalysisContext, config: DetectorConfig
    ) -> list[Violation]:
        root = _root_from_context(context)
        if root is None or any(_local_name(child.tag) == "title" for child in root):
            return []
        return [
            self.build_violation(
                config,
                location=Location(line=1, column=1),
                suggestion='Add <title id="..."> and reference it from aria-labelledby.',
            ),
        ]


class SvgAriaRoleDetector(ViolationDetector[DetectorConfig], LocationHelperMixin):
    """Detects root SVG elements missing image role and labeling attributes."""

    @property
    def name(self) -> str:
        return "svg-002"

    def detect(
        self, context: AnalysisContext, config: DetectorConfig
    ) -> list[Violation]:
        root = _root_from_context(context)
        if root is None:
            return []
        if root.attrib.get("role") == "img" and root.attrib.get("aria-labelledby"):
            return []
        return [
            self.build_violation(
                config,
                location=Location(line=1, column=1),
                suggestion='Set role="img" and aria-labelledby on the root <svg>.',
            ),
        ]


class SvgImageAltDetector(ViolationDetector[DetectorConfig], LocationHelperMixin):
    """Detects embedded image elements lacking alternative text metadata."""

    @property
    def name(self) -> str:
        return "svg-003"

    def detect(
        self, context: AnalysisContext, config: DetectorConfig
    ) -> list[Violation]:
        root = _root_from_context(context)
        if root is None:
            return []
        for image in root.iter():
            if _local_name(image.tag) != "image":
                continue
            if (
                image.attrib.get("alt")
                or image.attrib.get("aria-label")
                or image.attrib.get("title")
            ):
                continue
            return [
                self.build_violation(
                    config,
                    location=self.find_location_by_substring(context.code, "<image"),
                    suggestion="Add alt, aria-label, or title for embedded images.",
                ),
            ]
        return []


class SvgDescForComplexGraphicsDetector(
    ViolationDetector[DetectorConfig],
    LocationHelperMixin,
):
    """Detects complex SVG documents that lack a descriptive <desc> element."""

    @property
    def name(self) -> str:
        return "svg-004"

    def detect(
        self, context: AnalysisContext, config: DetectorConfig
    ) -> list[Violation]:
        root = _root_from_context(context)
        if root is None:
            return []
        if len(list(root.iter())) <= _COMPLEX_NODE_THRESHOLD:
            return []
        if any(_local_name(child.tag) == "desc" for child in root):
            return []
        return [
            self.build_violation(
                config,
                location=Location(line=1, column=1),
                suggestion="Add a <desc> element describing the complex graphic.",
            ),
        ]


class SvgInlineStyleDetector(ViolationDetector[DetectorConfig], LocationHelperMixin):
    """Detects inline style usage inside SVG markup."""

    @property
    def name(self) -> str:
        return "svg-005"

    def detect(
        self, context: AnalysisContext, config: DetectorConfig
    ) -> list[Violation]:
        if "style=" not in context.code:
            return []
        return [
            self.build_violation(
                config,
                location=self.find_location_by_substring(context.code, "style="),
                suggestion="Prefer presentation attributes, classes, or a <style> block.",
            ),
        ]


class SvgViewBoxDetector(ViolationDetector[DetectorConfig], LocationHelperMixin):
    """Detects fixed dimensions used without a responsive viewBox."""

    @property
    def name(self) -> str:
        return "svg-006"

    def detect(
        self, context: AnalysisContext, config: DetectorConfig
    ) -> list[Violation]:
        root = _root_from_context(context)
        if root is None:
            return []
        if {"width", "height"}.issubset(root.attrib) and "viewBox" not in root.attrib:
            return [
                self.build_violation(
                    config,
                    location=Location(line=1, column=1),
                    suggestion="Add viewBox when fixed width/height are declared.",
                ),
            ]
        return []


class SvgUnusedDefsDetector(ViolationDetector[DetectorConfig], LocationHelperMixin):
    """Detects IDs declared under defs that are never referenced."""

    @property
    def name(self) -> str:
        return "svg-007"

    def detect(
        self, context: AnalysisContext, config: DetectorConfig
    ) -> list[Violation]:
        root = _root_from_context(context)
        if root is None:
            return []
        defs_ids: set[str] = set()
        for defs in root.iter():
            if _local_name(defs.tag) != "defs":
                continue
            defs_ids |= {el.attrib["id"] for el in defs.iter() if el.attrib.get("id")}
        if not defs_ids:
            return []
        referenced: set[str] = set()
        for element in root.iter():
            for value in element.attrib.values():
                referenced |= set(_REF_RE.findall(value))
        if unused := sorted(defs_ids - referenced):
            return [
                self.build_violation(
                    config,
                    contains=unused[0],
                    location=self.find_location_by_substring(
                        context.code, f'id="{unused[0]}"'
                    ),
                    suggestion="Remove or reference unused defs entries.",
                ),
            ]
        return []


class SvgNestedGroupsDetector(ViolationDetector[DetectorConfig], LocationHelperMixin):
    """Detects excessive nesting depth of SVG group elements."""

    @property
    def name(self) -> str:
        return "svg-008"

    def detect(
        self, context: AnalysisContext, config: DetectorConfig
    ) -> list[Violation]:
        root = _root_from_context(context)
        if root is None:
            return []

        def _max_group_depth(node: ET.Element, depth: int = 0) -> int:
            next_depth = depth + 1 if _local_name(node.tag) == "g" else depth
            child_depths = [_max_group_depth(child, next_depth) for child in node]
            return max([next_depth, *child_depths], default=next_depth)

        if _max_group_depth(root) > _GROUP_DEPTH_LIMIT:
            return [
                self.build_violation(
                    config,
                    location=self.find_location_by_substring(context.code, "<g"),
                    suggestion="Flatten unnecessary nested <g> wrappers.",
                ),
            ]
        return []


class SvgDuplicateIdDetector(ViolationDetector[DetectorConfig], LocationHelperMixin):
    """Detects duplicate ID values across SVG elements."""

    @property
    def name(self) -> str:
        return "svg-009"

    def detect(
        self, context: AnalysisContext, config: DetectorConfig
    ) -> list[Violation]:
        root = _root_from_context(context)
        if root is None:
            return []
        seen: set[str] = set()
        duplicate: str | None = None
        for element in root.iter():
            element_id = element.attrib.get("id")
            if not element_id:
                continue
            if element_id in seen:
                duplicate = element_id
                break
            seen.add(element_id)
        if duplicate is not None:
            return [
                self.build_violation(
                    config,
                    contains=duplicate,
                    location=self.find_location_by_substring(
                        context.code, f'id="{duplicate}"'
                    ),
                    suggestion="Ensure every id value is globally unique in the SVG document.",
                ),
            ]
        return []


class SvgAbsolutePathOnlyDetector(
    ViolationDetector[DetectorConfig], LocationHelperMixin
):
    """Detects paths composed only of absolute command letters."""

    @property
    def name(self) -> str:
        return "svg-010"

    def detect(
        self, context: AnalysisContext, config: DetectorConfig
    ) -> list[Violation]:
        root = _root_from_context(context)
        if root is None:
            return []
        for path in root.iter():
            if _local_name(path.tag) != "path":
                continue
            commands = "".join(_PATH_CMD_RE.findall(path.attrib.get("d", "")))
            if (
                commands
                and commands.isupper()
                and not _RELATIVE_CMD_RE.search(commands)
            ):
                return [
                    self.build_violation(
                        config,
                        location=self.find_location_by_substring(context.code, "<path"),
                        suggestion="Use relative path commands where practical to reduce payload.",
                    ),
                ]
        return []


class SvgBase64ImageDetector(ViolationDetector[DetectorConfig], LocationHelperMixin):
    """Detects base64-embedded raster images in SVG content."""

    @property
    def name(self) -> str:
        return "svg-011"

    def detect(
        self, context: AnalysisContext, config: DetectorConfig
    ) -> list[Violation]:
        if not _BASE64_IMAGE_RE.search(context.code):
            return []
        return [
            self.build_violation(
                config,
                location=self.find_location_by_substring(context.code, "data:image"),
                suggestion="Prefer external image references or native vector elements.",
            ),
        ]


class SvgXmlnsDetector(ViolationDetector[DetectorConfig], LocationHelperMixin):
    """Detects missing core SVG XML namespace declarations."""

    @property
    def name(self) -> str:
        return "svg-012"

    def detect(
        self, context: AnalysisContext, config: DetectorConfig
    ) -> list[Violation]:
        root = _root_from_context(context)
        if root is None:
            return []
        if str(root.tag).startswith(f"{{{_SVG_NS}}}"):
            return []
        return [
            self.build_violation(
                config,
                location=Location(line=1, column=1),
                suggestion='Declare xmlns="http://www.w3.org/2000/svg" on the root element.',
            ),
        ]


class SvgDeprecatedXlinkHrefDetector(
    ViolationDetector[DetectorConfig],
    LocationHelperMixin,
):
    """Detects deprecated xlink:href attributes in SVG markup."""

    @property
    def name(self) -> str:
        return "svg-013"

    def detect(
        self, context: AnalysisContext, config: DetectorConfig
    ) -> list[Violation]:
        if "xlink:href" in context.code:
            return [
                self.build_violation(
                    config,
                    location=self.find_location_by_substring(
                        context.code, "xlink:href"
                    ),
                    suggestion="Replace xlink:href with href in SVG 2 documents.",
                ),
            ]
        root = _root_from_context(context)
        if root is None:
            return []
        deprecated_key = f"{{{_XLINK_NS}}}href"
        for element in root.iter():
            if deprecated_key in element.attrib:
                # Find the prefixed :href attribute token (e.g. xl:href, xlink:href)
                # using a word-boundary pattern to avoid matching unrelated text.
                m = _PREFIXED_HREF_RE.search(context.code)
                search_token = m.group(0) if m else "href"
                return [
                    self.build_violation(
                        config,
                        location=self.find_location_by_substring(
                            context.code, search_token
                        ),
                        suggestion="Replace xlink:href with href in SVG 2 documents.",
                    ),
                ]
        return []


class SvgNodeCountDetector(ViolationDetector[SvgNodeCountConfig], LocationHelperMixin):
    """Detects SVG documents exceeding a configurable node-count threshold."""

    @property
    def name(self) -> str:
        return "svg-014"

    def detect(
        self, context: AnalysisContext, config: SvgNodeCountConfig
    ) -> list[Violation]:
        root = _root_from_context(context)
        if root is None:
            return []
        node_count = len(list(root.iter()))
        if node_count <= config.max_node_count:
            return []
        return [
            self.build_violation(
                config,
                contains=str(node_count),
                location=Location(line=1, column=1),
                suggestion="Simplify SVG structure or split into symbols/sprites.",
            ),
        ]


class SvgProductionBloatDetector(
    ViolationDetector[DetectorConfig], LocationHelperMixin
):
    """Detects metadata/comments and editor namespace bloat in production SVG."""

    @property
    def name(self) -> str:
        return "svg-015"

    def detect(
        self, context: AnalysisContext, config: DetectorConfig
    ) -> list[Violation]:
        bloat_tokens = ("<metadata", "inkscape:", "sodipodi:", "<!--")
        for token in bloat_tokens:
            if token in context.code:
                return [
                    self.build_violation(
                        config,
                        contains=token,
                        location=self.find_location_by_substring(context.code, token),
                        suggestion="Remove editor metadata/comments from production SVG assets.",
                    ),
                ]
        return []


__all__ = [
    "SvgAbsolutePathOnlyDetector",
    "SvgAriaRoleDetector",
    "SvgBase64ImageDetector",
    "SvgDeprecatedXlinkHrefDetector",
    "SvgDescForComplexGraphicsDetector",
    "SvgDuplicateIdDetector",
    "SvgImageAltDetector",
    "SvgInlineStyleDetector",
    "SvgMissingTitleDetector",
    "SvgNestedGroupsDetector",
    "SvgNodeCountDetector",
    "SvgProductionBloatDetector",
    "SvgUnusedDefsDetector",
    "SvgViewBoxDetector",
    "SvgXmlnsDetector",
]
