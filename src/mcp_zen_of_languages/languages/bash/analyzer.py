"""Bash/shell analyzer implementation for detecting shell scripting anti-patterns.

Provides a rule-driven analysis pipeline for Bash source files, scanning for
dangerous practices such as missing strict mode, unquoted variable expansions,
``eval`` usage, single-bracket conditionals, and legacy backtick syntax that
cause real-world shell script failures in CI/CD and production automation.

See Also:
    [`BaseAnalyzer`][mcp_zen_of_languages.analyzers.base.BaseAnalyzer]: Template Method
    base class defining the analysis algorithm skeleton.
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

_SOURCE_RE = re.compile(r"""^(?:source|\.)[ \t]+['"]?([^\s'"]+)['"]?""")


class BashAnalyzer(BaseAnalyzer):
    """Bash/shell script analyzer using rule-driven detection pipeline.

    Orchestrates parsing, metric computation, and violation detection for
    Bash source code.  Because shell scripts lack a Python-accessible AST,
    parsing returns ``None`` and all detection is performed by regex-based
    line scanners in the detector pipeline.

    Attributes:
        _pipeline_config: Optional overrides merged into the default detector
            configuration at pipeline-build time.

    See Also:
        [`detectors`][mcp_zen_of_languages.languages.bash.detectors]: Individual
        violation detectors wired into this analyzer's pipeline.
    """

    def __init__(
        self,
        config: AnalyzerConfig | None = None,
        pipeline_config: PipelineConfig | None = None,
    ) -> None:
        """Initialize the Bash analyzer with optional configuration.

        Args:
            config: Threshold settings controlling detector sensitivity such as
                maximum script length without functions and minimum variable
                name length.
            pipeline_config: Optional overrides that are merged on top of
                rule-derived detector defaults, allowing per-project tuning
                via ``zen-config.yaml``.
        """
        self._pipeline_config = pipeline_config
        super().__init__(config=config)

    def default_config(self) -> AnalyzerConfig:
        """Return sensible default thresholds for Bash analysis.

        Returns:
            AnalyzerConfig: Baseline configuration used when no explicit config
            is supplied by the caller or the ``zen-config.yaml`` file.
        """
        return AnalyzerConfig()

    def language(self) -> str:
        """Return ``'bash'`` as the language key for factory lookup.

        Returns:
            str: The literal ``'bash'`` identifier used by
            [`AnalyzerFactory`][mcp_zen_of_languages.analyzers.analyzer_factory.AnalyzerFactory].
        """
        return "bash"

    def capabilities(self) -> AnalyzerCapabilities:
        """Declare support for source/dot-source dependency extraction."""
        return AnalyzerCapabilities(supports_dependency_analysis=True)

    def parse_code(self, _code: str) -> ParserResult | None:
        """Attempt to parse Bash source into a structured AST.

        Currently returns ``None`` because no Python-native Bash parser is
        integrated.  Detection relies on regex-based line scanning inside
        each detector.

        Args:
            code: Raw Bash/shell source text to parse.

        Returns:
            ParserResult | None: Always ``None`` for Bash; reserved for
            future tree-sitter-bash integration.
        """
        return None

    def compute_metrics(
        self,
        code: str,
        _ast_tree: ParserResult | None,
    ) -> tuple[CyclomaticSummary | None, float | None, int]:
        """Compute source-level metrics for the Bash file.

        Without an AST, cyclomatic complexity and maintainability index
        cannot be calculated.  Only the raw line count is returned.

        Args:
            code: Raw Bash source text.
            ast_tree: Parsed AST (always ``None`` for Bash today).

        Returns:
            tuple[CyclomaticSummary | None, float | None, int]: A three-element
            tuple of ``(None, None, line_count)``.
        """
        return None, None, len(code.splitlines())

    def build_pipeline(self) -> DetectionPipeline:
        """Build the Bash violation-detection pipeline.

        Delegates to the base class, which assembles detectors from the
        registry for the ``'bash'`` language key and applies any pipeline
        overrides from ``zen-config.yaml``.

        Returns:
            DetectionPipeline: Fully-configured pipeline of Bash detectors.
        """
        return super().build_pipeline()

    def _build_dependency_analysis(self, context: AnalysisContext) -> object | None:
        """Extract ``source`` and ``.`` includes and build a dependency graph.

        Args:
            context: Current analysis context with source text and metrics.

        Returns:
            DependencyAnalysis with include edges, or ``None`` when no sources found.
        """
        imports: list[str] = []
        for line in context.code.splitlines():
            stripped = line.strip()
            if stripped.startswith("#"):
                continue
            m = _SOURCE_RE.match(stripped)
            if m:
                imports.append(m.group(1))
        if not imports:
            return None
        from mcp_zen_of_languages.metrics.dependency_graph import build_import_graph

        return build_import_graph({(context.path or "<current>"): imports})
