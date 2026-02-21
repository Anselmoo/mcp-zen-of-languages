"""Detectors for GitLab CI pipeline zen principles."""

from __future__ import annotations

# ruff: noqa: D102
import re

from mcp_zen_of_languages.analyzers.base import (
    AnalysisContext,
    LocationHelperMixin,
    ViolationDetector,
)
from mcp_zen_of_languages.languages.configs import DetectorConfig
from mcp_zen_of_languages.models import Location, Violation
from mcp_zen_of_languages.utils.ci_yaml import (
    KEY_LINE_RE,
    TopLevelBlock,
    find_key_line,
    has_key,
    split_top_level_blocks,
)

GLOBAL_KEYS = {
    "stages",
    "variables",
    "include",
    "default",
    "workflow",
    "image",
    "services",
    "before_script",
    "after_script",
    "cache",
}
SECRET_NAME_RE = re.compile(
    r"(token|secret|password|passwd|api[_-]?key)", re.IGNORECASE
)
DEPENDENCY_INSTALL_RE = re.compile(
    r"(pip install|npm ci|npm install|yarn install|pnpm install|bundle install|go mod download|cargo build)",
    re.IGNORECASE,
)
LINE_THRESHOLD = 200


def _job_blocks(code: str) -> list[TopLevelBlock]:
    return [
        block
        for block in split_top_level_blocks(code)
        if block.name not in GLOBAL_KEYS and not block.name.startswith(".")
    ]


def _block_has_rules(block: TopLevelBlock) -> bool:
    return has_key(block, "rules")


def _before_script_commands(block: TopLevelBlock) -> tuple[str, ...]:
    commands: list[str] = []
    inside = False
    for line in block.lines:
        if re.match(r"^\s*before_script:\s*$", line):
            inside = True
            continue
        if inside:
            if re.match(r"^\s*[A-Za-z0-9_.-]+\s*:", line):
                break
            if re.match(r"^\s*-\s+", line):
                commands.append(re.sub(r"^\s*-\s+", "", line).strip())
                continue
            if line.strip() and not line.startswith((" ", "\t")):
                break
    return tuple(commands)


def _has_routing_keys(block: TopLevelBlock) -> bool:
    return has_key(block, "rules") or has_key(block, "only") or has_key(block, "except")


def _targets_merge_requests(block: TopLevelBlock) -> bool:
    return any(
        "merge_request" in line and not line.lstrip().startswith("#")
        for line in block.lines
    )


class UnpinnedImageTagDetector(ViolationDetector[DetectorConfig], LocationHelperMixin):
    """Detect images without pinned tags or with latest tag."""

    @property
    def name(self) -> str:
        return "gitlab-ci-001"

    def detect(
        self,
        context: AnalysisContext,
        config: DetectorConfig,
    ) -> list[Violation]:
        violations: list[Violation] = []
        for idx, line in enumerate(context.code.splitlines(), start=1):
            match = re.match(r"^\s*image:\s*([^\s#]+)", line)
            if not match:
                continue
            image = match[1].strip("'\"")
            if image.startswith(("$", "${")):
                continue
            if ":" not in image or image.endswith(":latest"):
                violations.append(
                    self.build_violation(
                        config,
                        contains=image,
                        location=Location(line=idx, column=1),
                        suggestion="Pin the image to a specific version tag.",
                    ),
                )
        return violations


class ExposedVariablesDetector(ViolationDetector[DetectorConfig], LocationHelperMixin):
    """Detect secret-like keys under top-level variables blocks."""

    @property
    def name(self) -> str:
        return "gitlab-ci-002"

    def detect(
        self,
        context: AnalysisContext,
        config: DetectorConfig,
    ) -> list[Violation]:
        violations: list[Violation] = []
        for block in split_top_level_blocks(context.code):
            if block.name != "variables":
                continue
            for offset, line in enumerate(block.lines[1:], start=1):
                match = KEY_LINE_RE.match(line)
                if match and SECRET_NAME_RE.search(match[1]):
                    violations.append(
                        self.build_violation(
                            config,
                            contains=match[1],
                            location=Location(line=block.start_line + offset, column=1),
                            suggestion="Store secrets in masked/protected CI variables.",
                        ),
                    )
        return violations


class AllowFailureWithoutRulesDetector(
    ViolationDetector[DetectorConfig],
    LocationHelperMixin,
):
    """Detect allow_failure enabled without a companion rules section."""

    @property
    def name(self) -> str:
        return "gitlab-ci-003"

    def detect(
        self,
        context: AnalysisContext,
        config: DetectorConfig,
    ) -> list[Violation]:
        violations: list[Violation] = []
        for block in _job_blocks(context.code):
            if _block_has_rules(block):
                continue
            line = find_key_line(block, "allow_failure")
            if line and re.search(
                r"allow_failure:\s*true", context.code.splitlines()[line - 1]
            ):
                violations.append(
                    self.build_violation(
                        config,
                        contains="allow_failure",
                        location=Location(line=line, column=1),
                        suggestion="Use rules-based conditions when allow_failure is enabled.",
                    ),
                )
        return violations


class GodPipelineDetector(ViolationDetector[DetectorConfig], LocationHelperMixin):
    """Detect oversized root pipelines that do not use include."""

    @property
    def name(self) -> str:
        return "gitlab-ci-004"

    def detect(
        self,
        context: AnalysisContext,
        config: DetectorConfig,
    ) -> list[Violation]:
        if len(context.code.splitlines()) <= LINE_THRESHOLD:
            return []
        if any(
            block.name == "include" for block in split_top_level_blocks(context.code)
        ):
            return []
        return [
            self.build_violation(
                config,
                contains="pipeline",
                location=Location(line=1, column=1),
                suggestion="Split large pipelines with include and child configs.",
            ),
        ]


class DuplicatedBeforeScriptDetector(
    ViolationDetector[DetectorConfig],
    LocationHelperMixin,
):
    """Detect repeated before_script command sequences across jobs."""

    @property
    def name(self) -> str:
        return "gitlab-ci-005"

    def detect(
        self,
        context: AnalysisContext,
        config: DetectorConfig,
    ) -> list[Violation]:
        violations: list[Violation] = []
        seen: dict[tuple[str, ...], int] = {}
        for block in _job_blocks(context.code):
            commands = _before_script_commands(block)
            if not commands:
                continue
            if commands in seen:
                violations.append(
                    self.build_violation(
                        config,
                        contains="before_script",
                        location=Location(line=block.start_line, column=1),
                        suggestion="Extract repeated before_script into hidden job + extends.",
                    ),
                )
                continue
            seen[commands] = block.start_line
        return violations


class MissingInterruptibleDetector(
    ViolationDetector[DetectorConfig],
    LocationHelperMixin,
):
    """Detect jobs missing interruptible true for stale pipeline cancellation."""

    @property
    def name(self) -> str:
        return "gitlab-ci-006"

    def detect(
        self,
        context: AnalysisContext,
        config: DetectorConfig,
    ) -> list[Violation]:
        violations: list[Violation] = []
        for block in _job_blocks(context.code):
            if _has_routing_keys(block) and not _targets_merge_requests(block):
                continue
            line = find_key_line(block, "interruptible")
            if line is None or not re.search(
                r"interruptible:\s*true",
                context.code.splitlines()[line - 1],
            ):
                violations.append(
                    self.build_violation(
                        config,
                        contains="interruptible",
                        location=Location(line=block.start_line, column=1),
                        suggestion="Set interruptible: true to cancel stale merge request jobs.",
                    ),
                )
        return violations


class MissingNeedsDetector(ViolationDetector[DetectorConfig], LocationHelperMixin):
    """Detect parallel jobs that omit explicit needs DAG edges."""

    @property
    def name(self) -> str:
        return "gitlab-ci-007"

    def detect(
        self,
        context: AnalysisContext,
        config: DetectorConfig,
    ) -> list[Violation]:
        violations: list[Violation] = []
        for block in _job_blocks(context.code):
            if not has_key(block, "parallel"):
                continue
            if not has_key(block, "needs"):
                violations.append(
                    self.build_violation(
                        config,
                        contains="needs",
                        location=Location(line=block.start_line, column=1),
                        suggestion="Use needs for parallel jobs to build an explicit DAG.",
                    ),
                )
        return violations


class OnlyExceptDetector(ViolationDetector[DetectorConfig], LocationHelperMixin):
    """Detect legacy only and except keys in place of rules."""

    @property
    def name(self) -> str:
        return "gitlab-ci-008"

    def detect(
        self,
        context: AnalysisContext,
        config: DetectorConfig,
    ) -> list[Violation]:
        violations: list[Violation] = []
        for idx, line in enumerate(context.code.splitlines(), start=1):
            stripped = line.lstrip()
            if stripped.startswith("#"):
                continue
            if re.match(r"^\s*(only|except)\s*:", line):
                violations.append(
                    self.build_violation(
                        config,
                        contains="only/except",
                        location=Location(line=idx, column=1),
                        suggestion="Migrate only/except to rules.",
                    ),
                )
        return violations


class MissingCacheKeyDetector(ViolationDetector[DetectorConfig], LocationHelperMixin):
    """Detect dependency install jobs that have no cache section."""

    @property
    def name(self) -> str:
        return "gitlab-ci-009"

    def detect(
        self,
        context: AnalysisContext,
        config: DetectorConfig,
    ) -> list[Violation]:
        violations: list[Violation] = []
        for block in _job_blocks(context.code):
            script_text = "\n".join(block.lines)
            if not DEPENDENCY_INSTALL_RE.search(script_text):
                continue
            if not has_key(block, "cache"):
                violations.append(
                    self.build_violation(
                        config,
                        contains="cache",
                        location=Location(line=block.start_line, column=1),
                        suggestion="Add cache with a stable key for dependency installs.",
                    ),
                )
        return violations


class ArtifactExpiryDetector(ViolationDetector[DetectorConfig], LocationHelperMixin):
    """Detect artifacts blocks that omit expire_in policy."""

    @property
    def name(self) -> str:
        return "gitlab-ci-010"

    def detect(
        self,
        context: AnalysisContext,
        config: DetectorConfig,
    ) -> list[Violation]:
        return [
            self.build_violation(
                config,
                contains="expire_in",
                location=Location(line=block.start_line, column=1),
                suggestion="Set artifacts.expire_in to avoid unbounded storage usage.",
            )
            for block in _job_blocks(context.code)
            if has_key(block, "artifacts") and not has_key(block, "expire_in")
        ]


__all__ = [
    "AllowFailureWithoutRulesDetector",
    "ArtifactExpiryDetector",
    "DuplicatedBeforeScriptDetector",
    "ExposedVariablesDetector",
    "GodPipelineDetector",
    "MissingCacheKeyDetector",
    "MissingInterruptibleDetector",
    "MissingNeedsDetector",
    "OnlyExceptDetector",
    "UnpinnedImageTagDetector",
]
