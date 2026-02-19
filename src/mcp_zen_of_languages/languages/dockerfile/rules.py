"""Dockerfile zen principles as Pydantic models."""

from pydantic import HttpUrl

from mcp_zen_of_languages.rules.base_models import (
    LanguageZenPrinciples,
    PrincipleCategory,
    ZenPrinciple,
)

DOCKERFILE_ZEN = LanguageZenPrinciples(
    language="dockerfile",
    name="Dockerfile",
    philosophy="Docker build and runtime hardening best practices",
    source_text="Dockerfile Best Practices",
    source_url=HttpUrl(
        "https://docs.docker.com/develop/develop-images/dockerfile_best-practices/",
    ),
    principles=[
        ZenPrinciple(
            id="dockerfile-001",
            principle="Avoid latest tags in base images",
            category=PrincipleCategory.SECURITY,
            severity=8,
            description="Pin base image versions to avoid unplanned upgrades.",
            violations=["FROM image:latest"],
            detectable_patterns=[":latest"],
            recommended_alternative="Use explicit version tags like `ubuntu:22.04`.",
        ),
        ZenPrinciple(
            id="dockerfile-002",
            principle="Run containers as non-root user",
            category=PrincipleCategory.SECURITY,
            severity=9,
            description="Final image should set a non-root USER directive.",
            violations=["Missing USER directive", "Final USER is root"],
            detectable_patterns=["USER root"],
            recommended_alternative="Create and switch to an unprivileged runtime user.",
        ),
        ZenPrinciple(
            id="dockerfile-003",
            principle="Prefer COPY over ADD unless extra features are needed",
            category=PrincipleCategory.CORRECTNESS,
            severity=6,
            description="ADD has surprising behavior for archives and remote URLs.",
            violations=["Using ADD for plain local copy"],
            detectable_patterns=["ADD "],
            recommended_alternative="Use COPY for local files and reserve ADD for tar/URL use cases.",
        ),
        ZenPrinciple(
            id="dockerfile-004",
            principle="Declare HEALTHCHECK for production images",
            category=PrincipleCategory.ROBUSTNESS,
            severity=7,
            description="Health checks improve orchestration reliability and recovery.",
            violations=["Missing HEALTHCHECK instruction"],
            detectable_patterns=["!HEALTHCHECK"],
        ),
        ZenPrinciple(
            id="dockerfile-005",
            principle="Use multi-stage builds for compiled workloads",
            category=PrincipleCategory.PERFORMANCE,
            severity=6,
            description="Compiled builds should separate build and runtime stages.",
            violations=["Single-stage Dockerfile for compiled build commands"],
        ),
        ZenPrinciple(
            id="dockerfile-006",
            principle="Keep secrets out of ENV and ARG instructions",
            category=PrincipleCategory.SECURITY,
            severity=9,
            description="Credentials in Dockerfile instructions leak into image metadata/layers.",
            violations=["ENV with secret-like key", "ARG with credential-like key"],
        ),
        ZenPrinciple(
            id="dockerfile-007",
            principle="Maintain layer discipline",
            category=PrincipleCategory.PERFORMANCE,
            severity=5,
            description="Excessive RUN layers increase image size and cache fragmentation.",
            violations=["Too many RUN instructions"],
            metrics={"max_run_instructions": 5},
        ),
        ZenPrinciple(
            id="dockerfile-008",
            principle="Keep .dockerignore coherent with broad context copies",
            category=PrincipleCategory.CONFIGURATION,
            severity=4,
            description="Broad context copies should be paired with .dockerignore hygiene.",
            violations=["COPY/ADD from build context without .dockerignore"],
            detectable_patterns=["COPY .", "ADD ."],
        ),
    ],
)
