"""GitLab CI zen principles as Pydantic models."""

from pydantic import HttpUrl

from mcp_zen_of_languages.rules.base_models import (
    LanguageZenPrinciples,
    PrincipleCategory,
    ZenPrinciple,
)

GITLAB_CI_ZEN = LanguageZenPrinciples(
    language="gitlab_ci",
    name="GitLab CI",
    philosophy="Secure, maintainable, and idiomatic GitLab CI pipelines",
    source_text="GitLab CI/CD documentation",
    source_url=HttpUrl("https://docs.gitlab.com/ee/ci/"),
    principles=[
        ZenPrinciple(
            id="gitlab-ci-001",
            principle="Pin container image tags",
            category=PrincipleCategory.SECURITY,
            severity=8,
            description="Avoid floating image tags such as 'python' or ':latest'.",
            violations=["Unpinned image tags"],
        ),
        ZenPrinciple(
            id="gitlab-ci-002",
            principle="Avoid exposed variables in repository YAML",
            category=PrincipleCategory.SECURITY,
            severity=8,
            description="Top-level variables should not contain secret-like values.",
            violations=["Exposed variables in top-level variables block"],
        ),
        ZenPrinciple(
            id="gitlab-ci-003",
            principle="Use allow_failure only with rules-based context",
            category=PrincipleCategory.SECURITY,
            severity=6,
            description="allow_failure should be justified by explicit rules.",
            violations=["allow_failure: true without rules"],
        ),
        ZenPrinciple(
            id="gitlab-ci-004",
            principle="Avoid god pipelines",
            category=PrincipleCategory.STRUCTURE,
            severity=6,
            description="Large root pipelines should be split using include.",
            violations=["Large .gitlab-ci.yml without include"],
        ),
        ZenPrinciple(
            id="gitlab-ci-005",
            principle="Reduce duplicated before_script blocks",
            category=PrincipleCategory.CONSISTENCY,
            severity=5,
            description="Repeated before_script commands should be extracted.",
            violations=["Duplicated before_script command lists"],
        ),
        ZenPrinciple(
            id="gitlab-ci-006",
            principle="Use interruptible pipelines",
            category=PrincipleCategory.PERFORMANCE,
            severity=5,
            description="Jobs should be interruptible to cancel stale MR pipelines.",
            violations=["Missing interruptible: true"],
        ),
        ZenPrinciple(
            id="gitlab-ci-007",
            principle="Model job DAG dependencies with needs",
            category=PrincipleCategory.PERFORMANCE,
            severity=5,
            description="Parallel jobs should usually declare needs for faster execution.",
            violations=["Parallelizable jobs missing needs"],
        ),
        ZenPrinciple(
            id="gitlab-ci-008",
            principle="Prefer rules over only/except",
            category=PrincipleCategory.IDIOMS,
            severity=6,
            description="only/except is legacy syntax compared with rules.",
            violations=["Legacy only/except syntax"],
        ),
        ZenPrinciple(
            id="gitlab-ci-009",
            principle="Cache dependency installs",
            category=PrincipleCategory.PERFORMANCE,
            severity=5,
            description="Dependency-installing jobs should define cache keys.",
            violations=["Dependency installation without cache"],
        ),
        ZenPrinciple(
            id="gitlab-ci-010",
            principle="Expire artifacts",
            category=PrincipleCategory.CONFIGURATION,
            severity=5,
            description="Artifacts should define expire_in to control storage growth.",
            violations=["Artifacts block missing expire_in"],
        ),
    ],
)
