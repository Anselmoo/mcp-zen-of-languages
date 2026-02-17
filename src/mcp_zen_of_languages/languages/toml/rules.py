"""TOML zen principles as Pydantic models."""

from pydantic import HttpUrl

from ...rules.base_models import LanguageZenPrinciples, PrincipleCategory, ZenPrinciple

TOML_ZEN = LanguageZenPrinciples(
    language="toml",
    name="TOML",
    philosophy="TOML Specification v1.0.0",
    source_text="TOML Specification",
    source_url=HttpUrl("https://toml.io/en/"),
    principles=[
        ZenPrinciple(
            id="toml-001",
            principle="Avoid inline tables",
            category=PrincipleCategory.READABILITY,
            severity=6,
            description="Inline tables are harder to read; use full tables instead.",
            violations=["Inline table definitions in assignments"],
        ),
        ZenPrinciple(
            id="toml-002",
            principle="Avoid duplicate keys",
            category=PrincipleCategory.CORRECTNESS,
            severity=8,
            description="Duplicate keys can overwrite previous values.",
            violations=["Duplicate key definitions"],
        ),
        ZenPrinciple(
            id="toml-003",
            principle="Use lowercase keys",
            category=PrincipleCategory.CONSISTENCY,
            severity=5,
            description="Lowercase keys improve consistency across configurations.",
            violations=["Uppercase characters in keys"],
        ),
        ZenPrinciple(
            id="toml-004",
            principle="Avoid trailing commas",
            category=PrincipleCategory.READABILITY,
            severity=5,
            description="Trailing commas reduce readability in TOML arrays/tables.",
            violations=["Trailing commas before closing brackets"],
        ),
        ZenPrinciple(
            id="toml-005",
            principle="Clarity is paramount",
            category=PrincipleCategory.CLARITY,
            severity=5,
            description="Explain magic values with comments.",
            violations=["Magic values without comments"],
            metrics={"min_comment_lines": 1},
        ),
        ZenPrinciple(
            id="toml-006",
            principle="Order implies importance",
            category=PrincipleCategory.ORGANIZATION,
            severity=4,
            description="Group related keys together before arrays or tables.",
            violations=["Repeated table headers spread apart"],
        ),
        ZenPrinciple(
            id="toml-007",
            principle="Time is specific",
            category=PrincipleCategory.CORRECTNESS,
            severity=6,
            description="Use ISO 8601 timestamps for dates.",
            violations=["Non-ISO date strings"],
        ),
        ZenPrinciple(
            id="toml-008",
            principle="Floats are not integers",
            category=PrincipleCategory.CORRECTNESS,
            severity=6,
            description="Use integer types where appropriate, avoid decimal .0 values.",
            violations=["Floats that represent integers"],
        ),
    ],
)
