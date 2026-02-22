from __future__ import annotations

from typing import ClassVar

from mcp_zen_of_languages.analyzers.base import (
    AnalysisContext,
    AnalyzerConfig,
    BaseAnalyzer,
)
from mcp_zen_of_languages.models import CyclomaticSummary
from mcp_zen_of_languages.utils.subprocess_runner import (
    SubprocessResult,
    SubprocessToolRunner,
    ToolResolution,
)


class _ExternalDummyAnalyzer(BaseAnalyzer):
    def default_config(self) -> AnalyzerConfig:
        return AnalyzerConfig()

    def language(self) -> str:
        return "python"

    def parse_code(self, code: str):
        _ = code

    def compute_metrics(self, code: str, ast_tree):
        _ = ast_tree
        return CyclomaticSummary(blocks=[], average=0.0), 0.0, len(code.splitlines())

    def build_pipeline(self):
        class _Pipeline:
            detectors: ClassVar[list] = []

            def run(self, context, config):
                _ = context, config
                return []

        return _Pipeline()


def test_external_analysis_disabled_exposes_opt_in_hint(monkeypatch):
    analyzer = _ExternalDummyAnalyzer()
    monkeypatch.setattr(
        SubprocessToolRunner,
        "resolve_tool",
        lambda self, tool, **_kwargs: ToolResolution(
            tool=tool,
            command=["ruff"],
            strategy="path",
            attempts=["path:ruff"],
        ),
    )

    result = analyzer.analyze("x = 1", enable_external_tools=False)

    assert result.external_analysis is not None
    assert result.external_analysis.enabled is False
    assert result.external_analysis.tools
    assert result.external_analysis.tools[0].status == "available"


def test_external_analysis_enabled_handles_unavailable_tool(monkeypatch):
    analyzer = _ExternalDummyAnalyzer()
    monkeypatch.setattr(
        SubprocessToolRunner,
        "resolve_tool",
        lambda self, tool, **_kwargs: ToolResolution(tool=tool, attempts=["path:ruff"]),
    )

    result = analyzer.analyze("x = 1", enable_external_tools=True)

    assert result.external_analysis is not None
    assert result.external_analysis.enabled is True
    assert result.external_analysis.tools[0].status == "unavailable"
    assert result.external_analysis.tools[0].recommendation is not None


def test_external_analysis_enabled_runs_tool_when_available(monkeypatch):
    analyzer = _ExternalDummyAnalyzer()
    monkeypatch.setattr(
        SubprocessToolRunner,
        "resolve_tool",
        lambda self, tool, **_kwargs: ToolResolution(
            tool=tool,
            command=["ruff"],
            strategy="path",
            attempts=["path:ruff"],
        ),
    )
    monkeypatch.setattr(
        SubprocessToolRunner,
        "run",
        lambda self, tool, args, *, code="", **_kwargs: SubprocessResult(
            tool=tool,
            returncode=0,
            stdout="ok",
            stderr="",
            strategy="path",
            command=["ruff", *(args or [])],
            resolution_attempts=["path:ruff"],
        ),
    )

    result = analyzer.analyze("x = 1", enable_external_tools=True)

    assert result.external_analysis is not None
    assert result.external_analysis.enabled is True
    assert result.external_analysis.tools[0].status == "passed"
    assert result.external_analysis.tools[0].returncode == 0


def test_external_analysis_enabled_handles_execution_failure(monkeypatch):
    analyzer = _ExternalDummyAnalyzer()
    monkeypatch.setattr(
        SubprocessToolRunner,
        "resolve_tool",
        lambda self, tool, **_kwargs: ToolResolution(
            tool=tool,
            command=["ruff"],
            strategy="path",
            attempts=["path:ruff"],
        ),
    )
    monkeypatch.setattr(
        SubprocessToolRunner,
        "run",
        lambda self, tool, args, *, code="", **_kwargs: None,
    )

    result = analyzer.analyze("x = 1", enable_external_tools=True)

    assert result.external_analysis is not None
    assert result.external_analysis.tools[0].status == "execution_failed"


def test_external_analysis_truncates_long_tool_output(monkeypatch):
    analyzer = _ExternalDummyAnalyzer()
    long_output = "x" * 5000
    monkeypatch.setattr(
        SubprocessToolRunner,
        "resolve_tool",
        lambda self, tool, **_kwargs: ToolResolution(
            tool=tool,
            command=["ruff"],
            strategy="path",
            attempts=["path:ruff"],
        ),
    )
    monkeypatch.setattr(
        SubprocessToolRunner,
        "run",
        lambda self, tool, args, *, code="", **_kwargs: SubprocessResult(
            tool=tool,
            returncode=0,
            stdout=long_output,
            stderr=long_output,
            strategy="path",
            command=["ruff", *(args or [])],
            resolution_attempts=["path:ruff"],
        ),
    )

    result = analyzer.analyze("x = 1", enable_external_tools=True)

    assert result.external_analysis is not None
    tool_result = result.external_analysis.tools[0]
    assert tool_result.stdout is not None
    assert tool_result.stderr is not None
    assert tool_result.stdout.endswith("... [truncated]")
    assert tool_result.stderr.endswith("... [truncated]")


def test_build_result_handles_invalid_external_analysis_dict():
    analyzer = _ExternalDummyAnalyzer()
    context = AnalysisContext(
        code="x = 1", language="python", external_analysis={"bad": 1}
    )
    context.cyclomatic_summary = CyclomaticSummary(blocks=[], average=0.0)
    context.lines_of_code = 1

    result = analyzer._build_result(context, [])

    assert result.external_analysis is None
