"""Framework-specific pydantic zen principles used by the generated analyzer surfaces."""

from __future__ import annotations

from pydantic import HttpUrl

from mcp_zen_of_languages.rules.base_models import LanguageZenPrinciples
from mcp_zen_of_languages.rules.base_models import PrincipleCategory
from mcp_zen_of_languages.rules.base_models import ZenPrinciple


def _principle(  # noqa: PLR0913
    rule_id: str,
    principle: str,
    category: PrincipleCategory,
    severity: int,
    description: str,
    patterns: list[str],
    recommendation: str,
) -> ZenPrinciple:
    return ZenPrinciple(
        id=rule_id,
        principle=principle,
        category=category,
        severity=severity,
        description=description,
        violations=[principle],
        detectable_patterns=patterns,
        recommended_alternative=recommendation,
    )


PYDANTIC_ZEN = LanguageZenPrinciples(
    language="pydantic",
    name="Pydantic",
    philosophy="Declarative data validation driven by explicit type annotations and fail-fast contracts.",
    source_text="Pydantic v2 documentation",
    source_url=HttpUrl("https://docs.pydantic.dev/latest/"),
    principles=[
        _principle(
            rule_id="pydantic-001",
            principle="Use model_dump and model_dump_json instead of v1 serialization APIs",
            category=PrincipleCategory.IDIOMS,
            severity=8,
            description="Pydantic v2 renamed serialization APIs to make model boundaries more explicit.",
            patterns=["re:\\.(?:dict|json)\\("],
            recommendation="Use model_dump() or model_dump_json() on Pydantic models.",
        ),
        _principle(
            rule_id="pydantic-002",
            principle="Use model_validate instead of parse_obj or parse_raw",
            category=PrincipleCategory.IDIOMS,
            severity=8,
            description="v2 validation APIs center around model_validate and model_validate_json.",
            patterns=["re:\\b(?:parse_obj|parse_raw|from_orm)\\("],
            recommendation="Use model_validate(), model_validate_json(), or from_attributes-compatible validation.",
        ),
        _principle(
            rule_id="pydantic-003",
            principle="Mutable defaults should use Field(default_factory=...)",
            category=PrincipleCategory.CORRECTNESS,
            severity=9,
            description="Plain list, dict, and set defaults are shared between instances and create state leaks.",
            patterns=[
                "re::\\s*(?:list|dict|set)\\b[^=\\n]*=\\s*(?:\\[\\]|\\{\\}|set\\(\\))"
            ],
            recommendation="Use Field(default_factory=list), dict, or set instead of a mutable literal default.",
        ),
        _principle(
            rule_id="pydantic-004",
            principle="Prefer model_config over nested Config classes",
            category=PrincipleCategory.IDIOMS,
            severity=7,
            description="Pydantic v2 consolidated model configuration into the model_config attribute.",
            patterns=["re:^\\s*class\\s+Config\\s*:"],
            recommendation="Replace the nested Config class with model_config = ConfigDict(...).",
        ),
        _principle(
            rule_id="pydantic-005",
            principle="Use field_validator instead of validator",
            category=PrincipleCategory.IDIOMS,
            severity=7,
            description="v2 split validation hooks into explicit decorator families such as field_validator and model_validator.",
            patterns=["re:@validator\\b"],
            recommendation="Use @field_validator or @model_validator in Pydantic v2 code.",
        ),
        _principle(
            rule_id="pydantic-006",
            principle="Avoid __fields__; use model_fields in v2",
            category=PrincipleCategory.IDIOMS,
            severity=7,
            description="The v2 model introspection surface renamed __fields__ to model_fields.",
            patterns=["re:\\.__fields__\\b"],
            recommendation="Use model_fields for field metadata lookups.",
        ),
        _principle(
            rule_id="pydantic-007",
            principle="Prefer X | None over Optional[X] in modern Python code",
            category=PrincipleCategory.IDIOMS,
            severity=4,
            description="Modern union syntax is the project standard for Python 3.12+ and keeps annotations consistent.",
            patterns=["re:\\bOptional\\["],
            recommendation="Use X | None instead of Optional[X].",
        ),
        _principle(
            rule_id="pydantic-008",
            principle="Use from_attributes instead of orm_mode",
            category=PrincipleCategory.IDIOMS,
            severity=7,
            description="Pydantic v2 renamed ORM compatibility settings to from_attributes.",
            patterns=["re:orm_mode\\s*=\\s*True"],
            recommendation="Configure from_attributes=True via model_config.",
        ),
    ],
)
