from __future__ import annotations

import pytest

from mcp_zen_of_languages import server

MAX_LINE_LENGTH_OVERRIDE = 100
RELAXED_COMPLEXITY_TARGET = 15


@pytest.mark.asyncio
async def test_get_config_and_overrides_round_trip():
    status = await server.get_config.fn()
    assert status.languages
    status = await server.set_config_override.fn(
        "python",
        max_line_length=MAX_LINE_LENGTH_OVERRIDE,
    )
    assert (
        status.overrides_applied["python"]["max_line_length"]
        == MAX_LINE_LENGTH_OVERRIDE
    )
    status = await server.clear_config_overrides.fn()
    assert "python" not in status.overrides_applied


@pytest.mark.asyncio
async def test_get_supported_languages_includes_python():
    langs = await server.get_supported_languages.fn()
    assert "python" in langs


@pytest.mark.asyncio
async def test_onboard_project_relaxed():
    guide = await server.onboard_project.fn(
        "/tmp/project",
        primary_language="python",
        team_size="small",
        strictness="relaxed",
    )
    assert (
        guide.recommended_config["max_cyclomatic_complexity"]
        == RELAXED_COMPLEXITY_TARGET
    )
