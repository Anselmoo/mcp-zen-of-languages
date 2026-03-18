"""Framework-specific vue zen principles used by the generated analyzer surfaces."""

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


VUE_ZEN = LanguageZenPrinciples(
    language="vue",
    name="Vue",
    philosophy="Progressive UI architecture with explicit reactivity and readable templates.",
    source_text="Vue Style Guide",
    source_url=HttpUrl("https://vuejs.org/style-guide/"),
    principles=[
        _principle(
            rule_id="vue-001",
            principle="Components should use multi-word names",
            category=PrincipleCategory.READABILITY,
            severity=7,
            description="Multi-word component names reduce collisions with native HTML elements and improve readability.",
            patterns=["re:\\bname\\s*:\\s*[\\\"\\'][A-Z][a-zA-Z0-9]*[\\\"\\']"],
            recommendation="Rename the component to a multi-word name such as UserCard or TodoList.",
        ),
        _principle(
            rule_id="vue-002",
            principle="Props should declare explicit types",
            category=PrincipleCategory.CORRECTNESS,
            severity=8,
            description="Untyped props weaken runtime validation and make component contracts harder to understand.",
            patterns=[
                "re:(?:defineProps\\(\\s*\\[[^\\]]+\\]\\s*\\)|props\\s*:\\s*\\[[^\\]]+\\])"
            ],
            recommendation="Declare props with defineProps<T>() or a typed props object.",
        ),
        _principle(
            rule_id="vue-003",
            principle="v-for directives need a :key binding on the same element",
            category=PrincipleCategory.CORRECTNESS,
            severity=9,
            description="Stable keys are required for predictable diffing and component state preservation.",
            patterns=[
                "re:<[^>]+\\bv-for\\s*=\\s*[\\\"\\'][^\\\"\\']+[\\\"\\'](?:(?!:key=)[^>])*>"
            ],
            recommendation="Add a :key binding derived from stable item identity.",
        ),
        _principle(
            rule_id="vue-004",
            principle="Avoid using v-if and v-for on the same element",
            category=PrincipleCategory.CORRECTNESS,
            severity=9,
            description="Combining v-if and v-for on the same node makes rendering intent harder to reason about.",
            patterns=[
                "re:<[^>]+\\bv-if\\s*=.*\\bv-for\\s*=|<[^>]+\\bv-for\\s*=.*\\bv-if\\s*="
            ],
            recommendation="Split the conditional wrapper from the looped element or filter the data first.",
        ),
        _principle(
            rule_id="vue-005",
            principle="Props should not be mutated directly",
            category=PrincipleCategory.CORRECTNESS,
            severity=10,
            description="Direct prop mutation breaks one-way data flow and can desynchronize parent and child state.",
            patterns=["re:\\bprops\\.\\w+\\s*="],
            recommendation="Emit an event or derive local state instead of mutating props.",
        ),
    ],
)
