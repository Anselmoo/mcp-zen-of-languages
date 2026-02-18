from __future__ import annotations

import logging
from pathlib import Path

import pytest

from mcp_zen_of_languages import server


@pytest.mark.asyncio
async def test_analyze_repository_unknown_lang_skips(tmp_path):
    file_path = tmp_path / "sample.unknown"
    file_path.write_text("data", encoding="utf-8")
    results = await server.analyze_repository.fn(
        str(tmp_path), ["unknown"], max_files=1
    )
    assert results


@pytest.mark.asyncio
async def test_analyze_repository_skips_non_files(tmp_path):
    (tmp_path / "dir").mkdir()
    results = await server.analyze_repository.fn(str(tmp_path), ["python"], max_files=1)
    assert results == []


@pytest.mark.asyncio
async def test_analyze_repository_surfaces_read_errors(tmp_path, monkeypatch, caplog):
    file_path = tmp_path / "broken.py"
    file_path.write_text("def foo():\n    pass\n", encoding="utf-8")
    original_read_text = Path.read_text

    def _broken_read_text(self: Path, *args, **kwargs):
        if self.name == "broken.py":
            msg = "cannot read file"
            raise OSError(msg)
        return original_read_text(self, *args, **kwargs)

    monkeypatch.setattr(Path, "read_text", _broken_read_text)
    with caplog.at_level(logging.WARNING):
        results = await server.analyze_repository.fn(
            str(tmp_path), ["python"], max_files=1
        )

    assert len(results) == 1
    assert results[0].result.violations
    assert results[0].result.violations[0].principle == "analysis.file_read_error"
    assert "cannot read file" in results[0].result.violations[0].message
    assert any("Failed to read" in message for message in caplog.messages)
