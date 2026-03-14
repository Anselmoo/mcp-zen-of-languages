"""FastAPI zen principles."""

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


FASTAPI_ZEN = LanguageZenPrinciples(
    language="fastapi",
    name="FastAPI",
    philosophy="Type-driven API design with async-first I/O and explicit request/response contracts.",
    source_text="FastAPI documentation",
    source_url=HttpUrl("https://fastapi.tiangolo.com/"),
    principles=[
        _principle(
            rule_id="fastapi-001",
            principle="Route decorators should declare response_model explicitly",
            category=PrincipleCategory.CLARITY,
            severity=7,
            description="Explicit response models keep the OpenAPI contract and response serialization predictable.",
            patterns=[
                "re:@(?:app|router)\\.(?:get|post|put|delete|patch)\\((?:(?!response_model=)[^)\\n])+\\)"
            ],
            recommendation="Add response_model=... to the route decorator.",
        ),
        _principle(
            rule_id="fastapi-002",
            principle="POST routes should declare an explicit status_code",
            category=PrincipleCategory.CLARITY,
            severity=5,
            description="POST handlers commonly create resources and should communicate that with an explicit HTTP status.",
            patterns=["re:@(?:app|router)\\.post\\((?:(?!status_code=)[^)\\n])+\\)"],
            recommendation="Add status_code=201 or another explicit status that matches the route semantics.",
        ),
        _principle(
            rule_id="fastapi-003",
            principle="Route handlers should not raise bare Exception",
            category=PrincipleCategory.CORRECTNESS,
            severity=7,
            description="Bare exceptions bypass FastAPI's explicit HTTP contract and usually leak implementation details.",
            patterns=["re:raise\\s+Exception\\("],
            recommendation="Raise HTTPException with a status code and detail payload.",
        ),
        _principle(
            rule_id="fastapi-004",
            principle="Background work should use BackgroundTasks instead of raw threads",
            category=PrincipleCategory.CORRECTNESS,
            severity=7,
            description="FastAPI provides BackgroundTasks for request-scoped background work without manual thread management.",
            patterns=["re:\\bthreading\\.Thread\\("],
            recommendation="Use BackgroundTasks or a proper task queue instead of spawning threads in handlers.",
        ),
        _principle(
            rule_id="fastapi-005",
            principle="Async routes should avoid blocking I/O helpers",
            category=PrincipleCategory.PERFORMANCE,
            severity=9,
            description="Blocking calls inside async handlers reduce concurrency and can stall the event loop.",
            patterns=[
                "re:async\\s+def[\\s\\S]*?\\b(?:requests\\.\\w+|time\\.sleep\\(|subprocess\\.run\\()"
            ],
            recommendation="Use async-aware clients and non-blocking primitives inside async route functions.",
        ),
        _principle(
            rule_id="fastapi-006",
            principle="Prefer explicit HTTP verb decorators over app.route",
            category=PrincipleCategory.IDIOMS,
            severity=6,
            description="Method-specific decorators make API intent clearer than the generic app.route entry point.",
            patterns=["re:@(?:app|router)\\.route\\("],
            recommendation="Use @app.get, @app.post, and related verb-specific decorators.",
        ),
    ],
)
