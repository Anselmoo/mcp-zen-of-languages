"""XML zen principles as Pydantic models."""

from pydantic import HttpUrl

from ...rules.base_models import LanguageZenPrinciples, PrincipleCategory, ZenPrinciple

XML_ZEN = LanguageZenPrinciples(
    language="xml",
    name="XML",
    philosophy="Extensible Markup Language (W3C)",
    source_text="W3C XML",
    source_url=HttpUrl("https://www.w3.org/XML/"),
    principles=[
        ZenPrinciple(
            id="xml-001",
            principle="Mark up meaning, not presentation",
            category=PrincipleCategory.CLARITY,
            severity=5,
            description="Prefer semantic tags over presentational markup.",
            violations=["Deprecated presentational tags or style attributes"],
        ),
        ZenPrinciple(
            id="xml-002",
            principle="Attributes for metadata, Elements for data",
            category=PrincipleCategory.STRUCTURE,
            severity=5,
            description="Use attributes for metadata and elements for structured data.",
            violations=["Large text content stored in attributes"],
        ),
        ZenPrinciple(
            id="xml-003",
            principle="Namespaces prevent local collisions",
            category=PrincipleCategory.CORRECTNESS,
            severity=6,
            description="Declare namespaces when using prefixed elements.",
            violations=["Prefixed elements without xmlns declarations"],
        ),
        ZenPrinciple(
            id="xml-004",
            principle="Validity supersedes well-formedness",
            category=PrincipleCategory.CORRECTNESS,
            severity=6,
            description="Provide schema references for validation.",
            violations=["Missing schema declaration"],
        ),
        ZenPrinciple(
            id="xml-005",
            principle="Hierarchy represents ownership",
            category=PrincipleCategory.STRUCTURE,
            severity=4,
            description="Use nested structures to represent ownership.",
            violations=["Flat repeated elements without grouping"],
        ),
        ZenPrinciple(
            id="xml-006",
            principle="Closing tags complete the thought",
            category=PrincipleCategory.CORRECTNESS,
            severity=5,
            description="Avoid self-closing tags when content is expected.",
            violations=["Self-closing tags for non-empty elements"],
        ),
    ],
)
