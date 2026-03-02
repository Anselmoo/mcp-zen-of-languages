"""Detectors for Terraform infrastructure-as-code maintainability and security."""
# ruff: noqa: D102

from __future__ import annotations

import re

from mcp_zen_of_languages.analyzers.base import AnalysisContext
from mcp_zen_of_languages.analyzers.base import LocationHelperMixin
from mcp_zen_of_languages.analyzers.base import ViolationDetector
from mcp_zen_of_languages.languages.configs import TerraformBackendConfig
from mcp_zen_of_languages.languages.configs import TerraformHardcodedIdConfig
from mcp_zen_of_languages.languages.configs import TerraformModuleVersionPinningConfig
from mcp_zen_of_languages.languages.configs import TerraformNamingConventionConfig
from mcp_zen_of_languages.languages.configs import TerraformNoHardcodedSecretsConfig
from mcp_zen_of_languages.languages.configs import TerraformProviderVersionPinningConfig
from mcp_zen_of_languages.languages.configs import (
    TerraformVariableOutputDescriptionConfig,
)
from mcp_zen_of_languages.models import Location
from mcp_zen_of_languages.models import Violation


_PROVIDER_START_RE = re.compile(r'^\s*provider\s+"([^"]+)"\s*\{')
_MODULE_START_RE = re.compile(r'^\s*module\s+"([^"]+)"\s*\{')
_VARIABLE_START_RE = re.compile(r'^\s*variable\s+"([^"]+)"\s*\{')
_VARIABLE_OR_OUTPUT_START_RE = re.compile(r'^\s*(?:variable|output)\s+"([^"]+)"\s*\{')
_RESOURCE_START_RE = re.compile(r'^\s*resource\s+"([^"]+)"\s+"([^"]+)"\s*\{')
_TERRAFORM_BLOCK_RE = re.compile(r"^\s*terraform\s*\{")
_BACKEND_RE = re.compile(r'^\s*backend\s+"[^"]+"\s*\{')
_REQUIRED_PROVIDERS_RE = re.compile(r"^\s*required_providers\s*\{")
_PROVIDER_ENTRY_RE = re.compile(r"^\s*([A-Za-z0-9_-]+)\s*=\s*\{")
_DESCRIPTION_RE = re.compile(r"^\s*description\s*=")
_VERSION_RE = re.compile(r"^\s*version\s*=")
_SOURCE_RE = re.compile(r'^\s*source\s*=\s*"([^"]+)"')
_ASSIGNMENT_RE = re.compile(r'^\s*([A-Za-z_][A-Za-z0-9_]*)\s*=\s*"([^"]+)"')
_SECRET_KEY_RE = re.compile(
    r"(secret|token|password|passwd|pwd|api[_-]?key|credential)",
    re.IGNORECASE,
)
_HARD_ID_VALUE_RE = re.compile(
    r"(arn:[A-Za-z0-9:_/\-]+|vpc-[a-z0-9]+|subnet-[a-z0-9]+|sg-[a-z0-9]+|i-[a-z0-9]+)",
    re.IGNORECASE,
)
_SNAKE_CASE_RE = re.compile(r"^[a-z][a-z0-9_]*$")


def _iter_block_lines(
    code: str,
    start_re: re.Pattern[str],
) -> list[tuple[int, str, list[str]]]:
    blocks: list[tuple[int, str, list[str]]] = []
    lines = code.splitlines()
    idx = 0
    while idx < len(lines):
        line = lines[idx]
        if not (match := start_re.match(line)):
            idx += 1
            continue
        start_line = idx + 1
        label = match.group(1)
        brace_depth = line.count("{") - line.count("}")
        body: list[str] = []
        idx += 1
        while idx < len(lines) and brace_depth > 0:
            body_line = lines[idx]
            brace_depth += body_line.count("{") - body_line.count("}")
            body.append(body_line)
            idx += 1
        blocks.append((start_line, label, body))
    return blocks


def _providers_with_required_versions(code: str) -> set[str]:  # noqa: C901
    providers: set[str] = set()
    lines = code.splitlines()
    idx = 0
    while idx < len(lines):
        terraform_line = lines[idx]
        if not _TERRAFORM_BLOCK_RE.match(terraform_line):
            idx += 1
            continue
        terraform_depth = terraform_line.count("{") - terraform_line.count("}")
        idx += 1
        terraform_body: list[str] = []
        while idx < len(lines) and terraform_depth > 0:
            current_line = lines[idx]
            terraform_depth += current_line.count("{") - current_line.count("}")
            terraform_body.append(current_line)
            idx += 1
        body_idx = 0
        while body_idx < len(terraform_body):
            line = terraform_body[body_idx]
            if not _REQUIRED_PROVIDERS_RE.match(line):
                body_idx += 1
                continue
            brace_depth = line.count("{") - line.count("}")
            body_idx += 1
            while body_idx < len(terraform_body) and brace_depth > 0:
                provider_line = terraform_body[body_idx]
                brace_depth += provider_line.count("{") - provider_line.count("}")
                provider_entry = _PROVIDER_ENTRY_RE.match(provider_line)
                if not provider_entry:
                    body_idx += 1
                    continue
                provider_name = provider_entry[1]
                provider_depth = provider_line.count("{") - provider_line.count("}")
                body_idx += 1
                has_version = False
                while body_idx < len(terraform_body) and provider_depth > 0:
                    entry_line = terraform_body[body_idx]
                    provider_depth += entry_line.count("{") - entry_line.count("}")
                    if _VERSION_RE.search(entry_line):
                        has_version = True
                    body_idx += 1
                if has_version:
                    providers.add(provider_name)
    return providers


class TerraformProviderVersionPinningDetector(
    ViolationDetector[TerraformProviderVersionPinningConfig],
    LocationHelperMixin,
):
    """Flag provider blocks that omit explicit version constraints."""

    @property
    def name(self) -> str:
        return "tf-001"

    def detect(
        self,
        context: AnalysisContext,
        config: TerraformProviderVersionPinningConfig,
    ) -> list[Violation]:
        violations: list[Violation] = []
        required_provider_versions = _providers_with_required_versions(context.code)
        for line_no, provider_name, body in _iter_block_lines(
            context.code, _PROVIDER_START_RE
        ):
            if provider_name in required_provider_versions:
                continue
            if any(_VERSION_RE.search(line) for line in body):
                continue
            violations.append(
                self.build_violation(
                    config,
                    contains=provider_name,
                    location=Location(line=line_no, column=1),
                    suggestion="Pin provider versions explicitly to avoid breaking changes.",
                ),
            )
        return violations


class TerraformModuleVersionPinningDetector(
    ViolationDetector[TerraformModuleVersionPinningConfig],
    LocationHelperMixin,
):
    """Flag module blocks that are not pinned to versions or refs."""

    @property
    def name(self) -> str:
        return "tf-002"

    def detect(
        self,
        context: AnalysisContext,
        config: TerraformModuleVersionPinningConfig,
    ) -> list[Violation]:
        violations: list[Violation] = []
        for line_no, module_name, body in _iter_block_lines(
            context.code, _MODULE_START_RE
        ):
            source = ""
            has_version = False
            for line in body:
                if _VERSION_RE.search(line):
                    has_version = True
                if match := _SOURCE_RE.search(line):
                    source = match[1]
            if source.startswith(("./", "../", "/")):
                continue
            if has_version or "?ref=" in source:
                continue
            violations.append(
                self.build_violation(
                    config,
                    contains=module_name,
                    location=Location(line=line_no, column=1),
                    suggestion="Pin external modules with version or commit ref.",
                ),
            )
        return violations


class TerraformVariableOutputDescriptionDetector(
    ViolationDetector[TerraformVariableOutputDescriptionConfig],
    LocationHelperMixin,
):
    """Require description fields on variable and output blocks."""

    @property
    def name(self) -> str:
        return "tf-003"

    def detect(
        self,
        context: AnalysisContext,
        config: TerraformVariableOutputDescriptionConfig,
    ) -> list[Violation]:
        violations: list[Violation] = []
        for line_no, name, body in _iter_block_lines(
            context.code, _VARIABLE_OR_OUTPUT_START_RE
        ):
            if any(_DESCRIPTION_RE.search(line) for line in body):
                continue
            violations.append(
                self.build_violation(
                    config,
                    contains=name,
                    location=Location(line=line_no, column=1),
                    suggestion="Add a description to improve module maintainability.",
                ),
            )
        return violations


class TerraformHardcodedIdDetector(
    ViolationDetector[TerraformHardcodedIdConfig],
    LocationHelperMixin,
):
    """Detect hardcoded cloud resource IDs and ARNs in assignments."""

    @property
    def name(self) -> str:
        return "tf-004"

    def detect(
        self,
        context: AnalysisContext,
        config: TerraformHardcodedIdConfig,
    ) -> list[Violation]:
        violations: list[Violation] = []
        for idx, line in enumerate(context.code.splitlines(), start=1):
            if line.strip().startswith(("#", "//")):
                continue
            if not (match := _ASSIGNMENT_RE.match(line)):
                continue
            key, value = match[1], match[2]
            if key.startswith(("source", "description")):
                continue
            if _HARD_ID_VALUE_RE.search(value):
                violations.append(
                    self.build_violation(
                        config,
                        contains=value,
                        location=Location(line=idx, column=1),
                        suggestion="Prefer data sources or variables over hardcoded IDs/ARNs.",
                    ),
                )
        return violations


class TerraformNoHardcodedSecretsDetector(
    ViolationDetector[TerraformNoHardcodedSecretsConfig],
    LocationHelperMixin,
):
    """Detect likely hardcoded secret values in Terraform assignments."""

    @property
    def name(self) -> str:
        return "tf-005"

    def detect(
        self,
        context: AnalysisContext,
        config: TerraformNoHardcodedSecretsConfig,
    ) -> list[Violation]:
        violations: list[Violation] = []
        for idx, line in enumerate(context.code.splitlines(), start=1):
            if not (match := _ASSIGNMENT_RE.match(line)):
                continue
            key, value = match[1], match[2]
            if not _SECRET_KEY_RE.search(key):
                continue
            if value.startswith(("var.", "local.", "data.", "module.")):
                continue
            violations.append(
                self.build_violation(
                    config,
                    contains=key,
                    location=Location(line=idx, column=1),
                    suggestion="Use variables or secret managers for sensitive values.",
                ),
            )
        return violations


class TerraformBackendConfigDetector(
    ViolationDetector[TerraformBackendConfig],
    LocationHelperMixin,
):
    """Ensure terraform blocks declare an explicit backend configuration."""

    @property
    def name(self) -> str:
        return "tf-006"

    def detect(
        self,
        context: AnalysisContext,
        config: TerraformBackendConfig,
    ) -> list[Violation]:
        lines = context.code.splitlines()
        terraform_line = next(
            (
                idx
                for idx, line in enumerate(lines, start=1)
                if _TERRAFORM_BLOCK_RE.match(line)
            ),
            None,
        )
        has_backend = any(_BACKEND_RE.match(line) for line in lines)
        if terraform_line is None or has_backend:
            return []
        return [
            self.build_violation(
                config,
                contains="backend",
                location=Location(line=terraform_line, column=1),
                suggestion="Configure a remote state backend for team environments.",
            ),
        ]


class TerraformNamingConventionDetector(
    ViolationDetector[TerraformNamingConventionConfig],
    LocationHelperMixin,
):
    """Enforce snake_case naming for Terraform variables and resources."""

    @property
    def name(self) -> str:
        return "tf-007"

    def detect(
        self,
        context: AnalysisContext,
        config: TerraformNamingConventionConfig,
    ) -> list[Violation]:
        violations: list[Violation] = []
        for idx, line in enumerate(context.code.splitlines(), start=1):
            if match := _RESOURCE_START_RE.match(line):
                resource_name = match[2]
                if not _SNAKE_CASE_RE.match(resource_name):
                    violations.append(
                        self.build_violation(
                            config,
                            contains=resource_name,
                            location=Location(line=idx, column=1),
                            suggestion="Use snake_case naming for resources and variables.",
                        ),
                    )
            if match := _VARIABLE_START_RE.match(line):
                object_name = match[1]
                if not _SNAKE_CASE_RE.match(object_name):
                    violations.append(
                        self.build_violation(
                            config,
                            contains=object_name,
                            location=Location(line=idx, column=1),
                            suggestion="Use snake_case naming for resources and variables.",
                        ),
                    )
        return violations


__all__ = [
    "TerraformBackendConfigDetector",
    "TerraformHardcodedIdDetector",
    "TerraformModuleVersionPinningDetector",
    "TerraformNamingConventionDetector",
    "TerraformNoHardcodedSecretsDetector",
    "TerraformProviderVersionPinningDetector",
    "TerraformVariableOutputDescriptionDetector",
]
