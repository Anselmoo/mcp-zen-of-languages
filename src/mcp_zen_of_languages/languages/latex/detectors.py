"""Detectors for LaTeX document quality and maintainability."""

from __future__ import annotations

import re
from pathlib import Path

from mcp_zen_of_languages.analyzers.base import (
    AnalysisContext,
    LocationHelperMixin,
    ViolationDetector,
)
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
from mcp_zen_of_languages.models import Location, Violation

_LABEL_PATTERN = re.compile(r"\\label\{([^}]+)\}")
_REF_PATTERN = re.compile(r"\\(?:eqref|ref)\{([^}]+)\}")
_CAPTION_PATTERN = re.compile(r"\\caption(?:\[[^\]]*])?\{")
_ABSOLUTE_LENGTH_PATTERN = re.compile(
    r"(?<![A-Za-z])\d+(?:\.\d+)?\s*(pt|cm|mm|in|pc|bp|dd|cc|sp)\b",
)
_CITE_PATTERN = re.compile(r"\\cite[a-zA-Z*]*\{([^}]+)\}")
_BIBITEM_PATTERN = re.compile(r"\\bibitem(?:\[[^\]]*])?\{([^}]+)\}")
_USEPACKAGE_PATTERN = re.compile(r"\\usepackage(?:\[[^\]]*\])?\{([^}]+)\}")

_PACKAGE_COMMAND_HINTS: dict[str, tuple[str, ...]] = {
    "graphicx": ("\\includegraphics",),
    "amsmath": ("\\begin{align", "\\[", "\\eqref"),
    "amssymb": ("\\mathbb", "\\mathfrak", "\\mathcal"),
    "xcolor": ("\\textcolor", "\\color", "\\definecolor"),
    "booktabs": ("\\toprule", "\\midrule", "\\bottomrule"),
    "hyperref": ("\\url", "\\href", "\\hyperref"),
    "tikz": ("\\begin{tikzpicture}",),
}


def _line_number(code: str, index: int) -> int:
    return code.count("\n", 0, index) + 1


def _extract_include_targets(code: str) -> list[str]:
    targets = re.findall(r"\\(?:input|include)\{([^}]+)\}", code)
    return [target.strip() for target in targets if target.strip()]


def _resolve_target(target: str, source: str, files: set[str]) -> str | None:
    source_path = Path(source)
    target_path = Path(target)
    candidates: list[Path] = [
        target_path,
        source_path.parent / target_path,
    ]
    if not target_path.suffix:
        candidates.extend(
            (
                target_path.with_suffix(".tex"),
                source_path.parent / target_path.with_suffix(".tex"),
                target_path.with_suffix(".ltx"),
                source_path.parent / target_path.with_suffix(".ltx"),
                target_path.with_suffix(".sty"),
                source_path.parent / target_path.with_suffix(".sty"),
            ),
        )
    for candidate in candidates:
        candidate_str = str(candidate)
        if candidate_str in files:
            return candidate_str
    target_name = target_path.name
    for file_name in files:
        if Path(file_name).name == target_name:
            return file_name
    return None


class LatexMacroDefinitionDetector(
    ViolationDetector[LatexMacroDefinitionConfig],
    LocationHelperMixin,
):
    r"""Detect raw ``\def`` macro declarations."""

    @property
    def name(self) -> str:
        """Return the detector rule ID."""
        return "latex-001"

    def detect(
        self,
        context: AnalysisContext,
        config: LatexMacroDefinitionConfig,
    ) -> list[Violation]:
        r"""Return a violation when ``\def`` is used."""
        if match := re.search(r"\\def\s*\\[A-Za-z@]+", context.code):
            line = _line_number(context.code, match.start())
            return [
                self.build_violation(
                    config,
                    location=Location(line=line, column=1),
                    suggestion="Use \\newcommand or \\renewcommand for safer macro definitions.",
                ),
            ]
        return []


class LatexLabelRefDisciplineDetector(
    ViolationDetector[LatexLabelRefDisciplineConfig],
    LocationHelperMixin,
):
    """Validate that labels and references are mutually consistent."""

    @property
    def name(self) -> str:
        """Return the detector rule ID."""
        return "latex-002"

    def detect(
        self,
        context: AnalysisContext,
        config: LatexLabelRefDisciplineConfig,
    ) -> list[Violation]:
        """Return violations for unresolved refs or unused labels."""
        labels = set(_LABEL_PATTERN.findall(context.code))
        refs = {
            ref.strip()
            for raw in _REF_PATTERN.findall(context.code)
            for ref in raw.split(",")
            if ref.strip()
        }
        unused_labels = sorted(labels - refs)
        unresolved_refs = sorted(refs - labels)
        if unused_labels:
            return [
                self.build_violation(
                    config,
                    message=f"Label '{unused_labels[0]}' is never referenced.",
                    location=Location(line=1, column=1),
                    suggestion="Remove stale labels or add matching references.",
                ),
            ]
        if unresolved_refs:
            return [
                self.build_violation(
                    config,
                    message=f"Reference '{unresolved_refs[0]}' has no matching label.",
                    location=Location(line=1, column=1),
                    suggestion="Add the missing \\label or fix the reference key.",
                ),
            ]
        return []


class LatexCaptionCompletenessDetector(
    ViolationDetector[LatexCaptionCompletenessConfig],
    LocationHelperMixin,
):
    """Check that ``figure`` and ``table`` environments define captions."""

    @property
    def name(self) -> str:
        """Return the detector rule ID."""
        return "latex-003"

    def detect(
        self,
        context: AnalysisContext,
        config: LatexCaptionCompletenessConfig,
    ) -> list[Violation]:
        """Return violations for captionless figure/table blocks."""
        for env in ("figure", "table"):
            pattern = re.compile(
                rf"\\begin\{{{env}\*?\}}(.*?)\\end\{{{env}\*?\}}",
                re.DOTALL,
            )
            for match in pattern.finditer(context.code):
                if _CAPTION_PATTERN.search(match[1]) is None:
                    line = _line_number(context.code, match.start())
                    return [
                        self.build_violation(
                            config,
                            message=f"{env.title()} environment is missing a \\caption.",
                            location=Location(line=line, column=1),
                            suggestion="Add a descriptive \\caption{...} to the environment.",
                        ),
                    ]
        return []


class LatexBibliographyHygieneDetector(
    ViolationDetector[LatexBibliographyHygieneConfig],
    LocationHelperMixin,
):
    """Detect manual bibliography drift and uncited entries."""

    @property
    def name(self) -> str:
        """Return the detector rule ID."""
        return "latex-004"

    def detect(
        self,
        context: AnalysisContext,
        config: LatexBibliographyHygieneConfig,
    ) -> list[Violation]:
        """Return violations for manual or stale bibliography entries."""
        bibitems = [key.strip() for key in _BIBITEM_PATTERN.findall(context.code)]
        cites = {
            key.strip()
            for raw in _CITE_PATTERN.findall(context.code)
            for key in raw.split(",")
            if key.strip()
        }
        if bibitems and "\\bibliography{" not in context.code and "\\addbibresource{" not in context.code:
            return [
                self.build_violation(
                    config,
                    message="Manual \\bibitem entries detected; prefer .bib-backed citations.",
                    location=Location(line=1, column=1),
                    suggestion="Move bibliography entries to a .bib file and cite keys via \\cite{...}.",
                ),
            ]
        uncited = sorted(set(bibitems) - cites)
        if uncited:
            return [
                self.build_violation(
                    config,
                    message=f"Bibliography entry '{uncited[0]}' is never cited.",
                    location=Location(line=1, column=1),
                    suggestion="Remove unused \\bibitem entries or add citations.",
                ),
            ]
        return []


class LatexWidthAbstractionDetector(
    ViolationDetector[LatexWidthAbstractionConfig],
    LocationHelperMixin,
):
    """Find hardcoded absolute lengths in layout-related commands."""

    @property
    def name(self) -> str:
        """Return the detector rule ID."""
        return "latex-005"

    def detect(
        self,
        context: AnalysisContext,
        config: LatexWidthAbstractionConfig,
    ) -> list[Violation]:
        """Return violations for absolute layout units."""
        if match := _ABSOLUTE_LENGTH_PATTERN.search(context.code):
            line = _line_number(context.code, match.start())
            return [
                self.build_violation(
                    config,
                    message=f"Hardcoded length '{match[0]}' found; prefer relative lengths.",
                    location=Location(line=line, column=1),
                    suggestion="Use \\textwidth, \\linewidth, or \\baselineskip when possible.",
                ),
            ]
        return []


class LatexSemanticMarkupDetector(
    ViolationDetector[LatexSemanticMarkupConfig],
    LocationHelperMixin,
):
    """Flag visual styling commands used where semantic emphasis is preferred."""

    @property
    def name(self) -> str:
        """Return the detector rule ID."""
        return "latex-006"

    def detect(
        self,
        context: AnalysisContext,
        config: LatexSemanticMarkupConfig,
    ) -> list[Violation]:
        """Return violations for visual emphasis commands."""
        if match := re.search(r"\\text(?:it|bf)\{", context.code):
            line = _line_number(context.code, match.start())
            return [
                self.build_violation(
                    config,
                    message=f"Visual command '{match[0][:-1]}' detected; prefer semantic markup.",
                    location=Location(line=line, column=1),
                    suggestion="Use \\emph{...} for emphasis and reserve bold for semantic intent.",
                ),
            ]
        return []


class LatexIncludeLoopDetector(
    ViolationDetector[LatexIncludeLoopConfig],
    LocationHelperMixin,
):
    """Detect circular include/input chains across LaTeX files."""

    @property
    def name(self) -> str:
        """Return the detector rule ID."""
        return "latex-007"

    def detect(
        self,
        context: AnalysisContext,
        config: LatexIncludeLoopConfig,
    ) -> list[Violation]:
        """Return violations for circular include dependency graphs."""
        file_map = dict(context.other_files or {})
        current_path = context.path or "__current__.tex"
        file_map[current_path] = context.code
        file_names = set(file_map)

        edges: dict[str, list[str]] = {}
        for file_name, code in file_map.items():
            targets = [
                resolved
                for target in _extract_include_targets(code)
                if (resolved := _resolve_target(target, file_name, file_names))
            ]
            edges[file_name] = targets

        visited: set[str] = set()
        stack: set[str] = set()

        def _has_cycle(node: str) -> bool:
            if node in stack:
                return True
            if node in visited:
                return False
            visited.add(node)
            stack.add(node)
            for neighbor in edges.get(node, []):
                if _has_cycle(neighbor):
                    return True
            stack.remove(node)
            return False

        if _has_cycle(current_path):
            return [
                self.build_violation(
                    config,
                    location=Location(line=1, column=1),
                    suggestion="Break circular \\input/\\include chains by flattening dependencies.",
                ),
            ]
        return []


class LatexEncodingDeclarationDetector(
    ViolationDetector[LatexEncodingDeclarationConfig],
    LocationHelperMixin,
):
    """Require UTF-8 encoding declaration for non-LuaTeX/XeTeX documents."""

    @property
    def name(self) -> str:
        """Return the detector rule ID."""
        return "latex-008"

    def detect(
        self,
        context: AnalysisContext,
        config: LatexEncodingDeclarationConfig,
    ) -> list[Violation]:
        """Return violations for missing UTF-8 declaration intent."""
        lower = context.code.lower()
        has_utf8_inputenc = "\\usepackage[utf8]{inputenc}" in lower
        uses_unicode_engine = "fontspec" in lower or "xelatex" in lower or "lualatex" in lower
        if not has_utf8_inputenc and not uses_unicode_engine:
            return [
                self.build_violation(
                    config,
                    location=Location(line=1, column=1),
                    suggestion="Add \\usepackage[utf8]{inputenc} or compile with LuaLaTeX/XeLaTeX.",
                ),
            ]
        return []


class LatexUnusedPackagesDetector(
    ViolationDetector[LatexUnusedPackagesConfig],
    LocationHelperMixin,
):
    """Warn about package declarations with no observable command usage."""

    @property
    def name(self) -> str:
        """Return the detector rule ID."""
        return "latex-009"

    def detect(
        self,
        context: AnalysisContext,
        config: LatexUnusedPackagesConfig,
    ) -> list[Violation]:
        """Return violations for unused package declarations."""
        packages = [
            package.strip()
            for group in _USEPACKAGE_PATTERN.findall(context.code)
            for package in group.split(",")
            if package.strip()
        ]
        unused = [
            package
            for package in packages
            if package in _PACKAGE_COMMAND_HINTS
            and not any(command in context.code for command in _PACKAGE_COMMAND_HINTS[package])
        ]
        if unused:
            return [
                self.build_violation(
                    config,
                    message=f"Package '{unused[0]}' appears unused in this document.",
                    location=Location(line=1, column=1),
                    suggestion="Remove unused packages to reduce compile overhead.",
                ),
            ]
        return []


__all__ = [
    "LatexBibliographyHygieneDetector",
    "LatexCaptionCompletenessDetector",
    "LatexEncodingDeclarationDetector",
    "LatexIncludeLoopDetector",
    "LatexLabelRefDisciplineDetector",
    "LatexMacroDefinitionDetector",
    "LatexSemanticMarkupDetector",
    "LatexUnusedPackagesDetector",
    "LatexWidthAbstractionDetector",
]
