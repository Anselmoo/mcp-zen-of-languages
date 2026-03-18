"""Framework-specific react zen principles used by the generated analyzer surfaces."""

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


REACT_ZEN = LanguageZenPrinciples(
    language="react",
    name="React",
    philosophy="Composable, predictable UI driven by state and props.",
    source_text="React documentation and Rules of React",
    source_url=HttpUrl("https://react.dev/"),
    principles=[
        _principle(
            rule_id="react-001",
            principle="List keys must be stable and not derived from array indexes",
            category=PrincipleCategory.CORRECTNESS,
            severity=9,
            description="React list rendering depends on stable keys to preserve component identity across renders.",
            patterns=["re:key=\\{(?:index|i|itemIndex)\\}"],
            recommendation="Use an identifier from the data model instead of the array index.",
        ),
        _principle(
            rule_id="react-002",
            principle="JSX event handlers should avoid inline callbacks in hot paths",
            category=PrincipleCategory.PERFORMANCE,
            severity=5,
            description="Inline callbacks create new function identities on every render and can trigger avoidable child updates.",
            patterns=[
                "re:on(?:Click|Change|Submit|Input|KeyDown|KeyUp)=\\{\\s*(?:\\([^)]*\\)|[A-Za-z_]\\w*)\\s*=>"
            ],
            recommendation="Extract a named callback or memoized handler outside the JSX attribute.",
        ),
        _principle(
            rule_id="react-003",
            principle="Component logic should not manipulate the DOM directly",
            category=PrincipleCategory.ARCHITECTURE,
            severity=7,
            description="React should remain the source of truth for UI updates instead of ad-hoc DOM queries and mutations.",
            patterns=[
                "re:\\bdocument\\.(?:getElementById|querySelector|querySelectorAll)\\("
            ],
            recommendation="Use refs, state, and declarative rendering instead of direct DOM access.",
        ),
        _principle(
            rule_id="react-004",
            principle="Hooks must not be called conditionally",
            category=PrincipleCategory.CORRECTNESS,
            severity=10,
            description="Conditional hook calls break React's call ordering guarantees and lead to runtime bugs.",
            patterns=["re:\\bif\\s*\\([^)]*\\)\\s*\\{[\\s\\S]*?\\buse[A-Z]\\w*\\("],
            recommendation="Move hooks to the top level of the component and branch on derived values instead.",
        ),
        _principle(
            rule_id="react-005",
            principle="Effects that register timers or listeners need an explicit cleanup review",
            category=PrincipleCategory.CORRECTNESS,
            severity=7,
            description="Effects that add listeners or timers are a common source of leaks when cleanup is omitted.",
            patterns=["re:useEffect\\([\\s\\S]*?(?:setInterval|addEventListener)\\("],
            recommendation="Return a cleanup function from useEffect that tears down timers or listeners.",
        ),
    ],
)
