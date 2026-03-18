"""Framework-specific django zen principles used by the generated analyzer surfaces."""

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


DJANGO_ZEN = LanguageZenPrinciples(
    language="django",
    name="Django",
    philosophy="Explicit, batteries-included web architecture with strong defaults for security and maintainability.",
    source_text="Django documentation",
    source_url=HttpUrl("https://docs.djangoproject.com/"),
    principles=[
        _principle(
            rule_id="django-001",
            principle="Raw SQL must not interpolate user-controlled strings directly",
            category=PrincipleCategory.SECURITY,
            severity=10,
            description="String-built SQL in Django bypasses ORM protections and opens injection risk.",
            patterns=[
                "re:cursor\\.execute\\(\\s*(?:f[\\\"\\']|[rbuf]*[\\\"\\'][\\s\\S]*?[\\\"\\']\\s*(?:%|\\.format\\())"
            ],
            recommendation="Use parameterized queries or ORM expressions instead of interpolated SQL.",
        ),
        _principle(
            rule_id="django-002",
            principle="Settings files should not hardcode secrets",
            category=PrincipleCategory.SECURITY,
            severity=10,
            description="Hardcoded secrets in settings are difficult to rotate and often leak into logs, repos, or test fixtures.",
            patterns=["re:^\\s*(?:SECRET_KEY|DATABASE_URL)\\s*=\\s*[\\\"\\']"],
            recommendation="Load secrets from environment variables or a dedicated secret store.",
        ),
        _principle(
            rule_id="django-003",
            principle="Production-facing settings should not leave DEBUG enabled",
            category=PrincipleCategory.SECURITY,
            severity=9,
            description="DEBUG=True exposes verbose internals and unsafe error surfaces outside local development.",
            patterns=["re:^\\s*DEBUG\\s*=\\s*True\\b"],
            recommendation="Set DEBUG from the environment and keep production defaults false.",
        ),
        _principle(
            rule_id="django-004",
            principle="Redirects and URL construction should avoid hardcoded internal paths",
            category=PrincipleCategory.ORGANIZATION,
            severity=7,
            description="Hardcoded paths drift when route definitions change and bypass Django's URL reversing tools.",
            patterns=["re:\\b(?:redirect|HttpResponseRedirect)\\(\\s*[\\\"\\']\\/"],
            recommendation="Use reverse() or reverse_lazy() instead of embedding internal paths.",
        ),
        _principle(
            rule_id="django-005",
            principle="Signal hookups should be reviewed carefully",
            category=PrincipleCategory.ARCHITECTURE,
            severity=6,
            description="Django signals create hidden coupling and should remain a deliberate design choice.",
            patterns=[
                "re:\\b(?:post_save|pre_save|post_delete|m2m_changed)\\.connect\\("
            ],
            recommendation="Keep signal usage explicit and consider service-layer orchestration when behavior becomes complex.",
        ),
        _principle(
            rule_id="django-006",
            principle="Looping over querysets without related loading hints should be reviewed",
            category=PrincipleCategory.PERFORMANCE,
            severity=8,
            description="Related-field access in queryset loops often leads to N+1 queries when select_related/prefetch_related are missing.",
            patterns=["re:for\\s+\\w+\\s+in\\s+\\w+\\.objects\\.(?:all|filter)\\("],
            recommendation="Consider select_related() or prefetch_related() before iterating related ORM objects.",
        ),
    ],
)
