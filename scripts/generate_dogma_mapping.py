"""Generate dogma↔language-rule reverse-mapping docs.

Run::

    uv run python scripts/generate_dogma_mapping.py          # write files
    uv run python scripts/generate_dogma_mapping.py --check  # CI dry-run

The script imports all language zen principles and uses
``infer_dogmas_for_principle()`` to build a reverse mapping from each
of the 10 universal dogmas to the language-specific rules that implement
them.
"""

from __future__ import annotations

import argparse
import importlib
import sys

from collections import defaultdict
from pathlib import Path

from mcp_zen_of_languages.core.universal_dogmas import UniversalDogmaID
from mcp_zen_of_languages.core.universal_dogmas import infer_dogmas_for_principle
from mcp_zen_of_languages.rules import get_all_languages
from mcp_zen_of_languages.rules import get_language_zen


MAPPING_OUTPUT_PATH = Path("docs/includes/generated/dogma-mapping.md")
DOGMA_SPEC_PATH = Path("docs/user-guide/rules/the-ten-dogmas.md")

# Display-friendly language names (module_key → display name)
_LANGUAGE_NAMES: dict[str, str] = {
    "python": "Python",
    "typescript": "TypeScript",
    "rust": "Rust",
    "go": "Go",
    "javascript": "JavaScript",
    "css": "CSS",
    "bash": "Bash",
    "powershell": "PowerShell",
    "ruby": "Ruby",
    "sql": "SQL",
    "cpp": "C++",
    "csharp": "C#",
    "docker_compose": "Docker Compose",
    "dockerfile": "Dockerfile",
    "terraform": "Terraform",
    "markdown": "Markdown",
    "latex": "LaTeX",
    "github-actions": "GitHub Actions",
    "gitlab_ci": "GitLab CI",
    "json": "JSON",
    "toml": "TOML",
    "xml": "XML",
    "yaml": "YAML",
}

# Dogma display names (short label for docs)
_DOGMA_LABELS: dict[UniversalDogmaID, str] = {
    UniversalDogmaID.UTILIZE_ARGUMENTS: "Purpose",
    UniversalDogmaID.EXPLICIT_INTENT: "Explicit Intent",
    UniversalDogmaID.RETURN_EARLY: "Flat Traversal",
    UniversalDogmaID.FAIL_FAST: "Loud Failures",
    UniversalDogmaID.RIGHT_ABSTRACTION: "Meaningful Abstraction",
    UniversalDogmaID.UNAMBIGUOUS_NAME: "Unambiguous Naming",
    UniversalDogmaID.VISIBLE_STATE: "Visible State",
    UniversalDogmaID.STRICT_FENCES: "Strict Fences",
    UniversalDogmaID.RUTHLESS_DELETION: "Ruthless Deletion",
    UniversalDogmaID.PROPORTIONATE_COMPLEXITY: "Proportionate Complexity",
}


# Dogma anchor slugs on philosophy.md (MkDocs auto-generated from headings)
_DOGMA_ANCHORS: dict[UniversalDogmaID, str] = {
    UniversalDogmaID.UTILIZE_ARGUMENTS: "1-dogma-of-purpose-zen-utilize-arguments",
    UniversalDogmaID.EXPLICIT_INTENT: "2-dogma-of-explicit-intent-zen-explicit-intent",
    UniversalDogmaID.RETURN_EARLY: "3-dogma-of-flat-traversal-zen-return-early",
    UniversalDogmaID.FAIL_FAST: "4-dogma-of-loud-failures-zen-fail-fast",
    UniversalDogmaID.RIGHT_ABSTRACTION: "5-dogma-of-meaningful-abstraction-zen-right-abstraction",
    UniversalDogmaID.UNAMBIGUOUS_NAME: "6-dogma-of-unambiguous-naming-zen-unambiguous-name",
    UniversalDogmaID.VISIBLE_STATE: "7-dogma-of-visible-state-zen-visible-state",
    UniversalDogmaID.STRICT_FENCES: "8-dogma-of-strict-fences-zen-strict-fences",
    UniversalDogmaID.RUTHLESS_DELETION: "9-dogma-of-ruthless-deletion-zen-ruthless-deletion",
    UniversalDogmaID.PROPORTIONATE_COMPLEXITY: "10-dogma-of-proportionate-complexity-zen-proportionate-complexity",
}

# Per-dogma (quote, rationale, anti-patterns list)
_DOGMA_DETAIL: dict[UniversalDogmaID, tuple[str, str, list[str]]] = {
    UniversalDogmaID.UTILIZE_ARGUMENTS: (
        "Every argument must be used or removed.",
        "Unused parameters signal dead intent. They mislead readers about a "
        "function's contract and accumulate as noise during refactors. In AI-assisted "
        "workflows, an agent generating a function signature should never leave behind "
        "vestigial parameters.",
        [
            "Accepting a parameter that is never referenced in the body.",
            "Keeping deprecated arguments for compatibility without a migration path.",
            "Forwarding `**kwargs` solely to suppress linter warnings about unused names.",
        ],
    ),
    UniversalDogmaID.EXPLICIT_INTENT: (
        "Avoid magic behavior and hidden assumptions.",
        "Implicit behavior — type coercion, default mutations, hidden global state — "
        "creates cognitive load that compounds across a codebase. When an AI assistant "
        "reviews code, explicit intent makes violations unambiguous and fixes mechanical.",
        [
            "Relying on mutable default arguments (`def f(x=[])`).",
            "Star-imports that hide the origin of names.",
            "Magic numbers without named constants.",
            "Implicit type conversions that silently change semantics.",
        ],
    ),
    UniversalDogmaID.RETURN_EARLY: (
        "Prefer guard clauses over deep nesting.",
        "Deeply nested code forces readers to maintain a mental stack of conditions. "
        "Guard clauses flatten the control flow and highlight the happy path. "
        "Detectors can measure nesting depth mechanically, making this an ideal "
        "candidate for automated enforcement.",
        [
            "`if`/`else` chains nested three or more levels deep.",
            "Wrapping entire function bodies in a single top-level `if`.",
            "Failing to invert negative conditions into early returns.",
        ],
    ),
    UniversalDogmaID.FAIL_FAST: (
        "Never silently swallow errors.",
        "Silent failures turn bugs into mysteries. When errors surface immediately, "
        "root-cause analysis becomes trivial. This is especially critical in MCP "
        "workflows where an agent may not observe side effects that a human would "
        "notice in a debugger.",
        [
            "Bare `except: pass` blocks.",
            "Catching broad exception types without logging or re-raising.",
            "Returning `None` as a silent error sentinel instead of raising.",
            "Using `.unwrap()` (Rust) or force-unwrapping (Swift) without context.",
        ],
    ),
    UniversalDogmaID.RIGHT_ABSTRACTION: (
        "Avoid flag-heavy abstractions.",
        "A boolean parameter that toggles behavior is two functions wearing one name. "
        "Premature or incorrect abstraction is worse than duplication — it couples "
        "unrelated concerns and makes extension fragile.",
        [
            "Functions with boolean `mode` flags that switch between unrelated behaviors.",
            "God Classes with dozens of methods spanning multiple responsibilities.",
            "Deep inheritance hierarchies where base classes know about leaf details.",
            "Circular dependencies between modules.",
        ],
    ),
    UniversalDogmaID.UNAMBIGUOUS_NAME: (
        "Clarity over clever shorthand.",
        "Names are the primary API for understanding code. Ambiguous or overly short "
        "identifiers force readers to trace definitions. For AI assistants consuming "
        "code via MCP, clear names reduce hallucination risk.",
        [
            "Single-letter variable names outside trivial loop counters.",
            "Abbreviations that save keystrokes but cost comprehension (`mgr`, `ctx`, `impl`).",
            "Naming style violations for the language (e.g., `camelCase` in Python).",
            "Inconsistent naming conventions across a project.",
        ],
    ),
    UniversalDogmaID.VISIBLE_STATE: (
        "Make mutation explicit and predictable.",
        "Hidden mutation — global state changes, in-place modifications without clear "
        "signals — is the leading cause of 'works on my machine' bugs. Visible state "
        "makes data flow traceable and diffs reviewable.",
        [
            "Mutating function arguments in place without documenting it.",
            "Global mutable singletons accessed from multiple modules.",
            "Implicit state changes through property setters that trigger side effects.",
            "Shadowing variables in nested scopes, creating ambiguity about which binding is alive.",
        ],
    ),
    UniversalDogmaID.STRICT_FENCES: (
        "Preserve encapsulation boundaries.",
        "Module and class boundaries exist to manage complexity. Breaking "
        "encapsulation — accessing private members, circular imports, leaking internal "
        "types — turns architecture diagrams into lies.",
        [
            "Accessing private/protected members from outside the owning module.",
            "Circular import dependencies between packages.",
            "Exposing internal implementation types in public APIs.",
            "Namespace pollution through wildcard re-exports.",
        ],
    ),
    UniversalDogmaID.RUTHLESS_DELETION: (
        "Remove dead and unreachable code.",
        "Dead code is technical debt with zero value. It misleads readers, inflates "
        "coverage metrics, and creates phantom dependencies. Version control preserves "
        "history — there is no reason to keep unused code in the working tree.",
        [
            "Commented-out code blocks left 'just in case.'",
            "Functions or classes that are defined but never called.",
            "Feature flags that are permanently off with no cleanup plan.",
            "Unreachable branches after an unconditional return.",
        ],
    ),
    UniversalDogmaID.PROPORTIONATE_COMPLEXITY: (
        "Choose the simplest design that works.",
        "Complexity must be justified by requirements, not by speculative generality. "
        "High cyclomatic complexity, long functions, and over-engineered abstractions "
        "all increase the cost of every future change.",
        [
            "Functions with cyclomatic complexity exceeding a configured threshold.",
            "Functions longer than a screen (configurable, default ~50 lines).",
            "Premature introduction of design patterns without a concrete need.",
            "Over-parameterized configurations when sensible defaults suffice.",
        ],
    ),
}

# Language key → docs filename mapping for cross-links
_LANGUAGE_DOC_FILES: dict[str, str] = {
    "python": "user-guide/languages/python.md",
    "typescript": "user-guide/languages/typescript.md",
    "rust": "user-guide/languages/rust.md",
    "go": "user-guide/languages/go.md",
    "javascript": "user-guide/languages/javascript.md",
    "css": "user-guide/languages/css.md",
    "bash": "user-guide/languages/bash.md",
    "powershell": "user-guide/languages/powershell.md",
    "ruby": "user-guide/languages/ruby.md",
    "sql": "user-guide/languages/sql.md",
    "cpp": "user-guide/languages/cpp.md",
    "csharp": "user-guide/languages/csharp.md",
    "docker_compose": "user-guide/languages/docker-compose.md",
    "dockerfile": "user-guide/languages/dockerfile.md",
    "terraform": "user-guide/languages/terraform.md",
    "markdown": "user-guide/languages/markdown.md",
    "latex": "user-guide/languages/latex.md",
    "github-actions": "user-guide/languages/github-actions.md",
    "gitlab_ci": "user-guide/languages/gitlab-ci.md",
    "json": "user-guide/languages/config-formats.md",
    "toml": "user-guide/languages/config-formats.md",
    "xml": "user-guide/languages/config-formats.md",
    "yaml": "user-guide/languages/config-formats.md",
}


def _load_zen(module_key: str):
    """Import LanguageZenPrinciples for a language."""
    # Normalize key for import (github-actions → github_actions)
    import_key = module_key.replace("-", "_")
    mod = importlib.import_module(
        f"mcp_zen_of_languages.languages.{import_key}.rules",
    )
    for attr in dir(mod):
        obj = getattr(mod, attr)
        if hasattr(obj, "principles") and hasattr(obj, "language"):
            return obj
    msg = f"No LanguageZenPrinciples found in {import_key}.rules"
    raise RuntimeError(msg)


def build_reverse_mapping() -> dict[str, list[tuple[str, str, str, int]]]:
    """Build dogma_id → list of (language_name, rule_id, principle, severity)."""
    mapping: dict[str, list[tuple[str, str, str, int]]] = defaultdict(list)

    for lang_key in sorted(get_all_languages()):
        zen = get_language_zen(lang_key)
        if not zen:
            continue
        display_name = _LANGUAGE_NAMES.get(lang_key, lang_key)
        for principle in zen.principles:
            dogmas = infer_dogmas_for_principle(principle)
            for dogma_id in dogmas:
                mapping[dogma_id].append(
                    (
                        display_name,
                        principle.id,
                        principle.principle,
                        principle.severity,
                    )
                )

    return dict(mapping)


def render_mapping(mapping: dict[str, list[tuple[str, str, str, int]]]) -> str:
    """Render the full dogma-mapping markdown snippet."""
    lines: list[str] = []

    for dogma in UniversalDogmaID:
        entries = mapping.get(dogma.value, [])
        if not entries:
            continue

        label = _DOGMA_LABELS[dogma]
        lines.append(f"### {label} — `{dogma.value}`")
        lines.append("")
        lines.append("| Language | Rule ID | Principle | Severity |")
        lines.append("|----------|---------|-----------|:--------:|")
        for lang_name, rule_id, principle_text, severity in entries:
            lines.append(
                f"| {lang_name} | `{rule_id}` | {principle_text} | {severity} |"
            )
        lines.append("")

    return "\n".join(lines).rstrip("\n") + "\n" if lines else ""


_DOGMA_SPEC_FRONTMATTER = """\
---
title: The 10 Dogmas of Zen
description: >-
  Ten universal cross-language rules that drive every detector
  and remediation prompt in mcp-zen-of-languages.
icon: material/gavel
tags:
  - Dogmas
  - Architecture
  - Quality
---
"""

_DOGMA_SPEC_INTRO = """\
# The 10 Dogmas of Zen

![The 10 Dogmas of Zen — ten stones in a zen garden representing the core code quality principles](../../assets/illustration-zen-dogma.svg)

`mcp-zen-of-languages` treats static analysis as **architectural coaching**, not just linting.
These 10 dogmas are universal, cross-language contracts — every language-specific rule and
every detector ultimately traces back to one of them.

!!! info "How this page is generated"
    This page is auto-generated by `scripts/generate_dogma_mapping.py` from the
    `UniversalDogmaID` enum in `src/mcp_zen_of_languages/core/universal_dogmas.py`.
    Do not edit it manually — run `uv run python scripts/generate_dogma_mapping.py` instead.

"""


def render_dogma_spec() -> str:
    """Render the full dogma-spec page for docs/user-guide/rules/the-ten-dogmas.md."""
    lines: list[str] = [_DOGMA_SPEC_FRONTMATTER, _DOGMA_SPEC_INTRO]

    for i, dogma in enumerate(UniversalDogmaID, start=1):
        label = _DOGMA_LABELS[dogma]
        quote, rationale, anti_patterns = _DOGMA_DETAIL[dogma]
        lines.append(f"## {i}. Dogma of {label} — `{dogma.value}`")
        lines.append("")
        lines.append(f"> {quote}")
        lines.append("")
        lines.append(f"**Rationale.** {rationale}")
        lines.append("")
        lines.append("**Anti-patterns:**")
        lines.append("")
        lines.extend(f"- {ap}" for ap in anti_patterns)
        lines.append("")
        lines.append("---")
        lines.append("")

    lines.append("## Cross-Language Rule Mapping")
    lines.append("")
    lines.append(
        "Each dogma is implemented by language-specific rules across the supported languages."
    )
    lines.append(
        "The tables below are **auto-generated** from the codebase's"
        " `infer_dogmas_for_principle()` mapping."
    )
    lines.append("")
    lines.append('--8<-- "docs/includes/generated/dogma-mapping.md"')
    lines.append("")
    lines.append("## See Also")
    lines.append("")
    lines.append(
        "- [Philosophy](../../getting-started/philosophy.md)"
        " — motivation and the architectural-coaching approach"
    )
    lines.append(
        "- [Architecture](../../contributing/architecture.md)"
        " — how dogmas drive detector and pipeline design"
    )
    lines.append(
        "- [Languages](../languages/index.md)"
        " — per-language principles derived from these dogmas"
    )
    lines.append(
        "- [Understanding Violations](../understanding-violations.md)"
        " — severity scores, worked examples, and the MCP workflow"
    )

    return "\n".join(lines).rstrip("\n") + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Generate dogma↔rule reverse-mapping docs snippets.",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Fail if generated snippet is stale.",
    )
    args = parser.parse_args()

    mapping = build_reverse_mapping()
    expected_outputs = {
        MAPPING_OUTPUT_PATH: render_mapping(mapping),
        DOGMA_SPEC_PATH: render_dogma_spec(),
    }

    if args.check:
        stale = False
        for output_path, expected in expected_outputs.items():
            if not output_path.exists():
                print(f"❌ {output_path}: generated output missing")
                stale = True
                continue
            current = output_path.read_text(encoding="utf-8")
            if current != expected:
                print(f"❌ {output_path}: stale generated output (run generator)")
                stale = True
        if stale:
            return 1
        print("✅ Dogma mapping checks passed")
        return 0

    for output_path, expected in expected_outputs.items():
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(expected, encoding="utf-8")
    total_rules = sum(len(v) for v in mapping.values())
    print(
        f"Generated dogma docs ({len(mapping)} dogmas,"
        f" {total_rules} rule links, {len(expected_outputs)} files)"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
