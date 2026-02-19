"""PowerShell analyzer implementation for detecting PS scripting anti-patterns.

Provides a rule-driven analysis pipeline for PowerShell source files, scanning
for practices such as alias usage in scripts, ``Write-Host`` misuse, global
scope pollution, missing ``CmdletBinding``, and unapproved verbs that
compromise production PowerShell automation reliability.

See Also:
    [`BaseAnalyzer`][mcp_zen_of_languages.analyzers.base.BaseAnalyzer]: Template Method
    base class defining the analysis algorithm skeleton.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from mcp_zen_of_languages.analyzers.pipeline import PipelineConfig
    from mcp_zen_of_languages.models import CyclomaticSummary, ParserResult

from mcp_zen_of_languages.analyzers.base import (
    AnalysisContext,
    AnalyzerConfig,
    BaseAnalyzer,
    DetectionPipeline,
)


class PowerShellAnalyzer(BaseAnalyzer):
    """PowerShell analyzer using rule-driven detection pipeline.

    Orchestrates parsing, metric computation, and violation detection for
    PowerShell source code.  Because PowerShell lacks a Python-accessible AST
    library, parsing returns ``None`` and detection relies on regex-based
    pattern scanning performed by individual detectors in the pipeline.

    Attributes:
        _pipeline_config: Optional overrides merged into the default detector
            configuration at pipeline-build time.

    See Also:
        [`detectors`][mcp_zen_of_languages.languages.powershell.detectors]: Individual
        violation detectors wired into this analyzer's pipeline.
    """

    def __init__(
        self,
        config: AnalyzerConfig | None = None,
        pipeline_config: PipelineConfig | None = None,
    ):
        """Initialize the PowerShell analyzer with optional configuration.

        Args:
            config: Threshold settings controlling detector sensitivity such as
                approved verb lists and parameter validation requirements.
            pipeline_config: Optional overrides that are merged on top of
                rule-derived detector defaults, allowing per-project tuning
                via ``zen-config.yaml``.
        """
        self._pipeline_config = pipeline_config
        super().__init__(config=config)

    def default_config(self) -> AnalyzerConfig:
        """Return sensible default thresholds for PowerShell analysis.

        Returns:
            AnalyzerConfig: Baseline configuration used when no explicit config
            is supplied by the caller or the ``zen-config.yaml`` file.
        """
        return AnalyzerConfig()

    def language(self) -> str:
        """Return ``'powershell'`` as the language key for factory lookup.

        Returns:
            str: The literal ``'powershell'`` identifier used by
            [`AnalyzerFactory`][mcp_zen_of_languages.analyzers.analyzer_factory.AnalyzerFactory].
        """
        return "powershell"

    def parse_code(self, code: str) -> ParserResult | None:
        """Attempt to parse PowerShell source into a structured AST.

        Currently returns ``None`` because no Python-native PowerShell parser
        is integrated.  Detection relies on regex-based line scanning inside
        each detector.

        Args:
            code: Raw PowerShell source text to parse.

        Returns:
            ParserResult | None: Always ``None`` for PowerShell; reserved for
            future tree-sitter integration.
        """
        return None

    def compute_metrics(
        self, code: str, ast_tree: ParserResult | None
    ) -> tuple[CyclomaticSummary | None, float | None, int]:
        """Compute source-level metrics for the PowerShell file.

        Without an AST, cyclomatic complexity and maintainability index
        cannot be calculated.  Only the raw line count is returned.

        Args:
            code: Raw PowerShell source text.
            ast_tree: Parsed AST (always ``None`` for PowerShell today).

        Returns:
            tuple[CyclomaticSummary | None, float | None, int]: A three-element
            tuple of ``(None, None, line_count)``.
        """
        return None, None, len(code.splitlines())

    def build_pipeline(self) -> DetectionPipeline:
        """Build the PowerShell violation-detection pipeline.

        Delegates to the base class, which assembles detectors from the
        registry for the ``'powershell'`` language key and applies any
        pipeline overrides from ``zen-config.yaml``.

        Returns:
            DetectionPipeline: Fully-configured pipeline of PS detectors.
        """
        return super().build_pipeline()

    def _build_dependency_analysis(self, context: AnalysisContext) -> object | None:
        """Build cross-file dependency data for PowerShell module imports.

        Not yet implemented for PowerShell; returns ``None``.  Future versions
        may parse ``Import-Module`` and dot-sourcing to detect circular
        dependencies.

        Args:
            context: Current analysis context with source text and metrics.

        Returns:
            object | None: Always ``None``; reserved for future cross-file analysis.
        """
        return None
