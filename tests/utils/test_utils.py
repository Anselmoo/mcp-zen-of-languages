from __future__ import annotations

from mcp_zen_of_languages.models import Violation
from mcp_zen_of_languages.utils.language_detection import (
    detect_language_by_extension,
    detect_language_from_content,
)
from mcp_zen_of_languages.utils.metric import calculate_code_quality_score

SINGLE_CRITICAL_VIOLATION_SCORE = 80.0
EMPTY_VIOLATIONS_SCORE = 100.0


def test_detect_language_by_extension_known():
    result = detect_language_by_extension("example.py")
    assert result.language == "python"
    assert result.method == "extension"


def test_detect_language_by_extension_scss():
    result = detect_language_by_extension("styles.scss")
    assert result.language == "css"
    assert result.method == "extension"


def test_detect_language_by_extension_less():
    result = detect_language_by_extension("styles.less")
    assert result.language == "css"
    assert result.method == "extension"


def test_detect_language_by_extension_sql():
    result = detect_language_by_extension("schema.ddl")
    assert result.language == "sql"


def test_detect_language_by_extension_markdown():
    result = detect_language_by_extension("README.md")
    assert result.language == "markdown"
    assert result.method == "extension"


def test_detect_language_by_extension_mdx():
    result = detect_language_by_extension("page.mdx")
    assert result.language == "markdown"
    assert result.method == "extension"


def test_detect_language_by_extension_unknown():
    result = detect_language_by_extension("example.unknown")
    assert result.language == "unknown"
    assert result.confidence < 1.0


def test_detect_language_by_extension_github_workflow():
    result = detect_language_by_extension(".github/workflows/ci.yml")
    assert result.language == "github-actions"


def test_detect_language_by_extension_dockerfile_name():
    result = detect_language_by_extension("Dockerfile.prod")
    assert result.language == "dockerfile"
    assert result.method == "extension"


def test_detect_language_by_extension_docker_compose_name():
    result = detect_language_by_extension("docker-compose.yml")
    assert result.language == "docker_compose"
    assert result.method == "extension"


def test_detect_language_from_content_python():
    result = detect_language_from_content("def foo():\n    pass\n")
    assert result.language == "python"


def test_detect_language_from_content_typescript():
    result = detect_language_from_content("interface Foo { }\n")
    assert result.language == "typescript"


def test_detect_language_from_content_javascript():
    result = detect_language_from_content("const foo = () => {}\n")
    assert result.language == "typescript"


def test_detect_language_from_content_unknown():
    result = detect_language_from_content("just some text")
    assert result.language == "unknown"


def test_detect_language_from_content_javascript_const():
    result = detect_language_from_content("const foo = 1\n")
    assert result.language == "javascript"


def test_calculate_code_quality_score_caps_at_zero():
    violations = [Violation(principle="T", severity=10, message="bad")]
    assert calculate_code_quality_score(violations) == SINGLE_CRITICAL_VIOLATION_SCORE
    assert calculate_code_quality_score(violations * 20) == 0.0


def test_calculate_code_quality_score_reduces_by_severity():
    violations = [
        Violation(principle="T1", severity=5, message="bad"),
        Violation(principle="T2", severity=10, message="bad"),
    ]
    assert calculate_code_quality_score(violations) == 100.0 - (5 + 10) * 2


def test_calculate_code_quality_score_empty_input():
    assert calculate_code_quality_score([]) == EMPTY_VIOLATIONS_SCORE
