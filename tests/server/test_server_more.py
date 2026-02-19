from __future__ import annotations

import pytest

from mcp_zen_of_languages import server


@pytest.mark.asyncio
async def test_analyze_repository_unknown_language(tmp_path):
    file_path = tmp_path / "sample.unknown"
    file_path.write_text("data", encoding="utf-8")
    results = await server.analyze_repository.fn(
        str(tmp_path),
        ["unknown"],
        max_files=1,
    )
    assert results
    assert results[0].language == "unknown"


@pytest.mark.asyncio
async def test_analyze_repository_typescript(tmp_path):
    file_path = tmp_path / "sample.ts"
    file_path.write_text("interface Foo {}", encoding="utf-8")
    results = await server.analyze_repository.fn(
        str(tmp_path),
        ["typescript"],
        max_files=1,
    )
    assert results


@pytest.mark.asyncio
async def test_analyze_repository_go(tmp_path):
    file_path = tmp_path / "sample.go"
    file_path.write_text("package main\nfunc main() {}", encoding="utf-8")
    results = await server.analyze_repository.fn(str(tmp_path), ["go"], max_files=1)
    assert results
