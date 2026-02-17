from __future__ import annotations

import pytest

from mcp_zen_of_languages.analyzers.registry import DetectorRegistry
from mcp_zen_of_languages.languages.configs import LineLengthConfig


def test_registry_merge_configs_and_get():
    registry = DetectorRegistry()
    config = LineLengthConfig()
    merged = registry.merge_configs([config], [config])
    assert merged
    with pytest.raises(KeyError):
        registry.get("missing")
