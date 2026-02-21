"""Detectors for Dockerfile container build hygiene."""
# ruff: noqa: D102

from __future__ import annotations

import re
from pathlib import Path

from mcp_zen_of_languages.analyzers.base import (
    AnalysisContext,
    LocationHelperMixin,
    ViolationDetector,
)
from mcp_zen_of_languages.languages.configs import (
    DockerfileAddInstructionConfig,
    DockerfileDockerignoreConfig,
    DockerfileHealthcheckConfig,
    DockerfileLatestTagConfig,
    DockerfileLayerDisciplineConfig,
    DockerfileMultiStageConfig,
    DockerfileNonRootUserConfig,
    DockerfileSecretHygieneConfig,
)
from mcp_zen_of_languages.models import Location, Violation

_FROM_RE = re.compile(r"^\s*FROM\s+([^\s]+)", re.IGNORECASE)
_USER_RE = re.compile(r"^\s*USER\s+([^\s#]+)", re.IGNORECASE)
_ADD_RE = re.compile(r"^\s*ADD\s+", re.IGNORECASE)
_HEALTHCHECK_RE = re.compile(r"^\s*HEALTHCHECK\b", re.IGNORECASE)
_RUN_RE = re.compile(r"^\s*RUN\b", re.IGNORECASE)
_COMPILED_HINT_RE = re.compile(
    r"\b(go\s+build|cargo\s+build|dotnet\s+publish|mvn\s+package|gradle\s+build|make)\b",
    re.IGNORECASE,
)
_SECRET_KEY_RE = re.compile(
    r"\b(secret|token|password|passwd|pwd|api[_-]?key|credential)\b",
    re.IGNORECASE,
)
_ENV_ARG_RE = re.compile(r"^\s*(ENV|ARG)\s+(.+)$", re.IGNORECASE)
_CONTEXT_COPY_RE = re.compile(r"^\s*(COPY|ADD)\s+\.\s", re.IGNORECASE)
_MIN_MULTISTAGE_FROM_COUNT = 2


class DockerfileLatestTagDetector(
    ViolationDetector[DockerfileLatestTagConfig],
    LocationHelperMixin,
):
    """Flags ``FROM`` instructions that pin to the mutable ``latest`` tag."""

    @property
    def name(self) -> str:
        return "dockerfile-001"

    def detect(
        self,
        context: AnalysisContext,
        config: DockerfileLatestTagConfig,
    ) -> list[Violation]:
        violations: list[Violation] = []
        for idx, line in enumerate(context.code.splitlines(), start=1):
            if (match := _FROM_RE.match(line)) and ":latest" in match[1].lower():
                violations.append(
                    self.build_violation(
                        config,
                        contains="latest",
                        location=Location(line=idx, column=1),
                        suggestion="Pin the base image to a specific version tag.",
                    ),
                )
        return violations


class DockerfileNonRootUserDetector(
    ViolationDetector[DockerfileNonRootUserConfig],
    LocationHelperMixin,
):
    """Ensures the final Docker runtime user is not root."""

    @property
    def name(self) -> str:
        return "dockerfile-002"

    def detect(
        self,
        context: AnalysisContext,
        config: DockerfileNonRootUserConfig,
    ) -> list[Violation]:
        users: list[tuple[int, str]] = [
            (idx, match[1].strip())
            for idx, line in enumerate(context.code.splitlines(), start=1)
            if (match := _USER_RE.match(line))
        ]
        if not users:
            return [
                self.build_violation(
                    config,
                    contains="Missing USER directive",
                    location=Location(line=1, column=1),
                    suggestion="Set a non-root USER in the final runtime stage.",
                ),
            ]
        final_line, final_user = users[-1]
        if final_user.lower() in {"root", "0"}:
            return [
                self.build_violation(
                    config,
                    contains="Final USER is root",
                    location=Location(line=final_line, column=1),
                    suggestion="Switch to a non-root runtime user.",
                ),
            ]
        return []


class DockerfileAddInstructionDetector(
    ViolationDetector[DockerfileAddInstructionConfig],
    LocationHelperMixin,
):
    """Discourages broad ``ADD`` usage when ``COPY`` is sufficient."""

    @property
    def name(self) -> str:
        return "dockerfile-003"

    def detect(
        self,
        context: AnalysisContext,
        config: DockerfileAddInstructionConfig,
    ) -> list[Violation]:
        return [
            self.build_violation(
                config,
                contains="ADD",
                location=Location(line=idx, column=1),
                suggestion="Prefer COPY unless ADD-specific features are required.",
            )
            for idx, line in enumerate(context.code.splitlines(), start=1)
            if _ADD_RE.match(line)
        ]


class DockerfileHealthcheckDetector(
    ViolationDetector[DockerfileHealthcheckConfig],
    LocationHelperMixin,
):
    """Reports Dockerfiles that do not declare a ``HEALTHCHECK`` instruction."""

    @property
    def name(self) -> str:
        return "dockerfile-004"

    def detect(
        self,
        context: AnalysisContext,
        config: DockerfileHealthcheckConfig,
    ) -> list[Violation]:
        if any(_HEALTHCHECK_RE.match(line) for line in context.code.splitlines()):
            return []
        return [
            self.build_violation(
                config,
                contains="Missing HEALTHCHECK instruction",
                location=Location(line=1, column=1),
                suggestion="Declare a HEALTHCHECK command for container liveness/readiness.",
            ),
        ]


class DockerfileMultiStageDetector(
    ViolationDetector[DockerfileMultiStageConfig],
    LocationHelperMixin,
):
    """Advises multi-stage builds when compiled build commands are detected."""

    @property
    def name(self) -> str:
        return "dockerfile-005"

    def detect(
        self,
        context: AnalysisContext,
        config: DockerfileMultiStageConfig,
    ) -> list[Violation]:
        lines = context.code.splitlines()
        from_count = sum(1 for line in lines if _FROM_RE.match(line))
        has_compiled_hint = any(_COMPILED_HINT_RE.search(line) for line in lines)
        if has_compiled_hint and from_count < _MIN_MULTISTAGE_FROM_COUNT:
            return [
                self.build_violation(
                    config,
                    contains="Single-stage Dockerfile for compiled build commands",
                    location=Location(line=1, column=1),
                    suggestion="Use a builder stage and copy only runtime artifacts to final image.",
                ),
            ]
        return []


class DockerfileSecretHygieneDetector(
    ViolationDetector[DockerfileSecretHygieneConfig],
    LocationHelperMixin,
):
    """Detects secret-like keys embedded in ``ENV`` and ``ARG`` declarations."""

    @property
    def name(self) -> str:
        return "dockerfile-006"

    def detect(
        self,
        context: AnalysisContext,
        config: DockerfileSecretHygieneConfig,
    ) -> list[Violation]:
        violations: list[Violation] = []
        for idx, line in enumerate(context.code.splitlines(), start=1):
            if not (match := _ENV_ARG_RE.match(line)):
                continue
            if _SECRET_KEY_RE.search(match[2]):
                violations.append(
                    self.build_violation(
                        config,
                        location=Location(line=idx, column=1),
                        suggestion="Use runtime secrets mounts or orchestrator secret managers.",
                    ),
                )
        return violations


class DockerfileLayerDisciplineDetector(
    ViolationDetector[DockerfileLayerDisciplineConfig],
    LocationHelperMixin,
):
    """Limits excessive ``RUN`` layer count in Dockerfiles."""

    @property
    def name(self) -> str:
        return "dockerfile-007"

    def detect(
        self,
        context: AnalysisContext,
        config: DockerfileLayerDisciplineConfig,
    ) -> list[Violation]:
        run_count = sum(1 for line in context.code.splitlines() if _RUN_RE.match(line))
        if run_count > config.max_run_instructions:
            return [
                self.build_violation(
                    config,
                    contains="Too many RUN instructions",
                    location=Location(line=1, column=1),
                    suggestion="Consolidate related RUN commands to reduce image layers.",
                ),
            ]
        return []


class DockerfileDockerignoreDetector(
    ViolationDetector[DockerfileDockerignoreConfig],
    LocationHelperMixin,
):
    """Warns when broad context copies are used without a ``.dockerignore`` file."""

    @property
    def name(self) -> str:
        return "dockerfile-008"

    def detect(
        self,
        context: AnalysisContext,
        config: DockerfileDockerignoreConfig,
    ) -> list[Violation]:
        lines = context.code.splitlines()
        if not any(_CONTEXT_COPY_RE.match(line) for line in lines):
            return []
        if context.other_files is None:
            return []
        has_dockerignore = any(
            Path(path).name == ".dockerignore" for path in context.other_files
        )
        if has_dockerignore:
            return []
        return [
            self.build_violation(
                config,
                contains="COPY/ADD from build context without .dockerignore",
                location=Location(line=1, column=1),
                suggestion="Add a .dockerignore file to exclude secrets and large artifacts.",
            ),
        ]


__all__ = [
    "DockerfileAddInstructionDetector",
    "DockerfileDockerignoreDetector",
    "DockerfileHealthcheckDetector",
    "DockerfileLatestTagDetector",
    "DockerfileLayerDisciplineDetector",
    "DockerfileMultiStageDetector",
    "DockerfileNonRootUserDetector",
    "DockerfileSecretHygieneDetector",
]
