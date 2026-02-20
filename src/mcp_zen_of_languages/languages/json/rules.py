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
    philosophy="JSON and JSON5 Configuration Discipline",
    source_text="RFC 8259 JSON + practical JSON5 interoperability",
    source_url=HttpUrl("https://www.json.org/json-en.html"),
    principles=[
        ZenPrinciple(
            id="json-001",
            principle="Choose strictness intentionally",
            category=PrincipleCategory.CORRECTNESS,
            severity=7,
            description="Trailing commas should be rejected for JSON unless JSON5 is explicitly targeted.",
            violations=["Trailing commas in strict JSON mode"],
            detectable_patterns=[",\\]", ",\\}"],
        ),
        ZenPrinciple(
            id="json-002",
            principle="Keep object depth understandable",
            category=PrincipleCategory.STRUCTURE,
            severity=6,
            description="Deeply nested objects/arrays are hard to reason about and validate.",
            violations=["Nesting depth exceeds configured threshold"],
        ),
        ZenPrinciple(
            id="json-003",
            principle="Keys must be unique",
            category=PrincipleCategory.CORRECTNESS,
            severity=8,
            description="Duplicate object keys silently override values in many parsers.",
            violations=["Duplicate keys in an object"],
        ),
        ZenPrinciple(
            id="json-004",
            principle="Avoid magic string repetition",
            category=PrincipleCategory.CLARITY,
            severity=5,
            description="Repeated string literals should be extracted or referenced consistently.",
            violations=["Repeated magic string values"],
        ),
        ZenPrinciple(
            id="json-005",
            principle="Keys are case-sensitive identifiers",
            category=PrincipleCategory.NAMING,
            severity=5,
            description="Avoid mixing camelCase, snake_case, and PascalCase at the same object level.",
            violations=["Mixed key casing at same object level"],
        ),
        ZenPrinciple(
            id="json-006",
            principle="Keep inline arrays bounded",
            category=PrincipleCategory.STRUCTURE,
            severity=4,
            description="Very large inline arrays are hard to review and often belong in separate data files.",
            violations=["Oversized inline arrays"],
        ),
        ZenPrinciple(
            id="json-007",
            principle="Prefer omission over null sprawl",
            category=PrincipleCategory.CORRECTNESS,
            severity=5,
            description="Excessive null usage usually indicates optional keys that can be omitted.",
            violations=["Excessive null values across the document"],
        ),
        ZenPrinciple(
            id="json-008",
            principle="Dates must follow ISO 8601",
            category=PrincipleCategory.CORRECTNESS,
            severity=6,
            description=(
                "Date strings should use ISO 8601 format (YYYY-MM-DD or "
                "YYYY-MM-DDTHH:MM:SSZ) for unambiguous, sortable representation. "
                "Locale-dependent formats such as MM/DD/YYYY create parsing ambiguity."
            ),
            violations=["Non-ISO 8601 date string detected"],
            detectable_patterns=[
                r"\d{1,2}/\d{1,2}/\d{2,4}",
                r"\d{1,2}\.\d{1,2}\.\d{4}",
            ],
        ),
        ZenPrinciple(
            id="json-009",
            principle="Prefer key omission over explicit null",
            category=PrincipleCategory.CLARITY,
            severity=5,
            description=(
                "Top-level object keys whose value is explicitly null should be "
                "omitted entirely. Explicit null at the top level signals optional "
                "absence, which is better expressed by omitting the key."
            ),
            violations=["Top-level key set to explicit null"],
        ),
    ],
)
