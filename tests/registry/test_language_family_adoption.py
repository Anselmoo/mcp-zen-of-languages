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
