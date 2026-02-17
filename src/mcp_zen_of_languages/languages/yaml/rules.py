"""YAML zen principles as Pydantic models."""

from pydantic import HttpUrl

from ...rules.base_models import LanguageZenPrinciples, PrincipleCategory, ZenPrinciple

YAML_ZEN = LanguageZenPrinciples(
    language="yaml",
    name="YAML",
    philosophy="YAML 1.2 Specification",
    source_text="YAML 1.2 Specification",
    source_url=HttpUrl("https://yaml.org/spec/1.2.2/"),
    principles=[
        ZenPrinciple(
            id="yaml-001",
            principle="Use consistent indentation",
            category=PrincipleCategory.READABILITY,
            severity=6,
            description="Indentation should be consistent to avoid structural mistakes.",
            violations=[
                "Mixed indentation widths",
                "Indentation not aligned to expected spaces",
            ],
            metrics={"indent_size": 2},
        ),
        ZenPrinciple(
            id="yaml-002",
            principle="Avoid tabs in indentation",
            category=PrincipleCategory.READABILITY,
            severity=7,
            description="YAML indentation should use spaces, not tabs.",
            violations=["Tab characters in indentation"],
            detectable_patterns=["\t"],
        ),
        ZenPrinciple(
            id="yaml-003",
            principle="Avoid duplicate keys",
            category=PrincipleCategory.CORRECTNESS,
            severity=8,
            description="Duplicate keys can cause data loss when parsing.",
            violations=["Duplicate mapping keys"],
        ),
        ZenPrinciple(
            id="yaml-004",
            principle="Use lowercase keys",
            category=PrincipleCategory.CONSISTENCY,
            severity=5,
            description="Lowercase keys improve consistency across configurations.",
            violations=["Uppercase characters in keys"],
        ),
        ZenPrinciple(
            id="yaml-005",
            principle="Keys should be self-explanatory",
            category=PrincipleCategory.NAMING,
            severity=5,
            description="Prefer descriptive keys over terse abbreviations.",
            violations=["Single-letter or cryptic keys"],
            metrics={"min_key_length": 3},
        ),
        ZenPrinciple(
            id="yaml-006",
            principle="Consistency provides comfort",
            category=PrincipleCategory.CONSISTENCY,
            severity=5,
            description="Use a consistent list style throughout the file.",
            violations=["Mixed list markers (- and *)"],
            metrics={"allowed_list_markers": ["-"]},
        ),
        ZenPrinciple(
            id="yaml-007",
            principle="Comments explain intent",
            category=PrincipleCategory.DOCUMENTATION,
            severity=4,
            description="Document complex sections with comments.",
            violations=["No comments in a complex configuration"],
            metrics={"min_comment_lines": 1, "min_nonempty_lines": 5},
        ),
        ZenPrinciple(
            id="yaml-008",
            principle="Strings should look like strings",
            category=PrincipleCategory.CLARITY,
            severity=6,
            description="Quote strings with spaces or special characters.",
            violations=["Unquoted strings with special characters"],
            metrics={"require_quotes_for_specials": True},
        ),
    ],
)
