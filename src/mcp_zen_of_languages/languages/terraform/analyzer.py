"""Terraform analyzer for infrastructure-as-code best-practice checks."""

from __future__ import annotations

import re

from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from mcp_zen_of_languages.analyzers.pipeline import PipelineConfig
    from mcp_zen_of_languages.models import CyclomaticSummary

from mcp_zen_of_languages.analyzers.base import AnalysisContext
from mcp_zen_of_languages.analyzers.base import AnalyzerCapabilities
from mcp_zen_of_languages.analyzers.base import AnalyzerConfig
from mcp_zen_of_languages.analyzers.base import BaseAnalyzer
from mcp_zen_of_languages.analyzers.base import DetectionPipeline
from mcp_zen_of_languages.models import ParserResult


_BLOCK_DECL_RE = re.compile(
    r'^\s*(terraform|provider|module|variable|output|resource|data)\s+"([^"]+)"(?:\s+"([^"]+)")?\s*\{',
)
_MODULE_SOURCE_RE = re.compile(r'^\s*source\s*=\s*"([^"]+)"')


class TerraformAnalyzer(BaseAnalyzer):
    """Analyze Terraform HCL files with Terraform-specific detectors."""

    def __init__(
        self,
        config: AnalyzerConfig | None = None,
        pipeline_config: PipelineConfig | None = None,
    ) -> None:
        """Initialize analyzer with optional threshold and pipeline overrides."""
        self._pipeline_config = pipeline_config
        super().__init__(config=config)

    def default_config(self) -> AnalyzerConfig:
        """Return baseline analyzer configuration for Terraform."""
        return AnalyzerConfig()

    def language(self) -> str:
        """Return canonical language key."""
        return "terraform"

    def capabilities(self) -> AnalyzerCapabilities:
        """Declare support for lightweight block parsing and dependency analysis."""
        return AnalyzerCapabilities(supports_ast=True, supports_dependency_analysis=True)

    def parse_code(self, code: str) -> ParserResult | None:
        """Parse Terraform source into lightweight block declarations."""
        blocks: list[dict[str, str | int | None]] = []
        for idx, line in enumerate(code.splitlines(), start=1):
            if not (match := _BLOCK_DECL_RE.match(line.strip())):
                continue
            blocks.append(
                {
                    "block_type": match[1],
                    "label": match[2],
                    "label2": match[3],
                    "line": idx,
                },
            )
        return ParserResult(type="terraform", tree={"blocks": blocks})

    def compute_metrics(
        self,
        code: str,
        _ast_tree: ParserResult | None,
    ) -> tuple[CyclomaticSummary | None, float | None, int]:
        """Return Terraform line count; complexity metrics are not applicable."""
        return None, None, len(code.splitlines())

    def build_pipeline(self) -> DetectionPipeline:
        """Assemble Terraform detection pipeline from registry mappings."""
        return super().build_pipeline()

    def _build_dependency_analysis(self, context: AnalysisContext) -> object | None:
        """Extract module source references and build a dependency graph."""
        imports: list[str] = []
        for line in context.code.splitlines():
            stripped = line.strip()
            if stripped.startswith(("#", "//")):
                continue
            if match := _MODULE_SOURCE_RE.match(stripped):
                imports.append(match[1])
        if not imports:
            return None
        from mcp_zen_of_languages.metrics.dependency_graph import build_import_graph

        return build_import_graph({(context.path or "<current>"): imports})
