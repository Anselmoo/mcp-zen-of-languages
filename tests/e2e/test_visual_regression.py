from __future__ import annotations

import os
import re
from io import StringIO
from pathlib import Path

import pytest
from jinja2 import Environment, StrictUndefined, select_autoescape
from rich.console import Console

from mcp_zen_of_languages import __version__, cli
from mcp_zen_of_languages.rendering.report import render_report_terminal
from mcp_zen_of_languages.rendering.themes import ZEN_THEME
from mcp_zen_of_languages.reporting.prompts import build_prompt_bundle
from mcp_zen_of_languages.reporting.report import generate_report
from mcp_zen_of_languages.reporting.terminal import render_prompt_panel

from .visual_utils import assert_balanced_boxes

FIXTURE_FILES = [
    "tests/fixtures/clean_file.py",
    "tests/fixtures/medium_violations.py",
    "tests/fixtures/many_violations.py",
]
GOLDEN_DIR = Path("tests/fixtures/golden")
TEMPLATE_ENV = Environment(
    autoescape=select_autoescape(default_for_string=False),
    undefined=StrictUndefined,
    keep_trailing_newline=True,
)
FIXTURE_PATH = "tests/fixtures/medium_violations.py"


def _assert_max_width(output: str, width: int = 88) -> None:
    ansi_re = re.compile(r"\x1b\[[0-9;]*m")
    for line in output.splitlines():
        assert len(ansi_re.sub("", line)) <= width


def _strip_ansi(output: str) -> str:
    cleaned = re.sub(r"\x1b\[[0-9;]*m", "", output)
    normalized = "\n".join(line.rstrip() for line in cleaned.splitlines())
    if cleaned.endswith("\n"):
        normalized += "\n"
    return normalized


def _render_template(path: Path, context: dict[str, str]) -> str:
    template = TEMPLATE_ENV.from_string(path.read_text(encoding="utf-8"))
    return template.render(**context)


def _to_template(output: str, context: dict[str, str]) -> str:
    templated = _strip_ansi(output)
    templated = templated.replace(f"v{context['version']}", "v{{ version }}")
    return templated.replace(context["fixture_path"], "{{ fixture_path }}")


def _assert_or_update_golden(path: Path, output: str, context: dict[str, str]) -> None:
    output = _strip_ansi(output)
    if os.getenv("UPDATE_GOLDEN") == "1":
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(_to_template(output, context), encoding="utf-8")
        return
    expected = _render_template(path, context)
    assert output == expected, (
        f"Golden mismatch for {path}. Re-run with UPDATE_GOLDEN=1 to update."
    )


@pytest.mark.parametrize("fixture", FIXTURE_FILES)
def test_report_visual_consistency(fixture: str):
    report = generate_report(fixture, include_prompts=True)
    buffer = StringIO()
    output_console = Console(
        file=buffer, width=88, force_terminal=True, no_color=True, theme=ZEN_THEME
    )
    render_report_terminal(report, output_console=output_console)
    output = buffer.getvalue()
    assert "Zen Report" in output
    _assert_max_width(output)
    assert_balanced_boxes(output)


def test_welcome_golden(monkeypatch):
    buffer = StringIO()
    output_console = Console(
        file=buffer, width=88, force_terminal=True, no_color=True, theme=ZEN_THEME
    )
    monkeypatch.setattr(cli, "console", output_console)
    monkeypatch.setattr(cli, "get_banner_art", lambda: "ZEN")
    cli._build_welcome_panel()
    output = buffer.getvalue()
    _assert_max_width(output)
    assert_balanced_boxes(output)
    _assert_or_update_golden(
        GOLDEN_DIR / "welcome.md.j2",
        output,
        {"version": __version__, "fixture_path": FIXTURE_PATH},
    )


def test_report_golden():
    report = generate_report(FIXTURE_PATH, include_prompts=True)
    buffer = StringIO()
    output_console = Console(
        file=buffer, width=88, force_terminal=True, no_color=True, theme=ZEN_THEME
    )
    render_report_terminal(report, output_console=output_console)
    output = buffer.getvalue()
    _assert_max_width(output)
    assert_balanced_boxes(output)
    _assert_or_update_golden(
        GOLDEN_DIR / "report.md.j2",
        output,
        {"version": __version__, "fixture_path": FIXTURE_PATH},
    )


def test_prompts_golden():
    target = Path(FIXTURE_PATH)
    results = cli._analyze_targets([(target, "python")], None)
    bundle = build_prompt_bundle(results)
    buffer = StringIO()
    output_console = Console(
        file=buffer, width=88, force_terminal=True, no_color=True, theme=ZEN_THEME
    )
    render_prompt_panel(bundle, results, output_console=output_console)
    output = buffer.getvalue()
    _assert_max_width(output)
    assert_balanced_boxes(output)
    _assert_or_update_golden(
        GOLDEN_DIR / "prompts.md.j2",
        output,
        {"version": __version__, "fixture_path": FIXTURE_PATH},
    )
