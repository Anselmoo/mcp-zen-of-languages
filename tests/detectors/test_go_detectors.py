from mcp_zen_of_languages.analyzers.base import AnalysisContext
from mcp_zen_of_languages.analyzers.registry import REGISTRY
from mcp_zen_of_languages.languages.go.detectors import GoContextUsageDetector
from mcp_zen_of_languages.languages.go.detectors import GoDeferUsageDetector
from mcp_zen_of_languages.languages.go.detectors import GoEmbeddingDepthDetector
from mcp_zen_of_languages.languages.go.detectors import GoErrorHandlingDetector
from mcp_zen_of_languages.languages.go.detectors import GoGoroutineLeakDetector
from mcp_zen_of_languages.languages.go.detectors import GoInterfaceSizeDetector
from mcp_zen_of_languages.languages.go.detectors import GoNamingConventionDetector
from mcp_zen_of_languages.languages.go.rules import GO_ZEN


def config_for(detector_type: str):
    return next(
        cfg for cfg in REGISTRY.configs_from_rules(GO_ZEN) if cfg.type == detector_type
    )


def run_detector(detector, code, config):
    ctx = AnalysisContext(code=code, path=None, language="go")
    return detector.detect(ctx, config)


def test_go_error_handling_detector():
    code = 'package main\nfunc main(){ panic("boom") }\n'
    violations = run_detector(
        GoErrorHandlingDetector(),
        code,
        config_for("go_error_handling"),
    )
    assert violations


def test_go_interface_size_detector():
    code = "type Foo interface { A()\nB()\nC()\nD() }"
    cfg = config_for("go_interface_size").model_copy(
        update={"max_interface_methods": 3},
    )
    violations = run_detector(GoInterfaceSizeDetector(), code, cfg)
    assert violations


def test_go_context_usage_detector():
    code = "package main\nfunc Work() {}"
    violations = run_detector(
        GoContextUsageDetector(),
        code,
        config_for("go_context_usage"),
    )
    assert violations


def test_go_defer_usage_detector():
    code = "for i := 0; i < 10; i++ { defer f() }"
    violations = run_detector(
        GoDeferUsageDetector(),
        code,
        config_for("go_defer_usage"),
    )
    assert violations


def test_go_defer_usage_detector_flags_missing_defer():
    code = "package main\nfunc main() { file.Close() }\n"
    violations = run_detector(
        GoDeferUsageDetector(),
        code,
        config_for("go_defer_usage"),
    )
    assert violations


def test_go_naming_convention_detector():
    code = "var thisIsAnExcessivelyLongVariableName = 1"
    violations = run_detector(
        GoNamingConventionDetector(),
        code,
        config_for("go_naming_convention"),
    )
    assert violations


def test_go_goroutine_leak_detector_flags_unclosed_channels():
    code = "package main\nfunc main() { ch := make(chan int); _ = ch }\n"
    violations = run_detector(
        GoGoroutineLeakDetector(),
        code,
        config_for("go_goroutine_leaks"),
    )
    assert violations


# --- GoEmbeddingDepthDetector tests ---


def test_go_embedding_depth_detector_flags_deep_embedding():
    """Three anonymous embedded types exceeds the default max of 2."""
    code = "package main\ntype Deep struct {\n    Base\n    Logger\n    Tracer\n}\n"
    cfg = config_for("go_embedding_depth")
    violations = run_detector(GoEmbeddingDepthDetector(), code, cfg)
    assert violations


def test_go_embedding_depth_detector_no_violation_within_limit():
    """Two anonymous embedded types is at the default max of 2 — no violation."""
    code = "package main\ntype OK struct {\n    Base\n    Logger\n}\n"
    cfg = config_for("go_embedding_depth")
    violations = run_detector(GoEmbeddingDepthDetector(), code, cfg)
    assert not violations


def test_go_embedding_depth_detector_ignores_named_fields():
    """Named fields (FieldName Type) must not be counted as embeddings."""
    code = (
        "package main\n"
        "type Named struct {\n"
        "    Name   string\n"
        "    Logger *log.Logger\n"
        "    Count  int\n"
        "}\n"
    )
    cfg = config_for("go_embedding_depth")
    violations = run_detector(GoEmbeddingDepthDetector(), code, cfg)
    assert not violations


def test_go_embedding_depth_detector_generic_struct():
    """Generic struct declarations with type parameters are detected."""
    code = (
        "package main\n"
        "type Generic[T any] struct {\n"
        "    Base\n"
        "    Logger\n"
        "    Tracer\n"
        "}\n"
    )
    cfg = config_for("go_embedding_depth")
    violations = run_detector(GoEmbeddingDepthDetector(), code, cfg)
    assert violations


def test_go_embedding_depth_detector_with_struct_tags():
    """Embedded types with struct tags are still counted as embeddings."""
    code = (
        "package main\n"
        "type Tagged struct {\n"
        '    Base    `json:"-"`\n'
        '    Logger  `yaml:"logger"`\n'
        "    Tracer\n"
        "}\n"
    )
    cfg = config_for("go_embedding_depth")
    violations = run_detector(GoEmbeddingDepthDetector(), code, cfg)
    assert violations


def test_go_embedding_depth_detector_pointer_embeddings():
    """Pointer-embedded types (e.g. *Base) are counted."""
    code = "package main\ntype Ptrs struct {\n    *Base\n    *Logger\n    *Tracer\n}\n"
    cfg = config_for("go_embedding_depth")
    violations = run_detector(GoEmbeddingDepthDetector(), code, cfg)
    assert violations


def test_go_embedding_depth_detector_no_struct():
    """Files with no struct definitions produce no violations."""
    code = "package main\nfunc main() {}\n"
    cfg = config_for("go_embedding_depth")
    violations = run_detector(GoEmbeddingDepthDetector(), code, cfg)
    assert not violations
