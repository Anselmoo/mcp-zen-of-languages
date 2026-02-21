from __future__ import annotations

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
