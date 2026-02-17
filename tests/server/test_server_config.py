from __future__ import annotations

import pytest

from mcp_zen_of_languages import server


@pytest.mark.asyncio
async def test_get_config_status():
    status = await server.get_config.fn()
    assert status.languages


@pytest.mark.asyncio
async def test_set_and_clear_config_override():
    status = await server.set_config_override.fn("python", max_cyclomatic_complexity=5)
    assert status.overrides_applied["python"]["max_cyclomatic_complexity"] == 5
    status = await server.clear_config_overrides.fn()
    assert "python" not in status.overrides_applied


@pytest.mark.asyncio
async def test_get_supported_languages():
    result = await server.get_supported_languages.fn()
    assert "python" in result
