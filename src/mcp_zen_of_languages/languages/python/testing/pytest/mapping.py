"""Pytest testing-family overlays for Python detectors."""

from __future__ import annotations

from mcp_zen_of_languages.analyzers.mapping_models import LanguageDetectorMap
from mcp_zen_of_languages.analyzers.mapping_models import RuleBinding
from mcp_zen_of_languages.analyzers.mapping_models import RuleDetectorBinding
from mcp_zen_of_languages.languages.configs import LineLengthConfig
from mcp_zen_of_languages.languages.python.detectors import LineLengthDetector


DETECTOR_MAP = LanguageDetectorMap(
    language="python",
    bindings=[
        RuleDetectorBinding(
            detector_id="line_length",
            detector_class=LineLengthDetector,
            config_model=LineLengthConfig,
            rules=[RuleBinding(rule_id="python-001")],
        ),
    ],
)
