"""Ruby language analyzer for idiomatic code quality and convention checks.

Applies the Template Method pattern to analyze Ruby source files against
zen principles covering naming conventions, metaprogramming discipline,
block preference, and the convention-over-configuration philosophy that
defines idiomatic Ruby.

See Also:
    ``BaseAnalyzer``: Abstract base defining the analysis template method.
    ``ruby/detectors.py``: Strategy-pattern detectors wired into this analyzer.
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

_REQUIRE_RE = re.compile(r"""^(?:require|require_relative|load)\s+['"](.+?)['"]""")


class RubyAnalyzer(BaseAnalyzer):
    """Rule-driven analyzer for Ruby source files.

    Orchestrates parsing, metric computation, and violation detection for Ruby
    code.  Ruby's dynamic nature and convention-heavy ecosystem require checks
    that go beyond syntax—covering naming, metaprogramming restraint, and
    expressive block usage.

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
        """Return default thresholds tuned for idiomatic Ruby conventions.

        Returns:
            AnalyzerConfig: Baseline settings for Ruby analysis with sensible
                community-aligned defaults.
        """
        return AnalyzerConfig()

    def language(self) -> str:
        """Return ``'ruby'`` as the language key for factory registration.

        Returns:
            str: The literal ``'ruby'`` identifier used by the analyzer factory.
        """
        return "ruby"

    def capabilities(self) -> AnalyzerCapabilities:
        """Declare support for require/require_relative dependency extraction."""
        return AnalyzerCapabilities(supports_dependency_analysis=True)

    def parse_code(self, _code: str) -> ParserResult | None:
        """Parse Ruby source into a structured syntax tree.

        Currently returns ``None`` because Ruby AST parsing is not yet
        integrated.  Detectors operate on raw source text instead.

        Args:
            code: Raw Ruby source text to parse.

        Returns:
            ParserResult | None: Always ``None`` until a Ruby parser is wired in.
        """
        return None

    def compute_metrics(
        self,
        code: str,
        _ast_tree: ParserResult | None,
    ) -> tuple[CyclomaticSummary | None, float | None, int]:
        """Compute complexity and size metrics for Ruby source code.

        Only line count is computed today; cyclomatic complexity and
        maintainability index require a Ruby-aware parser.

        Args:
            code: Ruby source text to measure.
            ast_tree: Parsed syntax tree, currently unused for Ruby.

        Returns:
            tuple[CyclomaticSummary | None, float | None, int]: A three-element
                tuple of ``(None, None, line_count)``.
        """
        return None, None, len(code.splitlines())

    def build_pipeline(self) -> DetectionPipeline:
        """Assemble the Ruby-specific detection pipeline from registered detectors.

        Returns:
            DetectionPipeline: Pipeline loaded with Ruby zen-rule detectors.
        """
        return super().build_pipeline()

    def _build_dependency_analysis(self, context: AnalysisContext) -> object | None:
        """Extract ``require`` / ``require_relative`` dependencies.

        Args:
            context: Current analysis context with source text and metrics.

        Returns:
            DependencyAnalysis with require edges, or ``None`` when none found.
        """
        imports: list[str] = []
        for line in context.code.splitlines():
            m = _REQUIRE_RE.match(line.strip())
            if m:
                imports.append(m.group(1))
        if not imports:
            return None
        from mcp_zen_of_languages.metrics.dependency_graph import build_import_graph

        return build_import_graph({(context.path or "<current>"): imports})
