"""Core universal zen detector contracts."""

from mcp_zen_of_languages.core.detector import (
    DOGMA_RULE_IDS,
    LanguageAdapter,
    ReporterInterface,
    UniversalZenDetector,
)
from mcp_zen_of_languages.core.universal_dogmas import (
    UniversalDogmaID,
    dogmas_for_rule,
    dogmas_for_rule_ids,
    infer_dogmas_for_principle,
)

__all__ = [
    "DOGMA_RULE_IDS",
    "LanguageAdapter",
    "ReporterInterface",
    "UniversalDogmaID",
    "UniversalZenDetector",
    "dogmas_for_rule",
    "dogmas_for_rule_ids",
    "infer_dogmas_for_principle",
]
