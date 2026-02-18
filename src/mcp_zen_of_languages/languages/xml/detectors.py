"""Detectors for XML document quality, enforcing semantic markup, namespace hygiene, and hierarchy."""

from __future__ import annotations

import re

from mcp_zen_of_languages.analyzers.base import (
    AnalysisContext,
    LocationHelperMixin,
    ViolationDetector,
)
from mcp_zen_of_languages.languages.configs import (
    XmlAttributeUsageConfig,
    XmlClosingTagsConfig,
    XmlHierarchyConfig,
    XmlNamespaceConfig,
    XmlSemanticMarkupConfig,
    XmlValidityConfig,
)
from mcp_zen_of_languages.models import Location, Violation

# Minimum number of tag occurrences before flagging as ungrouped repetition
MIN_TAG_OCCURRENCES_FOR_GROUP = 2


class XmlSemanticMarkupDetector(
    ViolationDetector[XmlSemanticMarkupConfig], LocationHelperMixin
):
    """Flags presentational HTML-era tags and inline style attributes in XML.

    Tags like ``<font>``, ``<center>``, ``<b>``, and ``<i>`` embed
    presentation concerns into a document that should express structure.
    Similarly, ``style="..."`` attributes couple layout decisions to content.
    This detector encourages separating presentation from semantics by using
    CSS or XSL stylesheets instead.
    """

    @property
    def name(self) -> str:
        """Return ``'xml-001'`` identifying the semantic markup detector.

        Returns:
            str: The ``'xml-001'`` rule identifier.
        """
        return "xml-001"

    def detect(
        self, context: AnalysisContext, config: XmlSemanticMarkupConfig
    ) -> list[Violation]:
        """Search for presentational tags (``<font>``, ``<b>``, etc.) and inline ``style`` attributes.

        Args:
            context: Analysis context holding the raw XML markup.
            config: Semantic markup thresholds and violation message templates.

        Returns:
            list[Violation]: A single violation when presentational elements are found.
        """
        if re.search(r"<(font|center|b|i)(\s|>)", context.code):
            return [
                self.build_violation(
                    config,
                    contains="presentational tag",
                    location=Location(line=1, column=1),
                    suggestion="Use semantic tags instead of presentational markup.",
                )
            ]
        if re.search(r"style=\"[^\"]+\"", context.code):
            return [
                self.build_violation(
                    config,
                    contains="style",
                    location=Location(line=1, column=1),
                    suggestion="Avoid presentation-oriented style attributes.",
                )
            ]
        return []


class XmlAttributeUsageDetector(
    ViolationDetector[XmlAttributeUsageConfig], LocationHelperMixin
):
    """Identifies oversized attribute values that belong in child elements instead.

    XML attributes are designed for short metadata—identifiers, flags, or
    references.  When an attribute value exceeds 30 characters it typically
    contains data that is better expressed as element content, where it can
    be formatted, validated, and read more easily.
    """

    @property
    def name(self) -> str:
        """Return ``'xml-002'`` identifying the attribute usage detector.

        Returns:
            str: The ``'xml-002'`` rule identifier.
        """
        return "xml-002"

    def detect(
        self, context: AnalysisContext, config: XmlAttributeUsageConfig
    ) -> list[Violation]:
        """Scan for attribute values longer than 30 characters that should be child elements.

        Args:
            context: Analysis context holding the raw XML markup.
            config: Attribute usage thresholds and violation message templates.

        Returns:
            list[Violation]: A single violation for the first oversized attribute found.
        """
        for idx, line in enumerate(context.code.splitlines(), start=1):
            if match := re.search(r"\w+=\"([^\"]{30,})\"", line):
                return [
                    self.build_violation(
                        config,
                        contains=match[1][:10],
                        location=Location(line=idx, column=1),
                        suggestion="Move large data values into child elements.",
                    )
                ]
        return []


class XmlNamespaceDetector(ViolationDetector[XmlNamespaceConfig], LocationHelperMixin):
    """Detects prefixed element names that lack a corresponding ``xmlns`` declaration.

    Namespace prefixes like ``<ns:element>`` are meaningless without a
    ``xmlns:ns="..."`` binding.  Missing declarations cause parser errors and
    make the document non-well-formed.  This detector catches the oversight
    early so authors can add the proper namespace URI.
    """

    @property
    def name(self) -> str:
        """Return ``'xml-003'`` identifying the namespace declaration detector.

        Returns:
            str: The ``'xml-003'`` rule identifier.
        """
        return "xml-003"

    def detect(
        self, context: AnalysisContext, config: XmlNamespaceConfig
    ) -> list[Violation]:
        """Check whether prefixed elements (``<prefix:tag>``) have a matching ``xmlns`` binding.

        Args:
            context: Analysis context holding the raw XML markup.
            config: Namespace thresholds and violation message templates.

        Returns:
            list[Violation]: A single violation when prefixed tags exist without ``xmlns`` declarations.
        """
        has_prefix = bool(re.search(r"<\w+:\w+", context.code))
        if has_prefix and "xmlns" not in context.code:
            return [
                self.build_violation(
                    config,
                    contains="xmlns",
                    location=Location(line=1, column=1),
                    suggestion="Declare XML namespaces for prefixed elements.",
                )
            ]
        return []


class XmlValidityDetector(ViolationDetector[XmlValidityConfig], LocationHelperMixin):
    """Checks for schema or DTD references that enable structural validation.

    An XML document without ``xsi:schemaLocation`` or ``DOCTYPE`` cannot be
    validated against a formal grammar, making it fragile and error-prone.
    This detector flags documents that lack any schema reference so authors
    can add one to enable automated validation tooling.
    """

    @property
    def name(self) -> str:
        """Return ``'xml-004'`` identifying the schema validity detector.

        Returns:
            str: The ``'xml-004'`` rule identifier.
        """
        return "xml-004"

    def detect(
        self, context: AnalysisContext, config: XmlValidityConfig
    ) -> list[Violation]:
        """Search for ``xsi:schemaLocation`` or ``DOCTYPE`` references in the document.

        Args:
            context: Analysis context holding the raw XML markup.
            config: Validity thresholds and violation message templates.

        Returns:
            list[Violation]: A single violation when no schema reference is present.
        """
        if re.search(r"xsi:schemaLocation|DOCTYPE", context.code) is None:
            return [
                self.build_violation(
                    config,
                    contains="schema",
                    location=Location(line=1, column=1),
                    suggestion="Include schema references (xsi:schemaLocation or DOCTYPE).",
                )
            ]
        return []


class XmlHierarchyDetector(ViolationDetector[XmlHierarchyConfig], LocationHelperMixin):
    """Flags repeated sibling elements that lack a grouping parent container.

    When the same tag name appears more than twice without being wrapped in a
    logical parent (e.g., ``<group>``), readers struggle to understand the
    document's hierarchy.  This detector recommends introducing a container
    element to clarify the relationship between repeated siblings.
    """

    @property
    def name(self) -> str:
        """Return ``'xml-005'`` identifying the element hierarchy detector.

        Returns:
            str: The ``'xml-005'`` rule identifier.
        """
        return "xml-005"

    def detect(
        self, context: AnalysisContext, config: XmlHierarchyConfig
    ) -> list[Violation]:
        """Count opening tags and flag any that repeat more than twice without a ``<group>`` wrapper.

        Args:
            context: Analysis context holding the raw XML markup.
            config: Hierarchy thresholds and violation message templates.

        Returns:
            list[Violation]: A single violation when ungrouped repeated elements are found.
        """
        if tag_counts := re.findall(r"<([A-Za-z0-9_]+)>", context.code):
            duplicates = {tag for tag in tag_counts if tag_counts.count(tag) > MIN_TAG_OCCURRENCES_FOR_GROUP}
            if duplicates and "<group>" not in context.code:
                return [
                    self.build_violation(
                        config,
                        contains=next(iter(duplicates)),
                        location=Location(line=1, column=1),
                        suggestion="Group repeated elements under a parent container.",
                    )
                ]
        return []


class XmlClosingTagsDetector(
    ViolationDetector[XmlClosingTagsConfig], LocationHelperMixin
):
    """Identifies self-closing tags (``<tag />``) where explicit closing tags are preferred.

    Self-closing syntax is valid XML, but in contexts where an element is
    expected to hold content (e.g., ``<description />``) it can mask missing
    data.  This detector flags self-closing elements so authors can verify
    that the empty content is intentional.
    """

    @property
    def name(self) -> str:
        """Return ``'xml-006'`` identifying the closing tags detector.

        Returns:
            str: The ``'xml-006'`` rule identifier.
        """
        return "xml-006"

    def detect(
        self, context: AnalysisContext, config: XmlClosingTagsConfig
    ) -> list[Violation]:
        """Search for self-closing tag syntax (``<tag />``) in the XML document.

        Args:
            context: Analysis context holding the raw XML markup.
            config: Closing tag thresholds and violation message templates.

        Returns:
            list[Violation]: A single violation when self-closing tags are found.
        """
        if re.search(r"<([A-Za-z0-9_]+)\s*/>", context.code):
            return [
                self.build_violation(
                    config,
                    contains="self-closing",
                    location=Location(line=1, column=1),
                    suggestion="Use explicit closing tags when content is expected.",
                )
            ]
        return []


__all__ = [
    "XmlAttributeUsageDetector",
    "XmlClosingTagsDetector",
    "XmlHierarchyDetector",
    "XmlNamespaceDetector",
    "XmlSemanticMarkupDetector",
    "XmlValidityDetector",
]
