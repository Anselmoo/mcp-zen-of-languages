"""CSS zen principles as Pydantic models."""

from pydantic import HttpUrl

from mcp_zen_of_languages.rules.base_models import (
    LanguageZenPrinciples,
    PrincipleCategory,
    ZenPrinciple,
)

CSS_ZEN = LanguageZenPrinciples(
    language="css",
    name="CSS/SCSS/Less",
    philosophy="Maintainable stylesheets through consistency and design tokens.",
    source_text="CSSWG + common modular CSS practices",
    source_url=HttpUrl("https://www.w3.org/TR/CSS/"),
    principles=[
        ZenPrinciple(
            id="css-001",
            principle="Avoid specificity creep",
            category=PrincipleCategory.ARCHITECTURE,
            severity=7,
            description="Deep selector nesting and !important overuse make styles brittle.",
            violations=["Deeply nested selectors", "Overuse of !important"],
            metrics={"max_selector_nesting": 3, "max_important_usages": 0},
        ),
        ZenPrinciple(
            id="css-002",
            principle="Avoid magic pixel values",
            category=PrincipleCategory.DESIGN,
            severity=6,
            description="Prefer design tokens and CSS variables over raw px values.",
            violations=["Raw pixel values used directly"],
            metrics={"max_raw_pixel_literals": 0},
        ),
        ZenPrinciple(
            id="css-003",
            principle="Limit inline color literals",
            category=PrincipleCategory.CONSISTENCY,
            severity=6,
            description="Prefer design tokens/variables over hardcoded color literals.",
            violations=["Inline hex/rgb/hsl color literal used"],
            metrics={"max_color_literals": 0},
        ),
        ZenPrinciple(
            id="css-004",
            principle="Keep stylesheets modular",
            category=PrincipleCategory.ORGANIZATION,
            severity=5,
            description="Very large stylesheet files should be split into modules.",
            violations=["Stylesheet exceeds line threshold"],
            metrics={"max_stylesheet_lines": 300},
        ),
        ZenPrinciple(
            id="css-005",
            principle="Prefer modern import strategy",
            category=PrincipleCategory.PERFORMANCE,
            severity=6,
            description="Avoid @import chains where @use/module composition is better.",
            violations=["@import usage detected"],
            metrics={"max_import_statements": 0},
        ),
        ZenPrinciple(
            id="css-006",
            principle="Use a z-index scale",
            category=PrincipleCategory.CONSISTENCY,
            severity=6,
            description="Arbitrary z-index values should follow a shared scale.",
            violations=["z-index value outside approved scale"],
            metrics={"allowed_z_index_values": [0, 1, 10, 100, 1000]},
        ),
        ZenPrinciple(
            id="css-007",
            principle="Avoid manual vendor prefixes",
            category=PrincipleCategory.CONSISTENCY,
            severity=5,
            description="Manual prefixes are typically handled by autoprefixer.",
            violations=["Manual vendor-prefixed property used"],
            metrics={"max_vendor_prefixed_properties": 0},
        ),
        ZenPrinciple(
            id="css-008",
            principle="Use a consistent breakpoint scale",
            category=PrincipleCategory.CONSISTENCY,
            severity=5,
            description="Media query breakpoints should align to a defined scale.",
            violations=["Media query breakpoint not in approved scale"],
            metrics={"allowed_breakpoint_values": [480, 768, 1024, 1280, 1440]},
        ),
    ],
)
