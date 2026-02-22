"""C++ language analyzer for modern idiom and safety checks.

Applies the Template Method pattern to analyze C++ source files against zen
principles covering RAII, smart pointers, const correctness, and the
transition from C-style patterns to modern C++ (C++11 through C++23).

See Also:
    ``BaseAnalyzer``: Abstract base defining the analysis template method.
    ``cpp/detectors.py``: Strategy-pattern detectors wired into this analyzer.
"""

from __future__ import annotations

import re
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from mcp_zen_of_languages.analyzers.pipeline import PipelineConfig
    from mcp_zen_of_languages.models import CyclomaticSummary, ParserResult

from mcp_zen_of_languages.analyzers.base import (
    AnalysisContext,
    AnalyzerCapabilities,
    AnalyzerConfig,
    BaseAnalyzer,
    DetectionPipeline,
)

_INCLUDE_RE = re.compile(r"""^#include\s+[<"](.+?)[>"]""")


class CppAnalyzer(BaseAnalyzer):
    """Rule-driven analyzer for C++ source files.

    Orchestrates parsing, metric computation, and violation detection for C++
    code.  Modern C++ best practices emphasise deterministic resource
    management (RAII), type safety through smart pointers and ``std::optional``,
    and compile-time guarantees via ``constexpr`` and ``const``—all of which
    this analyzer validates.

    Attributes:
        _pipeline_config: Optional overrides merged into detector defaults.

    See Also:
        ``BaseAnalyzer``: Template Method base class defining the analysis flow.
    """

    def __init__(
        self,
        config: AnalyzerConfig | None = None,
        pipeline_config: PipelineConfig | None = None,
    ) -> None:
        """Initialize instance.

        Args:
            config (AnalyzerConfig | None): Typed detector or analyzer configuration that controls thresholds.
            pipeline_config ('PipelineConfig' | None): Optional pipeline overrides used to customize detector configuration.
        """
        self._pipeline_config = pipeline_config
        super().__init__(config=config)

    def default_config(self) -> AnalyzerConfig:
        """Return default thresholds tuned for modern C++ best practices.

        Returns:
            AnalyzerConfig: Baseline settings aligned with C++ Core Guidelines.
        """
        return AnalyzerConfig()

    def language(self) -> str:
        """Return ``'cpp'`` as the language key for factory registration.

        Returns:
            str: The literal ``'cpp'`` identifier used by the analyzer factory.
        """
        return "cpp"

    def capabilities(self) -> AnalyzerCapabilities:
        """Declare support for #include dependency extraction."""
        return AnalyzerCapabilities(supports_dependency_analysis=True)

    def parse_code(self, _code: str) -> ParserResult | None:
        """Parse C++ source into a structured syntax tree.

        Currently returns ``None`` because a full C++ parser (e.g., libclang)
        is not yet integrated.  Detectors operate on regex-based source
        scanning instead.

        Args:
            code: Raw C++ source text to parse.

        Returns:
            ParserResult | None: Always ``None`` until a C++ parser is wired in.
        """
        return None

    def compute_metrics(
        self,
        code: str,
        _ast_tree: ParserResult | None,
    ) -> tuple[CyclomaticSummary | None, float | None, int]:
        """Compute complexity and size metrics for C++ source code.

        Only line count is computed today; cyclomatic complexity and
        maintainability index require a C++-aware parser like libclang.

        Args:
            code: C++ source text to measure.
            ast_tree: Parsed syntax tree, currently unused for C++.

        Returns:
            tuple[CyclomaticSummary | None, float | None, int]: A three-element
                tuple of ``(None, None, line_count)``.
        """
        return None, None, len(code.splitlines())

    def build_pipeline(self) -> DetectionPipeline:
        """Assemble the C++-specific detection pipeline from registered detectors.

        Returns:
            DetectionPipeline: Pipeline loaded with C++ zen-rule detectors.
        """
        return super().build_pipeline()

    def _build_dependency_analysis(self, context: AnalysisContext) -> object | None:
        """Extract ``#include`` directives and build a header dependency graph.

        Args:
            context: Current analysis context with source text and metrics.

        Returns:
            DependencyAnalysis with include edges, or ``None`` when no includes found.
        """
        imports: list[str] = []
        for line in context.code.splitlines():
            m = _INCLUDE_RE.match(line.strip())
            if m:
                imports.append(m.group(1))
        if not imports:
            return None
        from mcp_zen_of_languages.metrics.dependency_graph import build_import_graph

        return build_import_graph({(context.path or "<current>"): imports})
