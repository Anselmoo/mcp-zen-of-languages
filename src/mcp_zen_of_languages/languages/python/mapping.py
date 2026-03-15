"""Mapping module."""

from __future__ import annotations

from mcp_zen_of_languages.analyzers.base import AnalyzerConfig
from mcp_zen_of_languages.analyzers.mapping_models import DetectorGearbox
from mcp_zen_of_languages.analyzers.mapping_models import LanguageDetectorMap
from mcp_zen_of_languages.analyzers.mapping_models import NonRuleDetectorBinding
from mcp_zen_of_languages.analyzers.mapping_models import RuleBinding
from mcp_zen_of_languages.analyzers.mapping_models import RuleDetectorBinding
from mcp_zen_of_languages.languages.configs import BareExceptConfig
from mcp_zen_of_languages.languages.configs import CircularDependencyConfig
from mcp_zen_of_languages.languages.configs import ClassSizeConfig
from mcp_zen_of_languages.languages.configs import ComplexOneLinersConfig
from mcp_zen_of_languages.languages.configs import ConsistencyConfig
from mcp_zen_of_languages.languages.configs import ContextManagerConfig
from mcp_zen_of_languages.languages.configs import CyclomaticComplexityConfig
from mcp_zen_of_languages.languages.configs import DeepInheritanceConfig
from mcp_zen_of_languages.languages.configs import DocstringConfig
from mcp_zen_of_languages.languages.configs import DuplicateImplementationConfig
from mcp_zen_of_languages.languages.configs import ExplicitnessConfig
from mcp_zen_of_languages.languages.configs import FeatureEnvyConfig
from mcp_zen_of_languages.languages.configs import GodClassConfig
from mcp_zen_of_languages.languages.configs import LineLengthConfig
from mcp_zen_of_languages.languages.configs import LongFunctionConfig
from mcp_zen_of_languages.languages.configs import MagicMethodConfig
from mcp_zen_of_languages.languages.configs import MagicNumberConfig
from mcp_zen_of_languages.languages.configs import NameStyleConfig
from mcp_zen_of_languages.languages.configs import NamespaceConfig
from mcp_zen_of_languages.languages.configs import NestingDepthConfig
from mcp_zen_of_languages.languages.configs import PythonComplexUndocumentedConfig
from mcp_zen_of_languages.languages.configs import PythonExplicitSilenceConfig
from mcp_zen_of_languages.languages.configs import PythonIdiomConfig
from mcp_zen_of_languages.languages.configs import PythonPracticalityConfig
from mcp_zen_of_languages.languages.configs import PythonPrematureImplConfig
from mcp_zen_of_languages.languages.configs import PythonSimpleDocumentedConfig
from mcp_zen_of_languages.languages.configs import PythonTodoStubConfig
from mcp_zen_of_languages.languages.configs import ShortVariableNamesConfig
from mcp_zen_of_languages.languages.configs import SparseCodeConfig
from mcp_zen_of_languages.languages.configs import StarImportConfig
from mcp_zen_of_languages.languages.python.detectors import BareExceptDetector
from mcp_zen_of_languages.languages.python.detectors import CircularDependencyDetector
from mcp_zen_of_languages.languages.python.detectors import ClassSizeDetector
from mcp_zen_of_languages.languages.python.detectors import ComplexOneLinersDetector
from mcp_zen_of_languages.languages.python.detectors import ConsistencyDetector
from mcp_zen_of_languages.languages.python.detectors import ContextManagerDetector
from mcp_zen_of_languages.languages.python.detectors import CyclomaticComplexityDetector
from mcp_zen_of_languages.languages.python.detectors import DeepInheritanceDetector
from mcp_zen_of_languages.languages.python.detectors import DocstringDetector
from mcp_zen_of_languages.languages.python.detectors import (
    DuplicateImplementationDetector,
)
from mcp_zen_of_languages.languages.python.detectors import ExplicitnessDetector
from mcp_zen_of_languages.languages.python.detectors import FeatureEnvyDetector
from mcp_zen_of_languages.languages.python.detectors import GodClassDetector
from mcp_zen_of_languages.languages.python.detectors import LineLengthDetector
from mcp_zen_of_languages.languages.python.detectors import LongFunctionDetector
from mcp_zen_of_languages.languages.python.detectors import MagicMethodDetector
from mcp_zen_of_languages.languages.python.detectors import MagicNumberDetector
from mcp_zen_of_languages.languages.python.detectors import NameStyleDetector
from mcp_zen_of_languages.languages.python.detectors import NamespaceUsageDetector
from mcp_zen_of_languages.languages.python.detectors import NestingDepthDetector
from mcp_zen_of_languages.languages.python.detectors import (
    PythonComplexUndocumentedDetector,
)
from mcp_zen_of_languages.languages.python.detectors import (
    PythonExplicitSilenceDetector,
)
from mcp_zen_of_languages.languages.python.detectors import PythonIdiomDetector
from mcp_zen_of_languages.languages.python.detectors import PythonPracticalityDetector
from mcp_zen_of_languages.languages.python.detectors import PythonPrematureImplDetector
from mcp_zen_of_languages.languages.python.detectors import (
    PythonSimpleDocumentedDetector,
)
from mcp_zen_of_languages.languages.python.detectors import PythonTodoStubDetector
from mcp_zen_of_languages.languages.python.detectors import ShortVariableNamesDetector
from mcp_zen_of_languages.languages.python.detectors import SparseCodeDetector
from mcp_zen_of_languages.languages.python.detectors import StarImportDetector


def _dogmas(*dogma_ids: str) -> list[str]:
    """Return explicit universal dogma ids for the binding."""
    return list(dogma_ids)


DETECTOR_MAP = LanguageDetectorMap(
    language="python",
    bindings=[
        NonRuleDetectorBinding(
            detector_id="analyzer_defaults",
            detector_class=NameStyleDetector,
            config_model=AnalyzerConfig,
            default_order=0,
            enabled_by_default=False,
        ),
        RuleDetectorBinding(
            detector_id="name_style",
            detector_class=NameStyleDetector,
            config_model=NameStyleConfig,
            rules=[
                RuleBinding(
                    rule_id="python-001", dogma_ids=_dogmas("ZEN-UNAMBIGUOUS-NAME")
                )
            ],
            default_order=10,
        ),
        RuleDetectorBinding(
            detector_id="cyclomatic_complexity",
            detector_class=CyclomaticComplexityDetector,
            config_model=CyclomaticComplexityConfig,
            rules=[
                RuleBinding(
                    rule_id="python-003",
                    dogma_ids=_dogmas(
                        "ZEN-PROPORTIONATE-COMPLEXITY",
                        "ZEN-RETURN-EARLY",
                        "ZEN-RIGHT-ABSTRACTION",
                    ),
                    testing_ids=["pytest"],
                    projection_ids=["go", "typescript"],
                    verified_projection_ids=["go"],
                )
            ],
            default_order=20,
        ),
        RuleDetectorBinding(
            detector_id="complex_one_liners",
            detector_class=ComplexOneLinersDetector,
            config_model=ComplexOneLinersConfig,
            rules=[
                RuleBinding(
                    rule_id="python-003",
                    dogma_ids=_dogmas(
                        "ZEN-PROPORTIONATE-COMPLEXITY",
                        "ZEN-RETURN-EARLY",
                        "ZEN-RIGHT-ABSTRACTION",
                    ),
                )
            ],
            default_order=25,
        ),
        RuleDetectorBinding(
            detector_id="nesting_depth",
            detector_class=NestingDepthDetector,
            config_model=NestingDepthConfig,
            rules=[
                RuleBinding(
                    rule_id="python-005",
                    dogma_ids=_dogmas("ZEN-RETURN-EARLY"),
                    testing_ids=["pytest"],
                    projection_ids=["go", "typescript"],
                    verified_projection_ids=["go"],
                )
            ],
            default_order=30,
        ),
        RuleDetectorBinding(
            detector_id="long_functions",
            detector_class=LongFunctionDetector,
            config_model=LongFunctionConfig,
            rules=[
                RuleBinding(
                    rule_id="python-007", dogma_ids=_dogmas("ZEN-UNAMBIGUOUS-NAME")
                )
            ],
            default_order=40,
        ),
        RuleDetectorBinding(
            detector_id="short_variable_names",
            detector_class=ShortVariableNamesDetector,
            config_model=ShortVariableNamesConfig,
            rules=[
                RuleBinding(
                    rule_id="python-007", dogma_ids=_dogmas("ZEN-UNAMBIGUOUS-NAME")
                )
            ],
            default_order=45,
        ),
        RuleDetectorBinding(
            detector_id="god_classes",
            detector_class=GodClassDetector,
            config_model=GodClassConfig,
            rules=[
                RuleBinding(
                    rule_id="python-004",
                    dogma_ids=_dogmas(
                        "ZEN-RIGHT-ABSTRACTION", "ZEN-PROPORTIONATE-COMPLEXITY"
                    ),
                )
            ],
            default_order=50,
        ),
        RuleDetectorBinding(
            detector_id="magic_methods",
            detector_class=MagicMethodDetector,
            config_model=MagicMethodConfig,
            rules=[
                RuleBinding(
                    rule_id="python-002", dogma_ids=_dogmas("ZEN-EXPLICIT-INTENT")
                )
            ],
            default_order=60,
        ),
        RuleDetectorBinding(
            detector_id="circular_dependencies",
            detector_class=CircularDependencyDetector,
            config_model=CircularDependencyConfig,
            rules=[
                RuleBinding(
                    rule_id="python-004",
                    dogma_ids=_dogmas(
                        "ZEN-RIGHT-ABSTRACTION", "ZEN-PROPORTIONATE-COMPLEXITY"
                    ),
                )
            ],
            default_order=70,
        ),
        RuleDetectorBinding(
            detector_id="deep_inheritance",
            detector_class=DeepInheritanceDetector,
            config_model=DeepInheritanceConfig,
            rules=[
                RuleBinding(
                    rule_id="python-004",
                    dogma_ids=_dogmas(
                        "ZEN-RIGHT-ABSTRACTION", "ZEN-PROPORTIONATE-COMPLEXITY"
                    ),
                )
            ],
            default_order=80,
        ),
        RuleDetectorBinding(
            detector_id="feature_envy",
            detector_class=FeatureEnvyDetector,
            config_model=FeatureEnvyConfig,
            rules=[
                RuleBinding(
                    rule_id="python-011",
                    dogma_ids=_dogmas("ZEN-RIGHT-ABSTRACTION", "ZEN-VISIBLE-STATE"),
                )
            ],
            default_order=90,
        ),
        RuleDetectorBinding(
            detector_id="duplicate_implementations",
            detector_class=DuplicateImplementationDetector,
            config_model=DuplicateImplementationConfig,
            rules=[
                RuleBinding(
                    rule_id="python-011",
                    dogma_ids=_dogmas("ZEN-RIGHT-ABSTRACTION", "ZEN-VISIBLE-STATE"),
                )
            ],
            default_order=100,
        ),
        RuleDetectorBinding(
            detector_id="class_size",
            detector_class=ClassSizeDetector,
            config_model=ClassSizeConfig,
            rules=[
                RuleBinding(
                    rule_id="python-007", dogma_ids=_dogmas("ZEN-UNAMBIGUOUS-NAME")
                )
            ],
            default_order=110,
        ),
        RuleDetectorBinding(
            detector_id="star_imports",
            detector_class=StarImportDetector,
            config_model=StarImportConfig,
            rules=[
                RuleBinding(
                    rule_id="python-002", dogma_ids=_dogmas("ZEN-EXPLICIT-INTENT")
                )
            ],
            default_order=120,
        ),
        RuleDetectorBinding(
            detector_id="magic_number",
            detector_class=MagicNumberDetector,
            config_model=MagicNumberConfig,
            rules=[
                RuleBinding(
                    rule_id="python-002", dogma_ids=_dogmas("ZEN-EXPLICIT-INTENT")
                )
            ],
            default_order=125,
        ),
        RuleDetectorBinding(
            detector_id="bare_except",
            detector_class=BareExceptDetector,
            config_model=BareExceptConfig,
            rules=[
                RuleBinding(
                    rule_id="python-009",
                    dogma_ids=_dogmas("ZEN-FAIL-FAST", "ZEN-EXPLICIT-INTENT"),
                    testing_ids=["pytest"],
                    projection_ids=["go"],
                )
            ],
            default_order=130,
        ),
        RuleDetectorBinding(
            detector_id="line_length",
            detector_class=LineLengthDetector,
            config_model=LineLengthConfig,
            rules=[
                RuleBinding(
                    rule_id="python-001",
                    dogma_ids=_dogmas("ZEN-UNAMBIGUOUS-NAME"),
                    testing_ids=["pytest"],
                    projection_ids=["go", "typescript"],
                    verified_projection_ids=["go"],
                )
            ],
            default_order=140,
        ),
        RuleDetectorBinding(
            detector_id="sparse_code",
            detector_class=SparseCodeDetector,
            config_model=SparseCodeConfig,
            rules=[
                RuleBinding(
                    rule_id="python-006",
                    dogma_ids=_dogmas("ZEN-UNAMBIGUOUS-NAME", "ZEN-VISIBLE-STATE"),
                )
            ],
            default_order=145,
        ),
        RuleDetectorBinding(
            detector_id="docstrings",
            detector_class=DocstringDetector,
            config_model=DocstringConfig,
            rules=[
                RuleBinding(
                    rule_id="python-007", dogma_ids=_dogmas("ZEN-UNAMBIGUOUS-NAME")
                )
            ],
            default_order=150,
        ),
        RuleDetectorBinding(
            detector_id="consistency",
            detector_class=ConsistencyDetector,
            config_model=ConsistencyConfig,
            rules=[
                RuleBinding(
                    rule_id="python-008",
                    dogma_ids=_dogmas("ZEN-EXPLICIT-INTENT", "ZEN-FAIL-FAST"),
                )
            ],
            default_order=155,
        ),
        RuleDetectorBinding(
            detector_id="context_manager",
            detector_class=ContextManagerDetector,
            config_model=ContextManagerConfig,
            rules=[
                RuleBinding(
                    rule_id="python-011",
                    dogma_ids=_dogmas("ZEN-RIGHT-ABSTRACTION", "ZEN-VISIBLE-STATE"),
                )
            ],
            default_order=160,
        ),
        RuleDetectorBinding(
            detector_id="explicitness",
            detector_class=ExplicitnessDetector,
            config_model=ExplicitnessConfig,
            rules=[
                RuleBinding(
                    rule_id="python-010", dogma_ids=_dogmas("ZEN-EXPLICIT-INTENT")
                )
            ],
            default_order=165,
        ),
        RuleDetectorBinding(
            detector_id="namespace_usage",
            detector_class=NamespaceUsageDetector,
            config_model=NamespaceConfig,
            rules=[
                RuleBinding(
                    rule_id="python-012",
                    dogma_ids=_dogmas("ZEN-STRICT-FENCES", "ZEN-UNAMBIGUOUS-NAME"),
                ),
                RuleBinding(
                    rule_id="python-020",
                    dogma_ids=_dogmas("ZEN-STRICT-FENCES", "ZEN-UNAMBIGUOUS-NAME"),
                ),
            ],
            default_order=170,
        ),
        RuleDetectorBinding(
            detector_id="python_practicality",
            detector_class=PythonPracticalityDetector,
            config_model=PythonPracticalityConfig,
            rules=[
                RuleBinding(
                    rule_id="python-013",
                    dogma_ids=_dogmas(
                        "ZEN-RIGHT-ABSTRACTION", "ZEN-PROPORTIONATE-COMPLEXITY"
                    ),
                )
            ],
            default_order=180,
        ),
        RuleDetectorBinding(
            detector_id="python_explicit_silence",
            detector_class=PythonExplicitSilenceDetector,
            config_model=PythonExplicitSilenceConfig,
            rules=[
                RuleBinding(
                    rule_id="python-014",
                    dogma_ids=_dogmas("ZEN-EXPLICIT-INTENT", "ZEN-FAIL-FAST"),
                )
            ],
            default_order=190,
        ),
        RuleDetectorBinding(
            detector_id="python_todo_stub",
            detector_class=PythonTodoStubDetector,
            config_model=PythonTodoStubConfig,
            rules=[
                RuleBinding(
                    rule_id="python-015",
                    dogma_ids=_dogmas("ZEN-RETURN-EARLY", "ZEN-RUTHLESS-DELETION"),
                )
            ],
            default_order=200,
        ),
        RuleDetectorBinding(
            detector_id="python_premature_impl",
            detector_class=PythonPrematureImplDetector,
            config_model=PythonPrematureImplConfig,
            rules=[
                RuleBinding(
                    rule_id="python-016",
                    dogma_ids=_dogmas(
                        "ZEN-RIGHT-ABSTRACTION",
                        "ZEN-FAIL-FAST",
                        "ZEN-RUTHLESS-DELETION",
                    ),
                )
            ],
            default_order=210,
        ),
        RuleDetectorBinding(
            detector_id="python_complex_undocumented",
            detector_class=PythonComplexUndocumentedDetector,
            config_model=PythonComplexUndocumentedConfig,
            rules=[
                RuleBinding(
                    rule_id="python-017", dogma_ids=_dogmas("ZEN-UNAMBIGUOUS-NAME")
                )
            ],
            default_order=220,
        ),
        RuleDetectorBinding(
            detector_id="python_simple_documented",
            detector_class=PythonSimpleDocumentedDetector,
            config_model=PythonSimpleDocumentedConfig,
            rules=[
                RuleBinding(
                    rule_id="python-018",
                    dogma_ids=_dogmas(
                        "ZEN-UNAMBIGUOUS-NAME", "ZEN-PROPORTIONATE-COMPLEXITY"
                    ),
                )
            ],
            default_order=230,
        ),
        RuleDetectorBinding(
            detector_id="python_idiom",
            detector_class=PythonIdiomDetector,
            config_model=PythonIdiomConfig,
            rules=[
                RuleBinding(
                    rule_id="python-019", dogma_ids=_dogmas("ZEN-RIGHT-ABSTRACTION")
                )
            ],
            default_order=240,
        ),
    ],
)

GEARBOX = DetectorGearbox(language="python")
GEARBOX.extend(DETECTOR_MAP.bindings)
DETECTOR_MAP = GEARBOX.build_map()
