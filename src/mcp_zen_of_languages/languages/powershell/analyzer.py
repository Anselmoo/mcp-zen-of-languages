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

_IMPORT_MODULE_RE = re.compile(r"^Import-Module\s+(\S+)", re.IGNORECASE)
_DOT_SOURCE_RE = re.compile(r"""^\.\s+['"]?([^\s'"]+)['"]?""")


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
    ) -> None:
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

    def capabilities(self) -> AnalyzerCapabilities:
        """Declare support for Import-Module/dot-source dependency extraction."""
        return AnalyzerCapabilities(supports_dependency_analysis=True)

    def parse_code(self, _code: str) -> ParserResult | None:
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
        self,
        code: str,
        _ast_tree: ParserResult | None,
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
        """Extract ``Import-Module`` and dot-sourcing dependencies.

        Args:
            context: Current analysis context with source text and metrics.

        Returns:
            DependencyAnalysis with module dependency edges, or ``None`` when none found.
        """
        imports: list[str] = []
        for line in context.code.splitlines():
            stripped = line.strip()
            if stripped.startswith("#"):
                continue
            m = _IMPORT_MODULE_RE.match(stripped)
            if m:
                imports.append(m.group(1))
                continue
            m = _DOT_SOURCE_RE.match(stripped)
            if m:
                imports.append(m.group(1))
        if not imports:
            return None
        from mcp_zen_of_languages.metrics.dependency_graph import build_import_graph

        return build_import_graph({(context.path or "<current>"): imports})
