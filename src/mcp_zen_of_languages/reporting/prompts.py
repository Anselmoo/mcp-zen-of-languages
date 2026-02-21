"""Prompt generation that transforms analysis results into actionable remediation text.

This module sits between the raw violation data and the final report output.
For each analysed file with violations, ``build_prompt_bundle`` produces a
structured ``FilePrompt`` containing:

* A context/goal/requirements preamble drawn from module-level constants.
* A quality checklist (shared with ``remediation_patterns``).
* Up to eight violation entries enriched with theme classification, remediation
  action, before/after code snippets, and acceptance criteria.

Language-level ``GenericPrompt`` entries are drawn from
``GENERIC_PROMPTS_BY_LANGUAGE`` and appended for every language observed in the
analysis batch.  Finally, a ``BigPictureAnalysis`` (from ``theme_clustering``)
is attached so that consumers such as the terminal renderer can display roadmap
and health-score context alongside the prompts.

See Also:
    ``reporting.remediation_patterns``: Supplies per-violation fix guidance.
    ``reporting.theme_clustering``: Supplies big-picture analysis context.
    ``reporting.terminal.render_prompt_panel``: Renders the bundle as Rich output.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from mcp_zen_of_languages.reporting.models import (
    FilePrompt,
    GenericPrompt,
    PromptBundle,
)
from mcp_zen_of_languages.reporting.remediation_patterns import (
    QUALITY_CHECKLIST,
    resolve_pattern,
)
from mcp_zen_of_languages.reporting.theme_clustering import (
    build_big_picture_analysis,
    classify_violation,
)

if TYPE_CHECKING:
    from mcp_zen_of_languages.models import AnalysisResult, Violation

PROMPT_CONTEXT = "Remediate code quality violations in a multi-language codebase using zen principles."
PROMPT_GOAL = (
    "Provide actionable, prioritized remediation steps with before/after guidance and "
    "acceptance criteria."
)
PROMPT_REQUIREMENTS = [
    "Summarize the top violation themes and prioritize fixes.",
    "Include concrete before/after code patterns when possible.",
    "Provide a short checklist for verifying the fix.",
    "Keep steps clear and testable.",
]

# Maximum violations listed per file prompt before the "...and N more" line
MAX_VIOLATIONS_SHOWN = 8

GENERIC_PROMPTS_BY_LANGUAGE: dict[str, list[tuple[str, str]]] = {
    "bash": [
        (
            "Harden shell safety",
            "Add strict mode (set -euo pipefail), quote variables, and split large "
            "scripts into small functions.",
        ),
    ],
    "cpp": [
        (
            "RAII and ownership",
            "Replace raw new/delete with smart pointers, prefer RAII, and enforce "
            "const-correct interfaces.",
        ),
    ],
    "csharp": [
        (
            "Async/await hygiene",
            "Avoid blocking calls, propagate async/await, and prefer string "
            "interpolation over concatenation.",
        ),
    ],
    "css": [
        (
            "Design-token stylesheet hygiene",
            "Reduce selector nesting, replace magic literals with tokens, and "
            "standardize breakpoints and z-index scales.",
        ),
    ],
    "javascript": [
        (
            "Safer JavaScript",
            "Prefer const/let, avoid implicit coercion, and reduce inheritance "
            "depth with composition.",
        ),
    ],
    "powershell": [
        (
            "PowerShell hygiene",
            "Use approved verbs, add parameter validation, and emit data with "
            "Write-Output instead of Write-Host.",
        ),
    ],
    "python": [
        (
            "Refactor hotspots",
            "Review high-severity Python violations and refactor complex functions "
            "into smaller units with clear docstrings.",
        ),
    ],
    "ruby": [
        (
            "Simplify Ruby objects",
            "Limit metaprogramming, keep classes focused, and favor explicit "
            "modules or mixins.",
        ),
    ],
    "sql": [
        (
            "Harden SQL query safety",
            "Replace SELECT * and implicit joins with explicit columns and JOIN ... ON, "
            "then parameterize dynamic SQL and enforce transaction boundaries.",
        ),
    ],
    "typescript": [
        (
            "Harden strictness",
            "Audit tsconfig settings and enable strict mode with null checks.",
        ),
    ],
    "go": [
        (
            "Error handling audit",
            "Locate ignored errors and ensure explicit checks are enforced.",
        ),
    ],
    "rust": [
        (
            "Reduce unsafe/unwrap usage",
            "Replace unwrap/expect and unsafe blocks with safer patterns and "
            "document invariants.",
        ),
    ],
    "yaml": [
        (
            "YAML structure clarity",
            "Keep key naming consistent, avoid deeply nested mappings, and use "
            "anchors/aliases sparingly to preserve readability.",
        ),
    ],
    "toml": [
        (
            "TOML section hygiene",
            "Group related keys into focused tables, avoid duplicate semantics, "
            "and keep scalar values explicitly typed when possible.",
        ),
    ],
    "xml": [
        (
            "XML schema discipline",
            "Prefer clear element hierarchies, minimize mixed content, and "
            "validate documents against a schema or contract.",
        ),
    ],
    "json": [
        (
            "JSON payload consistency",
            "Use stable field naming conventions, avoid deeply nested payloads, "
            "and enforce schema validation for producer/consumer contracts.",
        ),
    ],
    "markdown": [
        (
            "Documentation flow and accessibility",
            "Keep heading levels sequential, add alt text for images, avoid bare URLs, "
            "and ensure MDX imports/exports stay clean.",
        ),
    ],
    "github-actions": [
        (
            "GitHub Actions hardening",
            "Pin third-party actions to commit SHAs, scope permissions tightly, "
            "and add timeouts/concurrency to avoid stale or risky runs.",
        ),
    ],
    "dockerfile": [
        (
            "Container image hardening",
            "Pin base image versions, run as non-root, avoid ENV/ARG secrets, and "
            "use multi-stage builds with a .dockerignore file.",
        ),
    ],
    "docker_compose": [
        (
            "Compose service hardening",
            "Pin service image tags, avoid root users, define healthchecks, and keep "
            "secret-like values out of inline environment blocks.",
        ),
    ],
}


def _format_file_prompt(result: AnalysisResult, violations: list[Violation]) -> str:
    """Render a self-contained remediation prompt for a single analysed file.

    The prompt is formatted as Markdown with a structured header (context, goal,
    requirements, checklist) followed by up to eight violation entries.  Each
    entry is enriched with theme classification, remediation action, idiomatic
    explanation, before/after code blocks, and acceptance criteria resolved via
    ``remediation_patterns.resolve_pattern``.

    Args:
        result: Analysis result for the target file.
        violations: Violation subset to include (typically ``result.violations``).

    Returns:
        str: Multi-line Markdown prompt text ready for embedding in a ``FilePrompt``.
    """
    path = result.path or "<input>"
    lines = [
        f"### File: {path}",
        f"Context: {PROMPT_CONTEXT}",
        f"Target: {path} ({result.language})",
        f"Goal: {PROMPT_GOAL}",
        "Requirements:",
        *[f"{idx}. {req}" for idx, req in enumerate(PROMPT_REQUIREMENTS, start=1)],
        "Checklist:",
        *[f"- {item}" for item in QUALITY_CHECKLIST],
        "",
        "Violations:",
    ]
    for violation in violations[:8]:
        pattern = resolve_pattern(violation, result.language)
        theme = classify_violation(violation)
        acceptance = (
            pattern.acceptance_criteria.format(path=path)
            if "{path}" in pattern.acceptance_criteria
            else pattern.acceptance_criteria
        )
        lines.extend(
            [
                f"- [{violation.severity}] {violation.principle}: {violation.message}",
                f"  Theme: {theme}",
                f"  Action: {pattern.action}",
                f"  Idiom: {pattern.idiom_explanation}",
                f"  Effort: {pattern.effort}",
            ],
        )
        if pattern.before_pattern:
            lines.append("  Before:")
            lines.append(f"  ```{result.language or 'text'}")
            lines.extend([f"  {line}" for line in pattern.before_pattern.splitlines()])
            lines.append("  ```")
        if pattern.after_pattern:
            lines.append("  After:")
            lines.append(f"  ```{result.language or 'text'}")
            lines.extend([f"  {line}" for line in pattern.after_pattern.splitlines()])
            lines.append("  ```")
        lines.append(f"  Acceptance: {acceptance}")
    if len(violations) > MAX_VIOLATIONS_SHOWN:
        lines.append(f"- ...and {len(violations) - MAX_VIOLATIONS_SHOWN} more.")
    return "\n".join(lines)


def build_prompt_bundle(results: list[AnalysisResult]) -> PromptBundle:
    """Assemble the complete prompt bundle for a batch of analysis results.

    Iterates every ``AnalysisResult`` that contains violations and produces a
    ``FilePrompt`` for each.  Adds language-level ``GenericPrompt`` entries for
    every language observed, plus a standing quality checklist prompt.  Attaches
    a ``BigPictureAnalysis`` to provide roadmap and health-score context.

    Args:
        results: Analysis results from one or more files and languages.

    Returns:
        PromptBundle: File prompts, generic prompts, and big-picture analysis.
    """
    file_prompts: list[FilePrompt] = []
    for result in results:
        if not result.violations:
            continue
        prompt = _format_file_prompt(result, result.violations)
        file_prompts.append(
            FilePrompt(
                path=result.path or "<input>",
                language=result.language,
                prompt=prompt,
            ),
        )

    generic_prompts: list[GenericPrompt] = [
        GenericPrompt(
            title="Quick quality checklist",
            prompt="\n".join(f"- {item}" for item in QUALITY_CHECKLIST),
        ),
    ]
    languages_seen = {result.language for result in results}
    for language in sorted(languages_seen):
        generic_prompts.extend(
            GenericPrompt(title=title, prompt=prompt)
            for title, prompt in GENERIC_PROMPTS_BY_LANGUAGE.get(language, [])
        )
    big_picture = build_big_picture_analysis(results)
    return PromptBundle(
        file_prompts=file_prompts,
        generic_prompts=generic_prompts,
        big_picture=big_picture,
    )
