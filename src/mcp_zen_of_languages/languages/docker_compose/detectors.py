"""Detectors for Docker Compose service-definition hygiene."""
# ruff: noqa: D102

from __future__ import annotations

import re

from mcp_zen_of_languages.analyzers.base import (
    AnalysisContext,
    LocationHelperMixin,
    ViolationDetector,
)
from mcp_zen_of_languages.languages.configs import (
    DockerComposeHealthcheckConfig,
    DockerComposeLatestTagConfig,
    DockerComposeNonRootUserConfig,
    DockerComposeSecretHygieneConfig,
)
from mcp_zen_of_languages.models import Location, Violation

_IMAGE_RE = re.compile(r"^\s*image:\s*([^\s#]+)", re.IGNORECASE)
_USER_RE = re.compile(r"^\s*user:\s*(.+?)\s*$", re.IGNORECASE)
_HEALTHCHECK_RE = re.compile(r"^\s*healthcheck\s*:", re.IGNORECASE)
_ENV_START_RE = re.compile(r"^\s*environment\s*:\s*$", re.IGNORECASE)
_KEY_VALUE_RE = re.compile(r"^\s*([A-Za-z_][A-Za-z0-9_]*)\s*[:=]\s*.+$")
_SECRET_KEY_RE = re.compile(
    r"(secret|token|password|passwd|pwd|api[_-]?key|credential)",
    re.IGNORECASE,
)


class DockerComposeLatestTagDetector(
    ViolationDetector[DockerComposeLatestTagConfig],
    LocationHelperMixin,
):
    """Flags compose ``image:`` entries using a mutable ``latest`` tag."""

    @property
    def name(self) -> str:
        return "docker-compose-001"

    def detect(
        self,
        context: AnalysisContext,
        config: DockerComposeLatestTagConfig,
    ) -> list[Violation]:
        violations: list[Violation] = []
        for idx, line in enumerate(context.code.splitlines(), start=1):
            if not (match := _IMAGE_RE.match(line)):
                continue
            if ":latest" in match[1].lower():
                violations.append(
                    self.build_violation(
                        config,
                        contains="latest",
                        location=Location(line=idx, column=1),
                        suggestion="Pin image tags to explicit versions.",
                    ),
                )
        return violations


class DockerComposeNonRootUserDetector(
    ViolationDetector[DockerComposeNonRootUserConfig],
    LocationHelperMixin,
):
    """Flags compose services configured to run as root."""

    @property
    def name(self) -> str:
        return "docker-compose-002"

    def detect(
        self,
        context: AnalysisContext,
        config: DockerComposeNonRootUserConfig,
    ) -> list[Violation]:
        violations: list[Violation] = []
        for idx, line in enumerate(context.code.splitlines(), start=1):
            if not (match := _USER_RE.match(line)):
                continue
            user_value = match[1].strip().strip("\"'")
            if user_value.lower() in {"root", "0", "0:0", "root:root"}:
                violations.append(
                    self.build_violation(
                        config,
                        contains="root",
                        location=Location(line=idx, column=1),
                        suggestion="Set a non-root user for the service.",
                    ),
                )
        return violations


class DockerComposeHealthcheckDetector(
    ViolationDetector[DockerComposeHealthcheckConfig],
    LocationHelperMixin,
):
    """Flags compose files without any ``healthcheck`` definitions."""

    @property
    def name(self) -> str:
        return "docker-compose-003"

    def detect(
        self,
        context: AnalysisContext,
        config: DockerComposeHealthcheckConfig,
    ) -> list[Violation]:
        if any(_HEALTHCHECK_RE.match(line) for line in context.code.splitlines()):
            return []
        return [
            self.build_violation(
                config,
                contains="missing healthcheck",
                location=Location(line=1, column=1),
                suggestion="Add healthcheck sections for production services.",
            ),
        ]


class DockerComposeSecretHygieneDetector(
    ViolationDetector[DockerComposeSecretHygieneConfig],
    LocationHelperMixin,
):
    """Detects secret-like keys in compose environment blocks."""

    @property
    def name(self) -> str:
        return "docker-compose-004"

    def detect(
        self,
        context: AnalysisContext,
        config: DockerComposeSecretHygieneConfig,
    ) -> list[Violation]:
        violations: list[Violation] = []
        in_environment = False
        env_indent = 0
        for idx, line in enumerate(context.code.splitlines(), start=1):
            indent = len(line) - len(line.lstrip(" "))
            if _ENV_START_RE.match(line):
                in_environment = True
                env_indent = indent
                continue
            if in_environment and line.strip() and indent <= env_indent:
                in_environment = False
            if not in_environment:
                continue
            if not (match := _KEY_VALUE_RE.match(line)):
                continue
            if _SECRET_KEY_RE.search(match[1]):
                violations.append(
                    self.build_violation(
                        config,
                        contains="secret",
                        location=Location(line=idx, column=1),
                        suggestion="Move secrets to Docker/Orchestrator secrets management.",
                    ),
                )
        return violations


__all__ = [
    "DockerComposeHealthcheckDetector",
    "DockerComposeLatestTagDetector",
    "DockerComposeNonRootUserDetector",
    "DockerComposeSecretHygieneDetector",
]
