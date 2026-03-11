import pytest

from mcp_zen_of_languages.adapters.universal import AnalyzerFactoryAdapter
from mcp_zen_of_languages.adapters.universal import build_universal_adapters
from mcp_zen_of_languages.analyzers.analyzer_factory import supported_languages
from mcp_zen_of_languages.core.detector import DOGMA_RULE_IDS
from mcp_zen_of_languages.core.detector import UniversalZenDetector
from mcp_zen_of_languages.core.detectors import ClutterDetector
from mcp_zen_of_languages.core.detectors import ControlFlowDetector
from mcp_zen_of_languages.core.detectors import SignatureDetector
from mcp_zen_of_languages.core.detectors import StateMutationDetector
from mcp_zen_of_languages.transport.reporters import CliReporter
from mcp_zen_of_languages.transport.reporters import McpReporter


UNIVERSAL_LANGUAGE_SNIPPETS = {
    "python": "def add(a, b):\n    return a + b\n",
    "typescript": "const value: number = 1;\n",
    "javascript": "const value = 1;\n",
    "go": "package main\n\nfunc add(a int, b int) int { return a + b }\n",
    "rust": "fn add(a: i32, b: i32) -> i32 { a + b }\n",
    "bash": "#!/usr/bin/env bash\necho 'hi'\n",
    "powershell": "Write-Output 'hi'\n",
    "ruby": "def add(a, b)\n  a + b\nend\n",
    "cpp": "#include <iostream>\nint main() { return 0; }\n",
    "csharp": "class Program { static void Main() { } }\n",
    "css": "body { color: red; }\n",
    "docker_compose": "services:\n  app:\n    image: alpine:latest\n",
    "dockerfile": "FROM alpine:3.20\nRUN echo hi\n",
    "ansible": "- hosts: all\n  tasks:\n    - name: ping\n      ansible.builtin.ping:\n",
    "terraform": 'terraform { required_version = ">= 1.6.0" }\nresource "null_resource" "example" {}\n',
    "yaml": "key: value\n",
    "github-actions": (
        "name: CI\n"
        "on: [push]\n"
        "jobs:\n"
        "  build:\n"
        "    runs-on: ubuntu-latest\n"
        "    steps:\n"
        "      - run: echo hi\n"
    ),
    "toml": 'name = "example"\n',
    "xml": "<root><item>v</item></root>\n",
    "svg": '<svg xmlns="http://www.w3.org/2000/svg"><title>i</title></svg>\n',
    "json": '{"name":"example"}\n',
    "sql": "SELECT 1;\n",
    "markdown": "# Title\n\nText.\n",
    "latex": ("\\documentclass{article}\n\\begin{document}\nHello\n\\end{document}\n"),
    "gitlab_ci": "stages:\n  - build\nbuild:\n  stage: build\n  script:\n    - echo hi\n",
}


def test_universal_language_snippet_matrix_matches_supported_languages() -> None:
    assert set(UNIVERSAL_LANGUAGE_SNIPPETS) == set(supported_languages())


@pytest.mark.parametrize("language", ["python", "typescript", "yaml"])
def test_universal_detector_single_language_adapter_cli_and_mcp_output(
    language: str,
) -> None:
    detector = UniversalZenDetector(
        adapters={language: AnalyzerFactoryAdapter(language)}
    )
    result = detector.analyze(
        UNIVERSAL_LANGUAGE_SNIPPETS[language],
        language=language,
    )

    cli_output = CliReporter().report(result)
    mcp_output = McpReporter().report(result)

    assert result.language == language
    assert "violations=" in cli_output
    assert mcp_output["language"] == language
    assert "violations" in mcp_output


def test_universal_detector_default_adapter_keys_match_supported_languages() -> None:
    assert set(build_universal_adapters()) == set(supported_languages())


@pytest.mark.parametrize("language", supported_languages())
def test_universal_detector_default_adapters_smoke_all_languages(
    language: str,
) -> None:
    detector = UniversalZenDetector()
    result = detector.analyze(
        UNIVERSAL_LANGUAGE_SNIPPETS[language],
        language=language,
    )
    cli_output = CliReporter().report(result)
    mcp_output = McpReporter().report(result)

    assert result.language == language
    assert "violations=" in cli_output
    assert mcp_output["language"] == language
    assert "violations" in mcp_output


def test_universal_detector_rejects_unsupported_language() -> None:
    detector = UniversalZenDetector(
        adapters={"python": AnalyzerFactoryAdapter("python")}
    )
    with pytest.raises(ValueError, match="Unsupported language adapter"):
        detector.analyze("x = 1", language="unknown")


def test_dogma_stub_detectors_expose_expected_rule_ids() -> None:
    expected_dogmas = 30  # 10 Universal + 10 TestingTactics + 10 TestingStrategy
    assert "ZEN-FAIL-FAST" in ControlFlowDetector().rule_ids
    assert "ZEN-UTILIZE-ARGUMENTS" in SignatureDetector().rule_ids
    assert "ZEN-VISIBLE-STATE" in StateMutationDetector().rule_ids
    assert "ZEN-RUTHLESS-DELETION" in ClutterDetector().rule_ids
    assert len(DOGMA_RULE_IDS) == expected_dogmas
