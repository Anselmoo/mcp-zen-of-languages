from __future__ import annotations

import pytest

from mcp_zen_of_languages import server


@pytest.mark.asyncio
async def test_analyze_zen_violations_rust():
    result = await server.analyze_zen_violations.fn("fn main() {}", "rust")
    assert result.language == "rust"


@pytest.mark.asyncio
async def test_analyze_zen_violations_go():
    result = await server.analyze_zen_violations.fn(
        "package main\nfunc main() {}",
        "go",
    )
    assert result.language == "go"


@pytest.mark.asyncio
async def test_analyze_repository_limits_files(tmp_path):
    (tmp_path / "one.py").write_text("def foo():\n    pass\n", encoding="utf-8")
    (tmp_path / "two.py").write_text("def bar():\n    pass\n", encoding="utf-8")
    results = await server.analyze_repository.fn(str(tmp_path), ["python"], max_files=1)
    assert len(results) == 1


@pytest.mark.asyncio
async def test_check_architectural_patterns_empty():
    result = await server.check_architectural_patterns.fn("", "python")
    assert result.patterns == []


@pytest.mark.asyncio
async def test_check_architectural_patterns_singleton():
    code = (
        "class Config:\n"
        "    _instance = None\n"
        "    @classmethod\n"
        "    def get_instance(cls): return cls._instance\n"
    )
    result = await server.check_architectural_patterns.fn(code, "python")
    names = [f.name for f in result.patterns]
    assert "singleton" in names


@pytest.mark.asyncio
async def test_check_architectural_patterns_observer_js():
    code = "element.addEventListener('click', fn);\nelement.removeEventListener('click', fn);\n"
    result = await server.check_architectural_patterns.fn(code, "javascript")
    names = [f.name for f in result.patterns]
    assert "observer" in names
