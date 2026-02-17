from __future__ import annotations

from mcp_zen_of_languages.utils.language_detection import (
    detect_language_from_content,
)


def test_language_detector_ruby_branch():
    result = detect_language_from_content("end\n")
    assert result.language == "unknown"
