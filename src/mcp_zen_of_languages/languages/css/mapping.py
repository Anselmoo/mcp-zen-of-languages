"""Mapping module."""

from __future__ import annotations

from mcp_zen_of_languages.analyzers.mapping_models import DetectorBinding
from mcp_zen_of_languages.analyzers.mapping_models import LanguageDetectorMap
from mcp_zen_of_languages.core.universal_dogmas import UNIVERSAL_DOGMA_IDS
from mcp_zen_of_languages.languages.configs import CssColorLiteralConfig
from mcp_zen_of_languages.languages.configs import CssGodStylesheetConfig
from mcp_zen_of_languages.languages.configs import CssImportChainConfig
from mcp_zen_of_languages.languages.configs import CssMagicPixelsConfig
from mcp_zen_of_languages.languages.configs import CssMediaQueryScaleConfig
from mcp_zen_of_languages.languages.configs import CssSpecificityConfig
from mcp_zen_of_languages.languages.configs import CssVendorPrefixConfig
from mcp_zen_of_languages.languages.configs import CssZIndexScaleConfig
from mcp_zen_of_languages.languages.css.detectors import CssColorLiteralDetector
from mcp_zen_of_languages.languages.css.detectors import CssGodStylesheetDetector
from mcp_zen_of_languages.languages.css.detectors import CssImportChainDetector
from mcp_zen_of_languages.languages.css.detectors import CssMagicPixelsDetector
from mcp_zen_of_languages.languages.css.detectors import CssMediaQueryScaleDetector
from mcp_zen_of_languages.languages.css.detectors import CssSpecificityDetector
from mcp_zen_of_languages.languages.css.detectors import CssVendorPrefixDetector
from mcp_zen_of_languages.languages.css.detectors import CssZIndexScaleDetector


FULL_DOGMA_IDS = list(UNIVERSAL_DOGMA_IDS)
DETECTOR_MAP = LanguageDetectorMap(
    language="css",
    bindings=[
        DetectorBinding(
            detector_id="css-001",
            detector_class=CssSpecificityDetector,
            config_model=CssSpecificityConfig,
            rule_ids=["css-001"],
            universal_dogma_ids=FULL_DOGMA_IDS,
            default_order=10,
        ),
        DetectorBinding(
            detector_id="css-002",
            detector_class=CssMagicPixelsDetector,
            config_model=CssMagicPixelsConfig,
            rule_ids=["css-002"],
            universal_dogma_ids=FULL_DOGMA_IDS,
            default_order=20,
        ),
        DetectorBinding(
            detector_id="css-003",
            detector_class=CssColorLiteralDetector,
            config_model=CssColorLiteralConfig,
            rule_ids=["css-003"],
            universal_dogma_ids=FULL_DOGMA_IDS,
            default_order=30,
        ),
        DetectorBinding(
            detector_id="css-004",
            detector_class=CssGodStylesheetDetector,
            config_model=CssGodStylesheetConfig,
            rule_ids=["css-004"],
            universal_dogma_ids=FULL_DOGMA_IDS,
            default_order=40,
        ),
        DetectorBinding(
            detector_id="css-005",
            detector_class=CssImportChainDetector,
            config_model=CssImportChainConfig,
            rule_ids=["css-005"],
            universal_dogma_ids=FULL_DOGMA_IDS,
            default_order=50,
        ),
        DetectorBinding(
            detector_id="css-006",
            detector_class=CssZIndexScaleDetector,
            config_model=CssZIndexScaleConfig,
            rule_ids=["css-006"],
            universal_dogma_ids=FULL_DOGMA_IDS,
            default_order=60,
        ),
        DetectorBinding(
            detector_id="css-007",
            detector_class=CssVendorPrefixDetector,
            config_model=CssVendorPrefixConfig,
            rule_ids=["css-007"],
            universal_dogma_ids=FULL_DOGMA_IDS,
            default_order=70,
        ),
        DetectorBinding(
            detector_id="css-008",
            detector_class=CssMediaQueryScaleDetector,
            config_model=CssMediaQueryScaleConfig,
            rule_ids=["css-008"],
            universal_dogma_ids=FULL_DOGMA_IDS,
            default_order=80,
        ),
    ],
)
