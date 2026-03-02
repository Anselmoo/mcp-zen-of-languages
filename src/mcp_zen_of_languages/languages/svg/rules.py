"""SVG zen principles as Pydantic models."""

from pydantic import HttpUrl

from mcp_zen_of_languages.rules.base_models import LanguageZenPrinciples
from mcp_zen_of_languages.rules.base_models import PrincipleCategory
from mcp_zen_of_languages.rules.base_models import ZenPrinciple


SVG_ZEN = LanguageZenPrinciples(
    language="svg",
    name="SVG",
    philosophy="Accessible, maintainable, and performant scalable vector graphics",
    source_text="W3C SVG 2",
    source_url=HttpUrl("https://www.w3.org/TR/SVG2/"),
    principles=[
        ZenPrinciple(
            id="svg-001",
            principle="Include a root title element for accessibility",
            category=PrincipleCategory.USABILITY,
            severity=8,
            description="SVGs without a <title> child on the root are not announced well by screen readers.",
            violations=["Missing <title> child on root <svg>"],
        ),
        ZenPrinciple(
            id="svg-002",
            principle="Use role=img with aria-labelledby for inline SVG",
            category=PrincipleCategory.USABILITY,
            severity=8,
            description="Inline SVGs should be exposed as images and linked to accessible labels.",
            violations=["Missing role=\"img\" and/or aria-labelledby on root <svg>"],
        ),
        ZenPrinciple(
            id="svg-003",
            principle="Give image nodes alternative text",
            category=PrincipleCategory.USABILITY,
            severity=7,
            description="Embedded raster images should carry alternative text for assistive technologies.",
            violations=["<image> element missing alt/title/aria-label text"],
        ),
        ZenPrinciple(
            id="svg-004",
            principle="Provide a long description for complex graphics",
            category=PrincipleCategory.DOCUMENTATION,
            severity=6,
            description="Charts or diagrams should provide a <desc> element to explain non-trivial content.",
            violations=["Complex SVG missing <desc> element"],
        ),
        ZenPrinciple(
            id="svg-005",
            principle="Prefer presentation attributes over inline styles",
            category=PrincipleCategory.CONSISTENCY,
            severity=5,
            description="Inline style attributes reduce maintainability and hinder targeted optimization.",
            violations=["Inline style attribute found in SVG element"],
        ),
        ZenPrinciple(
            id="svg-006",
            principle="Use viewBox with fixed dimensions",
            category=PrincipleCategory.STRUCTURE,
            severity=6,
            description="Hardcoded width/height without viewBox reduces responsive scalability.",
            violations=["Root SVG has width/height but no viewBox"],
        ),
        ZenPrinciple(
            id="svg-007",
            principle="Remove unused defs entries",
            category=PrincipleCategory.ORGANIZATION,
            severity=5,
            description="Unused gradients, symbols, or patterns in <defs> increase file complexity.",
            violations=["Unused ID defined under <defs>"],
        ),
        ZenPrinciple(
            id="svg-008",
            principle="Avoid excessive nested group depth",
            category=PrincipleCategory.COMPLEXITY,
            severity=5,
            description="Deeply nested <g> structures increase DOM complexity without semantic gain.",
            violations=["Nested <g> depth exceeds recommended threshold"],
        ),
        ZenPrinciple(
            id="svg-009",
            principle="Keep id attributes unique",
            category=PrincipleCategory.CORRECTNESS,
            severity=8,
            description="Duplicate IDs break references like <use>, url(#id), and ARIA links.",
            violations=["Duplicate id attribute value in SVG"],
        ),
        ZenPrinciple(
            id="svg-010",
            principle="Prefer relative path commands when practical",
            category=PrincipleCategory.IDIOMS,
            severity=4,
            description="Paths composed only of absolute commands are often larger and less portable.",
            violations=["Path uses only absolute commands"],
        ),
        ZenPrinciple(
            id="svg-011",
            principle="Avoid embedded base64 raster payloads",
            category=PrincipleCategory.PERFORMANCE,
            severity=7,
            description="Base64 raster data inflates file size and should usually be externalized.",
            violations=["<image> uses data:image/*;base64 payload"],
        ),
        ZenPrinciple(
            id="svg-012",
            principle="Declare the SVG XML namespace",
            category=PrincipleCategory.CORRECTNESS,
            severity=7,
            description="Missing xmlns=\"http://www.w3.org/2000/svg\" breaks parsing in non-browser contexts.",
            violations=["Missing SVG namespace declaration"],
        ),
        ZenPrinciple(
            id="svg-013",
            principle="Use href instead of deprecated xlink:href",
            category=PrincipleCategory.IDIOMS,
            severity=4,
            description="xlink:href is deprecated in SVG 2 and should be replaced with href.",
            violations=["Deprecated xlink:href attribute detected"],
        ),
        ZenPrinciple(
            id="svg-014",
            principle="Keep node count within maintainable limits",
            category=PrincipleCategory.PERFORMANCE,
            severity=6,
            description="Very large SVG DOM trees should be simplified or delivered as sprites.",
            violations=["SVG element count exceeds configured threshold"],
            metrics={"max_node_count": 500},
        ),
        ZenPrinciple(
            id="svg-015",
            principle="Remove production-bloat metadata and comments",
            category=PrincipleCategory.PERFORMANCE,
            severity=4,
            description="Editor metadata, vendor namespaces, and XML comments add unnecessary payload.",
            violations=["Metadata/comments/editor namespaces found in production SVG"],
        ),
    ],
)
