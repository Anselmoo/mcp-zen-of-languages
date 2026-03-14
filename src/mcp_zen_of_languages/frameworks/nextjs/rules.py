"""Next.js zen principles."""

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


NEXTJS_ZEN = LanguageZenPrinciples(
    language="nextjs",
    name="Next.js",
    philosophy="Server-first React with framework-level performance, routing, and deployment conventions.",
    source_text="Next.js documentation",
    source_url=HttpUrl("https://nextjs.org/docs"),
    principles=[
        _principle(
            rule_id="nextjs-001",
            principle="Internal navigation should use next/link instead of raw anchors",
            category=PrincipleCategory.IDIOMS,
            severity=6,
            description="next/link preserves client-side navigation behavior and framework optimizations.",
            patterns=["re:<a\\s+href=[\\\"\\']\\/"],
            recommendation="Replace raw internal anchors with the Link component from next/link.",
        ),
        _principle(
            rule_id="nextjs-002",
            principle="Images should use next/image when optimization matters",
            category=PrincipleCategory.PERFORMANCE,
            severity=7,
            description="next/image enables responsive delivery, lazy loading, and optimization defaults.",
            patterns=["re:<img\\s+"],
            recommendation="Use the Image component from next/image for managed images.",
        ),
        _principle(
            rule_id="nextjs-003",
            principle="App Router files should not rely on getServerSideProps",
            category=PrincipleCategory.CORRECTNESS,
            severity=8,
            description="getServerSideProps belongs to the Pages Router and is not the idiomatic App Router data-loading model.",
            patterns=["re:\\bgetServerSideProps\\b"],
            recommendation="Move data loading into Server Components, route handlers, or fetch in the App Router model.",
        ),
        _principle(
            rule_id="nextjs-004",
            principle="Route handlers should not serialize raw error objects",
            category=PrincipleCategory.SECURITY,
            severity=9,
            description="Returning raw error objects can leak implementation details to clients.",
            patterns=["re:return\\s+(?:NextResponse|Response)\\.json\\(\\s*error\\b"],
            recommendation="Return a sanitized error payload and log internal details separately.",
        ),
        _principle(
            rule_id="nextjs-005",
            principle="Client-side fetching inside effects should be reviewed against server-first defaults",
            category=PrincipleCategory.PERFORMANCE,
            severity=6,
            description="Fetching inside useEffect often ships extra client JavaScript when Server Components could do the work earlier.",
            patterns=["re:useEffect\\([\\s\\S]*?\\bfetch\\("],
            recommendation="Prefer server-side data fetching and keep client effects for truly client-only work.",
        ),
    ],
)
