"""Framework-specific angular zen principles used by the generated analyzer surfaces."""

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


ANGULAR_ZEN = LanguageZenPrinciples(
    language="angular",
    name="Angular",
    philosophy="Scalable frontend architecture with strong conventions around DI, templates, and change detection.",
    source_text="Angular Style Guide",
    source_url=HttpUrl("https://angular.dev/style-guide"),
    principles=[
        _principle(
            rule_id="angular-001",
            principle="Components should opt into OnPush change detection",
            category=PrincipleCategory.PERFORMANCE,
            severity=7,
            description="OnPush keeps Angular component trees predictable and reduces unnecessary change detection work.",
            patterns=[
                "re:@Component\\(\\{(?:(?!ChangeDetectionStrategy\\.OnPush)[\\s\\S])*?\\}\\)"
            ],
            recommendation="Add changeDetection: ChangeDetectionStrategy.OnPush to the component decorator.",
        ),
        _principle(
            rule_id="angular-002",
            principle="Type annotations should avoid any",
            category=PrincipleCategory.CORRECTNESS,
            severity=8,
            description="Using any bypasses Angular's TypeScript guarantees and hides template/data contract issues.",
            patterns=["re::\\s*any\\b"],
            recommendation="Replace any with a domain interface, union, or unknown plus narrowing.",
        ),
        _principle(
            rule_id="angular-003",
            principle="Manual subscriptions need an explicit lifecycle strategy",
            category=PrincipleCategory.CORRECTNESS,
            severity=9,
            description="Bare subscribe() calls often leak when they are not paired with takeUntil, async pipe, or cleanup logic.",
            patterns=["re:\\.subscribe\\("],
            recommendation="Use the async pipe, takeUntilDestroyed(), or an explicit teardown path.",
        ),
        _principle(
            rule_id="angular-004",
            principle="Component selectors should follow project naming conventions",
            category=PrincipleCategory.READABILITY,
            severity=5,
            description="Selector prefixes help keep large Angular workspaces consistent and collision-free.",
            patterns=["re:selector\\s*:\\s*[\\\"\\'](?!app-|lib-)[^\\\"\\']+[\\\"\\']"],
            recommendation="Prefix selectors with an application or library namespace such as app- or lib-.",
        ),
        _principle(
            rule_id="angular-005",
            principle="Feature routes should prefer lazy loading over eager component wiring",
            category=PrincipleCategory.PERFORMANCE,
            severity=6,
            description="Lazy-loaded route boundaries help keep initial bundles small and feature areas isolated.",
            patterns=[
                "re:path\\s*:\\s*[\\\"\\'][^\\\"\\']+[\\\"\\']\\s*,\\s*component\\s*:"
            ],
            recommendation="Use loadChildren or loadComponent for feature routes when appropriate.",
        ),
    ],
)
