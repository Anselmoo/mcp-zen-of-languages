"""Explicit universal-dogma assignments for framework rule mappings."""

from __future__ import annotations

from mcp_zen_of_languages.core.universal_dogmas import UniversalDogmaID


FRAMEWORK_RULE_DOGMAS: dict[str, tuple[str, ...]] = {
    "react-001": (
        UniversalDogmaID.EXPLICIT_INTENT.value,
        UniversalDogmaID.VISIBLE_STATE.value,
    ),
    "react-002": (UniversalDogmaID.PROPORTIONATE_COMPLEXITY.value,),
    "react-003": (
        UniversalDogmaID.RIGHT_ABSTRACTION.value,
        UniversalDogmaID.STRICT_FENCES.value,
    ),
    "react-004": (UniversalDogmaID.EXPLICIT_INTENT.value,),
    "react-005": (
        UniversalDogmaID.FAIL_FAST.value,
        UniversalDogmaID.STRICT_FENCES.value,
    ),
    "vue-001": (UniversalDogmaID.UNAMBIGUOUS_NAME.value,),
    "vue-002": (UniversalDogmaID.EXPLICIT_INTENT.value,),
    "vue-003": (
        UniversalDogmaID.EXPLICIT_INTENT.value,
        UniversalDogmaID.VISIBLE_STATE.value,
    ),
    "vue-004": (UniversalDogmaID.EXPLICIT_INTENT.value,),
    "vue-005": (
        UniversalDogmaID.VISIBLE_STATE.value,
        UniversalDogmaID.EXPLICIT_INTENT.value,
    ),
    "angular-001": (UniversalDogmaID.PROPORTIONATE_COMPLEXITY.value,),
    "angular-002": (UniversalDogmaID.EXPLICIT_INTENT.value,),
    "angular-003": (
        UniversalDogmaID.STRICT_FENCES.value,
        UniversalDogmaID.EXPLICIT_INTENT.value,
    ),
    "angular-004": (UniversalDogmaID.UNAMBIGUOUS_NAME.value,),
    "angular-005": (UniversalDogmaID.PROPORTIONATE_COMPLEXITY.value,),
    "nextjs-001": (
        UniversalDogmaID.RIGHT_ABSTRACTION.value,
        UniversalDogmaID.EXPLICIT_INTENT.value,
    ),
    "nextjs-002": (UniversalDogmaID.PROPORTIONATE_COMPLEXITY.value,),
    "nextjs-003": (
        UniversalDogmaID.RIGHT_ABSTRACTION.value,
        UniversalDogmaID.EXPLICIT_INTENT.value,
    ),
    "nextjs-004": (
        UniversalDogmaID.STRICT_FENCES.value,
        UniversalDogmaID.FAIL_FAST.value,
    ),
    "nextjs-005": (UniversalDogmaID.PROPORTIONATE_COMPLEXITY.value,),
    "pydantic-001": (
        UniversalDogmaID.RIGHT_ABSTRACTION.value,
        UniversalDogmaID.EXPLICIT_INTENT.value,
    ),
    "pydantic-002": (UniversalDogmaID.RIGHT_ABSTRACTION.value,),
    "pydantic-003": (
        UniversalDogmaID.VISIBLE_STATE.value,
        UniversalDogmaID.EXPLICIT_INTENT.value,
    ),
    "pydantic-004": (
        UniversalDogmaID.RIGHT_ABSTRACTION.value,
        UniversalDogmaID.EXPLICIT_INTENT.value,
    ),
    "pydantic-005": (
        UniversalDogmaID.RIGHT_ABSTRACTION.value,
        UniversalDogmaID.EXPLICIT_INTENT.value,
    ),
    "pydantic-006": (
        UniversalDogmaID.RIGHT_ABSTRACTION.value,
        UniversalDogmaID.UNAMBIGUOUS_NAME.value,
    ),
    "pydantic-007": (UniversalDogmaID.EXPLICIT_INTENT.value,),
    "pydantic-008": (
        UniversalDogmaID.RIGHT_ABSTRACTION.value,
        UniversalDogmaID.EXPLICIT_INTENT.value,
    ),
    "fastapi-001": (UniversalDogmaID.EXPLICIT_INTENT.value,),
    "fastapi-002": (UniversalDogmaID.EXPLICIT_INTENT.value,),
    "fastapi-003": (
        UniversalDogmaID.FAIL_FAST.value,
        UniversalDogmaID.EXPLICIT_INTENT.value,
    ),
    "fastapi-004": (UniversalDogmaID.RIGHT_ABSTRACTION.value,),
    "fastapi-005": (UniversalDogmaID.PROPORTIONATE_COMPLEXITY.value,),
    "fastapi-006": (
        UniversalDogmaID.RIGHT_ABSTRACTION.value,
        UniversalDogmaID.EXPLICIT_INTENT.value,
    ),
    "django-001": (
        UniversalDogmaID.STRICT_FENCES.value,
        UniversalDogmaID.FAIL_FAST.value,
    ),
    "django-002": (UniversalDogmaID.STRICT_FENCES.value,),
    "django-003": (
        UniversalDogmaID.STRICT_FENCES.value,
        UniversalDogmaID.FAIL_FAST.value,
    ),
    "django-004": (
        UniversalDogmaID.STRICT_FENCES.value,
        UniversalDogmaID.RIGHT_ABSTRACTION.value,
    ),
    "django-005": (UniversalDogmaID.RIGHT_ABSTRACTION.value,),
    "django-006": (UniversalDogmaID.PROPORTIONATE_COMPLEXITY.value,),
    "sqlalchemy-001": (
        UniversalDogmaID.STRICT_FENCES.value,
        UniversalDogmaID.FAIL_FAST.value,
    ),
    "sqlalchemy-002": (
        UniversalDogmaID.STRICT_FENCES.value,
        UniversalDogmaID.EXPLICIT_INTENT.value,
    ),
    "sqlalchemy-003": (UniversalDogmaID.RIGHT_ABSTRACTION.value,),
    "sqlalchemy-004": (UniversalDogmaID.RIGHT_ABSTRACTION.value,),
    "sqlalchemy-005": (
        UniversalDogmaID.PROPORTIONATE_COMPLEXITY.value,
        UniversalDogmaID.EXPLICIT_INTENT.value,
    ),
    "sqlalchemy-006": (UniversalDogmaID.PROPORTIONATE_COMPLEXITY.value,),
}


def framework_rule_dogmas(rule_id: str) -> tuple[str, ...]:
    """Return the explicit dogma set assigned to a framework rule."""
    return FRAMEWORK_RULE_DOGMAS[rule_id]


__all__ = ["FRAMEWORK_RULE_DOGMAS", "framework_rule_dogmas"]
