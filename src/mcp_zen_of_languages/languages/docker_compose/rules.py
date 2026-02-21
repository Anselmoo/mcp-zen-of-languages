"""Docker Compose zen principles as Pydantic models."""

from pydantic import HttpUrl

from mcp_zen_of_languages.rules.base_models import (
    LanguageZenPrinciples,
    PrincipleCategory,
    ZenPrinciple,
)

DOCKER_COMPOSE_ZEN = LanguageZenPrinciples(
    language="docker_compose",
    name="Docker Compose",
    philosophy="Docker Compose service configuration hardening best practices",
    source_text="Compose Specification",
    source_url=HttpUrl("https://compose-spec.io/"),
    principles=[
        ZenPrinciple(
            id="docker-compose-001",
            principle="Avoid latest tags in image definitions",
            category=PrincipleCategory.SECURITY,
            severity=8,
            description="Pin service image versions to avoid unplanned upgrades.",
            violations=["image uses latest tag"],
            detectable_patterns=[":latest"],
            recommended_alternative="Use explicit image tags for every service.",
        ),
        ZenPrinciple(
            id="docker-compose-002",
            principle="Run services as non-root user",
            category=PrincipleCategory.SECURITY,
            severity=9,
            description="Service user should not be root unless explicitly justified.",
            violations=["user is root or uid 0"],
            detectable_patterns=["user: root"],
        ),
        ZenPrinciple(
            id="docker-compose-003",
            principle="Declare service healthchecks",
            category=PrincipleCategory.ROBUSTNESS,
            severity=7,
            description="Services should define healthcheck probes for reliability.",
            violations=["missing healthcheck key"],
            detectable_patterns=["!healthcheck:"],
        ),
        ZenPrinciple(
            id="docker-compose-004",
            principle="Keep secrets out of environment literals",
            category=PrincipleCategory.SECURITY,
            severity=9,
            description="Secret-like keys should not be embedded directly in environment values.",
            violations=["secret-like key in environment block"],
        ),
    ],
)
