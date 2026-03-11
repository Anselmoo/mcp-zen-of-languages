"""Mapping module."""

from __future__ import annotations

from mcp_zen_of_languages.analyzers.base import AnalyzerConfig
from mcp_zen_of_languages.analyzers.mapping_models import DetectorBinding
from mcp_zen_of_languages.analyzers.mapping_models import DetectorGearbox
from mcp_zen_of_languages.analyzers.mapping_models import LanguageDetectorMap
from mcp_zen_of_languages.core.universal_dogmas import UNIVERSAL_DOGMA_IDS
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


FULL_DOGMA_IDS = list(UNIVERSAL_DOGMA_IDS)
DETECTOR_MAP = LanguageDetectorMap(
    language="python",
    bindings=[
        DetectorBinding(
            detector_id="analyzer_defaults",
            detector_class=NameStyleDetector,
            config_model=AnalyzerConfig,
            rule_ids=[],
            default_order=0,
            enabled_by_default=False,
        ),
        DetectorBinding(
            detector_id="name_style",
            detector_class=NameStyleDetector,
            config_model=NameStyleConfig,
            rule_ids=["python-001"],
            default_order=10,
        ),
        DetectorBinding(
            detector_id="cyclomatic_complexity",
            detector_class=CyclomaticComplexityDetector,
            config_model=CyclomaticComplexityConfig,
            rule_ids=["python-003"],
            default_order=20,
        ),
        DetectorBinding(
            detector_id="complex_one_liners",
            detector_class=ComplexOneLinersDetector,
            config_model=ComplexOneLinersConfig,
            rule_ids=["python-003"],
            default_order=25,
        ),
        DetectorBinding(
            detector_id="nesting_depth",
            detector_class=NestingDepthDetector,
            config_model=NestingDepthConfig,
            rule_ids=["python-005"],
            default_order=30,
        ),
        DetectorBinding(
            detector_id="long_functions",
            detector_class=LongFunctionDetector,
            config_model=LongFunctionConfig,
            rule_ids=["python-007"],
            default_order=40,
        ),
        DetectorBinding(
            detector_id="short_variable_names",
            detector_class=ShortVariableNamesDetector,
            config_model=ShortVariableNamesConfig,
            rule_ids=["python-007"],
            default_order=45,
        ),
        DetectorBinding(
            detector_id="god_classes",
            detector_class=GodClassDetector,
            config_model=GodClassConfig,
            rule_ids=["python-004"],
            default_order=50,
        ),
        DetectorBinding(
            detector_id="magic_methods",
            detector_class=MagicMethodDetector,
            config_model=MagicMethodConfig,
            rule_ids=["python-002"],
            default_order=60,
        ),
        DetectorBinding(
            detector_id="circular_dependencies",
            detector_class=CircularDependencyDetector,
            config_model=CircularDependencyConfig,
            rule_ids=["python-004"],
            default_order=70,
        ),
        DetectorBinding(
            detector_id="deep_inheritance",
            detector_class=DeepInheritanceDetector,
            config_model=DeepInheritanceConfig,
            rule_ids=["python-004"],
            default_order=80,
        ),
        DetectorBinding(
            detector_id="feature_envy",
            detector_class=FeatureEnvyDetector,
            config_model=FeatureEnvyConfig,
            rule_ids=["python-011"],
            default_order=90,
        ),
        DetectorBinding(
            detector_id="duplicate_implementations",
            detector_class=DuplicateImplementationDetector,
            config_model=DuplicateImplementationConfig,
            rule_ids=["python-011"],
            default_order=100,
        ),
        DetectorBinding(
            detector_id="class_size",
            detector_class=ClassSizeDetector,
            config_model=ClassSizeConfig,
            rule_ids=["python-007"],
            default_order=110,
        ),
        DetectorBinding(
            detector_id="star_imports",
            detector_class=StarImportDetector,
            config_model=StarImportConfig,
            rule_ids=["python-002"],
            default_order=120,
        ),
        DetectorBinding(
            detector_id="magic_number",
            detector_class=MagicNumberDetector,
            config_model=MagicNumberConfig,
            rule_ids=["python-002"],
            default_order=125,
        ),
        DetectorBinding(
            detector_id="bare_except",
            detector_class=BareExceptDetector,
            config_model=BareExceptConfig,
            rule_ids=["python-009"],
            default_order=130,
        ),
        DetectorBinding(
            detector_id="line_length",
            detector_class=LineLengthDetector,
            config_model=LineLengthConfig,
            rule_ids=["python-001"],
            default_order=140,
        ),
        DetectorBinding(
            detector_id="sparse_code",
            detector_class=SparseCodeDetector,
            config_model=SparseCodeConfig,
            rule_ids=["python-006"],
            default_order=145,
        ),
        DetectorBinding(
            detector_id="docstrings",
            detector_class=DocstringDetector,
            config_model=DocstringConfig,
            rule_ids=["python-007"],
            default_order=150,
        ),
        DetectorBinding(
            detector_id="consistency",
            detector_class=ConsistencyDetector,
            config_model=ConsistencyConfig,
            rule_ids=["python-008"],
            default_order=155,
        ),
        DetectorBinding(
            detector_id="context_manager",
            detector_class=ContextManagerDetector,
            config_model=ContextManagerConfig,
            rule_ids=["python-011"],
            default_order=160,
        ),
        DetectorBinding(
            detector_id="explicitness",
            detector_class=ExplicitnessDetector,
            config_model=ExplicitnessConfig,
            rule_ids=["python-010"],
            default_order=165,
        ),
        DetectorBinding(
            detector_id="namespace_usage",
            detector_class=NamespaceUsageDetector,
            config_model=NamespaceConfig,
            rule_ids=["python-012", "python-020"],
            default_order=170,
        ),
        DetectorBinding(
            detector_id="python_practicality",
            detector_class=PythonPracticalityDetector,
            config_model=PythonPracticalityConfig,
            rule_ids=["python-013"],
            default_order=180,
        ),
        DetectorBinding(
            detector_id="python_explicit_silence",
            detector_class=PythonExplicitSilenceDetector,
            config_model=PythonExplicitSilenceConfig,
            rule_ids=["python-014"],
            default_order=190,
        ),
        DetectorBinding(
            detector_id="python_todo_stub",
            detector_class=PythonTodoStubDetector,
            config_model=PythonTodoStubConfig,
            rule_ids=["python-015"],
            default_order=200,
        ),
        DetectorBinding(
            detector_id="python_premature_impl",
            detector_class=PythonPrematureImplDetector,
            config_model=PythonPrematureImplConfig,
            rule_ids=["python-016"],
            default_order=210,
        ),
        DetectorBinding(
            detector_id="python_complex_undocumented",
            detector_class=PythonComplexUndocumentedDetector,
            config_model=PythonComplexUndocumentedConfig,
            rule_ids=["python-017"],
            default_order=220,
        ),
        DetectorBinding(
            detector_id="python_simple_documented",
            detector_class=PythonSimpleDocumentedDetector,
            config_model=PythonSimpleDocumentedConfig,
            rule_ids=["python-018"],
            default_order=230,
        ),
        DetectorBinding(
            detector_id="python_idiom",
            detector_class=PythonIdiomDetector,
            config_model=PythonIdiomConfig,
            rule_ids=["python-019"],
            default_order=240,
        ),
    ],
)

GEARBOX = DetectorGearbox(language="python")
GEARBOX.extend(DETECTOR_MAP.bindings)
DETECTOR_MAP = GEARBOX.build_map()
