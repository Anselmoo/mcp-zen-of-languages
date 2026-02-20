"""Pre-commit hook: enforce baseline hyperlink coverage in docs."""

from __future__ import annotations

import re
import sys
from pathlib import Path

DOCS_ROOT = Path("docs")
MKDOCS_CONFIG = Path("mkdocs.yml")
LANGUAGE_DOCS = DOCS_ROOT / "user-guide" / "languages"
KEY_DOC_PAGES = [
    DOCS_ROOT / "getting-started" / "index.md",
    DOCS_ROOT / "user-guide" / "index.md",
    DOCS_ROOT / "api" / "index.md",
    DOCS_ROOT / "contributing" / "index.md",
]

MARKDOWN_LINK_RE = re.compile(r"\[[^\]]+\]\(([^)]+)\)")
EXTERNAL_SCHEMES = ("http://", "https://", "mailto:")
SOURCE_PROVENANCE_SECTION_RE = re.compile(
    r"^##\s+Source Provenance\b(.*?)(?=^##\s+|\Z)",
    re.MULTILINE | re.DOTALL,
)

MIN_INTERNAL_LINKS = 3


def _count_links(text: str) -> tuple[int, int]:
    links = MARKDOWN_LINK_RE.findall(text)
    external = sum(link.startswith(EXTERNAL_SCHEMES) for link in links)
    internal = len(links) - external
    return internal, external


def _check_key_pages(errors: list[str]) -> None:
    for page in KEY_DOC_PAGES:
        if not page.exists():
            errors.append(f"{page}: missing required key docs page")
            continue
        text = page.read_text(encoding="utf-8")
        if "## See Also" not in text:
            errors.append(f"{page}: missing '## See Also' section")
        internal, _external = _count_links(text)
        if internal < MIN_INTERNAL_LINKS:
            errors.append(
                f"{page}: expected at least 3 internal markdown links, found {internal}",
            )


def _check_language_pages(errors: list[str]) -> None:
    for page in sorted(LANGUAGE_DOCS.glob("*.md")):
        if page.name in {"index.md", "config-formats.md"}:
            continue
        text = page.read_text(encoding="utf-8")
        has_legacy_pattern = "drawn from [" in text
        section_match = SOURCE_PROVENANCE_SECTION_RE.search(text)
        section_external_links = 0
        if section_match:
            _internal, section_external_links = _count_links(section_match.group(1))
        has_provenance = has_legacy_pattern or section_external_links >= 1
        if not has_provenance:
            errors.append(
                f"{page}: missing linked source provenance in Zen Principles section",
            )
        _internal, external = _count_links(text)
        if external < 1:
            errors.append(
                f"{page}: expected at least one external markdown link, found {external}",
            )


def _check_mkdocs_magiclink(errors: list[str]) -> None:
    if not MKDOCS_CONFIG.exists():
        errors.append(f"{MKDOCS_CONFIG}: file not found")
        return
    text = MKDOCS_CONFIG.read_text(encoding="utf-8")
    if "pymdownx.magiclink" not in text:
        errors.append(
            f"{MKDOCS_CONFIG}: missing pymdownx.magiclink markdown extension config",
        )


def main() -> int:
    errors: list[str] = []

    _check_key_pages(errors)
    _check_language_pages(errors)
    _check_mkdocs_magiclink(errors)

    if errors:
        print("❌ Docs hyperlink checks failed:")
        for error in errors:
            print(f"  • {error}")
        return 1

    print("✅ Docs hyperlink checks passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
