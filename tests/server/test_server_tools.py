from __future__ import annotations

import pytest

from mcp_zen_of_languages import server
from mcp_zen_of_languages.models import (
    AnalysisResult,
    CyclomaticSummary,
    Metrics,
    Violation,
)


@pytest.mark.asyncio
async def test_detect_languages():
    result = await server.detect_languages.fn(repo_path=".")
    assert "python" in result.languages


@pytest.mark.asyncio
async def test_analyze_zen_violations_python():
    result = await server.analyze_zen_violations.fn("def foo():\n    pass\n", "python")
    assert result.language == "python"


@pytest.mark.asyncio
async def test_analyze_zen_violations_unsupported():
    with pytest.raises(ValueError, match="Unsupported language"):
        await server.analyze_zen_violations.fn("data", "unknownlang")


@pytest.mark.asyncio
async def test_analyze_zen_violations_applies_severity_threshold(monkeypatch):
    class _FakeAnalyzer:
        def analyze(self, _code: str) -> AnalysisResult:
            return AnalysisResult(
                language="python",
                metrics=Metrics(
                    cyclomatic=CyclomaticSummary(blocks=[], average=0.0),
                    maintainability_index=100.0,
                    lines_of_code=1,
                ),
                violations=[
                    Violation(principle="low", severity=3, message="low"),
                    Violation(principle="high", severity=8, message="high"),
                ],
                overall_score=90.0,
            )

    monkeypatch.setattr(
        server,
        "create_analyzer",
        lambda *_args, **_kwargs: _FakeAnalyzer(),
    )
    result = await server.analyze_zen_violations.fn("def foo(): pass", "python", 7)
    assert len(result.violations) == 1
    assert result.violations[0].principle == "high"


@pytest.mark.asyncio
async def test_analyze_zen_violations_applies_runtime_pipeline_override(monkeypatch):
    captured = {}

    class _FakeAnalyzer:
        def analyze(self, _code: str) -> AnalysisResult:
            return AnalysisResult(
                language="python",
                metrics=Metrics(
                    cyclomatic=CyclomaticSummary(blocks=[], average=0.0),
                    maintainability_index=100.0,
                    lines_of_code=1,
                ),
                violations=[],
                overall_score=100.0,
            )

    def _fake_create_analyzer(_language: str, **kwargs):
        captured["pipeline_config"] = kwargs["pipeline_config"]
        return _FakeAnalyzer()

    await server.clear_config_overrides.fn()
    await server.set_config_override.fn("python", max_nesting_depth=1)
    monkeypatch.setattr(server, "create_analyzer", _fake_create_analyzer)

    await server.analyze_zen_violations.fn("def foo(): pass", "python")
    detector_defaults = [
        detector
        for detector in captured["pipeline_config"].detectors
        if detector.type == "analyzer_defaults" and detector.max_nesting_depth == 1
    ]
    assert detector_defaults
    await server.clear_config_overrides.fn()


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("alias", "canonical"),
    [
        ("py", "python"),
        ("ts", "typescript"),
        ("tsx", "typescript"),
        ("js", "javascript"),
        ("jsx", "javascript"),
        ("rs", "rust"),
        ("shell", "bash"),
        ("rb", "ruby"),
        ("sh", "bash"),
        ("cs", "csharp"),
        ("ps", "powershell"),
        ("pwsh", "powershell"),
        ("c++", "cpp"),
        ("cc", "cpp"),
        ("cxx", "cpp"),
        ("yml", "yaml"),
    ],
)
async def test_analyze_zen_violations_accepts_supported_aliases(
    monkeypatch,
    alias,
    canonical,
):
    captured = {}

    class _FakeAnalyzer:
        def __init__(self, lang: str):
            self.lang = lang

        def analyze(self, _code: str) -> AnalysisResult:
            return AnalysisResult(
                language=self.lang,
                metrics=Metrics(
                    cyclomatic=CyclomaticSummary(blocks=[], average=0.0),
                    maintainability_index=100.0,
                    lines_of_code=1,
                ),
                violations=[],
                overall_score=100.0,
            )

    def _fake_create_analyzer(language: str, **_kwargs):
        captured["language"] = language
        return _FakeAnalyzer(language)

    monkeypatch.setattr(server, "create_analyzer", _fake_create_analyzer)
    result = await server.analyze_zen_violations.fn("code", alias)
    assert captured["language"] == canonical
    assert result.language == canonical


@pytest.mark.asyncio
async def test_generate_report_tool(tmp_path):
    sample = tmp_path / "sample.py"
    sample.write_text("def foo():\n    pass\n", encoding="utf-8")
    report = await server.generate_report_tool.fn(str(sample), include_prompts=True)
    assert report.markdown.startswith("# Zen of Languages Report")
    assert "prompts" in report.data


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("language", "code"),
    [
        ("python", "def foo():\n    pass\n"),
        ("typescript", "const foo = 1;"),
        ("go", "package main\n\nfunc main() {}"),
        ("rust", "fn main() {}"),
    ],
)
async def test_generate_prompts_tool_languages(language, code):
    bundle = await server.generate_prompts_tool.fn(code, language)
    assert bundle.generic_prompts


@pytest.mark.asyncio
async def test_generate_agent_tasks_tool(tmp_path):
    sample = tmp_path / "sample.py"
    sample.write_text("def foo():\n    pass\n", encoding="utf-8")
    tasks = await server.generate_agent_tasks_tool.fn(
        repo_path=str(tmp_path),
        languages=["python"],
        min_severity=1,
    )
    assert tasks.total_tasks >= 1


def test_server_registers_resources_and_prompt():
    resources = server.mcp._resource_manager._resources
    templates = server.mcp._resource_manager._templates
    prompts = server.mcp._prompt_manager._prompts

    assert "zen://config" in resources
    assert "zen://languages" in resources
    assert "zen://rules/{language}" in templates
    assert "zen_remediation_prompt" in prompts


def test_tools_include_annotations():
    assert server.analyze_zen_violations.annotations is not None
    assert server.analyze_zen_violations.annotations.readOnlyHint is True
    assert server.set_config_override.annotations is not None
    assert server.set_config_override.annotations.destructiveHint is True


@pytest.mark.asyncio
async def test_analyze_repository_reports_context_progress(tmp_path):
    sample = tmp_path / "sample.py"
    sample.write_text("def foo():\n    pass\n", encoding="utf-8")
    logs: list[str] = []
    progress: list[tuple[float, float | None]] = []

    class _Ctx:
        def log(self, message: str, *args, **kwargs) -> None:
            logs.append(message)

        def report_progress(
            self,
            current: float,
            total: float | None = None,
            message: str | None = None,
        ) -> None:
            progress.append((current, total))

    await server.analyze_repository.fn(
        str(tmp_path),
        ["python"],
        max_files=1,
        ctx=_Ctx(),
    )
    assert any("Analyzing" in msg for msg in logs)
    assert progress


@pytest.mark.asyncio
async def test_generate_report_reports_context_progress(tmp_path):
    sample = tmp_path / "sample.py"
    sample.write_text("def foo():\n    pass\n", encoding="utf-8")
    logs: list[str] = []
    progress: list[tuple[float, float | None]] = []

    class _Ctx:
        def log(self, message: str, *args, **kwargs) -> None:
            logs.append(message)

        def report_progress(
            self,
            current: float,
            total: float | None = None,
            message: str | None = None,
        ) -> None:
            progress.append((current, total))

    await server.generate_report_tool.fn(str(sample), include_prompts=False, ctx=_Ctx())
    assert any("Generating" in msg for msg in logs)
    assert progress
