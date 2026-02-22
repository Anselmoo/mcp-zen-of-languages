from __future__ import annotations

import inspect

from mcp_zen_of_languages.analyzers.analyzer_factory import (
    create_analyzer,
    supported_languages,
)
from mcp_zen_of_languages.analyzers.base import (
    AnalysisContext,
    AnalyzerCapabilities,
    AnalyzerConfig,
    AstStatus,
    BaseAnalyzer,
    DetectionPipeline,
    ViolationDetector,
)
from mcp_zen_of_languages.models import CyclomaticSummary, ParserResult

AST_CAPABLE_LANGUAGES = {
    "python",
    "sql",
    "github-actions",
    "yaml",
    "json",
    "toml",
    "xml",
    "docker_compose",
    "gitlab_ci",
}

DEPENDENCY_CAPABLE_LANGUAGES = {
    "python",
    "javascript",
    "typescript",
    "go",
    "rust",
    "bash",
    "ruby",
    "cpp",
    "csharp",
    "css",
    "dockerfile",
    "powershell",
}
PARSE_SIGNATURE_PARAM_COUNT = 2
METRICS_SIGNATURE_PARAM_COUNT = 3
DEPENDENCY_SIGNATURE_PARAM_COUNT = 2


def _analyzers_by_language() -> dict[str, BaseAnalyzer]:
    return {language: create_analyzer(language) for language in supported_languages()}


class _ProbeDetector(ViolationDetector[AnalyzerConfig]):
    def __init__(self) -> None:
        super().__init__()
        self.captured_context: AnalysisContext | None = None

    @property
    def name(self) -> str:
        return "probe-detector"

    def detect(
        self,
        context: AnalysisContext,
        config: AnalyzerConfig,
    ) -> list:
        _ = config
        self.captured_context = context
        return []


class _ProbeAnalyzer(BaseAnalyzer):
    def __init__(
        self, *, supports_ast: bool, parse_result: ParserResult | None
    ) -> None:
        self._supports_ast = supports_ast
        self._parse_result = parse_result
        self.probe = _ProbeDetector()
        super().__init__()

    def default_config(self) -> AnalyzerConfig:
        return AnalyzerConfig()

    def language(self) -> str:
        return "python"

    def capabilities(self) -> AnalyzerCapabilities:
        return AnalyzerCapabilities(supports_ast=self._supports_ast)

    def parse_code(self, code: str) -> ParserResult | None:
        _ = code
        return self._parse_result

    def compute_metrics(
        self,
        code: str,
        ast_tree: ParserResult | None,
    ) -> tuple[CyclomaticSummary | None, float | None, int]:
        _ = ast_tree
        return CyclomaticSummary(blocks=[], average=0.0), 0.0, len(code.splitlines())

    def build_pipeline(self) -> DetectionPipeline:
        return DetectionPipeline([self.probe])


def test_all_analyzers_have_parse_code() -> None:
    for analyzer in _analyzers_by_language().values():
        assert hasattr(type(analyzer), "parse_code")


def test_all_analyzers_have_compute_metrics() -> None:
    for analyzer in _analyzers_by_language().values():
        assert hasattr(type(analyzer), "compute_metrics")


def test_all_analyzers_have_build_dependency_analysis() -> None:
    for analyzer in _analyzers_by_language().values():
        assert hasattr(type(analyzer), "_build_dependency_analysis")


def test_parse_code_signature_preserved() -> None:
    for analyzer in _analyzers_by_language().values():
        params = list(inspect.signature(type(analyzer).parse_code).parameters.values())
        assert len(params) == PARSE_SIGNATURE_PARAM_COUNT
        assert params[0].name == "self"
        assert params[1].name in {"code", "_code"}


def test_compute_metrics_signature_has_ast_tree() -> None:
    for analyzer in _analyzers_by_language().values():
        params = list(
            inspect.signature(type(analyzer).compute_metrics).parameters.values()
        )
        assert len(params) == METRICS_SIGNATURE_PARAM_COUNT
        assert params[0].name == "self"
        assert params[1].name == "code"
        assert params[2].name in {"ast_tree", "_ast_tree"}


def test_build_dependency_analysis_signature_has_context() -> None:
    for analyzer in _analyzers_by_language().values():
        params = list(
            inspect.signature(
                type(analyzer)._build_dependency_analysis
            ).parameters.values(),
        )
        assert len(params) == DEPENDENCY_SIGNATURE_PARAM_COUNT
        assert params[0].name == "self"
        assert params[1].name in {"context", "_context"}


def test_placeholder_analyzers_return_none_from_parse_code() -> None:
    for language, analyzer in _analyzers_by_language().items():
        if language in AST_CAPABLE_LANGUAGES:
            continue
        assert analyzer.parse_code("placeholder source") is None


def test_capable_analyzers_declare_supports_ast() -> None:
    analyzers = _analyzers_by_language()
    for language in AST_CAPABLE_LANGUAGES:
        assert analyzers[language].capabilities().supports_ast is True


def test_placeholder_analyzers_have_default_capabilities() -> None:
    for language, analyzer in _analyzers_by_language().items():
        if language in AST_CAPABLE_LANGUAGES:
            continue
        if language in DEPENDENCY_CAPABLE_LANGUAGES:
            continue
        assert analyzer.capabilities().supports_ast is False


def test_dependency_capable_analyzers_declare_supports_dependency() -> None:
    analyzers = _analyzers_by_language()
    for language in DEPENDENCY_CAPABLE_LANGUAGES:
        assert analyzers[language].capabilities().supports_dependency_analysis is True


def test_context_has_ast_status_field() -> None:
    assert "ast_status" in AnalysisContext.model_fields


def test_context_has_capabilities_field() -> None:
    assert "capabilities" in AnalysisContext.model_fields


def test_analyze_sets_ast_status_parsed_via_probe() -> None:
    analyzer = _ProbeAnalyzer(
        supports_ast=True,
        parse_result=ParserResult(type="probe", tree={"ok": True}),
    )
    analyzer.analyze("x = 1")
    assert analyzer.probe.captured_context is not None
    assert analyzer.probe.captured_context.ast_status == AstStatus.parsed


def test_analyze_sets_ast_status_parse_failed_via_probe() -> None:
    analyzer = _ProbeAnalyzer(supports_ast=True, parse_result=None)
    analyzer.analyze("x = 1")
    assert analyzer.probe.captured_context is not None
    assert analyzer.probe.captured_context.ast_status == AstStatus.parse_failed


def test_analyze_sets_ast_status_unsupported_via_probe() -> None:
    analyzer = _ProbeAnalyzer(supports_ast=False, parse_result=None)
    analyzer.analyze("x = 1")
    assert analyzer.probe.captured_context is not None
    assert analyzer.probe.captured_context.ast_status == AstStatus.unsupported


def test_sql_analyzer_invalid_parse_and_defaults() -> None:
    analyzer = create_analyzer("sql")
    assert analyzer.parse_code("SELECT FROM") is None
    assert analyzer.compute_metrics("SELECT 1;", None)[2] == 1
    context = AnalysisContext(code="SELECT 1;", language="sql")
    assert analyzer._build_dependency_analysis(context) is None


def test_github_actions_analyzer_methods() -> None:
    analyzer = create_analyzer("github-actions")
    parsed = analyzer.parse_code(
        "name: CI\non: push\njobs:\n  test:\n    runs-on: ubuntu-latest\n    steps:\n      - run: echo hi\n",
    )
    assert parsed is not None
    assert analyzer.compute_metrics("name: CI\n", None)[2] == 1
    context = AnalysisContext(code="name: CI\n", language="github-actions")
    assert analyzer._build_dependency_analysis(context) is None
