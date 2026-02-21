from __future__ import annotations

from mcp_zen_of_languages.analyzers.base import AnalysisContext
from mcp_zen_of_languages.languages.configs import (
    LatexBibliographyHygieneConfig,
    LatexCaptionCompletenessConfig,
    LatexEncodingDeclarationConfig,
    LatexIncludeLoopConfig,
    LatexLabelRefDisciplineConfig,
    LatexMacroDefinitionConfig,
    LatexSemanticMarkupConfig,
    LatexUnusedPackagesConfig,
    LatexWidthAbstractionConfig,
)
from mcp_zen_of_languages.languages.latex.detectors import (
    LatexBibliographyHygieneDetector,
    LatexCaptionCompletenessDetector,
    LatexEncodingDeclarationDetector,
    LatexIncludeLoopDetector,
    LatexLabelRefDisciplineDetector,
    LatexMacroDefinitionDetector,
    LatexSemanticMarkupDetector,
    LatexUnusedPackagesDetector,
    LatexWidthAbstractionDetector,
)


def _detect(detector, code: str, config, **kwargs):
    return detector.detect(
        AnalysisContext(code=code, language="latex", **kwargs), config
    )


def test_latex_macro_definition_detector_flags_def():
    violations = _detect(
        LatexMacroDefinitionDetector(),
        r"\def\foo{bar}",
        LatexMacroDefinitionConfig(),
    )
    assert violations


def test_latex_label_ref_detector_flags_unresolved_ref():
    violations = _detect(
        LatexLabelRefDisciplineDetector(),
        r"\ref{eq:missing}",
        LatexLabelRefDisciplineConfig(),
    )
    assert violations


def test_latex_caption_detector_flags_missing_caption():
    violations = _detect(
        LatexCaptionCompletenessDetector(),
        "\\begin{figure}\n\\includegraphics{plot}\n\\end{figure}",
        LatexCaptionCompletenessConfig(),
    )
    assert violations


def test_latex_bibliography_detector_flags_uncited_bibitem():
    violations = _detect(
        LatexBibliographyHygieneDetector(),
        "\\begin{thebibliography}{9}\n\\bibitem{a} Ref\n\\end{thebibliography}",
        LatexBibliographyHygieneConfig(),
    )
    assert violations


def test_latex_width_detector_flags_absolute_units():
    violations = _detect(
        LatexWidthAbstractionDetector(),
        r"\setlength{\parindent}{12pt}",
        LatexWidthAbstractionConfig(),
    )
    assert violations


def test_latex_semantic_detector_flags_textit():
    violations = _detect(
        LatexSemanticMarkupDetector(),
        r"\textit{important}",
        LatexSemanticMarkupConfig(),
    )
    assert violations


def test_latex_include_loop_detector_flags_cycle():
    code = r"\input{chapter1}"
    other_files = {
        "chapter1.tex": r"\input{main}",
        "main.tex": code,
    }
    violations = _detect(
        LatexIncludeLoopDetector(),
        code,
        LatexIncludeLoopConfig(),
        path="main.tex",
        other_files=other_files,
    )
    assert violations


def test_latex_encoding_detector_flags_missing_declaration():
    violations = _detect(
        LatexEncodingDeclarationDetector(),
        r"\documentclass{article}\begin{document}Hi\end{document}",
        LatexEncodingDeclarationConfig(),
    )
    assert violations


def test_latex_unused_package_detector_flags_unused_package():
    violations = _detect(
        LatexUnusedPackagesDetector(),
        r"\usepackage{graphicx}\begin{document}Hello\end{document}",
        LatexUnusedPackagesConfig(),
    )
    assert violations
