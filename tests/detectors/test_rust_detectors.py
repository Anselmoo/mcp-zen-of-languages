from mcp_zen_of_languages.analyzers.base import AnalysisContext
from mcp_zen_of_languages.analyzers.registry import REGISTRY
from mcp_zen_of_languages.languages.rust.detectors import (
    RustCloneOverheadDetector,
    RustDebugDeriveDetector,
    RustEnumOverBoolDetector,
    RustErrorHandlingDetector,
    RustInteriorMutabilityDetector,
    RustIteratorPreferenceDetector,
    RustLifetimeUsageDetector,
    RustMustUseDetector,
    RustNewtypePatternDetector,
    RustStdTraitsDetector,
    RustTypeSafetyDetector,
    RustUnsafeBlocksDetector,
    RustUnwrapUsageDetector,
)
from mcp_zen_of_languages.languages.rust.rules import RUST_ZEN


def config_for(detector_type: str):
    return next(
        cfg
        for cfg in REGISTRY.configs_from_rules(RUST_ZEN)
        if cfg.type == detector_type
    )


def run_detector(detector, code, config):
    ctx = AnalysisContext(code=code, path=None, language="rust")
    return detector.detect(ctx, config)


def test_rust_unwrap_usage_detector():
    code = "fn main() { let _ = Some(1).unwrap(); }"
    violations = run_detector(
        RustUnwrapUsageDetector(), code, config_for("rust_unwrap_usage")
    )
    assert violations


def test_rust_unsafe_blocks_detector():
    code = "unsafe fn do_it() {}"
    violations = run_detector(
        RustUnsafeBlocksDetector(), code, config_for("rust_unsafe_blocks")
    )
    assert violations


def test_rust_unsafe_blocks_detector_allows_safety_comment():
    code = "// SAFETY: caller upholds invariants\nunsafe { do_it(); }\n"
    violations = run_detector(
        RustUnsafeBlocksDetector(), code, config_for("rust_unsafe_blocks")
    )
    assert not violations


def test_rust_clone_overhead_detector():
    code = "fn main(){ let x = foo.clone(); let y = foo.clone(); }"
    cfg = config_for("rust_clone_overhead").model_copy(update={"max_clone_calls": 1})
    violations = run_detector(RustCloneOverheadDetector(), code, cfg)
    assert violations


def test_rust_error_handling_detector():
    code = "fn main() { let result: Result<i32, i32> = Ok(1); }"
    violations = run_detector(
        RustErrorHandlingDetector(), code, config_for("rust_error_handling")
    )
    assert violations


def test_rust_error_handling_detector_panics():
    code = 'fn main() { panic!("boom"); }'
    cfg = config_for("rust_error_handling").model_copy(
        update={"detect_unhandled_results": False, "max_panics": 0}
    )
    violations = run_detector(RustErrorHandlingDetector(), code, cfg)
    assert violations


def test_rust_type_safety_detector():
    code = "struct User { id: i32 }\n"
    violations = run_detector(RustTypeSafetyDetector(), code, config_for("rust-002"))
    assert violations


def test_rust_iterator_preference_detector():
    code = 'for item in items { println!("{}", item); }\n'
    violations = run_detector(
        RustIteratorPreferenceDetector(), code, config_for("rust-003")
    )
    assert violations


def test_rust_must_use_detector():
    code = "fn foo() -> Result<i32, i32> { Ok(1) }\n"
    violations = run_detector(RustMustUseDetector(), code, config_for("rust-005"))
    assert violations


def test_rust_debug_derive_detector():
    code = "pub struct User { id: i32 }\n"
    violations = run_detector(RustDebugDeriveDetector(), code, config_for("rust-006"))
    assert violations


def test_rust_newtype_pattern_detector():
    code = "type UserId = i32;\n"
    violations = run_detector(
        RustNewtypePatternDetector(), code, config_for("rust-007")
    )
    assert violations


def test_rust_std_traits_detector():
    code = "struct Widget { id: i32 }\n"
    violations = run_detector(RustStdTraitsDetector(), code, config_for("rust-009"))
    assert violations


def test_rust_enum_over_bool_detector():
    code = "struct Flags { active: bool }\n"
    violations = run_detector(RustEnumOverBoolDetector(), code, config_for("rust-010"))
    assert violations


def test_rust_lifetime_usage_detector():
    code = "fn foo<'a>(name: &'a str) {}\n"
    violations = run_detector(RustLifetimeUsageDetector(), code, config_for("rust-011"))
    assert violations


def test_rust_interior_mutability_detector():
    code = (
        "use std::cell::RefCell; use std::rc::Rc; "
        "struct Foo { inner: Rc<RefCell<i32>> }\n"
    )
    violations = run_detector(
        RustInteriorMutabilityDetector(), code, config_for("rust-012")
    )
    assert violations


def test_rust_detector_names_cover_paths():
    assert RustTypeSafetyDetector().name == "rust-002"
    assert RustIteratorPreferenceDetector().name == "rust-003"
    assert RustMustUseDetector().name == "rust-005"
    assert RustDebugDeriveDetector().name == "rust-006"
    assert RustNewtypePatternDetector().name == "rust-007"
    assert RustStdTraitsDetector().name == "rust-009"
    assert RustEnumOverBoolDetector().name == "rust-010"
    assert RustLifetimeUsageDetector().name == "rust-011"
    assert RustInteriorMutabilityDetector().name == "rust-012"
