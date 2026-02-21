from __future__ import annotations

from mcp_zen_of_languages.analyzers.analyzer_factory import create_analyzer


def test_markdown_and_mdx_analyze_end_to_end():
    markdown_result = create_analyzer("markdown").analyze(
        "# Title\n\n### Skipped\n\nSee http://example.com",
        path="README.md",
    )
    assert markdown_result.language == "markdown"
    assert markdown_result.violations

    mdx_result = create_analyzer("mdx").analyze(
        'import Card from "./Card"\n\n# Title\n\nexport default function () { return <Card /> }\n',
        path="page.mdx",
    )
    assert mdx_result.language == "markdown"
    assert mdx_result.violations
