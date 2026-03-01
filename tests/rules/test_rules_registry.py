from mcp_zen_of_languages.rules import ZEN_REGISTRY
from mcp_zen_of_languages.rules import get_language_zen


def test_registry_contains_python():
    assert "python" in ZEN_REGISTRY
    python = get_language_zen("python")
    assert python is not None
    assert python.language == "python"
    assert python.principle_count > 0
