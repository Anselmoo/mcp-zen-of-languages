"""Universal dogma contracts and rule-to-dogma normalization helpers."""

from __future__ import annotations

from enum import StrEnum
from functools import cache
from typing import TYPE_CHECKING

from pydantic import BaseModel

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


class TestingTacticsDogmaID(StrEnum):
    """Micro-level testing dogma identifiers (F.I.R.S.T. + Clean Code + Kent Beck's Test Desiderata)."""

    ISOLATED = "ZEN-TEST-ISOLATED"
    DETERMINISTIC = "ZEN-TEST-DETERMINISTIC"
    SINGLE_CONCEPT = "ZEN-TEST-SINGLE-CONCEPT"
    EXPRESSIVE_NAME = "ZEN-TEST-EXPRESSIVE-NAME"
    NO_BRANCHING = "ZEN-TEST-NO-BRANCHING"
    FAST = "ZEN-TEST-FAST"
    DOCUMENTED_INTENT = "ZEN-TEST-DOCUMENTED-INTENT"
    FALSE_NEGATIVE_FREE = "ZEN-TEST-FALSE-NEGATIVE-FREE"
    CLEAN_CODE = "ZEN-TEST-CLEAN-CODE"
    PROPORTIONAL = "ZEN-TEST-PROPORTIONAL"


class TestingStrategyDogmaID(StrEnum):
    """Macro-level testing dogma identifiers (V-Model / Test Pyramid / ASPICE / Testing Manifesto)."""

    BOUNDARY = "ZEN-MACRO-BOUNDARY"
    TRACEABILITY = "ZEN-MACRO-TRACEABILITY"
    INTEGRATION = "ZEN-MACRO-INTEGRATION"
    RISK = "ZEN-MACRO-RISK"
    REALITY_CHECK = "ZEN-MACRO-REALITY-CHECK"
    FLAKINESS = "ZEN-MACRO-FLAKINESS"
    SHIFT_RIGHT = "ZEN-MACRO-SHIFT-RIGHT"
    OWNERSHIP = "ZEN-MACRO-OWNERSHIP"
    EVOLVABILITY = "ZEN-MACRO-EVOLVABILITY"
    VISIBILITY = "ZEN-MACRO-VISIBILITY"


DOGMA_RULE_IDS: tuple[str, ...] = (
    *tuple(dogma.value for dogma in UniversalDogmaID),
    *tuple(dogma.value for dogma in TestingTacticsDogmaID),
    *tuple(dogma.value for dogma in TestingStrategyDogmaID),
)

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
    ("flaky test", UniversalDogmaID.FAIL_FAST),
    ("test isolation", UniversalDogmaID.STRICT_FENCES),
    ("shared state", UniversalDogmaID.STRICT_FENCES),
    ("test branching", UniversalDogmaID.EXPLICIT_INTENT),
    ("assert all", UniversalDogmaID.PROPORTIONATE_COMPLEXITY),
    ("over-mocking", UniversalDogmaID.VISIBLE_STATE),
    ("slow test", UniversalDogmaID.FAIL_FAST),
    ("zombie test", UniversalDogmaID.RUTHLESS_DELETION),
)

_TESTING_TACTICS_UNIVERSAL_MAP: dict[TestingTacticsDogmaID, UniversalDogmaID] = {
    TestingTacticsDogmaID.ISOLATED: UniversalDogmaID.STRICT_FENCES,
    TestingTacticsDogmaID.DETERMINISTIC: UniversalDogmaID.VISIBLE_STATE,
    TestingTacticsDogmaID.SINGLE_CONCEPT: UniversalDogmaID.PROPORTIONATE_COMPLEXITY,
    TestingTacticsDogmaID.EXPRESSIVE_NAME: UniversalDogmaID.UNAMBIGUOUS_NAME,
    TestingTacticsDogmaID.NO_BRANCHING: UniversalDogmaID.EXPLICIT_INTENT,
    TestingTacticsDogmaID.FAST: UniversalDogmaID.FAIL_FAST,
    TestingTacticsDogmaID.DOCUMENTED_INTENT: UniversalDogmaID.EXPLICIT_INTENT,
    TestingTacticsDogmaID.FALSE_NEGATIVE_FREE: UniversalDogmaID.FAIL_FAST,
    TestingTacticsDogmaID.CLEAN_CODE: UniversalDogmaID.RUTHLESS_DELETION,
    TestingTacticsDogmaID.PROPORTIONAL: UniversalDogmaID.PROPORTIONATE_COMPLEXITY,
}

_TESTING_STRATEGY_UNIVERSAL_MAP: dict[TestingStrategyDogmaID, UniversalDogmaID] = {
    TestingStrategyDogmaID.BOUNDARY: UniversalDogmaID.RIGHT_ABSTRACTION,
    TestingStrategyDogmaID.TRACEABILITY: UniversalDogmaID.EXPLICIT_INTENT,
    TestingStrategyDogmaID.INTEGRATION: UniversalDogmaID.STRICT_FENCES,
    TestingStrategyDogmaID.RISK: UniversalDogmaID.PROPORTIONATE_COMPLEXITY,
    TestingStrategyDogmaID.REALITY_CHECK: UniversalDogmaID.VISIBLE_STATE,
    TestingStrategyDogmaID.FLAKINESS: UniversalDogmaID.FAIL_FAST,
    TestingStrategyDogmaID.SHIFT_RIGHT: UniversalDogmaID.VISIBLE_STATE,
    TestingStrategyDogmaID.OWNERSHIP: UniversalDogmaID.STRICT_FENCES,
    TestingStrategyDogmaID.EVOLVABILITY: UniversalDogmaID.RUTHLESS_DELETION,
    TestingStrategyDogmaID.VISIBILITY: UniversalDogmaID.UNAMBIGUOUS_NAME,
}


def resolve_tactics_dogma(tactics_id: TestingTacticsDogmaID) -> UniversalDogmaID:
    """Return the parent UniversalDogmaID for a micro testing dogma."""
    return _TESTING_TACTICS_UNIVERSAL_MAP[tactics_id]


def resolve_strategy_dogma(strategy_id: TestingStrategyDogmaID) -> UniversalDogmaID:
    """Return the parent UniversalDogmaID for a macro testing dogma."""
    return _TESTING_STRATEGY_UNIVERSAL_MAP[strategy_id]


class DogmaFamilyEntry(BaseModel):
    """Single dogma entry within a catalogue family."""

    id: str
    parent_universal_id: str | None = None


class DogmaFamily(BaseModel):
    """One named family of dogmas with its philosophy root."""

    family: str
    philosophy: str
    count: int
    dogmas: list[DogmaFamilyEntry]


class DogmaCatalogue(BaseModel):
    """Full cross-family dogma catalogue — single source of truth for all dogma discovery."""

    families: list[DogmaFamily]
    total: int


def build_dogma_catalogue() -> DogmaCatalogue:
    """Build and return the full dogma catalogue across all families.

    Returns:
        DogmaCatalogue: Structured catalogue with universal, testing-tactics,
            and testing-strategy families.
    """
    universal_family = DogmaFamily(
        family="universal",
        philosophy="Canonical zen principles",
        count=len(UniversalDogmaID),
        dogmas=[DogmaFamilyEntry(id=d.value) for d in UniversalDogmaID],
    )
    tactics_family = DogmaFamily(
        family="testing_tactics",
        philosophy="F.I.R.S.T. + Clean Code + Kent Beck's Test Desiderata",
        count=len(TestingTacticsDogmaID),
        dogmas=[
            DogmaFamilyEntry(
                id=d.value,
                parent_universal_id=_TESTING_TACTICS_UNIVERSAL_MAP[d].value,
            )
            for d in TestingTacticsDogmaID
        ],
    )
    strategy_family = DogmaFamily(
        family="testing_strategy",
        philosophy="V-Model, Test Pyramid, ASPICE, Testing Manifesto",
        count=len(TestingStrategyDogmaID),
        dogmas=[
            DogmaFamilyEntry(
                id=d.value,
                parent_universal_id=_TESTING_STRATEGY_UNIVERSAL_MAP[d].value,
            )
            for d in TestingStrategyDogmaID
        ],
    )
    families = [universal_family, tactics_family, strategy_family]
    return DogmaCatalogue(
        families=families,
        total=sum(f.count for f in families),
    )


@cache
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
