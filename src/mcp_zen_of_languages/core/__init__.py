"""Core universal zen detector contracts."""

from mcp_zen_of_languages.core.detector import DOGMA_RULE_IDS
from mcp_zen_of_languages.core.detector import LanguageAdapter
from mcp_zen_of_languages.core.detector import ReporterInterface
from mcp_zen_of_languages.core.detector import UniversalZenDetector
from mcp_zen_of_languages.core.universal_dogmas import ALL_DOGMA_IDS
from mcp_zen_of_languages.core.universal_dogmas import TESTING_STRATEGY_IDS
from mcp_zen_of_languages.core.universal_dogmas import TESTING_TACTICS_IDS
from mcp_zen_of_languages.core.universal_dogmas import UNIVERSAL_DOGMA_IDS
from mcp_zen_of_languages.core.universal_dogmas import DogmaCatalogue
from mcp_zen_of_languages.core.universal_dogmas import DogmaFamily
from mcp_zen_of_languages.core.universal_dogmas import DogmaFamilyEntry
from mcp_zen_of_languages.core.universal_dogmas import TestingStrategyDogmaID
from mcp_zen_of_languages.core.universal_dogmas import TestingTacticsDogmaID
from mcp_zen_of_languages.core.universal_dogmas import UniversalDogmaID
from mcp_zen_of_languages.core.universal_dogmas import build_dogma_catalogue
from mcp_zen_of_languages.core.universal_dogmas import dogmas_for_rule
from mcp_zen_of_languages.core.universal_dogmas import dogmas_for_rule_ids
from mcp_zen_of_languages.core.universal_dogmas import infer_dogmas_for_principle
from mcp_zen_of_languages.core.universal_dogmas import resolve_strategy_dogma
from mcp_zen_of_languages.core.universal_dogmas import resolve_tactics_dogma


__all__ = [
    "ALL_DOGMA_IDS",
    "DOGMA_RULE_IDS",
    "TESTING_STRATEGY_IDS",
    "TESTING_TACTICS_IDS",
    "UNIVERSAL_DOGMA_IDS",
    "DogmaCatalogue",
    "DogmaFamily",
    "DogmaFamilyEntry",
    "LanguageAdapter",
    "ReporterInterface",
    "TestingStrategyDogmaID",
    "TestingTacticsDogmaID",
    "UniversalDogmaID",
    "UniversalZenDetector",
    "build_dogma_catalogue",
    "dogmas_for_rule",
    "dogmas_for_rule_ids",
    "infer_dogmas_for_principle",
    "resolve_strategy_dogma",
    "resolve_tactics_dogma",
]
