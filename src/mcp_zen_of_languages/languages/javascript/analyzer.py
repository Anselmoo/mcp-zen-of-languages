"""JavaScript analyzer implementation for detecting idiomatic JS violations.

Provides a rule-driven analysis pipeline for JavaScript source files, scanning
for anti-patterns such as ``var`` usage, loose equality, callback hell, and
missing async error handling that compromise browser and Node.js runtime safety.

See Also:
    [`BaseAnalyzer`][mcp_zen_of_languages.analyzers.base.BaseAnalyzer]: Template Method
    base class defining the analysis algorithm skeleton.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from mcp_zen_of_languages.models import CyclomaticSummary, ParserResult
    from mcp_zen_of_languages.analyzers.pipeline import PipelineConfig

from mcp_zen_of_languages.analyzers.base import (
    AnalysisContext,
    AnalyzerConfig,
    BaseAnalyzer,
    DetectionPipeline,
)


class JavaScriptAnalyzer(BaseAnalyzer):
    """JavaScript analyzer using rule-driven detection pipeline.

    Orchestrates parsing, metric computation, and violation detection for
    JavaScript source code.  Because JavaScript lacks a Python-accessible AST
    library, parsing returns ``None`` and detection relies on regex-based
    pattern scanning performed by individual detectors in the pipeline.

    Attributes:
        _pipeline_config: Optional overrides merged into the default detector
            configuration at pipeline-build time.

    See Also:
        [`detectors`][mcp_zen_of_languages.languages.javascript.detectors]: Individual
        violation detectors wired into this analyzer's pipeline.
    """

    def __init__(
        self,
        config: AnalyzerConfig | None = None,
        pipeline_config: PipelineConfig | None = None,
    ):
        """Initialize the JavaScript analyzer with optional configuration.

        Args:
            config: Threshold settings controlling detector sensitivity such as
                maximum callback nesting depth and function length limits.
            pipeline_config: Optional overrides that are merged on top of
                rule-derived detector defaults, allowing per-project tuning
                via ``zen-config.yaml``.
        """
        self._pipeline_config = pipeline_config
        super().__init__(config=config)

    def default_config(self) -> AnalyzerConfig:
        """Return sensible default thresholds for JavaScript analysis.

        Returns:
            AnalyzerConfig: Baseline configuration used when no explicit config
            is supplied by the caller or the ``zen-config.yaml`` file.
        """
        return AnalyzerConfig()

    def language(self) -> str:
        """Return ``'javascript'`` as the language key for factory lookup.

        Returns:
            str: The literal ``'javascript'`` identifier used by
            [`AnalyzerFactory`][mcp_zen_of_languages.analyzers.analyzer_factory.AnalyzerFactory].
        """
        return "javascript"

    def parse_code(self, code: str) -> ParserResult | None:
        """Attempt to parse JavaScript source into a structured AST.

        Currently returns ``None`` because no Python-native JS parser is
        integrated.  Detection therefore relies on regex-based line scanning
        inside each detector.

        Args:
            code: Raw JavaScript source text to parse.

        Returns:
            ParserResult | None: Always ``None`` for JavaScript; reserved for
            future tree-sitter integration.
        """
        return None

    def compute_metrics(
        self, code: str, ast_tree: ParserResult | None
    ) -> tuple[CyclomaticSummary | None, float | None, int]:
        """Compute source-level metrics for the JavaScript file.

        Without an AST, cyclomatic complexity and maintainability index
        cannot be calculated.  Only the raw line count is returned.

        Args:
            code: Raw JavaScript source text.
            ast_tree: Parsed AST (always ``None`` for JavaScript today).

        Returns:
            tuple[CyclomaticSummary | None, float | None, int]: A three-element
            tuple of ``(None, None, line_count)``.
        """
        return None, None, len(code.splitlines())

    def build_pipeline(self) -> DetectionPipeline:
        """Build the JavaScript violation-detection pipeline.

        Delegates to the base class, which assembles detectors from the
        registry for the ``'javascript'`` language key and applies any
        pipeline overrides from ``zen-config.yaml``.

        Returns:
            DetectionPipeline: Fully-configured pipeline of JS detectors.
        """
        return super().build_pipeline()

    def _build_dependency_analysis(self, context: AnalysisContext) -> object | None:
        """Build cross-file dependency data for JavaScript imports.

        Not yet implemented for JavaScript; returns ``None``.  Future versions
        may parse ``import``/``require`` statements to detect circular
        dependencies and feature-envy patterns.

        Args:
            context: Current analysis context with source text and metrics.

        Returns:
            object | None: Always ``None``; reserved for future cross-file analysis.
        """
        return None
