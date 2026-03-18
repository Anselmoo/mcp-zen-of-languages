from __future__ import annotations

from mcp_zen_of_languages.analyzers.registry import DetectorRegistry


def test_python_language_mapping_authors_testing_and_projection_families() -> None:
    registry = DetectorRegistry()
    registry.bootstrap_from_mappings()

    assert registry.testing_ids_for("line_length", "python", "python-001") == ["pytest"]
    assert registry.verified_testing_ids_for("line_length", "python", "python-001") == [
        "pytest",
    ]
    assert registry.projection_ids_for("line_length", "python", "python-001") == [
        "go",
        "typescript",
    ]
    assert registry.verified_projection_ids_for(
        "line_length",
        "python",
        "python-001",
    ) == ["go"]

    assert registry.testing_ids_for(
        "cyclomatic_complexity",
        "python",
        "python-003",
    ) == ["pytest"]
    assert registry.projection_ids_for(
        "cyclomatic_complexity",
        "python",
        "python-003",
    ) == ["go", "typescript"]
    assert registry.verified_projection_ids_for(
        "cyclomatic_complexity",
        "python",
        "python-003",
    ) == ["go"]

    assert registry.testing_ids_for("bare_except", "python", "python-009") == [
        "pytest",
    ]
    assert registry.projection_ids_for("bare_except", "python", "python-009") == [
        "go",
    ]
    assert registry.verified_projection_ids_for(
        "bare_except",
        "python",
        "python-009",
    ) == ["go"]


def test_ruby_language_mapping_authors_rspec_and_projection_families() -> None:
    registry = DetectorRegistry()
    registry.bootstrap_from_mappings()

    assert registry.testing_ids_for("ruby_guard_clause", "ruby", "ruby-008") == [
        "rspec"
    ]
    assert registry.verified_testing_ids_for(
        "ruby_guard_clause",
        "ruby",
        "ruby-008",
    ) == ["rspec"]
    assert registry.projection_ids_for(
        "ruby_guard_clause",
        "ruby",
        "ruby-008",
    ) == ["python"]
    assert registry.verified_projection_ids_for(
        "ruby_guard_clause",
        "ruby",
        "ruby-008",
    ) == ["python"]

    assert registry.testing_ids_for(
        "ruby_block_preference",
        "ruby",
        "ruby-003",
    ) == ["rspec"]
    assert registry.projection_ids_for(
        "ruby_block_preference",
        "ruby",
        "ruby-003",
    ) == ["python", "typescript"]
    assert registry.verified_projection_ids_for(
        "ruby_block_preference",
        "ruby",
        "ruby-003",
    ) == ["python"]

    assert registry.testing_ids_for(
        "ruby_prefer_fail",
        "ruby",
        "ruby-011",
    ) == ["rspec"]


def test_go_language_mapping_authors_gotest_and_projection_families() -> None:
    registry = DetectorRegistry()
    registry.bootstrap_from_mappings()

    assert registry.testing_ids_for("go_test_presence", "go", "go-019") == [
        "gotest",
    ]
    assert registry.verified_testing_ids_for("go_test_presence", "go", "go-019") == [
        "gotest",
    ]
    assert registry.projection_ids_for("go_test_presence", "go", "go-019") == [
        "go",
    ]
    assert registry.verified_projection_ids_for("go_test_presence", "go", "go-019") == [
        "go",
    ]

    assert registry.testing_ids_for("go_benchmark", "go", "go-018") == [
        "gotest",
    ]
    assert registry.verified_testing_ids_for("go_benchmark", "go", "go-018") == [
        "gotest",
    ]
    assert registry.projection_ids_for("go_benchmark", "go", "go-018") == [
        "go",
    ]
    assert registry.verified_projection_ids_for("go_benchmark", "go", "go-018") == [
        "go",
    ]

    assert [
        model.detector_id
        for model in registry.testing_models_for_family("gotest", "go")
    ] == ["go_benchmark", "go_test_presence"]
    assert [
        model.detector_id for model in registry.projection_models_for_family("go", "go")
    ] == ["go_benchmark", "go_test_presence"]


def test_javascript_language_mapping_authors_jest_and_frontend_projection_families() -> (
    None
):
    registry = DetectorRegistry()
    registry.bootstrap_from_mappings()

    assert registry.testing_ids_for(
        "js_async_error_handling",
        "javascript",
        "js-007",
    ) == ["jest"]
    assert registry.verified_testing_ids_for(
        "js_async_error_handling",
        "javascript",
        "js-007",
    ) == ["jest"]
    assert registry.projection_ids_for(
        "js_async_error_handling",
        "javascript",
        "js-007",
    ) == ["react", "nextjs", "vue"]
    assert registry.verified_projection_ids_for(
        "js_async_error_handling",
        "javascript",
        "js-007",
    ) == ["nextjs"]

    assert registry.testing_ids_for("js_destructuring", "javascript", "js-012") == [
        "jest",
    ]
    assert registry.projection_ids_for("js_destructuring", "javascript", "js-012") == [
        "react",
        "nextjs",
        "vue",
    ]
    assert registry.verified_projection_ids_for(
        "js_destructuring",
        "javascript",
        "js-012",
    ) == ["react", "nextjs"]

    assert registry.testing_ids_for("js_object_spread", "javascript", "js-013") == [
        "jest",
    ]
    assert registry.projection_ids_for("js_object_spread", "javascript", "js-013") == [
        "react",
        "nextjs",
        "vue",
    ]
    assert registry.verified_projection_ids_for(
        "js_object_spread",
        "javascript",
        "js-013",
    ) == ["react", "nextjs"]

    assert [
        model.detector_id
        for model in registry.testing_models_for_family("jest", "javascript")
    ] == ["js_async_error_handling", "js_destructuring", "js_object_spread"]
    assert [
        model.detector_id
        for model in registry.projection_models_for_family("nextjs", "javascript")
    ] == ["js_async_error_handling", "js_destructuring", "js_object_spread"]


def test_typescript_language_mapping_authors_jest_and_frontend_projection_families() -> (
    None
):
    registry = DetectorRegistry()
    registry.bootstrap_from_mappings()

    assert registry.testing_ids_for(
        "ts_interface_preference", "typescript", "ts-003"
    ) == [
        "jest",
    ]
    assert registry.verified_testing_ids_for(
        "ts_interface_preference",
        "typescript",
        "ts-003",
    ) == ["jest"]
    assert registry.projection_ids_for(
        "ts_interface_preference",
        "typescript",
        "ts-003",
    ) == ["angular", "vue"]
    assert registry.verified_projection_ids_for(
        "ts_interface_preference",
        "typescript",
        "ts-003",
    ) == ["angular"]

    assert registry.testing_ids_for("ts_optional_chaining", "typescript", "ts-011") == [
        "jest",
    ]
    assert registry.projection_ids_for(
        "ts_optional_chaining",
        "typescript",
        "ts-011",
    ) == ["angular", "nextjs", "vue"]
    assert registry.verified_projection_ids_for(
        "ts_optional_chaining",
        "typescript",
        "ts-011",
    ) == ["angular", "nextjs"]

    assert registry.testing_ids_for("ts_async_await", "typescript", "ts-013") == [
        "jest",
    ]
    assert registry.projection_ids_for("ts_async_await", "typescript", "ts-013") == [
        "angular",
        "nextjs",
        "vue",
    ]
    assert registry.verified_projection_ids_for(
        "ts_async_await",
        "typescript",
        "ts-013",
    ) == ["nextjs"]

    assert [
        model.detector_id
        for model in registry.testing_models_for_family("jest", "typescript")
    ] == ["ts_async_await", "ts_interface_preference", "ts_optional_chaining"]
    assert [
        model.detector_id
        for model in registry.projection_models_for_family("angular", "typescript")
    ] == ["ts_async_await", "ts_interface_preference", "ts_optional_chaining"]


def test_language_family_rule_indexes_cover_authored_models_across_languages() -> None:
    registry = DetectorRegistry()
    registry.bootstrap_from_mappings()

    assert sorted(
        {
            model.detector_id
            for model in registry.testing_models_for_rule("python-001", "python")
        }
    ) == ["line_length"]
    assert sorted(
        {
            model.detector_id
            for model in registry.projection_models_for_rule("python-001", "python")
        }
    ) == ["line_length"]

    assert sorted(
        {
            model.detector_id
            for model in registry.testing_models_for_rule("ruby-008", "ruby")
        }
    ) == ["ruby_guard_clause"]
    assert sorted(
        {
            model.detector_id
            for model in registry.projection_models_for_rule("ruby-008", "ruby")
        }
    ) == ["ruby_guard_clause"]

    assert sorted(
        {
            model.detector_id
            for model in registry.testing_models_for_rule("go-019", "go")
        }
    ) == ["go_test_presence"]
    assert sorted(
        {
            model.detector_id
            for model in registry.projection_models_for_rule("go-019", "go")
        }
    ) == ["go_test_presence"]

    assert sorted(
        {
            model.detector_id
            for model in registry.testing_models_for_rule("js-007", "javascript")
        }
    ) == ["js_async_error_handling"]
    assert sorted(
        {
            model.detector_id
            for model in registry.projection_models_for_rule("js-007", "javascript")
        }
    ) == ["js_async_error_handling"]

    assert sorted(
        {
            model.detector_id
            for model in registry.testing_models_for_rule("ts-011", "typescript")
        }
    ) == ["ts_optional_chaining"]
    assert sorted(
        {
            model.detector_id
            for model in registry.projection_models_for_rule("ts-011", "typescript")
        }
    ) == ["ts_optional_chaining"]
