"""Universal dogma contracts and rule-to-dogma normalization helpers."""

from __future__ import annotations

from enum import StrEnum
from functools import lru_cache
from typing import TYPE_CHECKING

from mcp_zen_of_languages.rules import get_language_zen
from mcp_zen_of_languages.rules.base_models import PrincipleCategory

if TYPE_CHECKING:
    from collections.abc import Iterable

    from mcp_zen_of_languages.rules.base_models import ZenPrinciple


class UniversalDogmaID(StrEnum):
    """Canonical universal dogma identifiers."""

    UTILIZE_ARGUMENTS = "ZEN-UTILIZE-ARGUMENTS"
    EXPLICIT_INTENT = "ZEN-EXPLICIT-INTENT"
    RETURN_EARLY = "ZEN-RETURN-EARLY"
    FAIL_FAST = "ZEN-FAIL-FAST"
    RIGHT_ABSTRACTION = "ZEN-RIGHT-ABSTRACTION"
    UNAMBIGUOUS_NAME = "ZEN-UNAMBIGUOUS-NAME"
    VISIBLE_STATE = "ZEN-VISIBLE-STATE"
    STRICT_FENCES = "ZEN-STRICT-FENCES"
    RUTHLESS_DELETION = "ZEN-RUTHLESS-DELETION"
    PROPORTIONATE_COMPLEXITY = "ZEN-PROPORTIONATE-COMPLEXITY"


DOGMA_RULE_IDS: tuple[str, ...] = tuple(dogma.value for dogma in UniversalDogmaID)

_CATEGORY_TO_DOGMAS: dict[PrincipleCategory, tuple[UniversalDogmaID, ...]] = {
    PrincipleCategory.READABILITY: (UniversalDogmaID.UNAMBIGUOUS_NAME,),
    PrincipleCategory.CLARITY: (UniversalDogmaID.EXPLICIT_INTENT,),
    PrincipleCategory.COMPLEXITY: (UniversalDogmaID.PROPORTIONATE_COMPLEXITY,),
    PrincipleCategory.ARCHITECTURE: (UniversalDogmaID.RIGHT_ABSTRACTION,),
    PrincipleCategory.STRUCTURE: (UniversalDogmaID.RETURN_EARLY,),
    PrincipleCategory.CONSISTENCY: (UniversalDogmaID.EXPLICIT_INTENT,),
    PrincipleCategory.ERROR_HANDLING: (UniversalDogmaID.FAIL_FAST,),
    PrincipleCategory.CORRECTNESS: (UniversalDogmaID.EXPLICIT_INTENT,),
    PrincipleCategory.IDIOMS: (UniversalDogmaID.RIGHT_ABSTRACTION,),
    PrincipleCategory.ORGANIZATION: (UniversalDogmaID.STRICT_FENCES,),
    PrincipleCategory.ASYNC: (UniversalDogmaID.FAIL_FAST,),
    PrincipleCategory.IMMUTABILITY: (UniversalDogmaID.VISIBLE_STATE,),
    PrincipleCategory.TYPE_SAFETY: (UniversalDogmaID.EXPLICIT_INTENT,),
    PrincipleCategory.DESIGN: (UniversalDogmaID.RIGHT_ABSTRACTION,),
    PrincipleCategory.FUNCTIONAL: (UniversalDogmaID.RIGHT_ABSTRACTION,),
    PrincipleCategory.CONFIGURATION: (UniversalDogmaID.EXPLICIT_INTENT,),
    PrincipleCategory.CONCURRENCY: (UniversalDogmaID.VISIBLE_STATE,),
    PrincipleCategory.INITIALIZATION: (UniversalDogmaID.EXPLICIT_INTENT,),
    PrincipleCategory.PERFORMANCE: (UniversalDogmaID.PROPORTIONATE_COMPLEXITY,),
    PrincipleCategory.DEBUGGING: (UniversalDogmaID.EXPLICIT_INTENT,),
    PrincipleCategory.SAFETY: (UniversalDogmaID.FAIL_FAST,),
    PrincipleCategory.OWNERSHIP: (UniversalDogmaID.VISIBLE_STATE,),
    PrincipleCategory.RESOURCE_MANAGEMENT: (UniversalDogmaID.STRICT_FENCES,),
    PrincipleCategory.MEMORY_MANAGEMENT: (UniversalDogmaID.VISIBLE_STATE,),
    PrincipleCategory.SCOPE: (UniversalDogmaID.STRICT_FENCES,),
    PrincipleCategory.SECURITY: (UniversalDogmaID.STRICT_FENCES,),
    PrincipleCategory.ROBUSTNESS: (UniversalDogmaID.FAIL_FAST,),
    PrincipleCategory.USABILITY: (UniversalDogmaID.UNAMBIGUOUS_NAME,),
    PrincipleCategory.NAMING: (UniversalDogmaID.UNAMBIGUOUS_NAME,),
    PrincipleCategory.DOCUMENTATION: (UniversalDogmaID.UNAMBIGUOUS_NAME,),
}

_KEYWORD_TO_DOGMAS: tuple[tuple[str, UniversalDogmaID], ...] = (
    ("unused argument", UniversalDogmaID.UTILIZE_ARGUMENTS),
    ("unused parameter", UniversalDogmaID.UTILIZE_ARGUMENTS),
    ("implicit", UniversalDogmaID.EXPLICIT_INTENT),
    ("explicit", UniversalDogmaID.EXPLICIT_INTENT),
    ("magic", UniversalDogmaID.EXPLICIT_INTENT),
    ("nested", UniversalDogmaID.RETURN_EARLY),
    ("guard clause", UniversalDogmaID.RETURN_EARLY),
    ("error", UniversalDogmaID.FAIL_FAST),
    ("exception", UniversalDogmaID.FAIL_FAST),
    ("unwrap", UniversalDogmaID.FAIL_FAST),
    ("panic", UniversalDogmaID.FAIL_FAST),
    ("abstraction", UniversalDogmaID.RIGHT_ABSTRACTION),
    ("interface", UniversalDogmaID.RIGHT_ABSTRACTION),
    ("flag argument", UniversalDogmaID.RIGHT_ABSTRACTION),
    ("name", UniversalDogmaID.UNAMBIGUOUS_NAME),
    ("identifier", UniversalDogmaID.UNAMBIGUOUS_NAME),
    ("alias", UniversalDogmaID.UNAMBIGUOUS_NAME),
    ("mutability", UniversalDogmaID.VISIBLE_STATE),
    ("readonly", UniversalDogmaID.VISIBLE_STATE),
    ("state", UniversalDogmaID.VISIBLE_STATE),
    ("namespace", UniversalDogmaID.STRICT_FENCES),
    ("encapsulation", UniversalDogmaID.STRICT_FENCES),
    ("boundary", UniversalDogmaID.STRICT_FENCES),
    ("dead code", UniversalDogmaID.RUTHLESS_DELETION),
    ("unreachable", UniversalDogmaID.RUTHLESS_DELETION),
    ("complexity", UniversalDogmaID.PROPORTIONATE_COMPLEXITY),
    ("simple", UniversalDogmaID.PROPORTIONATE_COMPLEXITY),
)


@lru_cache(maxsize=None)
def _principles_by_id(language: str) -> dict[str, ZenPrinciple]:
    lang_zen = get_language_zen(language)
    if not lang_zen:
        return {}
    return {principle.id: principle for principle in lang_zen.principles}


def infer_dogmas_for_principle(principle: ZenPrinciple) -> tuple[str, ...]:
    """Infer universal dogmas for a language-specific rule."""
    baseline = _CATEGORY_TO_DOGMAS.get(
        principle.category,
        (UniversalDogmaID.PROPORTIONATE_COMPLEXITY,),
    )
    dogmas: list[str] = [dogma.value for dogma in baseline]

    violation_texts: list[str] = [
        str(violation) for violation in (principle.violations or [])
    ]
    pattern_texts: list[str] = [
        str(pattern) for pattern in (principle.detectable_patterns or [])
    ]
    haystack_parts: list[str] = [principle.principle, principle.description]
    haystack_parts.extend(violation_texts)
    haystack_parts.extend(pattern_texts)
    search_haystack = " ".join(haystack_parts).lower()
    for keyword, dogma in _KEYWORD_TO_DOGMAS:
        if keyword in search_haystack and dogma.value not in dogmas:
            dogmas.append(dogma.value)

    return tuple(dogmas)


def dogmas_for_rule(language: str, rule_id: str) -> tuple[str, ...]:
    """Return inferred universal dogmas for one rule ID in one language."""
    principle = _principles_by_id(language).get(rule_id)
    if principle is None:
        return ()
    return infer_dogmas_for_principle(principle)


def dogmas_for_rule_ids(language: str, rule_ids: Iterable[str]) -> tuple[str, ...]:
    """Return deduplicated inferred universal dogmas for multiple rule IDs."""
    ordered: list[str] = []
    seen: set[str] = set()
    for rule_id in rule_ids:
        for dogma in dogmas_for_rule(language, rule_id):
            if dogma in seen:
                continue
            seen.add(dogma)
            ordered.append(dogma)
    return tuple(ordered)
