from __future__ import annotations

import pytest

from mcp_zen_of_languages.adapters.rules_adapter import RulesAdapter, RulesAdapterConfig
from mcp_zen_of_languages.analyzers.analyzer_factory import create_analyzer
from mcp_zen_of_languages.analyzers.base import AnalysisContext, AnalyzerConfig
from mcp_zen_of_languages.analyzers.pipeline import PipelineConfig
from mcp_zen_of_languages.analyzers.registry import DetectorMetadata, DetectorRegistry
from mcp_zen_of_languages.config import ConfigModel, load_config
from mcp_zen_of_languages.languages.bash.detectors import BashEvalUsageDetector
from mcp_zen_of_languages.languages.configs import (
    BashEvalUsageConfig,
    ContextManagerConfig,
    DeepInheritanceConfig,
    FeatureEnvyConfig,
    NameStyleConfig,
    StarImportConfig,
)
from mcp_zen_of_languages.languages.python.detectors import (
    ContextManagerDetector,
    DuplicateImplementationDetector,
    FeatureEnvyDetector,
    NameStyleDetector,
    StarImportDetector,
)
from mcp_zen_of_languages.models import (
    CyclomaticSummary,
    DependencyAnalysis,
    DependencyCycle,
)
from mcp_zen_of_languages.reporting.prompts import build_prompt_bundle
from mcp_zen_of_languages.rules import get_principle_by_id
from mcp_zen_of_languages.rules.base_models import PrincipleCategory, ZenPrinciple
from mcp_zen_of_languages.rules.tools.detections import (
    detect_deep_inheritance,
    detect_dependency_cycles,
)
from mcp_zen_of_languages.utils.language_detection import (
    DetectionResult,
    detect_language_by_extension,
    detect_language_from_content,
)
from mcp_zen_of_languages.utils.parsers import (
    parse_python_with_builtin_ast,
    parse_python_with_treesitter,
)


def test_rules_adapter_dependency_edges_and_thresholds():
    adapter = RulesAdapter(
        language="python",
        config=RulesAdapterConfig(min_maintainability_index=80.0),
    )
    principle = ZenPrinciple(
        id="dep-1",
        principle="Deps",
        description="desc",
        severity=6,
        category=PrincipleCategory.STRUCTURE,
        violations=[],
        metrics={"max_dependencies": 1, "detect_circular_dependencies": True},
    )
    dep_model = DependencyAnalysis(
        nodes=["a", "b", "c"],
        edges=[("a", "b"), ("a", "c")],
        cycles=[DependencyCycle(cycle=["a", "b", "a"])],
    )
    violations = adapter._check_dependencies(
        dep_model,
        principle,
        principle.metrics or {},
    )
    assert any("Circular dependencies" in v.message for v in violations)
    assert any("exceeds maximum" in v.message for v in violations)


def test_rules_adapter_get_detector_config_metadata_and_patterns():
    adapter = RulesAdapter(language="python")
    config = adapter.get_detector_config("max_function_length")
    assert "max_function_length" in config.thresholds
    assert isinstance(config.patterns, list)


def test_rules_adapter_get_critical_violations_filters():
    adapter = RulesAdapter(language="python")
    violations = adapter.find_violations("def foo():\n    pass\n")
    adapter.config.severity_threshold = 1
    assert adapter.get_critical_violations(violations) == violations


def test_rules_adapter_missing_language_returns_defaults():
    adapter = RulesAdapter(language="unknown")
    config = adapter.get_detector_config("missing")
    assert config.thresholds == {}
    assert config.patterns == []


def test_base_analyzer_build_pipeline_errors_on_unknown_language():
    class BadAnalyzer(create_analyzer("python").__class__):
        def language(self) -> str:
            return "unknown"

        def default_config(self) -> AnalyzerConfig:
            return AnalyzerConfig()

    with pytest.raises(ValueError, match="No zen rules for language: unknown"):
        BadAnalyzer()


def test_base_analyzer_rules_summary_with_dict_dependency():
    class StubAnalyzer(create_analyzer("python").__class__):
        def build_pipeline(self):
            class _Pipeline:
                def run(self, context, config):
                    return []

                @property
                def detectors(self):
                    return []

            return _Pipeline()

        def parse_code(self, code: str):
            return None

        def compute_metrics(self, code: str, ast_tree):
            return CyclomaticSummary(blocks=[], average=0.0), 90.0, 1

        def _build_dependency_analysis(self, context: AnalysisContext):
            return {"nodes": ["a", "b"], "edges": [("a", "b")], "cycles": []}

    analyzer = StubAnalyzer()
    result = analyzer.analyze("def foo():\n    pass\n")
    assert result.rules_summary is not None


def test_pipeline_validate_detectors_rejects_non_list():
    with pytest.raises(TypeError):
        PipelineConfig.model_validate({"language": "python", "detectors": "bad"})


def test_detector_registry_project_principle_errors_on_unknown_metric():
    registry = DetectorRegistry()

    class DummyConfig(AnalyzerConfig):
        type: str = "dummy"
        max_depth: int = 1

    class DummyDetector(BashEvalUsageDetector):
        @property
        def name(self) -> str:
            return "dummy"

        def detect(self, context, config):
            return []

    metadata = DetectorMetadata(
        detector_id="dummy",
        detector_class=DummyDetector,
        config_model=DummyConfig,
        language="python",
        rule_ids=["python-999"],
    )
    registry.register(metadata)
    lang_zen = get_principle_by_id("python-001")
    assert lang_zen is not None
    principle = ZenPrinciple(
        id="python-999",
        principle="Bad metrics",
        description="desc",
        severity=5,
        category=PrincipleCategory.STRUCTURE,
        violations=[],
        metrics={"unknown_metric": 1},
    )
    with pytest.raises(ValueError, match="Unknown metric keys for python-999"):
        registry._project_principle(
            principle,
            "python",
            set(AnalyzerConfig.model_fields),
        )


def test_analyzer_factory_aliases():
    assert create_analyzer("py").language() == "python"
    assert create_analyzer("ts").language() == "typescript"
    assert create_analyzer("rs").language() == "rust"
    assert create_analyzer("jsx").language() == "javascript"
    assert create_analyzer("sh").language() == "bash"
    assert create_analyzer("ps").language() == "powershell"
    assert create_analyzer("rb").language() == "ruby"
    assert create_analyzer("cc").language() == "cpp"
    assert create_analyzer("cs").language() == "csharp"


def test_config_load_discovery_breaks_on_pyproject(tmp_path, monkeypatch):
    root = tmp_path / "project"
    root.mkdir()
    (root / "pyproject.toml").write_text("[build-system]\n", encoding="utf-8")
    (root / "child").mkdir()
    monkeypatch.chdir(root / "child")
    config = load_config(None)
    assert isinstance(config, ConfigModel)


def test_language_detection_helpers():
    assert detect_language_by_extension("file.py").language == "python"
    assert detect_language_from_content(
        "function foo() {}\nconst x = 1\n",
    ).language in {
        "typescript",
        "javascript",
    }
    result = DetectionResult(language="python")
    assert result.as_dict()["language"] == "python"


def test_parse_python_helpers_return_none_on_missing_treesitter():
    assert parse_python_with_treesitter("def foo():\n    pass\n") is None
    assert parse_python_with_builtin_ast("def foo():\n    pass\n") is not None


def test_python_detectors_additional_branches():
    context = AnalysisContext(code="open('file.txt')\n", language="python")
    assert ContextManagerDetector().detect(context, ContextManagerConfig()) is not None
    violations = ContextManagerDetector().detect(context, BashEvalUsageConfig())
    assert isinstance(violations, list)
    star = StarImportDetector().detect(
        AnalysisContext(code="from mod import *\n", language="python"),
        StarImportConfig(),
    )
    assert star
    name_style = NameStyleDetector().detect(
        AnalysisContext(code="FooBar = 1\n", language="python"),
        NameStyleConfig(),
    )
    assert name_style


def test_feature_envy_and_duplicates_detectors():
    code = "class A:\n    def foo(self):\n        other.x = 1\n        other.y = 2\n\n"
    context = AnalysisContext(code=code, language="python", other_files={"a.py": code})
    feature = FeatureEnvyDetector().detect(
        context,
        FeatureEnvyConfig().model_copy(update={"min_occurrences": 2}),
    )
    assert feature
    duplicates = DuplicateImplementationDetector().detect(
        context,
        DeepInheritanceConfig().model_copy(update={"max_depth": 1}),
    )
    assert duplicates == []


def test_bash_eval_detector_reports_violation():
    context = AnalysisContext(code="eval echo hi", language="bash")
    violations = BashEvalUsageDetector().detect(context, BashEvalUsageConfig())
    assert violations


def test_rules_tools_deep_inheritance_cycle():
    code_map = {
        "a.py": "class A(B):\n    pass\n",
        "b.py": "class B(C):\n    pass\n",
        "c.py": "class C:\n    pass\n",
    }
    findings = detect_deep_inheritance(code_map, max_depth=0)
    assert findings
    cycles = detect_dependency_cycles([("a", "b"), ("b", "a")])
    assert cycles


def test_reporting_prompt_bundle_generic_only():
    # Keep a minimal smoke-case for the empty-input branch.
    output = build_prompt_bundle([])
    assert output.file_prompts == []
