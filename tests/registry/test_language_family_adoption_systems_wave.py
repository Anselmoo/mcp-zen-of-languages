from __future__ import annotations

from mcp_zen_of_languages.analyzers.registry import DetectorRegistry


def test_csharp_language_mapping_authors_xunit_and_projection_families() -> None:
    registry = DetectorRegistry()
    registry.bootstrap_from_mappings()

    assert registry.testing_ids_for("csharp_async_await", "csharp", "cs-004") == [
        "xunit",
    ]
    assert registry.verified_testing_ids_for(
        "csharp_async_await", "csharp", "cs-004"
    ) == [
        "xunit",
    ]
    assert registry.projection_ids_for("csharp_async_await", "csharp", "cs-004") == [
        "csharp",
    ]
    assert registry.verified_projection_ids_for(
        "csharp_async_await",
        "csharp",
        "cs-004",
    ) == ["csharp"]

    assert registry.testing_ids_for("cs-012", "csharp", "cs-012") == ["xunit"]
    assert registry.verified_testing_ids_for("cs-012", "csharp", "cs-012") == [
        "xunit",
    ]
    assert registry.projection_ids_for("cs-012", "csharp", "cs-012") == ["csharp"]
    assert registry.verified_projection_ids_for("cs-012", "csharp", "cs-012") == [
        "csharp",
    ]

    assert [
        model.detector_id
        for model in registry.testing_models_for_family("xunit", "csharp")
    ] == ["cs-012", "csharp_async_await"]
    assert [
        model.detector_id
        for model in registry.projection_models_for_family("csharp", "csharp")
    ] == ["cs-012", "csharp_async_await"]


def test_rust_language_mapping_authors_cargo_test_and_projection_families() -> None:
    registry = DetectorRegistry()
    registry.bootstrap_from_mappings()

    assert registry.testing_ids_for("rust_unwrap_usage", "rust", "rust-001") == [
        "cargo-test",
    ]
    assert registry.verified_testing_ids_for(
        "rust_unwrap_usage", "rust", "rust-001"
    ) == [
        "cargo-test",
    ]
    assert registry.projection_ids_for("rust_unwrap_usage", "rust", "rust-001") == [
        "rust",
    ]
    assert registry.verified_projection_ids_for(
        "rust_unwrap_usage",
        "rust",
        "rust-001",
    ) == ["rust"]

    assert registry.testing_ids_for("rust_unsafe_blocks", "rust", "rust-008") == [
        "cargo-test",
    ]
    assert registry.verified_testing_ids_for(
        "rust_unsafe_blocks",
        "rust",
        "rust-008",
    ) == ["cargo-test"]
    assert registry.projection_ids_for("rust_unsafe_blocks", "rust", "rust-008") == [
        "rust",
    ]
    assert registry.verified_projection_ids_for(
        "rust_unsafe_blocks",
        "rust",
        "rust-008",
    ) == ["rust"]

    assert [
        model.detector_id
        for model in registry.testing_models_for_family("cargo-test", "rust")
    ] == ["rust_unsafe_blocks", "rust_unwrap_usage"]
    assert [
        model.detector_id
        for model in registry.projection_models_for_family("rust", "rust")
    ] == ["rust_unsafe_blocks", "rust_unwrap_usage"]


def test_cpp_language_mapping_authors_gtest_and_projection_families() -> None:
    registry = DetectorRegistry()
    registry.bootstrap_from_mappings()

    assert registry.testing_ids_for("cpp_smart_pointers", "cpp", "cpp-002") == [
        "gtest",
    ]
    assert registry.verified_testing_ids_for(
        "cpp_smart_pointers", "cpp", "cpp-002"
    ) == [
        "gtest",
    ]
    assert registry.projection_ids_for("cpp_smart_pointers", "cpp", "cpp-002") == [
        "cpp",
    ]
    assert registry.verified_projection_ids_for(
        "cpp_smart_pointers",
        "cpp",
        "cpp-002",
    ) == ["cpp"]

    assert registry.testing_ids_for("cpp-001", "cpp", "cpp-001") == ["gtest"]
    assert registry.verified_testing_ids_for("cpp-001", "cpp", "cpp-001") == ["gtest"]
    assert registry.projection_ids_for("cpp-001", "cpp", "cpp-001") == ["cpp"]
    assert registry.verified_projection_ids_for("cpp-001", "cpp", "cpp-001") == [
        "cpp",
    ]

    assert [
        model.detector_id
        for model in registry.testing_models_for_family("gtest", "cpp")
    ] == ["cpp-001", "cpp_smart_pointers"]
    assert [
        model.detector_id
        for model in registry.projection_models_for_family("cpp", "cpp")
    ] == ["cpp-001", "cpp_smart_pointers"]


def test_sql_language_mapping_authors_sqllogictest_and_projection_families() -> None:
    registry = DetectorRegistry()
    registry.bootstrap_from_mappings()

    assert registry.testing_ids_for("sql-001", "sql", "sql-001") == ["sqllogictest"]
    assert registry.verified_testing_ids_for("sql-001", "sql", "sql-001") == [
        "sqllogictest",
    ]
    assert registry.projection_ids_for("sql-001", "sql", "sql-001") == ["sql"]
    assert registry.verified_projection_ids_for("sql-001", "sql", "sql-001") == ["sql"]

    assert registry.testing_ids_for("sql-002", "sql", "sql-002") == ["sqllogictest"]
    assert registry.verified_testing_ids_for("sql-002", "sql", "sql-002") == [
        "sqllogictest",
    ]
    assert registry.projection_ids_for("sql-002", "sql", "sql-002") == ["sql"]
    assert registry.verified_projection_ids_for("sql-002", "sql", "sql-002") == ["sql"]

    assert [
        model.detector_id
        for model in registry.testing_models_for_family("sqllogictest", "sql")
    ] == ["sql-001", "sql-002"]
    assert [
        model.detector_id
        for model in registry.projection_models_for_family("sql", "sql")
    ] == ["sql-001", "sql-002"]
