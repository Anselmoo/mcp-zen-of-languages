"""Pre-commit hook: validate docs CSS/JS quality gates.

Checks:
1. docs/stylesheets/extra.css is a valid modular manifest with @import entries
2. merged stylesheet content contains @media (prefers-reduced-motion)
3. merged stylesheet content contains :focus-visible styles
4. !important count does not exceed threshold (excluding @media print)
5. extra.js uses document$.subscribe() (not DOMContentLoaded)
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

# Paths relative to repo root
CSS_ROOT = Path("docs/stylesheets")
CSS_MANIFEST_PATH = CSS_ROOT / "extra.css"
JS_PATH = Path("docs/javascripts/extra.js")
README_PATH = Path("README.md")

README_REQUIRED_ASSET_BASES: tuple[str, ...] = (
    "docs/assets/logo",
    "docs/assets/social-card-github",
)

# Thresholds
MAX_IMPORTANT_COUNT = 4  # excluding @media print block and exempt files
IMPORT_RE = re.compile(r'@import\s+url\("(?P<path>[^"]+)"\);')

# Files where !important is structurally required (e.g. overriding
# third-party inline styles that cannot be beaten by specificity alone).
# Each entry maps the import path suffix to a human-readable justification
# so reviewers understand *why* the exemption exists.
IMPORTANT_EXEMPT_FILES: dict[str, str] = {
    "components/mermaid.css": "Mermaid.js renders SVG with inline style attrs; !important is the only CSS override mechanism",
}


def _strip_at_blocks(css: str, keyword: str) -> str:
    """Remove @media <keyword> { ... } blocks using brace counting."""
    result = css
    while True:
        match = re.search(rf"@media\s+{keyword}\s*\{{", result)
        if not match:
            break
        depth = 0
        for i in range(match.end() - 1, len(result)):
            if result[i] == "{":
                depth += 1
            elif result[i] == "}":
                depth -= 1
            if depth == 0:
                result = result[: match.start()] + result[i + 1 :]
                break
    return result


def _load_manifest_css(
    manifest_css: str,
) -> tuple[list[tuple[str, str]], list[str]]:
    """Load CSS sources referenced by the manifest.

    Returns ([(relative_import, css_text), ...], errors).
    """
    errors: list[str] = []
    imports = [m.group("path") for m in IMPORT_RE.finditer(manifest_css)]
    if not imports:
        errors.append(f"{CSS_MANIFEST_PATH}: missing @import entries")
        return [], errors

    merged: list[tuple[str, str]] = []
    for relative_import in imports:
        import_path = CSS_ROOT / relative_import
        if not import_path.exists():
            errors.append(
                f"{CSS_MANIFEST_PATH}: import target not found: {import_path.as_posix()}"
            )
            continue
        merged.append((relative_import, import_path.read_text(encoding="utf-8")))

    return merged, errors


def check_css(css_manifest: str) -> list[str]:
    """Validate modular CSS quality gates."""
    errors: list[str] = []
    merged_css_pairs, errors_from_manifest = _load_manifest_css(css_manifest)
    errors.extend(errors_from_manifest)
    css = "\n".join(text for _, text in merged_css_pairs)

    if "prefers-reduced-motion" not in css:
        errors.append(
            f"{CSS_ROOT}: missing @media (prefers-reduced-motion) section "
            "(expected in utilities/motion.css)"
        )

    if ":focus-visible" not in css:
        errors.append(
            f"{CSS_ROOT}: missing :focus-visible styles "
            "(expected in utilities/focus.css)"
        )

    # Count !important outside @media print blocks, excluding exempt files
    # (e.g. mermaid.css needs !important to override inline SVG styles).
    non_exempt_css = "\n".join(
        text for path, text in merged_css_pairs if path not in IMPORTANT_EXEMPT_FILES
    )
    css_no_print = _strip_at_blocks(non_exempt_css, "print")
    important_count = css_no_print.count("!important")
    if important_count > MAX_IMPORTANT_COUNT:
        errors.append(
            f"{CSS_ROOT}: {important_count} !important declarations "
            f"(max {MAX_IMPORTANT_COUNT}, excluding @media print and exempt files)"
        )

    return errors


def check_js(js: str) -> list[str]:
    """Validate JS quality gates."""
    errors: list[str] = []

    if "document$.subscribe" not in js:
        errors.append(
            f"{JS_PATH}: must use document$.subscribe() "
            f"(not DOMContentLoaded) for instant navigation compatibility"
        )

    if "DOMContentLoaded" in js:
        errors.append(
            f"{JS_PATH}: uses DOMContentLoaded — "
            f"breaks with navigation.instant; use document$.subscribe()"
        )

    return errors


def check_readme_assets(readme_content: str) -> list[str]:
    """Validate README hero/logo asset references and file existence."""
    errors: list[str] = []

    for asset_base in README_REQUIRED_ASSET_BASES:
        png_path = f"{asset_base}.png"
        svg_path = f"{asset_base}.svg"
        if png_path not in readme_content and svg_path not in readme_content:
            errors.append(
                f"{README_PATH}: missing asset reference for '{asset_base}' "
                f"(expected .png or .svg)"
            )
        if not Path(png_path).exists() and not Path(svg_path).exists():
            errors.append(
                f"{README_PATH}: referenced asset missing for '{asset_base}' "
                f"(expected .png or .svg file)"
            )

    return errors


def main() -> int:
    errors: list[str] = []

    if CSS_MANIFEST_PATH.exists():
        errors.extend(check_css(CSS_MANIFEST_PATH.read_text(encoding="utf-8")))
    else:
        errors.append(f"{CSS_MANIFEST_PATH}: file not found")

    if JS_PATH.exists():
        errors.extend(check_js(JS_PATH.read_text()))
    else:
        errors.append(f"{JS_PATH}: file not found")

    if README_PATH.exists():
        errors.extend(check_readme_assets(README_PATH.read_text(encoding="utf-8")))
    else:
        errors.append(f"{README_PATH}: file not found")

    if errors:
        print("❌ Docs asset quality checks failed:")
        for err in errors:
            print(f"  • {err}")
        return 1

    print("✅ Docs asset quality checks passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
