"""Tests for the analyze_batch and analyze_batch_summary MCP tools."""

from __future__ import annotations

import base64
import json

import pytest

from mcp_zen_of_languages import server
from mcp_zen_of_languages.models import AnalysisResult
from mcp_zen_of_languages.models import BatchPage
from mcp_zen_of_languages.models import BatchSummary
from mcp_zen_of_languages.models import CyclomaticSummary
from mcp_zen_of_languages.models import Metrics
from mcp_zen_of_languages.models import RepositoryAnalysis
from mcp_zen_of_languages.models import Violation
from mcp_zen_of_languages.server import _decode_cursor
from mcp_zen_of_languages.server import _encode_cursor
from mcp_zen_of_languages.server import _estimate_tokens


# ---------------------------------------------------------------------------
# Helper builders
# ---------------------------------------------------------------------------


def _make_result(
    path: str,
    language: str = "python",
    violations: list[Violation] | None = None,
    overall_score: float = 8.0,
) -> RepositoryAnalysis:
    return RepositoryAnalysis(
        path=path,
        language=language,
        result=AnalysisResult(
            language=language,
            path=path,
            metrics=Metrics(
                cyclomatic=CyclomaticSummary(blocks=[], average=0.0),
                maintainability_index=80.0,
                lines_of_code=10,
            ),
            violations=violations or [],
            overall_score=overall_score,
        ),
    )


# ---------------------------------------------------------------------------
# Unit tests for cursor helpers
# ---------------------------------------------------------------------------


def test_encode_decode_cursor_roundtrip():
    encoded = _encode_cursor(7, 3)
    file_idx, offset = _decode_cursor(encoded)
    assert file_idx == 7
    assert offset == 3


def test_encode_cursor_default_offset():
    encoded = _encode_cursor(5)
    file_idx, offset = _decode_cursor(encoded)
    assert file_idx == 5
    assert offset == 0


def test_decode_cursor_valid_base64():
    payload = base64.b64encode(json.dumps({"file": 10, "offset": 0}).encode()).decode()
    file_idx, offset = _decode_cursor(payload)
    assert file_idx == 10
    assert offset == 0


def test_decode_cursor_invalid_raises():
    with pytest.raises(ValueError, match="Invalid batch cursor"):
        _decode_cursor("not-valid-base64!!!!")


def test_estimate_tokens_basic():
    tokens = _estimate_tokens("hello world")
    assert tokens >= 1


def test_estimate_tokens_scales_with_length():
    short = _estimate_tokens("hi")
    long = _estimate_tokens("x" * 1000)
    assert long > short


# ---------------------------------------------------------------------------
# Unit tests for _build_batch_violations_list
# ---------------------------------------------------------------------------


def test_build_batch_violations_sorted_by_severity():
    results = [
        _make_result(
            "a.py",
            violations=[
                Violation(principle="low", severity=2, message="low"),
                Violation(principle="high", severity=9, message="high"),
            ],
        ),
        _make_result(
            "b.py",
            violations=[
                Violation(principle="mid", severity=5, message="mid"),
            ],
        ),
    ]
    violations = server._build_batch_violations_list(results)
    severities = [v.severity for v in violations]
    assert severities == sorted(severities, reverse=True)


def test_build_batch_violations_empty_results():
    violations = server._build_batch_violations_list([])
    assert violations == []


def test_build_batch_violations_carries_file_path():
    results = [
        _make_result(
            "src/foo.py",
            violations=[Violation(principle="p", severity=5, message="m")],
        )
    ]
    violations = server._build_batch_violations_list(results)
    assert violations[0].file == "src/foo.py"
    assert violations[0].language == "python"


# ---------------------------------------------------------------------------
# Integration tests for analyze_batch
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_analyze_batch_first_page_no_cursor(tmp_path, monkeypatch):
    """First call without a cursor returns page 1."""
    fake_results = [_make_result(str(tmp_path / "a.py"), violations=[])]
    monkeypatch.setattr(
        server,
        "_analyze_repository_internal",
        lambda *_a, **_kw: _async_return(fake_results),
    )
    page = await server.analyze_batch.fn(
        str(tmp_path), "python", cursor=None, max_tokens=8000
    )
    assert isinstance(page, BatchPage)
    assert page.page >= 1
    assert page.files_total == 1


@pytest.mark.asyncio
async def test_analyze_batch_no_violations_no_more(tmp_path, monkeypatch):
    """Empty violation list → has_more=False, cursor=None."""
    fake_results = [_make_result(str(tmp_path / "a.py"), violations=[])]
    monkeypatch.setattr(
        server,
        "_analyze_repository_internal",
        lambda *_a, **_kw: _async_return(fake_results),
    )
    page = await server.analyze_batch.fn(str(tmp_path), "python")
    assert page.has_more is False
    assert page.cursor is None


@pytest.mark.asyncio
async def test_analyze_batch_token_budget_enforced(tmp_path, monkeypatch):
    """Violations are truncated to respect max_tokens budget."""
    max_tokens = 500
    many_violations = [
        Violation(
            principle=f"p{i}",
            severity=5,
            message="x" * 500,  # large message to exhaust budget quickly
        )
        for i in range(50)
    ]
    fake_results = [_make_result(str(tmp_path / "a.py"), violations=many_violations)]
    monkeypatch.setattr(
        server,
        "_analyze_repository_internal",
        lambda *_a, **_kw: _async_return(fake_results),
    )
    page = await server.analyze_batch.fn(str(tmp_path), "python", max_tokens=max_tokens)
    # Should not include all 50 violations
    assert len(page.violations) < 50
    # Serialised payload must fit within the token budget
    tokens = server._estimate_tokens(json.dumps(page.model_dump()))
    assert tokens <= max_tokens


@pytest.mark.asyncio
async def test_analyze_batch_token_budget_oversized_single_violation(
    tmp_path, monkeypatch
):
    """A single violation too large for the budget is skipped, not included."""
    oversized = Violation(
        principle="oversized",
        severity=5,
        message="x" * 10000,  # extremely large message
    )
    fake_results = [_make_result(str(tmp_path / "a.py"), violations=[oversized])]
    monkeypatch.setattr(
        server,
        "_analyze_repository_internal",
        lambda *_a, **_kw: _async_return(fake_results),
    )
    max_tokens = 100
    page = await server.analyze_batch.fn(str(tmp_path), "python", max_tokens=max_tokens)
    # Oversized item must not be included (budget exceeded on first item)
    assert len(page.violations) == 0
    # Serialised payload must still fit within the token budget
    tokens = server._estimate_tokens(json.dumps(page.model_dump()))
    assert tokens <= max_tokens


@pytest.mark.asyncio
async def test_analyze_batch_cursor_pagination(tmp_path, monkeypatch):
    """Cursor from first page resumes at correct position."""
    violations = [
        Violation(principle=f"p{i}", severity=i + 1, message="x" * 400)
        for i in range(10)
    ]
    fake_results = [_make_result(str(tmp_path / "a.py"), violations=violations)]
    monkeypatch.setattr(
        server,
        "_analyze_repository_internal",
        lambda *_a, **_kw: _async_return(fake_results),
    )
    # Very small budget so we get pagination
    page1 = await server.analyze_batch.fn(str(tmp_path), "python", max_tokens=300)
    assert page1.has_more is True
    assert page1.cursor is not None

    page2 = await server.analyze_batch.fn(
        str(tmp_path), "python", cursor=page1.cursor, max_tokens=300
    )
    # The second page should not repeat violations from page 1
    p1_principles = {v.principle for v in page1.violations}
    p2_principles = {v.principle for v in page2.violations}
    assert p1_principles.isdisjoint(p2_principles)


@pytest.mark.asyncio
async def test_analyze_batch_violations_sorted_worst_first(tmp_path, monkeypatch):
    """Returned violations are sorted by severity descending."""
    violations = [
        Violation(principle="low", severity=2, message="m"),
        Violation(principle="high", severity=9, message="m"),
        Violation(principle="mid", severity=5, message="m"),
    ]
    fake_results = [_make_result(str(tmp_path / "a.py"), violations=violations)]
    monkeypatch.setattr(
        server,
        "_analyze_repository_internal",
        lambda *_a, **_kw: _async_return(fake_results),
    )
    page = await server.analyze_batch.fn(str(tmp_path), "python", max_tokens=8000)
    severities = [v.severity for v in page.violations]
    assert severities == sorted(severities, reverse=True)


@pytest.mark.asyncio
async def test_analyze_batch_invalid_cursor_raises(tmp_path, monkeypatch):
    fake_results: list[RepositoryAnalysis] = []
    monkeypatch.setattr(
        server,
        "_analyze_repository_internal",
        lambda *_a, **_kw: _async_return(fake_results),
    )
    with pytest.raises(ValueError, match="Invalid batch cursor"):
        await server.analyze_batch.fn(str(tmp_path), "python", cursor="!!!invalid!!!")


# ---------------------------------------------------------------------------
# Integration tests for analyze_batch_summary
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_analyze_batch_summary_basic(tmp_path, monkeypatch):
    fake_results = [
        _make_result(
            str(tmp_path / "a.py"),
            violations=[Violation(principle="p", severity=7, message="m")],
            overall_score=6.0,
        ),
        _make_result(str(tmp_path / "b.py"), violations=[], overall_score=9.0),
    ]
    monkeypatch.setattr(
        server,
        "_analyze_repository_internal",
        lambda *_a, **_kw: _async_return(fake_results),
    )
    summary = await server.analyze_batch_summary.fn(str(tmp_path), "python")
    assert isinstance(summary, BatchSummary)
    assert summary.total_files == 2
    assert summary.total_violations == 1
    assert 0 <= summary.health_score <= 100


@pytest.mark.asyncio
async def test_analyze_batch_summary_hotspots_limited_to_five(tmp_path, monkeypatch):
    """Hotspots list contains at most 5 entries."""
    fake_results = [
        _make_result(
            str(tmp_path / f"f{i}.py"),
            violations=[Violation(principle="p", severity=5, message="m")] * (i + 1),
        )
        for i in range(10)
    ]
    monkeypatch.setattr(
        server,
        "_analyze_repository_internal",
        lambda *_a, **_kw: _async_return(fake_results),
    )
    summary = await server.analyze_batch_summary.fn(str(tmp_path), "python")
    assert len(summary.hotspots) <= 5


@pytest.mark.asyncio
async def test_analyze_batch_summary_hotspots_ordered_by_violations(
    tmp_path, monkeypatch
):
    """Hotspots are ordered descending by violation count."""
    fake_results = [
        _make_result(
            str(tmp_path / "few.py"),
            violations=[Violation(principle="p", severity=3, message="m")],
        ),
        _make_result(
            str(tmp_path / "many.py"),
            violations=[Violation(principle="p", severity=3, message="m")] * 10,
        ),
    ]
    monkeypatch.setattr(
        server,
        "_analyze_repository_internal",
        lambda *_a, **_kw: _async_return(fake_results),
    )
    summary = await server.analyze_batch_summary.fn(str(tmp_path), "python")
    counts = [h.violations for h in summary.hotspots]
    assert counts == sorted(counts, reverse=True)


@pytest.mark.asyncio
async def test_analyze_batch_summary_empty_repo(tmp_path, monkeypatch):
    """Empty repository returns safe defaults."""
    monkeypatch.setattr(
        server,
        "_analyze_repository_internal",
        lambda *_a, **_kw: _async_return([]),
    )
    summary = await server.analyze_batch_summary.fn(str(tmp_path), "python")
    assert summary.total_files == 0
    assert summary.total_violations == 0
    assert summary.health_score == 100.0
    assert summary.hotspots == []


@pytest.mark.asyncio
async def test_analyze_batch_summary_health_score_range(tmp_path, monkeypatch):
    """Health score is between 0 and 100."""
    fake_results = [
        _make_result(str(tmp_path / "a.py"), overall_score=5.0),
    ]
    monkeypatch.setattr(
        server,
        "_analyze_repository_internal",
        lambda *_a, **_kw: _async_return(fake_results),
    )
    summary = await server.analyze_batch_summary.fn(str(tmp_path), "python")
    assert 0.0 <= summary.health_score <= 100.0


# ---------------------------------------------------------------------------
# Legacy compat shim test
# ---------------------------------------------------------------------------


def test_batch_tools_have_fn_attribute():
    """Both batch tools have the .fn attribute expected by tests."""
    assert hasattr(server.analyze_batch, "fn")
    assert hasattr(server.analyze_batch_summary, "fn")


# ---------------------------------------------------------------------------
# Async helper
# ---------------------------------------------------------------------------


async def _async_return(value):
    return value
