from __future__ import annotations

import asyncio

from mcp_zen_of_languages.server import (
    analyze_repository,
    detect_languages,
    generate_report_tool,
)


def test_server_detect_languages(tmp_path):
    sample = tmp_path / "sample.py"
    sample.write_text("def foo():\n    pass\n", encoding="utf-8")
    result = asyncio.run(detect_languages.fn(repo_path=str(sample)))
    assert "python" in result.languages


def test_server_analyze_repository_other_language(tmp_path):
    sample = tmp_path / "sample.py"
    sample.write_text("def foo():\n    pass\n", encoding="utf-8")
    result = asyncio.run(
        analyze_repository.fn(
            repo_path=str(tmp_path), languages=["kotlin"], max_files=1
        )
    )
    assert result == []


def test_server_analyze_repository_unknown_files(tmp_path):
    (tmp_path / "sample.txt").write_text("text", encoding="utf-8")
    result = asyncio.run(
        analyze_repository.fn(
            repo_path=str(tmp_path), languages=["unknown"], max_files=1
        )
    )
    assert result


def test_server_generate_report_tool(tmp_path):
    sample = tmp_path / "sample.py"
    sample.write_text("def foo():\n    pass\n", encoding="utf-8")
    report = asyncio.run(generate_report_tool.fn(target_path=str(sample)))
    assert report.markdown.startswith("# Zen of Languages Report")
