"""Mapping module."""

from __future__ import annotations

from mcp_zen_of_languages.analyzers.mapping_models import (
    DetectorBinding,
    LanguageDetectorMap,
)
from mcp_zen_of_languages.languages.configs import (
    CssColorLiteralConfig,
    CssGodStylesheetConfig,
    CssImportChainConfig,
    CssMagicPixelsConfig,
    CssMediaQueryScaleConfig,
    CssSpecificityConfig,
    CssVendorPrefixConfig,
    CssZIndexScaleConfig,
)
from mcp_zen_of_languages.languages.css.detectors import (
    CssColorLiteralDetector,
    CssGodStylesheetDetector,
    CssImportChainDetector,
    CssMagicPixelsDetector,
    CssMediaQueryScaleDetector,
    CssSpecificityDetector,
    CssVendorPrefixDetector,
    CssZIndexScaleDetector,
)

DETECTOR_MAP = LanguageDetectorMap(
    language="css",
    bindings=[
        DetectorBinding(
            detector_id="css-001",
            detector_class=CssSpecificityDetector,
            config_model=CssSpecificityConfig,
            rule_ids=["css-001"],
            default_order=10,
        ),
        DetectorBinding(
            detector_id="css-002",
            detector_class=CssMagicPixelsDetector,
            config_model=CssMagicPixelsConfig,
            rule_ids=["css-002"],
            default_order=20,
        ),
        DetectorBinding(
            detector_id="css-003",
            detector_class=CssColorLiteralDetector,
            config_model=CssColorLiteralConfig,
            rule_ids=["css-003"],
            default_order=30,
        ),
        DetectorBinding(
            detector_id="css-004",
            detector_class=CssGodStylesheetDetector,
            config_model=CssGodStylesheetConfig,
            rule_ids=["css-004"],
            default_order=40,
        ),
        DetectorBinding(
            detector_id="css-005",
            detector_class=CssImportChainDetector,
            config_model=CssImportChainConfig,
            rule_ids=["css-005"],
            default_order=50,
        ),
        DetectorBinding(
            detector_id="css-006",
            detector_class=CssZIndexScaleDetector,
            config_model=CssZIndexScaleConfig,
            rule_ids=["css-006"],
            default_order=60,
        ),
        DetectorBinding(
            detector_id="css-007",
            detector_class=CssVendorPrefixDetector,
            config_model=CssVendorPrefixConfig,
            rule_ids=["css-007"],
            default_order=70,
        ),
        DetectorBinding(
            detector_id="css-008",
            detector_class=CssMediaQueryScaleDetector,
            config_model=CssMediaQueryScaleConfig,
            rule_ids=["css-008"],
            default_order=80,
        ),
    ],
)
