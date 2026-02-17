"""Canonical remediation patterns that map violation types to concrete fix guidance.

Each ``RemediationPattern`` encapsulates everything an agent or developer needs
to remediate a specific class of violation: an action summary, an idiomatic
explanation, optional before/after code snippets, an effort estimate, and
testable acceptance criteria.

Pattern resolution works by keyword matching: ``resolve_pattern`` scans a
violation's ``principle`` and ``message`` against each pattern's ``matchers``
list and returns the first hit.  When no language-specific pattern matches,
a generic fallback is synthesised on the fly.

Currently only Python patterns are registered in ``REMEDIATION_REGISTRY``;
additional languages can be added by appending to the registry dict.

The ``QUALITY_CHECKLIST`` list is shared across patterns and attached to
every generated prompt and agent task as a lightweight self-review aid.

See Also:
    ``reporting.prompts``: Calls ``resolve_pattern`` to enrich file prompts.
    ``reporting.agent_tasks``: Calls ``resolve_pattern`` to populate task actions.
"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

from mcp_zen_of_languages.models import Violation


class RemediationPattern(BaseModel):
    """Structured remediation instructions for one category of zen violation.

    Patterns are registered per language in ``REMEDIATION_REGISTRY`` and
    resolved at prompt-generation time via keyword matching.  The before/after
    snippets provide concrete visual diff guidance, while ``effort`` and
    ``acceptance_criteria`` help agents estimate and verify their work.

    Attributes:
        rule_id: Canonical rule identifier (e.g. ``"python-complexity"``).
        title: Short human-readable label for the remediation action.
        matchers: Lowercase keywords that trigger this pattern during resolution.
        theme: Remediation theme aligning with ``theme_clustering.THEME_TAGS``.
        action: Imperative description of the fix to apply.
        idiom_explanation: Why the idiomatic alternative is preferred.
        before_pattern: Example code *before* remediation (may contain ``{path}``).
        after_pattern: Example code *after* remediation.
        effort: T-shirt size estimate — ``"S"`` (minutes), ``"M"`` (hours), ``"L"`` (days).
        acceptance_criteria: Testable statement confirming the fix (supports ``{path}``).
        checklist: Quality checklist items appended to generated prompts.
    """

    rule_id: str
    title: str
    matchers: list[str] = Field(default_factory=list)
    theme: str
    action: str
    idiom_explanation: str
    before_pattern: str | None = None
    after_pattern: str | None = None
    effort: Literal["S", "M", "L"] = "M"
    acceptance_criteria: str
    checklist: list[str] = Field(default_factory=list)


QUALITY_CHECKLIST = [
    "Suggest 5 immediate code quality improvements.",
    "Pinpoint 5 technical debt hotspots to address.",
    "Find 5 opportunities for code reuse or simplification.",
    "Propose 5 improvements for variable or function naming.",
    "Identify 5 areas to make code more resilient or fault-tolerant.",
]

PYTHON_PATTERNS: list[RemediationPattern] = [
    RemediationPattern(
        rule_id="python-complexity",
        title="Reduce cyclomatic complexity",
        matchers=["cyclomatic", "complexity"],
        theme="Complexity",
        action="Split complex functions into smaller helpers and reduce branching.",
        idiom_explanation="Python favors small, single-purpose functions with clear names.",
        before_pattern="def handler(...):\n    if ...:\n        ...\n    elif ...:\n        ...",
        after_pattern="def handler(...):\n    _validate_inputs(...)\n    _dispatch_action(...)",
        effort="L",
        acceptance_criteria="No functions exceed the configured cyclomatic complexity threshold in {path}.",
        checklist=QUALITY_CHECKLIST,
    ),
    RemediationPattern(
        rule_id="python-nesting",
        title="Flatten nested logic",
        matchers=["nesting", "nested"],
        theme="Complexity",
        action="Refactor deep nesting into guard clauses and early returns.",
        idiom_explanation="Guard clauses make Python flows easier to read and test.",
        before_pattern="if condition:\n    if other:\n        ...",
        after_pattern="if not condition:\n    return\nif not other:\n    return\n...",
        effort="M",
        acceptance_criteria="No blocks exceed the configured nesting depth in {path}.",
        checklist=QUALITY_CHECKLIST,
    ),
    RemediationPattern(
        rule_id="python-long-function",
        title="Shorten long functions",
        matchers=["long function", "function length", "too long"],
        theme="Complexity",
        action="Extract cohesive helper functions and keep functions under the size limit.",
        idiom_explanation="Shorter functions improve readability and reduce test surface area.",
        before_pattern="def process(...):\n    # 100+ lines\n    ...",
        after_pattern="def process(...):\n    _load_inputs(...)\n    _validate(...)\n    return _build_response(...)",
        effort="M",
        acceptance_criteria="No functions exceed the configured max function length in {path}.",
        checklist=QUALITY_CHECKLIST,
    ),
    RemediationPattern(
        rule_id="python-docstrings",
        title="Add missing docstrings",
        matchers=["docstring"],
        theme="Documentation",
        action="Add Google-style docstrings with summary, args, and return details.",
        idiom_explanation="Explicit docstrings document intent and reduce onboarding time.",
        before_pattern="def fetch_data(client, query):\n    ...",
        after_pattern='def fetch_data(client, query):\n    """Fetch data for a query.\n\n    Args:\n        client: API client.\n        query: Query string.\n\n    Returns:\n        Parsed response data.\n    """\n    ...',
        effort="S",
        acceptance_criteria="Public functions and classes include docstrings in {path}.",
        checklist=QUALITY_CHECKLIST,
    ),
    RemediationPattern(
        rule_id="python-bare-except",
        title="Replace bare except",
        matchers=["bare except", "bare-except"],
        theme="Safety & Error Handling",
        action="Catch specific exceptions and log or re-raise as needed.",
        idiom_explanation="Explicit exception handling prevents hiding unexpected failures.",
        before_pattern="try:\n    ...\nexcept:\n    ...",
        after_pattern='try:\n    ...\nexcept (ValueError, IOError) as exc:\n    logger.exception("...")\n    raise',
        effort="M",
        acceptance_criteria="No bare-except blocks remain in {path}.",
        checklist=QUALITY_CHECKLIST,
    ),
    RemediationPattern(
        rule_id="python-magic-number",
        title="Replace magic numbers",
        matchers=["magic number", "magic-number"],
        theme="Naming & Style",
        action="Replace literals with named constants or enums.",
        idiom_explanation="Named constants make intent explicit and simplify change.",
        before_pattern="timeout = 30",
        after_pattern="DEFAULT_TIMEOUT_SECONDS = 30\n...\ntimeout = DEFAULT_TIMEOUT_SECONDS",
        effort="S",
        acceptance_criteria="Magic numbers are replaced with named constants in {path}.",
        checklist=QUALITY_CHECKLIST,
    ),
]

REMEDIATION_REGISTRY: dict[str, list[RemediationPattern]] = {
    "python": PYTHON_PATTERNS,
}


def resolve_pattern(violation: Violation, language: str) -> RemediationPattern:
    """Resolve the best-matching remediation pattern for a given violation.

    Scans ``REMEDIATION_REGISTRY[language]`` for a pattern whose ``matchers``
    list contains a keyword found in the violation's combined principle and
    message text.  Returns the first match, or a generic fallback pattern
    whose action mirrors the original violation message.

    Args:
        violation: Violation record to match against registered patterns.
        language: Language key used to look up the pattern registry.

    Returns:
        RemediationPattern: Matched pattern with action, snippets, and criteria.
    """

    text = f"{violation.principle} {violation.message}".lower()
    for pattern in REMEDIATION_REGISTRY.get(language, []):
        if any(token in text for token in pattern.matchers):
            return pattern
    return RemediationPattern(
        rule_id="generic",
        title="General remediation",
        theme="General",
        action=violation.message,
        idiom_explanation="Follow the language's zen principles and keep changes focused.",
        effort="S",
        acceptance_criteria=(
            "Resolve the violation and confirm it no longer appears in {path}."
        ),
        checklist=QUALITY_CHECKLIST,
    )
