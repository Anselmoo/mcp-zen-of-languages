"""Detectors for Ansible playbook, role, and task zen principles."""

from __future__ import annotations

import re

from collections.abc import Iterable
from typing import Any

from mcp_zen_of_languages.analyzers.base import AnalysisContext
from mcp_zen_of_languages.analyzers.base import LocationHelperMixin
from mcp_zen_of_languages.analyzers.base import ViolationDetector
from mcp_zen_of_languages.languages.configs import AnsibleBecomeConfig
from mcp_zen_of_languages.languages.configs import AnsibleFqcnConfig
from mcp_zen_of_languages.languages.configs import AnsibleIdempotencyConfig
from mcp_zen_of_languages.languages.configs import AnsibleJinjaSpacingConfig
from mcp_zen_of_languages.languages.configs import AnsibleNamingConfig
from mcp_zen_of_languages.languages.configs import AnsibleNoCleartextPasswordConfig
from mcp_zen_of_languages.languages.configs import AnsibleStateExplicitConfig
from mcp_zen_of_languages.models import Location
from mcp_zen_of_languages.models import Violation


_SECRET_RE = re.compile(
    r"(?i)\b(password|passwd|passphrase|token|secret|api[_-]?key)\b\s*:\s*([^\n#]+)"
)
_BAD_JINJA_SPACING_RE = re.compile(r"\{\{\S|\S\}\}")

_STATEFUL_MODULES = {
    "apt",
    "dnf",
    "file",
    "git",
    "group",
    "package",
    "pip",
    "service",
    "systemd",
    "user",
    "yum",
}
_TASK_META_KEYS = {
    "always",
    "args",
    "async",
    "become",
    "become_flags",
    "become_method",
    "become_user",
    "block",
    "changed_when",
    "check_mode",
    "collections",
    "debugger",
    "delay",
    "delegate_facts",
    "delegate_to",
    "diff",
    "environment",
    "failed_when",
    "ignore_errors",
    "ignore_unreachable",
    "loop",
    "loop_control",
    "name",
    "no_log",
    "notify",
    "poll",
    "register",
    "rescue",
    "retries",
    "run_once",
    "sudo",
    "tags",
    "throttle",
    "timeout",
    "until",
    "vars",
    "when",
}


def _to_plays(tree: Any) -> list[dict[str, Any]]:
    if isinstance(tree, list):
        return [item for item in tree if isinstance(item, dict)]
    if isinstance(tree, dict):
        return [tree]
    return []


def _iter_tasks(play: dict[str, Any]) -> Iterable[dict[str, Any]]:
    for key in ("tasks", "pre_tasks", "post_tasks", "handlers"):
        entries = play.get(key)
        if isinstance(entries, list):
            for entry in entries:
                if isinstance(entry, dict):
                    yield entry


def _task_module(task: dict[str, Any]) -> str | None:
    for key in task:
        if key in _TASK_META_KEYS or key.startswith("with_"):
            continue
        return key
    return None


def _line_of_token(code: str, token: str, default: int = 1) -> int:
    for idx, line in enumerate(code.splitlines(), start=1):
        if token in line:
            return idx
    return default


class AnsibleNamingDetector(ViolationDetector[AnsibleNamingConfig], LocationHelperMixin):
    """Ensure Ansible plays and tasks include descriptive names."""

    @property
    def name(self) -> str:
        return "ansible-001"

    def detect(
        self,
        context: AnalysisContext,
        config: AnsibleNamingConfig,
    ) -> list[Violation]:
        tree = context.ast_tree.tree if context.ast_tree is not None else None
        plays = _to_plays(tree)
        if not plays:
            return []
        violations: list[Violation] = []
        for play in plays:
            if "hosts" in play and not play.get("name"):
                line = _line_of_token(context.code, "hosts:")
                violations.append(
                    self.build_violation(
                        config,
                        location=Location(line=line, column=1),
                        suggestion="Add a descriptive name for this play.",
                    )
                )
            for task in _iter_tasks(play):
                if task.get("name"):
                    continue
                module = _task_module(task)
                if module is None:
                    continue
                line = _line_of_token(context.code, f"{module}:")
                violations.append(
                    self.build_violation(
                        config,
                        location=Location(line=line, column=1),
                        suggestion="Add a descriptive task name.",
                    )
                )
        return violations


class AnsibleFqcnDetector(ViolationDetector[AnsibleFqcnConfig], LocationHelperMixin):
    """Detect short module names that should use fully qualified collection names."""

    @property
    def name(self) -> str:
        return "ansible-002"

    def detect(
        self,
        context: AnalysisContext,
        config: AnsibleFqcnConfig,
    ) -> list[Violation]:
        tree = context.ast_tree.tree if context.ast_tree is not None else None
        violations: list[Violation] = []
        for play in _to_plays(tree):
            for task in _iter_tasks(play):
                module = _task_module(task)
                if module is None or "." in module:
                    continue
                line = _line_of_token(context.code, f"{module}:")
                violations.append(
                    self.build_violation(
                        config,
                        contains=module,
                        location=Location(line=line, column=1),
                        suggestion=f"Use FQCN form like ansible.builtin.{module}.",
                    )
                )
        return violations


class AnsibleIdempotencyDetector(
    ViolationDetector[AnsibleIdempotencyConfig], LocationHelperMixin
):
    """Flag shell/command usage where idempotent modules should be preferred."""

    @property
    def name(self) -> str:
        return "ansible-003"

    def detect(
        self,
        context: AnalysisContext,
        config: AnsibleIdempotencyConfig,
    ) -> list[Violation]:
        tree = context.ast_tree.tree if context.ast_tree is not None else None
        violations: list[Violation] = []
        disallowed = {"shell", "command", "ansible.builtin.shell", "ansible.builtin.command"}
        for play in _to_plays(tree):
            for task in _iter_tasks(play):
                module = _task_module(task)
                if module not in disallowed:
                    continue
                line = _line_of_token(context.code, f"{module}:")
                violations.append(
                    self.build_violation(
                        config,
                        contains=module,
                        location=Location(line=line, column=1),
                        suggestion="Use a dedicated idempotent module when available.",
                    )
                )
        return violations


class AnsibleBecomeDetector(ViolationDetector[AnsibleBecomeConfig], LocationHelperMixin):
    """Flag deprecated sudo usage in plays or tasks."""

    @property
    def name(self) -> str:
        return "ansible-004"

    def detect(
        self,
        context: AnalysisContext,
        config: AnsibleBecomeConfig,
    ) -> list[Violation]:
        violations: list[Violation] = []
        for idx, line in enumerate(context.code.splitlines(), start=1):
            if re.search(r"^\s*sudo\s*:", line):
                violations.append(
                    self.build_violation(
                        config,
                        location=Location(line=idx, column=1),
                        suggestion="Use become: true instead of sudo.",
                    )
                )
        return violations


class AnsibleStateExplicitDetector(
    ViolationDetector[AnsibleStateExplicitConfig], LocationHelperMixin
):
    """Ensure stateful modules specify explicit state values."""

    @property
    def name(self) -> str:
        return "ansible-005"

    def detect(
        self,
        context: AnalysisContext,
        config: AnsibleStateExplicitConfig,
    ) -> list[Violation]:
        tree = context.ast_tree.tree if context.ast_tree is not None else None
        violations: list[Violation] = []
        for play in _to_plays(tree):
            for task in _iter_tasks(play):
                module = _task_module(task)
                if module is None:
                    continue
                module_name = module.split(".")[-1]
                if module_name not in _STATEFUL_MODULES:
                    continue
                module_args = task.get(module)
                if isinstance(module_args, dict) and "state" in module_args:
                    continue
                if "state" in task:
                    continue
                line = _line_of_token(context.code, f"{module}:")
                violations.append(
                    self.build_violation(
                        config,
                        contains=module,
                        location=Location(line=line, column=1),
                        suggestion="Specify state explicitly for this module.",
                    )
                )
        return violations


class AnsibleNoCleartextPasswordDetector(
    ViolationDetector[AnsibleNoCleartextPasswordConfig], LocationHelperMixin
):
    """Detect likely cleartext secret assignments in YAML variables."""

    @property
    def name(self) -> str:
        return "ansible-006"

    def detect(
        self,
        context: AnalysisContext,
        config: AnsibleNoCleartextPasswordConfig,
    ) -> list[Violation]:
        violations: list[Violation] = []
        for idx, line in enumerate(context.code.splitlines(), start=1):
            match = _SECRET_RE.search(line)
            if not match:
                continue
            value = match[2].strip()
            if "{{" in value or "!vault" in value or "lookup(" in value:
                continue
            violations.append(
                self.build_violation(
                    config,
                    contains=match[1],
                    location=Location(line=idx, column=1),
                    suggestion="Use Ansible Vault or external secret lookup.",
                )
            )
        return violations


class AnsibleJinjaSpacingDetector(
    ViolationDetector[AnsibleJinjaSpacingConfig], LocationHelperMixin
):
    """Enforce consistent spacing inside Jinja2 interpolation delimiters."""

    @property
    def name(self) -> str:
        return "ansible-007"

    def detect(
        self,
        context: AnalysisContext,
        config: AnsibleJinjaSpacingConfig,
    ) -> list[Violation]:
        violations: list[Violation] = []
        for idx, line in enumerate(context.code.splitlines(), start=1):
            if _BAD_JINJA_SPACING_RE.search(line):
                violations.append(
                    self.build_violation(
                        config,
                        location=Location(line=idx, column=1),
                        suggestion="Use spacing like {{ variable_name }}.",
                    )
                )
        return violations


__all__ = [
    "AnsibleBecomeDetector",
    "AnsibleFqcnDetector",
    "AnsibleIdempotencyDetector",
    "AnsibleJinjaSpacingDetector",
    "AnsibleNamingDetector",
    "AnsibleNoCleartextPasswordDetector",
    "AnsibleStateExplicitDetector",
]
