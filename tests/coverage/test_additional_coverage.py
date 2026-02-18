from __future__ import annotations

import json
import types

import pytest

from mcp_zen_of_languages.adapters.rules_adapter import RulesAdapter, RulesAdapterConfig
from mcp_zen_of_languages.analyzers.base import (
    AnalysisContext,
    AnalyzerConfig,
    DetectionPipeline,
)
from mcp_zen_of_languages.analyzers.pipeline import (
    PipelineConfig,
    merge_pipeline_overrides,
)
from mcp_zen_of_languages.analyzers.registry import DetectorRegistry
from mcp_zen_of_languages.cli import (
    _filter_result,
    _placeholder_result,
    _render_report_output,
    main,
)
from mcp_zen_of_languages.config import ConfigModel, load_config
from mcp_zen_of_languages.languages.placeholder import PlaceholderDetector
from mcp_zen_of_languages.metrics.collector import MetricsCollector
from mcp_zen_of_languages.metrics.dependency_graph import (
    build_import_graph,
    find_cycles,
)
from mcp_zen_of_languages.models import (
    AnalysisResult,
    CyclomaticSummary,
    Metrics,
    ParserResult,
    Violation,
)
from mcp_zen_of_languages.reporting.gaps import build_gap_analysis
from mcp_zen_of_languages.reporting.prompts import build_prompt_bundle
from mcp_zen_of_languages.reporting.report import (
    _format_analysis_markdown,
    _format_gap_markdown,
    _format_prompts_markdown,
    _summarize_results,
    generate_report,
)
from mcp_zen_of_languages.rules import get_all_languages, get_all_principles_by_category
from mcp_zen_of_languages.rules.base_models import PrincipleCategory, ZenPrinciple
from mcp_zen_of_languages.utils.language_detection import (
    detect_language_by_extension,
    detect_language_from_content,
)
from mcp_zen_of_languages.utils.parsers import parse_python


def test_main_entrypoint_module_executes(monkeypatch):
    import mcp_zen_of_languages.__main__ as main_module

    called: dict[str, bool] = {"run": False}

    def fake_run():
        called["run"] = True

    monkeypatch.setattr(main_module.mcp, "run", fake_run)
    main_module.main()
    assert called["run"] is True


def test_detection_pipeline_logs_errors(capsys):
    class BoomDetector(PlaceholderDetector):
        @property
        def name(self) -> str:
            return "boom"

        def detect(self, context: AnalysisContext, config):
            msg = "boom"
            raise RuntimeError(msg)

    pipeline = DetectionPipeline([BoomDetector()])
    pipeline.run(AnalysisContext(code="", language="python"), AnalyzerConfig())
    captured = capsys.readouterr()
    assert "Error in detector boom" in captured.out


def test_pipeline_merge_override_language_mismatch():
    base = PipelineConfig.from_rules("python")
    overrides = PipelineConfig.from_rules("go")
    with pytest.raises(ValueError):
        merge_pipeline_overrides(base, overrides)


def test_cli_filter_result_and_placeholder():
    cyclomatic = CyclomaticSummary(blocks=[], average=0.0)
    metrics = Metrics(cyclomatic=cyclomatic, maintainability_index=0.0, lines_of_code=1)
    violations = [Violation(principle="p", severity=2, message="low")]
    result = AnalysisResult(
        language="python",
        path="file.py",
        metrics=metrics,
        violations=violations,
        overall_score=98.0,
    )
    filtered = _filter_result(result, min_severity=5)
    assert filtered.violations == []
    placeholder = _placeholder_result("python", "file.py")
    assert placeholder.language == "python"


def test_cli_render_report_output():
    report_data = {"foo": "bar"}
    report = types.SimpleNamespace(markdown="# Title", data=report_data)
    assert "# Title" in _render_report_output(report, "markdown")
    assert json.loads(_render_report_output(report, "json"))["foo"] == "bar"
    both = json.loads(_render_report_output(report, "both"))
    assert "markdown" in both


def test_cli_main_unknown_command(tmp_path, capsys):
    exit_code = main(["list-rules", "unknown"])
    assert exit_code == 2
    captured = capsys.readouterr()
    assert "Unsupported language" in captured.err


def test_config_load_defaults_and_missing(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    cfg = load_config(None)
    assert isinstance(cfg, ConfigModel)
    assert "python" in cfg.languages
    missing = load_config(str(tmp_path / "nope.yaml"))
    assert isinstance(missing, ConfigModel)


def test_language_detector_fallbacks():
    assert detect_language_by_extension("file.txt").language == "unknown"
    assert detect_language_from_content("#!/bin/bash\n").language == "unknown"


def test_rules_adapter_dependency_edges_list_and_unknown_types():
    adapter = RulesAdapter(language="python", config=RulesAdapterConfig())
    principle = ZenPrinciple(
        id="dep-x",
        principle="Deps",
        description="desc",
        severity=6,
        category=PrincipleCategory.STRUCTURE,
        violations=[],
        metrics={"max_dependencies": 0, "detect_circular_dependencies": True},
    )
    dep = {"edges": [("a", "b")], "cycles": [{"cycle": ["a", "b", "a"]}]}
    violations = adapter._check_dependencies(dep, principle, principle.metrics or {})
    assert violations


def test_rules_adapter_maintainability_threshold():
    adapter = RulesAdapter(language="python", config=RulesAdapterConfig())
    principle = ZenPrinciple(
        id="maint-1",
        principle="Maintainable",
        description="desc",
        severity=5,
        category=PrincipleCategory.STRUCTURE,
        violations=[],
        metrics={"min_maintainability_index": 50.0},
    )
    violations = adapter._check_maintainability_index(
        40.0, principle, principle.metrics
    )
    assert violations


def test_rules_adapter_compiled_pattern_errors():
    class BadPrinciple(ZenPrinciple):
        def compiled_patterns(self):
            msg = "boom"
            raise ValueError(msg)

    adapter = RulesAdapter(language="python")
    principle = BadPrinciple(
        id="pat-1",
        principle="Patterns",
        description="desc",
        severity=4,
        category=PrincipleCategory.CORRECTNESS,
        violations=[],
        detectable_patterns=["TODO"],
    )
    violations = adapter._check_patterns("TODO", principle)
    assert violations == []


def test_rules_adapter_get_detector_config_metadata():
    adapter = RulesAdapter(language="python")
    config = adapter.get_detector_config("max_function_length")
    assert isinstance(config.thresholds, dict)


def test_models_getitem_and_violation_access():
    violation = Violation(principle="p", severity=5, message="m")
    assert violation["message"] == "m"


def test_metrics_collector_error_path(monkeypatch):
    def boom(_: str):
        msg = "boom"
        raise RuntimeError(msg)

    monkeypatch.setattr(
        "mcp_zen_of_languages.metrics.collector.compute_cyclomatic_complexity", boom
    )
    cc, mi, loc = MetricsCollector.collect("line\n")
    assert cc is None
    assert mi is None
    assert loc == 1


def test_dependency_graph_build_and_find_cycles():
    graph = build_import_graph({"a.py": ["b"], "b.py": ["a"]})
    assert graph.edges
    cycle_graph = __import__("networkx").DiGraph()
    cycle_graph.add_edge("a", "b")
    cycle_graph.add_edge("b", "a")
    assert find_cycles(cycle_graph)


def test_parser_normalizer_and_parse_python():
    parsed = parse_python("def foo():\n    pass\n")
    assert isinstance(parsed, ParserResult)


def test_reporting_formats_and_prompts(tmp_path):
    target = tmp_path / "sample.py"
    target.write_text("def foo():\n    pass\n", encoding="utf-8")
    report = generate_report(str(target), include_prompts=True)
    assert report.markdown.startswith("# Zen of Languages Report")
    assert "Gap Analysis" in report.markdown
    assert "Remediation Prompts" in report.markdown
    assert report.data["prompts"] is not None


def test_reporting_markdown_helpers():
    cyclomatic = CyclomaticSummary(blocks=[], average=0.0)
    metrics = Metrics(cyclomatic=cyclomatic, maintainability_index=0.0, lines_of_code=1)
    result = AnalysisResult(
        language="python",
        path="file.py",
        metrics=metrics,
        violations=[],
        overall_score=100.0,
    )
    summary = _summarize_results([result])
    assert summary.total_files == 1
    assert _format_analysis_markdown([result])
    gaps = (
        build_gap_analysis(["python"])
        if get_all_languages()
        else build_gap_analysis([])
    )
    assert _format_gap_markdown(gaps)
    prompts = build_prompt_bundle([result])
    context = types.SimpleNamespace(prompts=prompts)
    assert _format_prompts_markdown(context)


def test_rules_registry_helpers():
    languages = get_all_languages()
    assert "python" in languages
    by_cat = get_all_principles_by_category(PrincipleCategory.READABILITY)
    assert isinstance(by_cat, dict)


def test_detector_registry_adapter_cache():
    registry = DetectorRegistry()
    with pytest.raises(ValueError):
        registry.get_config_union()


def test_rules_adapter_missing_language_defaults():
    adapter = RulesAdapter(language="unknown")
    assert adapter.find_violations("def foo():\n    pass\n") == []


def test_language_models_critical_counts():
    cyclomatic = CyclomaticSummary(blocks=[], average=0.0)
    metrics = Metrics(cyclomatic=cyclomatic, maintainability_index=0.0, lines_of_code=1)
    violation = Violation(principle="p", severity=9, message="m")
    result = AnalysisResult(
        language="python",
        path="file.py",
        metrics=metrics,
        violations=[violation],
        overall_score=80.0,
    )
    assert result.rules_summary is None
