from __future__ import annotations

import importlib
import sys
from io import StringIO

from rich.console import Console
from rich.panel import Panel
from rich.progress import MofNCompleteColumn
from rich.table import Table

from mcp_zen_of_languages import __version__
from mcp_zen_of_languages.rendering import progress as progress_module
from mcp_zen_of_languages.rendering.console import (
    get_banner_art,
    print_banner,
    print_error,
    set_quiet,
)
from mcp_zen_of_languages.rendering.layout import MAX_OUTPUT_WIDTH, get_output_width
from mcp_zen_of_languages.rendering.panels import (
    build_project_summary_panel,
    build_worst_offenders_panel,
)
from mcp_zen_of_languages.rendering.progress import analysis_progress
from mcp_zen_of_languages.rendering.tables import build_violation_table
from mcp_zen_of_languages.rendering.themes import (
    BOX_BANNER,
    BOX_CONTENT,
    BOX_SUMMARY,
    ZEN_THEME,
    file_glyph,
    pass_fail_glyph,
    score_glyph,
    severity_badge,
    severity_style,
)


def test_severity_style_and_badge():
    assert severity_style(9) == "severity.critical"
    assert severity_style(7) == "severity.high"
    assert severity_style(4) == "severity.medium"
    assert severity_style(1) == "severity.low"
    badge = severity_badge(9)
    assert "CRIT" in badge
    assert any(symbol in badge for symbol in ("🔴", "●"))


def test_build_violation_table_title():
    location = type("Loc", (), {"line": 1, "column": 2})
    violation = type(
        "Violation",
        (),
        {"severity": 7, "principle": "P", "message": "Msg", "location": location},
    )
    table = build_violation_table([violation], "sample.py")
    assert isinstance(table, Table)
    assert table.title == "Violations - sample.py"
    assert table.box == BOX_CONTENT


def test_build_project_summary_panel():
    summary = type(
        "Summary",
        (),
        {
            "total_files": 2,
            "total_violations": 5,
            "critical": 1,
            "high": 2,
            "medium": 1,
            "low": 1,
        },
    )
    panel = build_project_summary_panel(summary)
    assert isinstance(panel, Panel)
    assert panel.title == "Project Summary"
    assert panel.box == BOX_SUMMARY


def test_build_worst_offenders_panel():
    offender = type("Offender", (), {"path": "sample.py", "violation_count": 3})
    panel = build_worst_offenders_panel([offender])
    assert isinstance(panel, Panel)
    assert panel.box == BOX_CONTENT


def test_build_worst_offenders_panel_empty():
    panel = build_worst_offenders_panel([])
    assert panel.renderable.row_count == 1


def test_status_glyphs():
    assert pass_fail_glyph(passed=True) in {"✅", "[OK]"}
    assert pass_fail_glyph(passed=False) in {"❌", "[FAIL]"}
    assert file_glyph() in {"📄", "-"}
    assert score_glyph() in {"⭐", "*"}


def test_get_output_width_is_capped():
    test_console = Console(width=200, force_terminal=True)
    assert get_output_width(test_console) == MAX_OUTPUT_WIDTH


def test_print_error_writes_to_stderr(capsys):
    print_error("boom")
    captured = capsys.readouterr()
    assert "boom" in captured.err


class _DummyStream:
    def __init__(self, *, isatty: bool) -> None:
        self._isatty = isatty

    def isatty(self) -> bool:
        return self._isatty


def test_supports_color_respects_no_color(monkeypatch):
    monkeypatch.setenv("NO_COLOR", "1")
    monkeypatch.setenv("TERM", "xterm")
    console_module = importlib.import_module("mcp_zen_of_languages.rendering.console")
    assert console_module._supports_color(_DummyStream(isatty=True)) is False


def test_supports_color_respects_dumb_terminal(monkeypatch):
    monkeypatch.delenv("NO_COLOR", raising=False)
    monkeypatch.setenv("TERM", "dumb")
    console_module = importlib.import_module("mcp_zen_of_languages.rendering.console")
    assert console_module._supports_color(_DummyStream(isatty=True)) is False


def test_supports_color_enabled(monkeypatch):
    monkeypatch.delenv("NO_COLOR", raising=False)
    monkeypatch.setenv("TERM", "xterm")
    console_module = importlib.import_module("mcp_zen_of_languages.rendering.console")
    assert console_module._supports_color(_DummyStream(isatty=True)) is True


def test_severity_badge_fallback(monkeypatch):
    from mcp_zen_of_languages.rendering import themes

    monkeypatch.setattr(themes, "_use_emoji", lambda: False)
    assert "●" in themes.severity_badge(9)
    assert "▲" in themes.severity_badge(7)
    assert "◆" in themes.severity_badge(4)
    assert "○" in themes.severity_badge(1)
    assert "[OK]" in themes.pass_fail_glyph(passed=True)


def test_analysis_progress_yields_progress(monkeypatch):
    set_quiet(value=False)
    monkeypatch.setattr(sys.stdout, "isatty", lambda: True)
    test_console = Console(force_terminal=True)
    monkeypatch.setattr(progress_module, "console", test_console)
    with analysis_progress(enabled=True) as progress:
        assert progress is not None
        assert any(
            isinstance(column, MofNCompleteColumn) for column in progress.columns
        )


def test_print_banner_outputs(monkeypatch, capsys):
    set_quiet(value=False)
    monkeypatch.setattr(sys.stdout, "isatty", lambda: True)
    print_banner()
    captured = capsys.readouterr()
    assert f"v{__version__}" in captured.out
    assert ("of Languages" in captured.out) or ("********" in captured.out)


def test_print_banner_snapshot(monkeypatch):
    set_quiet(value=False)
    monkeypatch.setattr(sys.stdout, "isatty", lambda: True)
    console_module = importlib.import_module("mcp_zen_of_languages.rendering.console")
    monkeypatch.setattr(console_module, "_render_banner_art", lambda: "ZEN")
    buffer = StringIO()
    capture_console = Console(
        file=buffer, width=40, force_terminal=True, no_color=True, theme=ZEN_THEME
    )
    print_banner(output_console=capture_console)
    output = buffer.getvalue()
    assert "ZEN" in output
    assert f"v{__version__}" in output
    assert "╔" in output


def test_get_banner_art_uses_pyfiglet(monkeypatch):
    console_module = importlib.import_module("mcp_zen_of_languages.rendering.console")

    class _FakePyfiglet:
        @staticmethod
        def figlet_format(*_args, **_kwargs):
            return "ZEN\n"

    monkeypatch.setattr(console_module, "import_module", lambda _name: _FakePyfiglet)
    art = get_banner_art()
    assert "ZEN" in art
    assert "of Languages" in art


def test_get_banner_art_falls_back_when_pyfiglet_errors(monkeypatch):
    console_module = importlib.import_module("mcp_zen_of_languages.rendering.console")
    monkeypatch.setattr(
        console_module,
        "import_module",
        lambda _name: (_ for _ in ()).throw(RuntimeError("boom")),
    )
    art = get_banner_art()
    assert "_____" in art
    assert "of Languages" in art


def test_box_style_hierarchy_is_distinct():
    assert BOX_BANNER != BOX_SUMMARY
    assert BOX_SUMMARY != BOX_CONTENT
