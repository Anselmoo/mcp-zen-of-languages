from __future__ import annotations

import json

import pytest

from mcp_zen_of_languages.adapters.rules_adapter import RulesAdapter, RulesAdapterConfig
from mcp_zen_of_languages.analyzers.base import (
    AnalysisContext,
    AnalyzerConfig,
    BaseAnalyzer,
    DetectionPipeline,
)
from mcp_zen_of_languages.analyzers.pipeline import PipelineConfig
from mcp_zen_of_languages.analyzers.registry import DetectorRegistry
from mcp_zen_of_languages.cli import main
from mcp_zen_of_languages.config import load_config
from mcp_zen_of_languages.languages.configs import LineLengthConfig
from mcp_zen_of_languages.models import CyclomaticSummary
from mcp_zen_of_languages.reporting.report import generate_report
from mcp_zen_of_languages.rules import get_principle_by_id
from mcp_zen_of_languages.rules.base_models import PrincipleCategory, ZenPrinciple

EMPTY_VIOLATIONS_SCORE = 100.0
REPORT_FAILURE_EXIT_CODE = 2


class DummyAnalyzer(BaseAnalyzer):
    def __init__(self):
        self._pipeline_config = PipelineConfig(language="python", detectors=[])
        super().__init__()

    def default_config(self) -> AnalyzerConfig:
        return AnalyzerConfig()

    def language(self) -> str:
        return "python"

    def parse_code(self, code: str):
        return None

    def compute_metrics(self, code: str, ast_tree):
        return CyclomaticSummary(blocks=[], average=0.0), 90.0, 1


class NoPatternAnalyzer(DummyAnalyzer):
    def __init__(self):
        self._pipeline_config = PipelineConfig(language="python", detectors=[])
        super().__init__()

    def parse_code(self, code: str):
        return None

    def compute_metrics(self, code: str, ast_tree):
        return CyclomaticSummary(blocks=[], average=0.0), None, 1


class BoomPipeline(DetectionPipeline):
    def run(self, context: AnalysisContext, config: AnalyzerConfig):
        msg = "boom"
        raise RuntimeError(msg)

    def build_pipeline(self):
        return BoomPipeline([])


class EmptyPipeline(DetectionPipeline):
    def __init__(self):
        super().__init__([])


class EmptyAnalyzer(DummyAnalyzer):
    def build_pipeline(self):
        return EmptyPipeline()


class WrongLangAnalyzer(DummyAnalyzer):
    def language(self) -> str:
        return "unknown"


class DictDepAnalyzer(DummyAnalyzer):
    def build_pipeline(self):
        return EmptyPipeline()

    def _build_dependency_analysis(self, context: AnalysisContext):
        return {"nodes": ["a"], "edges": [("a", "b")], "cycles": []}


class DisabledPatternAnalyzer(DummyAnalyzer):
    def __init__(self):
        self._pipeline_config = PipelineConfig(
            language="python", detectors=[LineLengthConfig()]
        )
        super().__init__()
        self.config.enable_pattern_detection = False

    def build_pipeline(self):
        return EmptyPipeline()


def test_base_analyzer_errors_and_helpers():
    with pytest.raises(TypeError):
        DummyAnalyzer(config=object())

    analyzer = DummyAnalyzer()
    assert analyzer._calculate_overall_score([]) == EMPTY_VIOLATIONS_SCORE

    assert analyzer._create_context("", None, None, None).language == "python"


def test_base_analyzer_rule_adapter_branches():
    analyzer = DictDepAnalyzer()
    analyzer.config.enable_pattern_detection = True
    result = analyzer.analyze("def foo():\n    pass\n")
    assert result.rules_summary is not None

    analyzer = DisabledPatternAnalyzer()
    result = analyzer.analyze("def foo():\n    pass\n")
    assert result.rules_summary is not None

    with pytest.raises(ValueError, match="No zen rules for language: unknown"):
        WrongLangAnalyzer()


def test_pipeline_config_error_path():
    with pytest.raises(ValueError, match="No zen rules for language: unknown"):
        PipelineConfig.from_rules("unknown")


def test_registry_get_unknown():
    registry = DetectorRegistry()
    with pytest.raises(KeyError):
        registry.get("missing")


def test_config_pipeline_overrides(tmp_path):
    cfg_path = tmp_path / "zen-config.yaml"
    cfg_path.write_text(
        "languages:\n  - python\npipelines:\n  - language: python\n    detectors: []\n",
        encoding="utf-8",
    )
    cfg = load_config(str(cfg_path))
    assert cfg.pipeline_for("python").language == "python"


def test_cli_report_no_files(tmp_path, capsys):
    exit_code = main(["report", str(tmp_path)])
    assert exit_code == REPORT_FAILURE_EXIT_CODE
    captured = capsys.readouterr()
    assert "No analyzable files" in captured.err


def test_cli_report_missing_path(tmp_path, capsys):
    exit_code = main(["report", str(tmp_path / "missing")])
    assert exit_code == REPORT_FAILURE_EXIT_CODE
    captured = capsys.readouterr()
    assert "Path not found" in captured.err


def test_cli_report_json_single_file(tmp_path):
    sample = tmp_path / "sample.py"
    sample.write_text("def foo():\n    pass\n", encoding="utf-8")
    output = tmp_path / "report.json"
    exit_code = main(["report", str(sample), "--format", "json", "--out", str(output)])
    assert exit_code == 0
    payload = json.loads(output.read_text(encoding="utf-8"))
    assert payload["target"].endswith("sample.py")


def test_reporting_without_analysis(tmp_path):
    target = tmp_path / "sample.py"
    target.write_text("def foo():\n    pass\n", encoding="utf-8")
    report = generate_report(str(target), include_analysis=False, include_gaps=False)
    assert report.data["analysis"] == []


def test_rules_adapter_empty_and_patterns():
    adapter = RulesAdapter(language="python", config=RulesAdapterConfig())
    assert adapter.find_violations("def foo():\n    pass\n") == []
    principle = ZenPrinciple(
        id="pat-2",
        principle="Pattern",
        description="desc",
        severity=4,
        category=PrincipleCategory.CORRECTNESS,
        violations=["TODO"],
        detectable_patterns=["TODO"],
    )
    violations = adapter._check_patterns("TODO", principle)
    assert violations


def test_language_detector_branches():
    assert get_principle_by_id("python-001") is not None
