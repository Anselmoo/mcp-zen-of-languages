import pytest

from mcp_zen_of_languages.adapters.python_mvp import PythonMVPAdapter
from mcp_zen_of_languages.core.detector import DOGMA_RULE_IDS, UniversalZenDetector
from mcp_zen_of_languages.core.detectors import (
    ClutterDetector,
    ControlFlowDetector,
    SignatureDetector,
    StateMutationDetector,
)
from mcp_zen_of_languages.transport.reporters import CliReporter, McpReporter


def test_universal_detector_python_mvp_cli_and_mcp_output() -> None:
    detector = UniversalZenDetector(adapters={"python": PythonMVPAdapter()})
    result = detector.analyze("def add(a, b):\n    return a + b\n", language="python")

    cli_output = CliReporter().report(result)
    mcp_output = McpReporter().report(result)

    assert result.language == "python"
    assert "violations=" in cli_output
    assert mcp_output["language"] == "python"
    assert "violations" in mcp_output


def test_universal_detector_default_adapters_cover_all_languages() -> None:
    detector = UniversalZenDetector()

    python_result = detector.analyze(
        "def add(a, b):\n    return a + b\n", language="python"
    )
    ts_result = detector.analyze("const value: number = 1;", language="typescript")

    assert python_result.language == "python"
    assert ts_result.language == "typescript"


def test_universal_detector_rejects_unsupported_language() -> None:
    detector = UniversalZenDetector(adapters={"python": PythonMVPAdapter()})
    with pytest.raises(ValueError, match="Unsupported language adapter"):
        detector.analyze("x = 1", language="unknown")


def test_dogma_stub_detectors_expose_expected_rule_ids() -> None:
    expected_dogmas = 10
    assert "ZEN-FAIL-FAST" in ControlFlowDetector.rule_ids
    assert "ZEN-UTILIZE-ARGUMENTS" in SignatureDetector.rule_ids
    assert "ZEN-VISIBLE-STATE" in StateMutationDetector.rule_ids
    assert "ZEN-RUTHLESS-DELETION" in ClutterDetector.rule_ids
    assert len(DOGMA_RULE_IDS) == expected_dogmas
