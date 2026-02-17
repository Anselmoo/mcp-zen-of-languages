from __future__ import annotations

from mcp_zen_of_languages.analyzers.analyzer_factory import create_analyzer


def test_create_analyzer_types():
    python = create_analyzer("python")
    assert python.language() == "python"
    rust = create_analyzer("rust")
    assert rust.language() == "rust"
    json = create_analyzer("json")
    assert json.language() == "json"
    xml = create_analyzer("xml")
    assert xml.language() == "xml"
