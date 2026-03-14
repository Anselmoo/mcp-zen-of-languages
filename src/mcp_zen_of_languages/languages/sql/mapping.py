"""SQL detector-to-rule binding map."""

from __future__ import annotations

from mcp_zen_of_languages.analyzers.mapping_models import LanguageDetectorMap
from mcp_zen_of_languages.analyzers.mapping_models import RuleBinding
from mcp_zen_of_languages.analyzers.mapping_models import RuleDetectorBinding
from mcp_zen_of_languages.languages.configs import SqlAliasClarityConfig
from mcp_zen_of_languages.languages.configs import SqlAnsi89JoinConfig
from mcp_zen_of_languages.languages.configs import SqlDynamicSqlConfig
from mcp_zen_of_languages.languages.configs import SqlImplicitJoinCoercionConfig
from mcp_zen_of_languages.languages.configs import SqlInsertColumnListConfig
from mcp_zen_of_languages.languages.configs import SqlNolockConfig
from mcp_zen_of_languages.languages.configs import SqlSelectStarConfig
from mcp_zen_of_languages.languages.configs import SqlTransactionBoundaryConfig
from mcp_zen_of_languages.languages.configs import SqlUnboundedQueryConfig
from mcp_zen_of_languages.languages.sql.detectors import SqlAliasClarityDetector
from mcp_zen_of_languages.languages.sql.detectors import SqlAnsi89JoinDetector
from mcp_zen_of_languages.languages.sql.detectors import SqlDynamicSqlDetector
from mcp_zen_of_languages.languages.sql.detectors import SqlImplicitJoinCoercionDetector
from mcp_zen_of_languages.languages.sql.detectors import SqlInsertColumnListDetector
from mcp_zen_of_languages.languages.sql.detectors import SqlNolockDetector
from mcp_zen_of_languages.languages.sql.detectors import SqlSelectStarDetector
from mcp_zen_of_languages.languages.sql.detectors import SqlTransactionBoundaryDetector
from mcp_zen_of_languages.languages.sql.detectors import SqlUnboundedQueryDetector


def _dogmas(*dogma_ids: str) -> list[str]:
    """Return explicit universal dogma ids for the binding."""
    return list(dogma_ids)


DETECTOR_MAP = LanguageDetectorMap(
    language="sql",
    bindings=[
        RuleDetectorBinding(
            detector_id="sql-001",
            detector_class=SqlSelectStarDetector,
            config_model=SqlSelectStarConfig,
            rules=[
                RuleBinding(
                    rule_id="sql-001",
                    dogma_ids=_dogmas(
                        "ZEN-PROPORTIONATE-COMPLEXITY", "ZEN-EXPLICIT-INTENT"
                    ),
                )
            ],
            default_order=10,
        ),
        RuleDetectorBinding(
            detector_id="sql-002",
            detector_class=SqlInsertColumnListDetector,
            config_model=SqlInsertColumnListConfig,
            rules=[
                RuleBinding(
                    rule_id="sql-002",
                    dogma_ids=_dogmas("ZEN-EXPLICIT-INTENT", "ZEN-VISIBLE-STATE"),
                )
            ],
            default_order=20,
        ),
        RuleDetectorBinding(
            detector_id="sql-003",
            detector_class=SqlDynamicSqlDetector,
            config_model=SqlDynamicSqlConfig,
            rules=[
                RuleBinding(rule_id="sql-003", dogma_ids=_dogmas("ZEN-STRICT-FENCES"))
            ],
            default_order=30,
        ),
        RuleDetectorBinding(
            detector_id="sql-004",
            detector_class=SqlNolockDetector,
            config_model=SqlNolockConfig,
            rules=[
                RuleBinding(rule_id="sql-004", dogma_ids=_dogmas("ZEN-EXPLICIT-INTENT"))
            ],
            default_order=40,
        ),
        RuleDetectorBinding(
            detector_id="sql-005",
            detector_class=SqlImplicitJoinCoercionDetector,
            config_model=SqlImplicitJoinCoercionConfig,
            rules=[
                RuleBinding(
                    rule_id="sql-005",
                    dogma_ids=_dogmas(
                        "ZEN-PROPORTIONATE-COMPLEXITY", "ZEN-EXPLICIT-INTENT"
                    ),
                )
            ],
            default_order=50,
        ),
        RuleDetectorBinding(
            detector_id="sql-006",
            detector_class=SqlUnboundedQueryDetector,
            config_model=SqlUnboundedQueryConfig,
            rules=[
                RuleBinding(
                    rule_id="sql-006", dogma_ids=_dogmas("ZEN-PROPORTIONATE-COMPLEXITY")
                )
            ],
            default_order=60,
        ),
        RuleDetectorBinding(
            detector_id="sql-007",
            detector_class=SqlAliasClarityDetector,
            config_model=SqlAliasClarityConfig,
            rules=[
                RuleBinding(
                    rule_id="sql-007",
                    dogma_ids=_dogmas("ZEN-EXPLICIT-INTENT", "ZEN-UNAMBIGUOUS-NAME"),
                )
            ],
            default_order=70,
        ),
        RuleDetectorBinding(
            detector_id="sql-008",
            detector_class=SqlTransactionBoundaryDetector,
            config_model=SqlTransactionBoundaryConfig,
            rules=[
                RuleBinding(rule_id="sql-008", dogma_ids=_dogmas("ZEN-EXPLICIT-INTENT"))
            ],
            default_order=80,
        ),
        RuleDetectorBinding(
            detector_id="sql-009",
            detector_class=SqlAnsi89JoinDetector,
            config_model=SqlAnsi89JoinConfig,
            rules=[
                RuleBinding(
                    rule_id="sql-009",
                    dogma_ids=_dogmas("ZEN-UNAMBIGUOUS-NAME", "ZEN-EXPLICIT-INTENT"),
                )
            ],
            default_order=90,
        ),
    ],
)
