"""Detectors for GitHub Actions workflow issues."""

from __future__ import annotations

import re

from mcp_zen_of_languages.analyzers.base import (
    AnalysisContext,
    LocationHelperMixin,
    ViolationDetector,
)
from mcp_zen_of_languages.languages.ci_yaml_utils import job_steps, workflow_jobs
from mcp_zen_of_languages.languages.configs import GitHubActionsWorkflowConfig
from mcp_zen_of_languages.models import Violation

_SEVERITY: dict[str, int] = {
    "gha-001": 9,
    "gha-002": 10,
    "gha-003": 10,
    "gha-004": 8,
    "gha-005": 7,
    "gha-006": 5,
    "gha-007": 5,
    "gha-008": 6,
    "gha-009": 5,
    "gha-010": 4,
    "gha-011": 7,
    "gha-012": 7,
    "gha-013": 4,
    "gha-014": 4,
    "gha-015": 4,
}
_GOD_WORKFLOW_LINE_THRESHOLD = 300


class GitHubActionsWorkflowDetector(
    ViolationDetector[GitHubActionsWorkflowConfig],
    LocationHelperMixin,
):
    """Composite detector covering GitHub Actions security and quality checks."""

    @property
    def name(self) -> str:
        """Return detector identifier."""
        return "gha-workflow"

    def _violation(
        self, context: AnalysisContext, principle: str, token: str, message: str
    ) -> Violation:
        return Violation(
            principle=principle,
            severity=_SEVERITY[principle],
            message=message,
            location=self.find_location_by_substring(context.code, token),
        )

    def detect(  # noqa: C901, PLR0912, PLR0915
        self,
        context: AnalysisContext,
        _config: GitHubActionsWorkflowConfig,
    ) -> list[Violation]:
        """Detect security, maintainability, and idiomatic workflow issues."""
        document = (
            context.ast_tree.tree
            if context.ast_tree and isinstance(context.ast_tree.tree, dict)
            else {}
        )
        jobs = workflow_jobs(document)
        code = context.code
        violations: list[Violation] = []

        for match in re.finditer(r"uses:\s*([^\s@]+)@([^\s]+)", code):
            version = match.group(2)
            if not re.fullmatch(r"[a-f0-9]{40}", version):
                violations.append(
                    self._violation(
                        context,
                        "gha-001",
                        match.group(0),
                        "Pin actions by full 40-char commit SHA.",
                    ),
                )
                break

        if (
            "pull_request_target" in code
            and "github.event.pull_request.head.sha" in code
        ):
            violations.append(
                self._violation(
                    context,
                    "gha-002",
                    "pull_request_target",
                    "Avoid checking out untrusted PR head SHA in pull_request_target workflows.",
                ),
            )
        if "run:" in code and "${{ secrets." in code:
            violations.append(
                self._violation(
                    context,
                    "gha-003",
                    "${{ secrets.",
                    "Secrets referenced in run blocks may leak into logs.",
                ),
            )

        permissions = document.get("permissions")
        if permissions == "write-all" or permissions is None:
            token = (
                "permissions: write-all"
                if permissions == "write-all"
                else "permissions:"
            )
            violations.append(
                self._violation(
                    context,
                    "gha-004",
                    token,
                    "Define minimal workflow-level permissions instead of write-all or implicit defaults.",
                ),
            )
        if permissions is None and any(
            "permissions" not in job for job in jobs.values()
        ):
            violations.append(
                self._violation(
                    context,
                    "gha-005",
                    "jobs:",
                    "Set explicit minimal permissions per job when workflow-level permissions are absent.",
                ),
            )

        if len(code.splitlines()) > _GOD_WORKFLOW_LINE_THRESHOLD:
            violations.append(
                self._violation(
                    context,
                    "gha-006",
                    "name:",
                    "Workflow is large; split into reusable workflow_call units.",
                ),
            )

        step_signatures: dict[tuple[str, str], set[str]] = {}
        for job_name, job in jobs.items():
            for step in job_steps(job):
                signature = (str(step.get("uses", "")), str(step.get("run", "")))
                if signature == ("", ""):
                    continue
                step_signatures.setdefault(signature, set()).add(job_name)
        if any(len(job_names) > 1 for job_names in step_signatures.values()):
            violations.append(
                self._violation(
                    context,
                    "gha-007",
                    "steps:",
                    "Duplicate steps appear across jobs; extract a reusable action.",
                ),
            )

        if any("timeout-minutes" not in job for job in jobs.values()):
            violations.append(
                self._violation(
                    context, "gha-008", "jobs:", "Set timeout-minutes for every job."
                ),
            )
        if "concurrency" not in document:
            violations.append(
                self._violation(
                    context,
                    "gha-009",
                    "on:",
                    "Add workflow concurrency to cancel stale runs.",
                ),
            )

        for job in jobs.values():
            strategy = job.get("strategy")
            if not isinstance(strategy, dict):
                continue
            matrix = strategy.get("matrix")
            if not isinstance(matrix, dict):
                continue
            if (
                any(
                    isinstance(value, list) and len(value) > 1
                    for value in matrix.values()
                )
                and "include" not in matrix
                and "exclude" not in matrix
            ):
                violations.append(
                    self._violation(
                        context,
                        "gha-010",
                        "matrix:",
                        "Prefer include/exclude strategy when matrix values are hardcoded.",
                    ),
                )
                break

        if "::set-output" in code:
            violations.append(
                self._violation(
                    context,
                    "gha-011",
                    "::set-output",
                    "Replace deprecated ::set-output with GITHUB_OUTPUT.",
                ),
            )
        if "::save-state" in code or "::set-env" in code:
            token = "::save-state" if "::save-state" in code else "::set-env"
            violations.append(
                self._violation(
                    context,
                    "gha-012",
                    token,
                    "Replace deprecated workflow commands with GITHUB_STATE / GITHUB_ENV.",
                ),
            )

        if any(
            "run" in step and "shell" not in step
            for job in jobs.values()
            for step in job_steps(job)
        ):
            violations.append(
                self._violation(
                    context, "gha-013", "run:", "Declare shell explicitly on run steps."
                ),
            )

        has_dependency_install = bool(
            re.search(
                r"\b(pip install|npm ci|npm install|yarn install|poetry install)\b",
                code,
            ),
        )
        has_cache = "actions/cache@" in code or "cache:" in code
        if has_dependency_install and not has_cache:
            violations.append(
                self._violation(
                    context,
                    "gha-014",
                    "run:",
                    "Add dependency caching for install-heavy workflow steps.",
                ),
            )

        upload_steps = [
            step
            for job in jobs.values()
            for step in job_steps(job)
            if str(step.get("uses", "")).startswith("actions/upload-artifact@")
        ]
        if any(
            not isinstance(step.get("with"), dict)
            or "retention-days" not in step["with"]
            for step in upload_steps
        ):
            violations.append(
                self._violation(
                    context,
                    "gha-015",
                    "actions/upload-artifact@",
                    "Set retention-days for upload-artifact steps.",
                ),
            )

        return violations


__all__ = ["GitHubActionsWorkflowDetector"]
