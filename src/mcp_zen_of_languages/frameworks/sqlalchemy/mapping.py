"""Mapping module."""

from __future__ import annotations

from mcp_zen_of_languages.analyzers.mapping_models import LanguageDetectorMap
from mcp_zen_of_languages.analyzers.mapping_models import RuleBinding
from mcp_zen_of_languages.analyzers.mapping_models import RuleDetectorBinding
from mcp_zen_of_languages.frameworks.mapping_helpers import dogma_ids as _dogmas
from mcp_zen_of_languages.frameworks.mapping_helpers import (
    make_rule_config as _rule_config,
)
from mcp_zen_of_languages.frameworks.mapping_helpers import (
    projection_ids as _projection,
)
from mcp_zen_of_languages.frameworks.mapping_helpers import testing_ids as _testing
from mcp_zen_of_languages.frameworks.sqlalchemy.detectors import (
    SqlalchemyBulkInsertDetector,
)
from mcp_zen_of_languages.frameworks.sqlalchemy.detectors import (
    SqlalchemyDeclarativeBaseDetector,
)
from mcp_zen_of_languages.frameworks.sqlalchemy.detectors import (
    SqlalchemyMappedColumnDetector,
)
from mcp_zen_of_languages.frameworks.sqlalchemy.detectors import (
    SqlalchemyParameterizedTextDetector,
)
from mcp_zen_of_languages.frameworks.sqlalchemy.detectors import (
    SqlalchemyRelationshipLoadingDetector,
)
from mcp_zen_of_languages.frameworks.sqlalchemy.detectors import (
    SqlalchemySessionScopeDetector,
)


DETECTOR_MAP = LanguageDetectorMap(
    language="sqlalchemy",
    bindings=[
        RuleDetectorBinding(
            detector_id="sqlalchemy-001",
            detector_class=SqlalchemyParameterizedTextDetector,
            config_model=_rule_config("sqlalchemy-001"),
            rules=[
                RuleBinding(
                    rule_id="sqlalchemy-001",
                    dogma_ids=_dogmas("ZEN-STRICT-FENCES", "ZEN-FAIL-FAST"),
                    testing_ids=_testing("pytest"),
                    projection_ids=_projection("sql"),
                )
            ],
            default_order=10,
        ),
        RuleDetectorBinding(
            detector_id="sqlalchemy-002",
            detector_class=SqlalchemySessionScopeDetector,
            config_model=_rule_config("sqlalchemy-002"),
            rules=[
                RuleBinding(
                    rule_id="sqlalchemy-002",
                    dogma_ids=_dogmas("ZEN-STRICT-FENCES", "ZEN-EXPLICIT-INTENT"),
                    testing_ids=_testing("pytest"),
                )
            ],
            default_order=20,
        ),
        RuleDetectorBinding(
            detector_id="sqlalchemy-003",
            detector_class=SqlalchemyMappedColumnDetector,
            config_model=_rule_config("sqlalchemy-003"),
            rules=[
                RuleBinding(
                    rule_id="sqlalchemy-003",
                    dogma_ids=_dogmas("ZEN-RIGHT-ABSTRACTION"),
                    testing_ids=_testing("pytest"),
                )
            ],
            default_order=30,
        ),
        RuleDetectorBinding(
            detector_id="sqlalchemy-004",
            detector_class=SqlalchemyDeclarativeBaseDetector,
            config_model=_rule_config("sqlalchemy-004"),
            rules=[
                RuleBinding(
                    rule_id="sqlalchemy-004",
                    dogma_ids=_dogmas("ZEN-RIGHT-ABSTRACTION"),
                    testing_ids=_testing("pytest"),
                )
            ],
            default_order=40,
        ),
        RuleDetectorBinding(
            detector_id="sqlalchemy-005",
            detector_class=SqlalchemyRelationshipLoadingDetector,
            config_model=_rule_config("sqlalchemy-005"),
            rules=[
                RuleBinding(
                    rule_id="sqlalchemy-005",
                    dogma_ids=_dogmas(
                        "ZEN-PROPORTIONATE-COMPLEXITY", "ZEN-EXPLICIT-INTENT"
                    ),
                    testing_ids=_testing("pytest"),
                    projection_ids=_projection("sql"),
                    verified_projection_ids=[],
                )
            ],
            default_order=50,
        ),
        RuleDetectorBinding(
            detector_id="sqlalchemy-006",
            detector_class=SqlalchemyBulkInsertDetector,
            config_model=_rule_config("sqlalchemy-006"),
            rules=[
                RuleBinding(
                    rule_id="sqlalchemy-006",
                    dogma_ids=_dogmas("ZEN-PROPORTIONATE-COMPLEXITY"),
                    testing_ids=_testing("pytest"),
                )
            ],
            default_order=60,
        ),
    ],
)
