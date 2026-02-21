"""Generate and validate implementation coverage counts for critical docs sections."""

from __future__ import annotations

import argparse
import importlib
import json
import re
import sys
from dataclasses import asdict, dataclass
from pathlib import Path

from mcp_zen_of_languages.rules import get_language_zen

README_PATH = Path("README.md")
DOCS_INDEX_PATH = Path("docs/index.md")
LANGUAGES_INDEX_PATH = Path("docs/user-guide/languages/index.md")
HOME_TEMPLATE_PATH = Path("docs/overrides/main.html")
COUNTS_MD_PATH = Path("docs/includes/generated/implementation-counts.md")
COUNTS_JSON_PATH = Path("docs/includes/generated/implementation-counts.json")

README_START_MARKER = "<!-- --8<-- [start:what-you-get] -->"
README_END_MARKER = "<!-- --8<-- [end:what-you-get] -->"
README_BLOCK_RE = re.compile(
    rf"({re.escape(README_START_MARKER)}\n\n)(.*?)(\n{re.escape(README_END_MARKER)})",
    re.DOTALL,
)

PROGRAMMING_LANGUAGES: list[tuple[str, str]] = [
    ("python", "python"),
    ("typescript", "typescript"),
    ("rust", "rust"),
    ("go", "go"),
    ("javascript", "javascript"),
    ("css", "css"),
    ("bash", "bash"),
    ("powershell", "powershell"),
    ("ruby", "ruby"),
    ("cpp", "cpp"),
    ("csharp", "csharp"),
    ("docker_compose", "docker_compose"),
    ("dockerfile", "dockerfile"),
    ("markdown", "markdown"),
]
WORKFLOW_LANGUAGES: list[tuple[str, str]] = [("github_actions", "github-actions")]
CONFIG_LANGUAGES: list[tuple[str, str]] = [
    ("json", "json"),
    ("toml", "toml"),
    ("xml", "xml"),
    ("yaml", "yaml"),
]

STATIC_WHAT_YOU_GET_LINES = [
    "- **MCP server** for IDE and agent workflows (13 tools, 3 resources, 1 prompt)",
    "- **CLI reports** with remediation prompts and JSON / Markdown export",
    "- **Rule-driven pipelines** configurable per language and project",
]


@dataclass(slots=True)
class CoverageCounts:
    """Coverage counters used in generated docs claims and validation checks."""

    programming_principles: int
    programming_detectors: int
    workflow_principles: int
    workflow_checks: int
    config_principles: int
    config_detectors: int
    total_principles: int
    total_coverage_points: int


def _count_principles(language_key: str) -> int:
    zen = get_language_zen(language_key)
    if not zen:
        msg = f"Unsupported language in count generation: {language_key}"
        raise ValueError(msg)
    return len(zen.principles)


def _count_detectors(module_key: str) -> int:
    mapping_module = importlib.import_module(
        f"mcp_zen_of_languages.languages.{module_key}.mapping",
    )
    return len(
        {
            binding.detector_class.__name__
            for binding in mapping_module.DETECTOR_MAP.bindings
            if binding.detector_id != "analyzer_defaults"
        },
    )


def compute_counts() -> CoverageCounts:
    """Calculate live coverage counts from rule and detector mappings."""
    programming_principles = sum(
        _count_principles(language_key) for _, language_key in PROGRAMMING_LANGUAGES
    )
    programming_detectors = sum(
        _count_detectors(module_key) for module_key, _ in PROGRAMMING_LANGUAGES
    )

    workflow_principles = sum(
        _count_principles(language_key) for _, language_key in WORKFLOW_LANGUAGES
    )
    # Workflow automation coverage is represented as rule-level checks.
    workflow_checks = workflow_principles

    config_principles = sum(
        _count_principles(language_key) for _, language_key in CONFIG_LANGUAGES
    )
    config_detectors = sum(
        _count_detectors(module_key) for module_key, _ in CONFIG_LANGUAGES
    )

    total_principles = programming_principles + workflow_principles + config_principles
    total_coverage_points = programming_detectors + workflow_checks + config_detectors

    return CoverageCounts(
        programming_principles=programming_principles,
        programming_detectors=programming_detectors,
        workflow_principles=workflow_principles,
        workflow_checks=workflow_checks,
        config_principles=config_principles,
        config_detectors=config_detectors,
        total_principles=total_principles,
        total_coverage_points=total_coverage_points,
    )


def _render_counts_bullets(counts: CoverageCounts) -> list[str]:
    return [
        (
            f"- **{counts.total_principles} zen principles** across programming, "
            "workflow, and config domains"
        ),
        (
            f"- **{counts.total_coverage_points} detector/check coverage points** "
            "with severity scoring"
        ),
    ]


def _render_generated_counts_snippet(counts: CoverageCounts) -> str:
    return "\n".join(_render_counts_bullets(counts)) + "\n"


def _render_readme_block_content(counts: CoverageCounts) -> str:
    lines = [*_render_counts_bullets(counts), *STATIC_WHAT_YOU_GET_LINES]
    return "\n".join(lines)


def _sync_readme_counts_block(readme_text: str, counts: CoverageCounts) -> str:
    replacement = rf"\1{_render_readme_block_content(counts)}\3"
    updated, matched = README_BLOCK_RE.subn(replacement, readme_text, count=1)
    if matched != 1:
        msg = "README what-you-get marker block not found or duplicated."
        raise ValueError(msg)
    return updated


def _validate_language_index_totals(counts: CoverageCounts, errors: list[str]) -> None:
    text = LANGUAGES_INDEX_PATH.read_text(encoding="utf-8")
    principles_match = re.search(
        r"- \*\*Principles \(all categories\):\*\* (\d+)",
        text,
    )
    coverage_match = re.search(
        r"- \*\*Detectors \+ workflow checks:\*\* (\d+)",
        text,
    )
    if not principles_match or not coverage_match:
        errors.append(
            f"{LANGUAGES_INDEX_PATH}: missing coverage total lines generated by language docs",
        )
        return
    if int(principles_match.group(1)) != counts.total_principles:
        errors.append(
            f"{LANGUAGES_INDEX_PATH}: principles total mismatch (expected {counts.total_principles})",
        )
    if int(coverage_match.group(1)) != counts.total_coverage_points:
        errors.append(
            f"{LANGUAGES_INDEX_PATH}: coverage total mismatch (expected {counts.total_coverage_points})",
        )


def _validate_docs_index_surface(errors: list[str]) -> None:
    text = DOCS_INDEX_PATH.read_text(encoding="utf-8")
    include_line = '--8<-- "README.md:what-you-get"'
    if include_line not in text:
        errors.append(
            f"{DOCS_INDEX_PATH}: missing required include for README what-you-get block",
        )


def _validate_home_surface(errors: list[str]) -> None:
    text = HOME_TEMPLATE_PATH.read_text(encoding="utf-8")
    if "14+ languages" in text:
        errors.append(
            f"{HOME_TEMPLATE_PATH}: stale hardcoded language count found ('14+ languages')",
        )


def _run_check_mode(counts: CoverageCounts) -> int:
    errors: list[str] = []

    expected_snippet = _render_generated_counts_snippet(counts)
    if not COUNTS_MD_PATH.exists():
        errors.append(f"{COUNTS_MD_PATH}: generated counts snippet missing")
    elif COUNTS_MD_PATH.read_text(encoding="utf-8") != expected_snippet:
        errors.append(
            f"{COUNTS_MD_PATH}: stale generated counts snippet (run generator)",
        )

    expected_json = json.dumps(asdict(counts), indent=2, sort_keys=True) + "\n"
    if not COUNTS_JSON_PATH.exists():
        errors.append(f"{COUNTS_JSON_PATH}: generated counts json missing")
    elif COUNTS_JSON_PATH.read_text(encoding="utf-8") != expected_json:
        errors.append(
            f"{COUNTS_JSON_PATH}: stale generated counts json (run generator)"
        )

    readme_text = README_PATH.read_text(encoding="utf-8")
    try:
        expected_readme = _sync_readme_counts_block(readme_text, counts)
    except ValueError as exc:
        errors.append(f"{README_PATH}: {exc}")
    else:
        if expected_readme != readme_text:
            errors.append(
                f"{README_PATH}: what-you-get count section is stale (run generator)",
            )

    _validate_language_index_totals(counts, errors)
    _validate_docs_index_surface(errors)
    _validate_home_surface(errors)

    if errors:
        print("❌ Implementation count checks failed:")
        for error in errors:
            print(f"  • {error}")
        return 1

    print("✅ Implementation count checks passed")
    return 0


def _run_generate_mode(counts: CoverageCounts) -> int:
    COUNTS_MD_PATH.parent.mkdir(parents=True, exist_ok=True)
    COUNTS_MD_PATH.write_text(
        _render_generated_counts_snippet(counts), encoding="utf-8"
    )
    COUNTS_JSON_PATH.write_text(
        json.dumps(asdict(counts), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    readme_text = README_PATH.read_text(encoding="utf-8")
    updated_readme = _sync_readme_counts_block(readme_text, counts)
    README_PATH.write_text(updated_readme, encoding="utf-8")

    print(
        "Generated implementation counts "
        f"(principles={counts.total_principles}, "
        f"coverage={counts.total_coverage_points})",
    )
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Generate and validate implementation coverage counts for docs surfaces.",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Fail if generated counts artifacts and critical docs sections are stale.",
    )
    args = parser.parse_args()

    counts = compute_counts()
    return _run_check_mode(counts) if args.check else _run_generate_mode(counts)


if __name__ == "__main__":
    sys.exit(main())
