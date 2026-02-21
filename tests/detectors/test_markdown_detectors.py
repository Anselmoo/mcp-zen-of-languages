from __future__ import annotations

from mcp_zen_of_languages.analyzers.base import AnalysisContext
from mcp_zen_of_languages.languages.configs import (
    MarkdownAltTextConfig,
    MarkdownBareUrlConfig,
    MarkdownCodeFenceLanguageConfig,
    MarkdownFrontMatterConfig,
    MarkdownHeadingHierarchyConfig,
    MarkdownMdxImportHygieneConfig,
    MarkdownMdxNamedDefaultExportConfig,
)
from mcp_zen_of_languages.languages.markdown.detectors import (
    MarkdownAltTextDetector,
    MarkdownBareUrlDetector,
    MarkdownCodeFenceLanguageDetector,
    MarkdownFrontMatterDetector,
    MarkdownHeadingHierarchyDetector,
    MarkdownMdxImportHygieneDetector,
    MarkdownMdxNamedDefaultExportDetector,
    _extract_imported_identifiers,
    _parse_named_imports,
)


def _detect(detector, code: str, config, path: str | None = None):
    context = AnalysisContext(code=code, language="markdown", path=path)
    return detector.detect(context, config)


def test_markdown_heading_hierarchy_violation():
    code = "# Title\n\n### Skipped level\n"
    violations = _detect(
        MarkdownHeadingHierarchyDetector(),
        code,
        MarkdownHeadingHierarchyConfig(),
    )
    assert violations


def test_markdown_alt_text_violation():
    violations = _detect(
        MarkdownAltTextDetector(),
        "![ ](image.png)",
        MarkdownAltTextConfig(),
    )
    assert violations


def test_markdown_bare_url_violation():
    violations = _detect(
        MarkdownBareUrlDetector(),
        "See http://example.com for details.",
        MarkdownBareUrlConfig(),
    )
    assert violations


def test_markdown_code_fence_language_violation():
    violations = _detect(
        MarkdownCodeFenceLanguageDetector(),
        "```\nprint('hi')\n```",
        MarkdownCodeFenceLanguageConfig(),
    )
    assert violations


def test_markdown_code_fence_with_language_no_violation():
    violations = _detect(
        MarkdownCodeFenceLanguageDetector(),
        "```python\nprint('hi')\n```",
        MarkdownCodeFenceLanguageConfig(),
    )
    assert not violations


def test_markdown_frontmatter_missing_required_keys():
    violations = _detect(
        MarkdownFrontMatterDetector(),
        "---\ntitle: Doc\n---\n# Doc\n",
        MarkdownFrontMatterConfig(required_frontmatter_keys=["title", "description"]),
    )
    assert violations


def test_markdown_frontmatter_complete_no_violation():
    violations = _detect(
        MarkdownFrontMatterDetector(),
        "---\ntitle: Doc\ndescription: Desc\n---\n# Doc\n",
        MarkdownFrontMatterConfig(required_frontmatter_keys=["title", "description"]),
    )
    assert not violations


def test_mdx_unnamed_default_export_violation():
    violations = _detect(
        MarkdownMdxNamedDefaultExportDetector(),
        "export default function () {\n  return <div />\n}\n",
        MarkdownMdxNamedDefaultExportConfig(),
        path="page.mdx",
    )
    assert violations


def test_mdx_class_default_export_violation():
    violations = _detect(
        MarkdownMdxNamedDefaultExportDetector(),
        "export default class {\n}\n",
        MarkdownMdxNamedDefaultExportConfig(),
        path="page.mdx",
    )
    assert violations


def test_mdx_expression_default_export_violation():
    violations = _detect(
        MarkdownMdxNamedDefaultExportDetector(),
        "export default ({ title: 'doc' })\n",
        MarkdownMdxNamedDefaultExportConfig(),
        path="page.mdx",
    )
    assert violations


def test_mdx_default_export_detector_skips_plain_markdown():
    violations = _detect(
        MarkdownMdxNamedDefaultExportDetector(),
        "# Plain markdown\n",
        MarkdownMdxNamedDefaultExportConfig(),
        path="README.md",
    )
    assert not violations


def test_mdx_default_export_detector_ignores_fenced_export_in_markdown():
    code = "```js\nexport default function () {}\n```\n"
    violations = _detect(
        MarkdownMdxNamedDefaultExportDetector(),
        code,
        MarkdownMdxNamedDefaultExportConfig(),
        path="README.md",
    )
    assert not violations


def test_mdx_import_hygiene_violation():
    code = 'import Card from "./Card"\n\n# Docs\n\nText only.\n'
    violations = _detect(
        MarkdownMdxImportHygieneDetector(),
        code,
        MarkdownMdxImportHygieneConfig(),
        path="page.mdx",
    )
    assert violations


def test_mdx_import_hygiene_ignores_fenced_import_snippet():
    code = "```jsx\nimport Card from './Card'\n```\n# Docs\n"
    violations = _detect(
        MarkdownMdxImportHygieneDetector(),
        code,
        MarkdownMdxImportHygieneConfig(),
        path="README.md",
    )
    assert not violations


def test_mdx_import_hygiene_allows_used_and_side_effect_imports():
    code = 'import "./theme.css"\nimport Card, { Badge as Pill } from "./ui"\n\n<Card />\n<Pill />\n'
    violations = _detect(
        MarkdownMdxImportHygieneDetector(),
        code,
        MarkdownMdxImportHygieneConfig(),
        path="page.mdx",
    )
    assert not violations


def test_markdown_bare_url_detector_ignores_links_and_autolinks():
    violations = _detect(
        MarkdownBareUrlDetector(),
        "[Docs](https://example.com) and <https://example.org>",
        MarkdownBareUrlConfig(),
    )
    assert not violations


def test_markdown_bare_url_detector_ignores_inline_code_urls():
    violations = _detect(
        MarkdownBareUrlDetector(),
        "Use `http://example.com` in examples.",
        MarkdownBareUrlConfig(),
    )
    assert not violations


def test_import_identifier_parsers_cover_branches():
    assert _extract_imported_identifiers("{ Card as MyCard }") == {"MyCard"}
    assert _extract_imported_identifiers("* as UI") == {"UI"}
    assert _extract_imported_identifiers("Card, * as UI") == {"Card", "UI"}
    assert _extract_imported_identifiers("Card, { Badge }") == {"Card", "Badge"}
    assert _parse_named_imports("{ Foo as Bar, Baz }") == {"Bar", "Baz"}
