"""Universal dogma analysis exports."""

from mcp_zen_of_languages.dogmas.analyzer import UniversalDogmaAnalyzer
from mcp_zen_of_languages.dogmas.catalog import RULE_DOGMA_CATALOG
from mcp_zen_of_languages.dogmas.catalog import dogmas_for_rule_id
from mcp_zen_of_languages.dogmas.catalog import dogmas_for_rule_ids
from mcp_zen_of_languages.dogmas.interface import attach_dogma_analysis


__all__ = [
    "RULE_DOGMA_CATALOG",
    "UniversalDogmaAnalyzer",
    "attach_dogma_analysis",
    "dogmas_for_rule_id",
    "dogmas_for_rule_ids",
]
