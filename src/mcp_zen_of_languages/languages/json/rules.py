"""JSON zen principles as Pydantic models."""

from pydantic import HttpUrl

from mcp_zen_of_languages.rules.base_models import (
    LanguageZenPrinciples,
    PrincipleCategory,
    ZenPrinciple,
)

JSON_ZEN = LanguageZenPrinciples(
    language="json",
    name="JSON",
    philosophy="JSON Data Interchange Syntax",
    source_text="JSON Data Interchange Syntax",
    source_url=HttpUrl("https://www.json.org/json-en.html"),
    principles=[
        ZenPrinciple(
            id="json-001",
            principle="Strictness enables interoperability",
            category=PrincipleCategory.CORRECTNESS,
            severity=7,
            description="Avoid comments and trailing commas for strict JSON compliance.",
            violations=["Comments in JSON", "Trailing commas in objects/arrays"],
            detectable_patterns=["//", "/\\*", ",\\]", ",\\}"],
        ),
        ZenPrinciple(
            id="json-002",
            principle="Structure implies Schema",
            category=PrincipleCategory.STRUCTURE,
            severity=6,
            description="Keep object shapes consistent within arrays.",
            violations=["Array objects with inconsistent keys"],
        ),
        ZenPrinciple(
            id="json-003",
            principle="Dates should be standard",
            category=PrincipleCategory.CORRECTNESS,
            severity=6,
            description="Use ISO 8601 date/time strings.",
            violations=["Non-ISO date strings"],
        ),
        ZenPrinciple(
            id="json-004",
            principle="Null is a value, missing is unknown",
            category=PrincipleCategory.CORRECTNESS,
            severity=5,
            description="Prefer explicit nulls for optional keys when applicable.",
            violations=["Optional keys missing without nulls"],
        ),
        ZenPrinciple(
            id="json-005",
            principle="Keys are case-sensitive identifiers",
            category=PrincipleCategory.NAMING,
            severity=5,
            description="Use consistent key casing (e.g., lower_snake or lowerCamel).",
            violations=["Mixed key casing"],
        ),
        ZenPrinciple(
            id="json-006",
            principle="Arrays are ordered, Objects are not",
            category=PrincipleCategory.CLARITY,
            severity=4,
            description="Do not rely on object key order; use arrays when ordering matters.",
            violations=["Object keys imply ordering"],
        ),
    ],
)
