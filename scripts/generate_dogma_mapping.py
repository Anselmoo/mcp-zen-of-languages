"""Generate dogma↔language-rule reverse-mapping snippets for docs.

Run::

    uv run python scripts/generate_dogma_mapping.py          # write files
    uv run python scripts/generate_dogma_mapping.py --check  # CI dry-run

The script imports all language zen principles and uses
``infer_dogmas_for_principle()`` to build a reverse mapping from each
of the 10 universal dogmas to the language-specific rules that implement
them.  Output is written to ``docs/includes/generated/dogma-mapping.md``.
"""

from __future__ import annotations

import argparse
import importlib
import sys
from collections import defaultdict
from pathlib import Path

from mcp_zen_of_languages.core.universal_dogmas import (
    UniversalDogmaID,
    infer_dogmas_for_principle,
)
from mcp_zen_of_languages.rules import get_all_languages, get_language_zen

OUTPUT_PATH = Path("docs/includes/generated/dogma-mapping.md")

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
    expected = render_mapping(mapping)

    if args.check:
        if not OUTPUT_PATH.exists():
            print(f"❌ {OUTPUT_PATH}: generated dogma mapping missing")
            return 1
        current = OUTPUT_PATH.read_text(encoding="utf-8")
        if current != expected:
            print(f"❌ {OUTPUT_PATH}: stale dogma mapping (run generator)")
            return 1
        print("✅ Dogma mapping checks passed")
        return 0

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(expected, encoding="utf-8")
    total_rules = sum(len(v) for v in mapping.values())
    print(f"Generated dogma mapping ({len(mapping)} dogmas, {total_rules} rule links)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
