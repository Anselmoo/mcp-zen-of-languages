from __future__ import annotations

import pytest

from mcp_zen_of_languages import cli
from mcp_zen_of_languages.adapters.rules_adapter import RulesAdapter
from mcp_zen_of_languages.analyzers.base import (
    AnalysisContext,
    AnalyzerConfig,
    BaseAnalyzer,
    LocationHelperMixin,
    ViolationDetector,
)
from mcp_zen_of_languages.analyzers.pipeline import merge_pipeline_overrides
from mcp_zen_of_languages.analyzers.registry import DetectorMetadata, DetectorRegistry
from mcp_zen_of_languages.config import ConfigModel, load_config
from mcp_zen_of_languages.languages.configs import (
    DetectorConfig,
    ExplicitnessConfig,
)
from mcp_zen_of_languages.models import (
    CyclomaticSummary,
    DependencyAnalysis,
    DependencyCycle,
    ParserResult,
    RulesSummary,
)
from mcp_zen_of_languages.rules.base_models import (
    LanguageZenPrinciples,
    PrincipleCategory,
    ZenPrinciple,
)
from mcp_zen_of_languages.utils.parsers import (
    parse_python_with_builtin_ast,
)


class _DummyDetector(ViolationDetector[ExplicitnessConfig]):
    @property
    def name(self) -> str:
        return "dummy"

    def detect(self, context: AnalysisContext, config: ExplicitnessConfig) -> list:
        return []


class _DummyLocation(LocationHelperMixin):
    pass


class _DummyAnalyzer(BaseAnalyzer):
    def default_config(self) -> AnalyzerConfig:
        return AnalyzerConfig()

    def language(self) -> str:
        return "python"

    def parse_code(self, code: str):
        return None

    def compute_metrics(self, code: str, ast_tree):
        return CyclomaticSummary(blocks=[], average=0.0), None, 0


def test_cli_run_report_invalid_path(capsys):
    args = type(
        "Args",
        (),
        {
            "path": "does-not-exist",
            "language": None,
            "config": None,
            "format": "markdown",
            "out": None,
            "export_json": None,
            "export_markdown": None,
            "export_log": None,
            "include_prompts": False,
            "skip_analysis": False,
            "skip_gaps": False,
        },
    )()
    assert cli._run_report(args) == 2
    captured = capsys.readouterr()
    assert "Path not found" in captured.err


def test_cli_filter_result_unchanged():
    result = cli._placeholder_result("python", None)
    filtered = cli._filter_result(result, None)
    assert filtered is result


def test_load_config_missing_file_returns_default(tmp_path):
    missing = tmp_path / "missing.yaml"
    config = load_config(str(missing))
    assert "python" in config.languages


def test_load_config_invalid_pipelines_type(tmp_path):
    config_path = tmp_path / "zen-config.yaml"
    config_path.write_text("pipelines: bad", encoding="utf-8")
    with pytest.raises(TypeError):
        load_config(str(config_path))


def test_config_model_pipeline_for_with_override():
    base = ConfigModel(pipelines=[])
    override = base.pipeline_for("python")
    override = override.model_copy(update={"language": "python", "detectors": []})
    config = ConfigModel(pipelines=[override])
    result = config.pipeline_for("python")
    assert result.language == "python"


def test_pipeline_merge_language_mismatch():
    base = type("Base", (), {"language": "python", "detectors": []})()
    override = type("Override", (), {"language": "go", "detectors": []})()
    with pytest.raises(ValueError):
        merge_pipeline_overrides(base, override)


def test_registry_get_config_union_no_detectors():
    registry = DetectorRegistry()
    with pytest.raises(ValueError):
        registry.get_config_union()


def test_rules_adapter_dependency_handling():
    principle = ZenPrinciple(
        id="python-999",
        principle="Avoid cycles",
        category=PrincipleCategory.ARCHITECTURE,
        severity=7,
        description="",
        metrics={"detect_circular_dependencies": True, "max_dependencies": 1},
    )
    rules = LanguageZenPrinciples(
        language="python",
        name="Python",
        philosophy="pep",
        source_text="src",
        source_url="https://example.com/src",
        principles=[principle],
    )
    adapter = RulesAdapter(language="python", config=None)
    adapter.lang_zen = rules
    dependency = DependencyAnalysis(
        nodes=["a", "b"],
        edges=[("a", "b"), ("a", "c")],
        cycles=[DependencyCycle(cycle=["a", "b", "a"])],
    )
    metrics = {"detect_circular_dependencies": True, "max_dependencies": 1}
    violations = adapter._check_dependencies(dependency, principle, metrics)
    assert violations

    custom_cycle = type("Cycle", (), {"cycle": ("a", "b")})()
    more = adapter._check_dependencies(
        {"cycles": [custom_cycle]}, principle, {"detect_circular_dependencies": True}
    )
    assert more


def test_rules_adapter_patterns_fallback():
    principle = ZenPrinciple(
        id="python-888",
        principle="Avoid TODO",
        category=PrincipleCategory.CLARITY,
        severity=4,
        description="",
        detectable_patterns=["TODO("],
    )
    adapter = RulesAdapter(language="python", config=None)
    adapter.lang_zen = LanguageZenPrinciples(
        language="python",
        name="Python",
        philosophy="pep",
        source_text="src",
        source_url="https://example.com/src",
        principles=[principle],
    )
    violations = adapter._check_patterns("# TODO(1)", principle)
    assert violations


def test_rules_adapter_detector_config_default():
    adapter = RulesAdapter(language="python", config=None)
    adapter.lang_zen = None
    config = adapter.get_detector_config("long_functions")
    assert config.name == "long_functions"


def test_rules_adapter_detector_config_metadata_thresholds():
    adapter = RulesAdapter(language="python", config=None)
    adapter.lang_zen = LanguageZenPrinciples(
        language="python",
        name="Python",
        philosophy="pep",
        source_text="src",
        source_url="https://example.com/src",
        principles=[
            ZenPrinciple(
                id="python-123",
                principle="Threshold",
                category=PrincipleCategory.CLARITY,
                severity=5,
                description="",
                metrics={"max_function_length": "bad"},
            )
        ],
    )
    config = adapter.get_detector_config("long_functions")
    assert config.metadata["max_function_length"] == "bad"


def test_location_helper_ast_node_to_location_none():
    helper = _DummyLocation()
    assert helper.ast_node_to_location(None, None) is None


def test_violation_detector_build_violation_defaults():
    detector = _DummyDetector()
    config = ExplicitnessConfig(type="explicitness")
    violation = detector.build_violation(config, contains="Missing")
    assert violation.severity == 5


def test_parse_python_with_builtin_ast_syntax_error():
    assert parse_python_with_builtin_ast("def broken(") is None


def test_parse_python_returns_none_for_bad_code(monkeypatch):
    from mcp_zen_of_languages.utils import parsers as parser_module

    def _bad_ast(code: str):
        return None

    monkeypatch.setattr(parser_module, "parse_python_with_builtin_ast", _bad_ast)
    monkeypatch.setattr(
        parser_module, "parse_python_with_treesitter", lambda code: None
    )
    assert parser_module.parse_python("def broken(") is None


def test_filter_result_strips_rules_summary():
    result = cli._placeholder_result("python", None)
    result = result.model_copy(
        update={"rules_summary": RulesSummary(critical=1, high=0, medium=0, low=0)}
    )
    filtered = cli._filter_result(result, 7)
    assert filtered.rules_summary is not None


def test_rules_adapter_check_dependencies_dict_edges():
    principle = ZenPrinciple(
        id="python-777",
        principle="Limit dependencies",
        category=PrincipleCategory.ARCHITECTURE,
        severity=5,
        description="",
        metrics={"max_dependencies": 0},
    )
    adapter = RulesAdapter(language="python", config=None)
    adapter.lang_zen = LanguageZenPrinciples(
        language="python",
        name="Python",
        philosophy="pep",
        source_text="src",
        source_url="https://example.com/src",
        principles=[principle],
    )
    dep = {"edges": [("a", "b")]}
    violations = adapter._check_dependencies(dep, principle, {"max_dependencies": 0})
    assert violations


def test_rules_adapter_check_dependencies_missing_edges():
    principle = ZenPrinciple(
        id="python-666",
        principle="Limit dependencies",
        category=PrincipleCategory.ARCHITECTURE,
        severity=5,
        description="",
        metrics={"max_dependencies": 1},
    )
    adapter = RulesAdapter(language="python", config=None)
    adapter.lang_zen = LanguageZenPrinciples(
        language="python",
        name="Python",
        philosophy="pep",
        source_text="src",
        source_url="https://example.com/src",
        principles=[principle],
    )
    violations = adapter._check_dependencies(
        {"edges": "bad"}, principle, {"max_dependencies": 1}
    )
    assert violations == []


def test_rules_adapter_check_dependencies_edge_objects():
    principle = ZenPrinciple(
        id="python-333",
        principle="Limit dependencies",
        category=PrincipleCategory.ARCHITECTURE,
        severity=5,
        description="",
        metrics={"max_dependencies": 0},
    )
    adapter = RulesAdapter(language="python", config=None)
    adapter.lang_zen = LanguageZenPrinciples(
        language="python",
        name="Python",
        philosophy="pep",
        source_text="src",
        source_url="https://example.com/src",
        principles=[principle],
    )
    edge = type("Edge", (), {"from": "a", "to": "b"})()
    violations = adapter._check_dependencies(
        {"edges": [edge]}, principle, {"max_dependencies": 0}
    )
    assert violations


def test_rules_adapter_check_dependencies_no_cycles():
    principle = ZenPrinciple(
        id="python-555",
        principle="Avoid cycles",
        category=PrincipleCategory.ARCHITECTURE,
        severity=5,
        description="",
        metrics={"detect_circular_dependencies": True},
    )
    adapter = RulesAdapter(language="python", config=None)
    adapter.lang_zen = LanguageZenPrinciples(
        language="python",
        name="Python",
        philosophy="pep",
        source_text="src",
        source_url="https://example.com/src",
        principles=[principle],
    )
    violations = adapter._check_dependencies(
        {}, principle, {"detect_circular_dependencies": True}
    )
    assert violations == []


def test_rules_adapter_check_dependencies_cycle_string():
    principle = ZenPrinciple(
        id="python-444",
        principle="Avoid cycles",
        category=PrincipleCategory.ARCHITECTURE,
        severity=5,
        description="",
        metrics={"detect_circular_dependencies": True},
    )
    adapter = RulesAdapter(language="python", config=None)
    adapter.lang_zen = LanguageZenPrinciples(
        language="python",
        name="Python",
        philosophy="pep",
        source_text="src",
        source_url="https://example.com/src",
        principles=[principle],
    )
    violations = adapter._check_dependencies(
        {"cycles": ["a"]}, principle, {"detect_circular_dependencies": True}
    )
    assert violations


def test_rules_adapter_check_dependencies_cycle_bad_object():
    class BadCycle:
        def __iter__(self):
            raise TypeError("bad")

    principle = ZenPrinciple(
        id="python-333",
        principle="Avoid cycles",
        category=PrincipleCategory.ARCHITECTURE,
        severity=5,
        description="",
        metrics={"detect_circular_dependencies": True},
    )
    adapter = RulesAdapter(language="python", config=None)
    adapter.lang_zen = LanguageZenPrinciples(
        language="python",
        name="Python",
        philosophy="pep",
        source_text="src",
        source_url="https://example.com/src",
        principles=[principle],
    )
    violations = adapter._check_dependencies(
        {"cycles": [BadCycle()]}, principle, {"detect_circular_dependencies": True}
    )
    assert violations


def test_rules_adapter_check_dependencies_cycle_empty_metrics():
    principle = ZenPrinciple(
        id="python-222",
        principle="Avoid cycles",
        category=PrincipleCategory.ARCHITECTURE,
        severity=5,
        description="",
        metrics=None,
    )
    adapter = RulesAdapter(language="python", config=None)
    adapter.lang_zen = LanguageZenPrinciples(
        language="python",
        name="Python",
        philosophy="pep",
        source_text="src",
        source_url="https://example.com/src",
        principles=[principle],
    )
    violations = adapter._check_dependencies({"cycles": []}, principle, {})
    assert violations == []


def test_rules_adapter_dependency_analysis_unknown_shape():
    adapter = RulesAdapter(language="python", config=None)
    adapter.lang_zen = LanguageZenPrinciples(
        language="python",
        name="Python",
        philosophy="pep",
        source_text="src",
        source_url="https://example.com/src",
        principles=[],
    )
    violations = adapter._check_dependencies(
        "bad",
        ZenPrinciple(
            id="python-000",
            principle="Test",
            category=PrincipleCategory.CLARITY,
            severity=1,
            description="",
        ),
        {},
    )
    assert violations == []


def test_rules_adapter_check_patterns_bad_regex():
    principle = ZenPrinciple(
        id="python-111",
        principle="Avoid TODO",
        category=PrincipleCategory.CLARITY,
        severity=4,
        description="",
        detectable_patterns=["("],
    )
    adapter = RulesAdapter(language="python", config=None)
    adapter.lang_zen = LanguageZenPrinciples(
        language="python",
        name="Python",
        philosophy="pep",
        source_text="src",
        source_url="https://example.com/src",
        principles=[principle],
    )
    violations = adapter._check_patterns("( ", principle)
    assert violations


def test_rules_adapter_check_patterns_search_exception(monkeypatch):
    principle = ZenPrinciple(
        id="python-110",
        principle="Avoid TODO",
        category=PrincipleCategory.CLARITY,
        severity=4,
        description="",
        detectable_patterns=["TODO"],
    )
    adapter = RulesAdapter(language="python", config=None)
    adapter.lang_zen = LanguageZenPrinciples(
        language="python",
        name="Python",
        philosophy="pep",
        source_text="src",
        source_url="https://example.com/src",
        principles=[principle],
    )

    class BadPattern:
        pattern = "TODO"

        def search(self, _):
            raise RuntimeError("boom")

    monkeypatch.setattr(ZenPrinciple, "compiled_patterns", lambda self: [BadPattern()])
    assert adapter._check_patterns("TODO", principle) == []


class _DummyConfig(DetectorConfig):
    type: str = "dummy"


def test_violation_detector_build_violation_no_message():
    class _Detector(ViolationDetector[_DummyConfig]):
        @property
        def name(self) -> str:
            return "detector"

        def detect(self, context: AnalysisContext, config: _DummyConfig) -> list:
            return []

    detector = _Detector()
    config = _DummyConfig(type="dummy")
    violation = detector.build_violation(config, message=None)
    assert violation.message == "dummy"


def test_violation_detector_build_violation_fallback_message():
    detector = _DummyDetector()
    config = ExplicitnessConfig(type="explicitness")
    violation = detector.build_violation(config, message=None)
    assert violation.message == "explicitness"


def test_registry_configs_from_rules_unknown_metric():
    registry = DetectorRegistry()
    meta = DetectorMetadata(
        detector_id="dummy",
        detector_class=_DummyDetector,
        config_model=_DummyConfig,
        language="python",
        rule_ids=["python-001"],
    )
    registry.register(meta)
    principle = ZenPrinciple(
        id="python-001",
        principle="Dummy",
        category=PrincipleCategory.CLARITY,
        severity=5,
        description="",
        metrics={"unknown": 1},
    )
    lang = LanguageZenPrinciples(
        language="python",
        name="Python",
        philosophy="pep",
        source_text="src",
        source_url="https://example.com/src",
        principles=[principle],
    )
    with pytest.raises(ValueError):
        registry.configs_from_rules(lang)


def test_registry_get_missing_detector():
    registry = DetectorRegistry()
    with pytest.raises(KeyError):
        registry.get("missing")


@pytest.mark.filterwarnings("ignore::DeprecationWarning")
def test_analyzer_config_type_check():
    with pytest.raises(Exception):
        AnalyzerConfig.model_validate({"severity_threshold": "bad"})


def test_base_analyzer_invalid_config():
    with pytest.raises(TypeError):
        _DummyAnalyzer(config="bad")


def test_rules_adapter_get_critical_violations():
    adapter = RulesAdapter(language="python", config=None)
    adapter.config = type("Config", (), {"severity_threshold": 5})()
    violation = _DummyDetector().build_violation(
        ExplicitnessConfig(type="explicitness", severity=6)
    )
    assert adapter.get_critical_violations([violation])


def test_rules_adapter_find_violations_maintainability():
    adapter = RulesAdapter(language="python", config=None)
    principle = ZenPrinciple(
        id="python-010",
        principle="Maintainable",
        category=PrincipleCategory.CLARITY,
        severity=5,
        description="",
        metrics={"min_maintainability_index": 50},
    )
    adapter.lang_zen = LanguageZenPrinciples(
        language="python",
        name="Python",
        philosophy="pep",
        source_text="src",
        source_url="https://example.com/src",
        principles=[principle],
    )
    violations = adapter.find_violations(
        code="def foo():\n    pass",
        cyclomatic_summary=CyclomaticSummary(blocks=[], average=1),
        maintainability_index=10.0,
        dependency_analysis=None,
    )
    assert violations


def test_rules_adapter_find_violations_missing_metrics():
    adapter = RulesAdapter(language="python", config=None)
    principle = ZenPrinciple(
        id="python-011",
        principle="Maintainable",
        category=PrincipleCategory.CLARITY,
        severity=5,
        description="",
        metrics=None,
    )
    adapter.lang_zen = LanguageZenPrinciples(
        language="python",
        name="Python",
        philosophy="pep",
        source_text="src",
        source_url="https://example.com/src",
        principles=[principle],
    )
    violations = adapter.find_violations(
        code="def foo():\n    pass",
        cyclomatic_summary=CyclomaticSummary(blocks=[], average=1),
        maintainability_index=10.0,
        dependency_analysis=None,
    )
    assert violations == []


def test_parser_normalizer_returns_parser_result():
    from mcp_zen_of_languages.languages.python.parser_normalizer import ParserNormalizer

    parser_result = ParserResult(type="ast", tree={})
    assert ParserNormalizer.normalize(parser_result) is parser_result


def test_parser_normalizer_wraps_unknown():
    from mcp_zen_of_languages.languages.python.parser_normalizer import ParserNormalizer

    wrapped = ParserNormalizer.normalize({"tree": "raw"})
    assert wrapped
    assert wrapped.type == "unknown"


def test_detector_config_select_violation_message_contains():
    config = DetectorConfig(type="test", violation_messages=["alpha", "beta"])
    assert config.select_violation_message(contains="bet") == "beta"


def test_detector_config_select_violation_message_index():
    config = DetectorConfig(type="test", violation_messages=["alpha", "beta"])
    assert config.select_violation_message(index=1) == "beta"


def test_detector_config_select_violation_message_default():
    config = DetectorConfig(type="test")
    assert config.select_violation_message() == "test"


def test_build_repository_imports_empty(tmp_path):
    file_path = tmp_path / "sample.py"
    file_path.write_text("import ", encoding="utf-8")
    imports = cli._build_repository_imports([file_path])
    assert imports[str(file_path)] == []


def test_build_placeholder_result():
    result = cli._placeholder_result("python", "file.py")
    assert result.metrics.lines_of_code == 0


def test_language_detector_unknown_extension():
    from mcp_zen_of_languages.utils.language_detection import (
        detect_language_by_extension,
    )

    result = detect_language_by_extension("foo.unknown")
    assert result.language == "unknown"


def test_language_detector_javascript_heuristic():
    from mcp_zen_of_languages.utils.language_detection import (
        detect_language_from_content,
    )

    result = detect_language_from_content("function test() {}")
    assert result.language in ["typescript", "javascript"]


def test_language_detector_typescript_interface():
    from mcp_zen_of_languages.utils.language_detection import (
        detect_language_from_content,
    )

    result = detect_language_from_content("interface Foo {}")
    assert result.language == "typescript"


def test_server_analyze_repository_skips_missing_files(tmp_path):
    from mcp_zen_of_languages.server import analyze_repository

    missing = tmp_path / "missing.py"
    missing.write_text("", encoding="utf-8")
    missing.chmod(0o000)
    try:
        import asyncio

        result = asyncio.run(
            analyze_repository.fn(
                repo_path=str(tmp_path), languages=["python"], max_files=1
            )
        )
    finally:
        missing.chmod(0o644)
    assert result is not None


def test_server_analyze_repository_placeholder_language(tmp_path):
    from mcp_zen_of_languages.server import analyze_repository

    sample = tmp_path / "sample.rb"
    sample.write_text("puts 'hi'", encoding="utf-8")
    import asyncio

    result = asyncio.run(
        analyze_repository.fn(repo_path=str(tmp_path), languages=["ruby"], max_files=1)
    )
    assert result


def test_server_analyze_repository_rust(tmp_path, monkeypatch):
    from mcp_zen_of_languages.server import analyze_repository

    sample = tmp_path / "sample.rs"
    sample.write_text("fn main() {}", encoding="utf-8")

    def _boom(*args, **kwargs):
        raise OSError("nope")

    monkeypatch.setattr(type(sample), "read_text", _boom)
    import asyncio

    result = asyncio.run(
        analyze_repository.fn(repo_path=str(tmp_path), languages=["rust"], max_files=1)
    )
    assert result


def test_report_generate_skip_sections(tmp_path):
    path = tmp_path / "sample.py"
    path.write_text("def foo():\n    pass", encoding="utf-8")
    report = cli._render_report_output(
        __import__(
            "mcp_zen_of_languages.reporting.report", fromlist=["generate_report"]
        ).generate_report(str(path), include_analysis=False, include_gaps=False),
        "both",
    )
    assert "markdown" in report


def test_report_format_analysis_no_violations(tmp_path):
    from mcp_zen_of_languages.reporting.report import _format_analysis_markdown

    results = [cli._placeholder_result("python", str(tmp_path / "sample.py"))]
    lines = _format_analysis_markdown(results)
    assert "No violations" in " ".join(lines)


def test_build_report_with_prompts(tmp_path):
    path = tmp_path / "sample.py"
    path.write_text("def foo():\n    pass", encoding="utf-8")
    from mcp_zen_of_languages.reporting.report import generate_report

    report = generate_report(str(path), include_prompts=True)
    assert report.data["prompts"] is not None


def test_dependency_graph_empty_imports():
    from mcp_zen_of_languages.metrics.dependency_graph import build_import_graph

    result = build_import_graph({"a": [""]})
    assert "a" in result.nodes


def test_python_analyzer_parse_error():
    from mcp_zen_of_languages.languages.python.analyzer import PythonAnalyzer

    analyzer = PythonAnalyzer()
    assert analyzer.parse_code("def broken(") is None


def test_python_analyzer_dependency_error(monkeypatch):
    from mcp_zen_of_languages.languages.python.analyzer import PythonAnalyzer

    analyzer = PythonAnalyzer()

    def _boom(*args, **kwargs):
        raise RuntimeError("boom")

    monkeypatch.setattr(
        "mcp_zen_of_languages.metrics.dependency_graph.build_import_graph", _boom
    )
    result = analyzer._build_dependency_analysis(
        AnalysisContext(code="import os", language="python")
    )
    assert result is None


def test_python_analyzer_parse_exception(monkeypatch):
    from mcp_zen_of_languages.languages.python.analyzer import PythonAnalyzer

    analyzer = PythonAnalyzer()
    monkeypatch.setattr(
        "mcp_zen_of_languages.utils.parsers.parse_python",
        lambda _: iter(()).throw(RuntimeError("boom")),
    )
    assert analyzer.parse_code("def foo():\n    pass") is None


def test_cli_render_report_json():
    from mcp_zen_of_languages.reporting.models import ReportOutput

    report = ReportOutput(markdown="#", data={"foo": "bar"})
    output = cli._render_report_output(report, "json")
    assert "foo" in output


def test_cli_render_report_markdown():
    from mcp_zen_of_languages.reporting.models import ReportOutput

    report = ReportOutput(markdown="#", data={"foo": "bar"})
    output = cli._render_report_output(report, "markdown")
    assert output == "#"


def test_cli_main_help_for_unknown_command(capsys):
    with pytest.raises(SystemExit):
        cli.main(["unknown"])
    captured = capsys.readouterr()
    assert "usage" in captured.err.lower()


def test_cli_main_missing_args_prints_help(capsys):
    exit_code = cli.main([])
    assert exit_code == 0
    captured = capsys.readouterr()
    assert "Welcome to Zen of Languages." in captured.out


def test_rules_base_models_properties():
    principle = ZenPrinciple(
        id="python-002",
        principle="Doc",
        category=PrincipleCategory.DOCUMENTATION,
        severity=9,
        description="",
    )
    lang = LanguageZenPrinciples(
        language="python",
        name="Python",
        philosophy="pep",
        source_text="src",
        source_url="https://example.com/src",
        principles=[principle],
    )
    assert lang.principle_count == 1
    assert lang.get_by_id("python-002")
    assert lang.get_by_severity(9)
    assert lang.get_by_category(PrincipleCategory.DOCUMENTATION)


def test_rules_get_all_principles_by_category():
    from mcp_zen_of_languages.rules import get_all_principles_by_category

    result = get_all_principles_by_category(PrincipleCategory.CLARITY)
    assert isinstance(result, dict)


def test_main_entrypoint_runs(monkeypatch):
    from mcp_zen_of_languages import __main__

    called = {"ran": False}

    class Runner:
        def run(self):
            called["ran"] = True

    monkeypatch.setattr(__main__, "mcp", Runner())
    __main__.main()
    assert called["ran"]


def test_main_entrypoint_module_execution(monkeypatch):
    import importlib

    module = importlib.import_module("mcp_zen_of_languages.__main__")

    class Runner:
        def run(self):
            pass

    monkeypatch.setattr(module, "mcp", Runner())
    assert module.main() is None


@pytest.mark.parametrize(
    ("contents", "expected"),
    [
        ("import os\n", ["os"]),
        ("from sys import path\n", ["sys"]),
    ],
)
def test_build_repository_imports_values(tmp_path, contents, expected):
    file_path = tmp_path / "sample.py"
    file_path.write_text(contents, encoding="utf-8")
    imports = cli._build_repository_imports([file_path])
    assert imports[str(file_path)] == expected


def test_rules_tools_detect_deep_inheritance_cycles():
    from mcp_zen_of_languages.rules.tools.detections import detect_deep_inheritance

    code_map = {"a.py": "class A(B):\n    pass\nclass B(A):\n    pass\n"}
    results = detect_deep_inheritance(code_map, max_depth=0)
    assert results


def test_rules_tools_detect_dependency_cycles():
    from mcp_zen_of_languages.rules.tools.detections import detect_dependency_cycles

    cycles = detect_dependency_cycles([("a", "b"), ("b", "a")])
    assert cycles


def test_cli_filter_result_severity_summary():
    violation = _DummyDetector().build_violation(
        ExplicitnessConfig(type="explicitness", severity=8)
    )
    result = cli._placeholder_result("python", None).model_copy(
        update={"violations": [violation], "rules_summary": RulesSummary()}
    )
    filtered = cli._filter_result(result, 9)
    assert filtered.violations == []
    assert filtered.rules_summary is not None


def test_pipeline_merge_overrides_none():
    base = type("Base", (), {"language": "python", "detectors": []})()
    assert merge_pipeline_overrides(base, None) is base


def test_registry_adapter_caches_union():
    registry = DetectorRegistry()
    meta = DetectorMetadata(
        detector_id="dummy",
        detector_class=_DummyDetector,
        config_model=ExplicitnessConfig,
        language="python",
        rule_ids=["python-001"],
    )
    registry.register(meta)
    union = registry.get_config_union()
    assert registry.get_config_union() is union
    with pytest.raises(TypeError):
        registry.adapter()


def test_registry_configs_merge_updates():
    registry = DetectorRegistry()
    meta = DetectorMetadata(
        detector_id="explicitness",
        detector_class=_DummyDetector,
        config_model=ExplicitnessConfig,
        language="python",
        rule_ids=["python-001"],
    )
    registry.register(meta)
    base = [ExplicitnessConfig(type="explicitness", require_type_hints=False)]
    overrides = [ExplicitnessConfig(type="explicitness", require_type_hints=True)]
    merged = registry.merge_configs(base, overrides)
    assert merged[0].require_type_hints is True


def test_registry_create_pipeline_from_rules_error():
    registry = DetectorRegistry()
    principle = ZenPrinciple(
        id="python-001",
        principle="Explicit",
        category=PrincipleCategory.CLARITY,
        severity=5,
        description="",
    )
    lang = LanguageZenPrinciples(
        language="python",
        name="Python",
        philosophy="pep",
        source_text="src",
        source_url="https://example.com/src",
        principles=[principle],
    )
    pipeline = registry.create_pipeline_from_rules(lang)
    assert pipeline.detectors == []


def test_language_detector_ruby_heuristic():
    from mcp_zen_of_languages.utils.language_detection import (
        detect_language_from_content,
    )

    result = detect_language_from_content("def foo\nend")
    assert result.language == "python"


def test_language_detector_unknown_content():
    from mcp_zen_of_languages.utils.language_detection import (
        detect_language_from_content,
    )

    result = detect_language_from_content("console.log('x')")
    assert result.language == "unknown"


def test_build_gap_analysis_placeholder():
    from mcp_zen_of_languages.reporting.gaps import build_gap_analysis

    gaps = build_gap_analysis(["unknown"])
    assert gaps.feature_gaps


def test_build_gap_analysis_detects_placeholder():
    from mcp_zen_of_languages.reporting.gaps import build_gap_analysis

    gaps = build_gap_analysis(["python"])
    assert gaps.detector_gaps or gaps.feature_gaps


def test_report_format_gap_markdown_no_gaps():
    from mcp_zen_of_languages.reporting.gaps import GapAnalysis
    from mcp_zen_of_languages.reporting.report import _format_gap_markdown

    gaps = GapAnalysis(detector_gaps=[], feature_gaps=[])
    lines = _format_gap_markdown(gaps)
    assert "No gaps reported." in " ".join(lines)


def test_report_format_gap_markdown_with_gaps():
    from mcp_zen_of_languages.reporting.models import DetectorCoverageGap, GapAnalysis
    from mcp_zen_of_languages.reporting.report import _format_gap_markdown

    gaps = GapAnalysis(
        detector_gaps=[
            DetectorCoverageGap(
                language="python",
                rule_id="python-001",
                principle="Explicitness",
                severity=5,
                reason="Missing",
            )
        ],
        feature_gaps=[],
    )
    lines = _format_gap_markdown(gaps)
    assert "Detector" in " ".join(lines)
    assert "python-001" in " ".join(lines)


def test_rules_adapter_check_dependencies_none():
    principle = ZenPrinciple(
        id="python-010",
        principle="Avoid cycles",
        category=PrincipleCategory.ARCHITECTURE,
        severity=5,
        description="",
        metrics={"detect_circular_dependencies": True},
    )
    adapter = RulesAdapter(language="python", config=None)
    adapter.lang_zen = LanguageZenPrinciples(
        language="python",
        name="Python",
        philosophy="pep",
        source_text="src",
        source_url="https://example.com/src",
        principles=[principle],
    )
    assert adapter._check_dependencies(None, principle, {}) == []


def test_rules_adapter_check_dependencies_cycle_exception():
    class BadCycles(dict):
        def get(self, key, default=None):
            raise RuntimeError("boom")

    principle = ZenPrinciple(
        id="python-020",
        principle="Avoid cycles",
        category=PrincipleCategory.ARCHITECTURE,
        severity=5,
        description="",
        metrics={"detect_circular_dependencies": True},
    )
    adapter = RulesAdapter(language="python", config=None)
    adapter.lang_zen = LanguageZenPrinciples(
        language="python",
        name="Python",
        philosophy="pep",
        source_text="src",
        source_url="https://example.com/src",
        principles=[principle],
    )
    assert (
        adapter._check_dependencies(
            BadCycles(), principle, {"detect_circular_dependencies": True}
        )
        == []
    )


def test_rules_adapter_check_dependencies_bad_edge():
    class BadEdge:
        def __getattr__(self, name):
            raise RuntimeError("boom")

    principle = ZenPrinciple(
        id="python-030",
        principle="Limit dependencies",
        category=PrincipleCategory.ARCHITECTURE,
        severity=5,
        description="",
        metrics={"max_dependencies": 0},
    )
    adapter = RulesAdapter(language="python", config=None)
    adapter.lang_zen = LanguageZenPrinciples(
        language="python",
        name="Python",
        philosophy="pep",
        source_text="src",
        source_url="https://example.com/src",
        principles=[principle],
    )
    violations = adapter._check_dependencies(
        {"edges": [BadEdge()]}, principle, {"max_dependencies": 0}
    )
    assert violations == []


def test_rules_adapter_check_dependencies_max_exception():
    principle = ZenPrinciple(
        id="python-040",
        principle="Limit dependencies",
        category=PrincipleCategory.ARCHITECTURE,
        severity=5,
        description="",
        metrics={"max_dependencies": "bad"},
    )
    adapter = RulesAdapter(language="python", config=None)
    adapter.lang_zen = LanguageZenPrinciples(
        language="python",
        name="Python",
        philosophy="pep",
        source_text="src",
        source_url="https://example.com/src",
        principles=[principle],
    )
    violations = adapter._check_dependencies(
        {"edges": [("a", "b")]}, principle, {"max_dependencies": "bad"}
    )
    assert violations == []


def test_rules_adapter_summarize_violations_low():
    adapter = RulesAdapter(language="python", config=None)
    violation = _DummyDetector().build_violation(
        ExplicitnessConfig(type="explicitness", severity=1)
    )
    summary = adapter.summarize_violations([violation])
    assert summary["low"] == 1


def test_registry_configs_from_rules_updates_existing():
    registry = DetectorRegistry()
    meta = DetectorMetadata(
        detector_id="explicitness",
        detector_class=_DummyDetector,
        config_model=ExplicitnessConfig,
        language="python",
        rule_ids=["python-001"],
    )
    registry.register(meta)
    principles = [
        ZenPrinciple(
            id="python-001",
            principle="Explicitness",
            category=PrincipleCategory.CLARITY,
            severity=5,
            description="",
            metrics={"require_type_hints": False},
        ),
        ZenPrinciple(
            id="python-001",
            principle="Explicitness",
            category=PrincipleCategory.CLARITY,
            severity=5,
            description="",
            metrics={"require_type_hints": True},
        ),
    ]
    lang = LanguageZenPrinciples(
        language="python",
        name="Python",
        philosophy="pep",
        source_text="src",
        source_url="https://example.com/src",
        principles=principles,
    )
    with pytest.raises(TypeError):
        registry.configs_from_rules(lang)


def test_registry_create_pipeline_from_rules_with_detector():
    registry = DetectorRegistry()
    meta = DetectorMetadata(
        detector_id="explicitness",
        detector_class=_DummyDetector,
        config_model=ExplicitnessConfig,
        language="python",
        rule_ids=["python-001"],
    )
    registry.register(meta)
    principle = ZenPrinciple(
        id="python-001",
        principle="Explicitness",
        category=PrincipleCategory.CLARITY,
        severity=5,
        description="",
        metrics={"require_type_hints": True},
    )
    lang = LanguageZenPrinciples(
        language="python",
        name="Python",
        philosophy="pep",
        source_text="src",
        source_url="https://example.com/src",
        principles=[principle],
    )
    with pytest.raises(TypeError):
        registry.create_pipeline_from_rules(lang)
