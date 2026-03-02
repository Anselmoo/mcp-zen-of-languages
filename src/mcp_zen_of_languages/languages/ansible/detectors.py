"""Detectors for Ansible playbook, role, and task zen principles."""

from __future__ import annotations

# ruff: noqa: D102
import re

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
_STATE_ARG_RE = re.compile(r"(^|\s)state=")

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
    "action",
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
    "local_action",
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
_PLAY_KEYS = {"hosts", "tasks", "pre_tasks", "post_tasks", "roles", "gather_facts"}


def _to_plays(tree: object) -> list[dict[str, object]]:
    if isinstance(tree, list):
        return [
            {str(key): value for key, value in item.items()}
            for item in tree
            if isinstance(item, dict)
        ]
    if isinstance(tree, dict):
        return [{str(key): value for key, value in tree.items()}]
    return []


def _iter_tasks(play: dict[str, object]) -> list[dict[str, object]]:
    tasks: list[dict[str, object]] = []
    for key in ("tasks", "pre_tasks", "post_tasks", "handlers"):
        entries = play.get(key)
        if isinstance(entries, list):
            tasks.extend(entry for entry in entries if isinstance(entry, dict))
    return tasks


def _root_tasks(tree: object) -> list[dict[str, object]]:
    if not isinstance(tree, list):
        return []
    mappings = [
        {str(key): value for key, value in item.items()}
        for item in tree
        if isinstance(item, dict)
    ]
    if not mappings:
        return []
    if any(any(key in _PLAY_KEYS for key in item) for item in mappings):
        return []
    return mappings


def _task_module(task: dict[str, object]) -> str | None:
    for action_key in ("action", "local_action"):
        action_value = task.get(action_key)
        if isinstance(action_value, dict):
            module = action_value.get("module")
            if isinstance(module, str):
                return module
        if isinstance(action_value, str):
            return action_value.split(maxsplit=1)[0]
    for key in task:
        if key in _TASK_META_KEYS or key.startswith("with_"):
            continue
        return key
    return None


def _line_of_token(code: str, token: str, default: int = 1, start_line: int = 1) -> int:
    lines = code.splitlines()
    for idx in range(max(start_line, 1) - 1, len(lines)):
        if token in lines[idx]:
            return idx + 1
    # Fallback for callers using an offset when the token appears earlier in the file.
    for idx, line in enumerate(lines, start=1):
        if token in line:
            return idx
    return default


def _task_line(
    code: str,
    task: dict[str, object],
    module: str | None,
    *,
    default: int = 1,
    start_line: int = 1,
) -> int:
    if "action" in task:
        return _line_of_token(code, "action:", default=default, start_line=start_line)
    if "local_action" in task:
        return _line_of_token(
            code, "local_action:", default=default, start_line=start_line
        )
    if module is None:
        return default
    return _line_of_token(code, f"{module}:", default=default, start_line=start_line)


def _has_explicit_state(
    task: dict[str, object],
    module_args: object,
    action: object,
    local_action: object,
) -> bool:
    has_module_state = isinstance(module_args, dict) and "state" in module_args
    has_module_state_arg = isinstance(module_args, str) and bool(
        _STATE_ARG_RE.search(module_args)
    )
    has_task_state = "state" in task
    args = task.get("args")
    has_args_state = isinstance(args, dict) and "state" in args
    has_args_state_arg = isinstance(args, str) and bool(_STATE_ARG_RE.search(args))
    has_action_state_arg = isinstance(action, str) and bool(
        _STATE_ARG_RE.search(action)
    )
    has_local_action_state_arg = isinstance(local_action, str) and bool(
        _STATE_ARG_RE.search(local_action)
    )
    return any(
        (
            has_module_state,
            has_module_state_arg,
            has_task_state,
            has_args_state,
            has_args_state_arg,
            has_action_state_arg,
            has_local_action_state_arg,
        )
    )


class AnsibleNamingDetector(
    ViolationDetector[AnsibleNamingConfig], LocationHelperMixin
):
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
            plays = [{}]
        violations: list[Violation] = []
        root_tasks = _root_tasks(tree)
        task_groups = [(play, _iter_tasks(play)) for play in plays]
        if root_tasks:
            task_groups.append(({}, root_tasks))
        for play, tasks in task_groups:
            if "hosts" in play and not play.get("name"):
                line = _line_of_token(context.code, "hosts:")
                violations.append(
                    self.build_violation(
                        config,
                        location=Location(line=line, column=1),
                        suggestion="Add a descriptive name for this play.",
                    )
                )
            task_cursor = 1
            for task in tasks:
                if task.get("name"):
                    task_cursor = _task_line(
                        context.code,
                        task,
                        _task_module(task),
                        start_line=task_cursor,
                    )
                    continue
                module = _task_module(task)
                if module is None:
                    continue
                line = _task_line(
                    context.code, task, module, start_line=task_cursor, default=1
                )
                task_cursor = line + 1
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
        task_groups = [_iter_tasks(play) for play in _to_plays(tree)]
        if root_tasks := _root_tasks(tree):
            task_groups.append(root_tasks)
        for tasks in task_groups:
            task_cursor = 1
            for task in tasks:
                module = _task_module(task)
                if module is None or "." in module:
                    task_cursor = _task_line(
                        context.code,
                        task,
                        module,
                        start_line=task_cursor,
                    )
                    continue
                line = _task_line(
                    context.code, task, module, start_line=task_cursor, default=1
                )
                task_cursor = line + 1
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
        disallowed = {
            "shell",
            "command",
            "ansible.builtin.shell",
            "ansible.builtin.command",
        }
        task_groups = [_iter_tasks(play) for play in _to_plays(tree)]
        if root_tasks := _root_tasks(tree):
            task_groups.append(root_tasks)
        for tasks in task_groups:
            task_cursor = 1
            for task in tasks:
                module = _task_module(task)
                if module not in disallowed:
                    task_cursor = _task_line(
                        context.code,
                        task,
                        module,
                        start_line=task_cursor,
                    )
                    continue
                line = _task_line(
                    context.code, task, module, start_line=task_cursor, default=1
                )
                task_cursor = line + 1
                violations.append(
                    self.build_violation(
                        config,
                        contains=module,
                        location=Location(line=line, column=1),
                        suggestion="Use a dedicated idempotent module when available.",
                    )
                )
        return violations


class AnsibleBecomeDetector(
    ViolationDetector[AnsibleBecomeConfig], LocationHelperMixin
):
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
        task_groups = [_iter_tasks(play) for play in _to_plays(tree)]
        if root_tasks := _root_tasks(tree):
            task_groups.append(root_tasks)
        for tasks in task_groups:
            task_cursor = 1
            for task in tasks:
                module = _task_module(task)
                if module is None:
                    continue
                module_name = module.split(".")[-1]
                if module_name not in _STATEFUL_MODULES:
                    task_cursor = _task_line(
                        context.code,
                        task,
                        module,
                        start_line=task_cursor,
                    )
                    continue
                module_args = task.get(module)
                action = task.get("action")
                local_action = task.get("local_action")
                if module_args is None and isinstance(action, dict):
                    module_args = action
                if module_args is None and isinstance(local_action, dict):
                    module_args = local_action
                if _has_explicit_state(task, module_args, action, local_action):
                    continue
                line = _task_line(
                    context.code, task, module, start_line=task_cursor, default=1
                )
                task_cursor = line + 1
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
