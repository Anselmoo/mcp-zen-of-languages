"""Mapping module."""

from __future__ import annotations

from mcp_zen_of_languages.analyzers.mapping_models import LanguageDetectorMap
from mcp_zen_of_languages.analyzers.mapping_models import RuleBinding
from mcp_zen_of_languages.analyzers.mapping_models import RuleDetectorBinding
from mcp_zen_of_languages.frameworks.fastapi.detectors import FastapiAsyncIoDetector
from mcp_zen_of_languages.frameworks.fastapi.detectors import (
    FastapiBackgroundTasksDetector,
)
from mcp_zen_of_languages.frameworks.fastapi.detectors import (
    FastapiHttpExceptionDetector,
)
from mcp_zen_of_languages.frameworks.fastapi.detectors import (
    FastapiResponseModelDetector,
)
from mcp_zen_of_languages.frameworks.fastapi.detectors import FastapiStatusCodeDetector
from mcp_zen_of_languages.frameworks.fastapi.detectors import (
    FastapiVerbDecoratorDetector,
)
from mcp_zen_of_languages.frameworks.mapping_helpers import dogma_ids as _dogmas
from mcp_zen_of_languages.frameworks.mapping_helpers import (
    make_rule_config as _rule_config,
)
from mcp_zen_of_languages.frameworks.mapping_helpers import (
    projection_ids as _projection,
)
from mcp_zen_of_languages.frameworks.mapping_helpers import testing_ids as _testing


DETECTOR_MAP = LanguageDetectorMap(
    language="fastapi",
    bindings=[
        RuleDetectorBinding(
            detector_id="fastapi-005",
            detector_class=FastapiAsyncIoDetector,
            config_model=_rule_config("fastapi-005"),
            rules=[
                RuleBinding(
                    rule_id="fastapi-005",
                    dogma_ids=_dogmas("ZEN-PROPORTIONATE-COMPLEXITY"),
                    testing_ids=_testing("pytest"),
                )
            ],
            default_order=10,
        ),
        RuleDetectorBinding(
            detector_id="fastapi-004",
            detector_class=FastapiBackgroundTasksDetector,
            config_model=_rule_config("fastapi-004"),
            rules=[
                RuleBinding(
                    rule_id="fastapi-004",
                    dogma_ids=_dogmas("ZEN-RIGHT-ABSTRACTION"),
                    testing_ids=_testing("pytest"),
                )
            ],
            default_order=20,
        ),
        RuleDetectorBinding(
            detector_id="fastapi-003",
            detector_class=FastapiHttpExceptionDetector,
            config_model=_rule_config("fastapi-003"),
            rules=[
                RuleBinding(
                    rule_id="fastapi-003",
                    dogma_ids=_dogmas("ZEN-FAIL-FAST", "ZEN-EXPLICIT-INTENT"),
                    testing_ids=_testing("pytest"),
                    projection_ids=_projection("openapi"),
                    verified_projection_ids=[],
                )
            ],
            default_order=30,
        ),
        RuleDetectorBinding(
            detector_id="fastapi-001",
            detector_class=FastapiResponseModelDetector,
            config_model=_rule_config("fastapi-001"),
            rules=[
                RuleBinding(
                    rule_id="fastapi-001",
                    dogma_ids=_dogmas("ZEN-EXPLICIT-INTENT"),
                    testing_ids=_testing("pytest"),
                    projection_ids=_projection("openapi"),
                )
            ],
            default_order=40,
        ),
        RuleDetectorBinding(
            detector_id="fastapi-002",
            detector_class=FastapiStatusCodeDetector,
            config_model=_rule_config("fastapi-002"),
            rules=[
                RuleBinding(
                    rule_id="fastapi-002",
                    dogma_ids=_dogmas("ZEN-EXPLICIT-INTENT"),
                    testing_ids=_testing("pytest"),
                    projection_ids=_projection("openapi"),
                )
            ],
            default_order=50,
        ),
        RuleDetectorBinding(
            detector_id="fastapi-006",
            detector_class=FastapiVerbDecoratorDetector,
            config_model=_rule_config("fastapi-006"),
            rules=[
                RuleBinding(
                    rule_id="fastapi-006",
                    dogma_ids=_dogmas("ZEN-RIGHT-ABSTRACTION", "ZEN-EXPLICIT-INTENT"),
                    testing_ids=_testing("pytest"),
                    projection_ids=_projection("openapi"),
                )
            ],
            default_order=60,
        ),
    ],
)
