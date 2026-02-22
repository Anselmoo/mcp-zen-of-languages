from __future__ import annotations

from mcp_zen_of_languages.models import CyclomaticSummary, Metrics
from mcp_zen_of_languages.orchestration import analyze_targets


def test_analyze_targets_passes_other_files_for_latex(tmp_path):
    main = tmp_path / "main.tex"
    chapter = tmp_path / "chapter1.tex"
    main.write_text(r"\input{chapter1}", encoding="utf-8")
    chapter.write_text(r"\input{main}", encoding="utf-8")

    results = analyze_targets(
        [(main, "latex"), (chapter, "latex")],
        include_read_errors=True,
    )

    assert any(
        "Circular \\input/\\include dependency" in violation.message
        for result in results
        for violation in result.violations
    )


def test_analyze_targets_passes_enable_external_tools(monkeypatch, tmp_path):
    sample = tmp_path / "sample.py"
    sample.write_text("x = 1\n", encoding="utf-8")
    captured: dict[str, bool] = {}

    class _Config:
        def pipeline_for(self, _language: str):
            return None

    class _Analyzer:
        def analyze(
            self,
            _code: str,
            *,
            path: str | None = None,
            repository_imports: dict[str, list[str]] | None = None,
            enable_external_tools: bool = False,
        ):
            _ = path, repository_imports
            from mcp_zen_of_languages.models import AnalysisResult

            captured["enable_external_tools"] = enable_external_tools
            return AnalysisResult(
                language="python",
                path=str(sample),
                metrics=Metrics(
                    cyclomatic=CyclomaticSummary(blocks=[], average=0.0),
                    maintainability_index=100.0,
                    lines_of_code=1,
                ),
                violations=[],
                overall_score=100.0,
            )

    monkeypatch.setattr(
        "mcp_zen_of_languages.orchestration.load_config", lambda _p: _Config()
    )
    monkeypatch.setattr(
        "mcp_zen_of_languages.orchestration.create_analyzer",
        lambda *_args, **_kwargs: _Analyzer(),
    )

    analyze_targets([(sample, "python")], enable_external_tools=True)
    assert captured["enable_external_tools"] is True
