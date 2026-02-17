from __future__ import annotations

from mcp_zen_of_languages.analyzers.base import AnalysisContext
from mcp_zen_of_languages.languages.configs import (
    JsAsyncErrorHandlingConfig,
    JsFunctionLengthConfig,
    PowerShellApprovedVerbConfig,
)
from mcp_zen_of_languages.languages.javascript.detectors import (
    JsAsyncErrorHandlingDetector,
    JsFunctionLengthDetector,
)
from mcp_zen_of_languages.languages.powershell.detectors import (
    PowerShellApprovedVerbDetector,
)


def test_js_async_error_handling_detector():
    context = AnalysisContext(code="async function foo() {}", language="javascript")
    violations = JsAsyncErrorHandlingDetector().detect(
        context, JsAsyncErrorHandlingConfig()
    )
    assert violations


def test_js_async_error_handling_detector_for_promises():
    context = AnalysisContext(code="fetch(url).then(handle);", language="javascript")
    violations = JsAsyncErrorHandlingDetector().detect(
        context, JsAsyncErrorHandlingConfig()
    )
    assert violations


def test_js_function_length_detector():
    code = "function foo() {\n" + "  a++;\n" * 10 + "}\n"
    context = AnalysisContext(code=code, language="javascript")
    config = JsFunctionLengthConfig().model_copy(update={"max_function_length": 1})
    violations = JsFunctionLengthDetector().detect(context, config)
    assert violations


def test_powershell_approved_verb_detector():
    code = "function customThing-Thing { }\n"
    context = AnalysisContext(code=code, language="powershell")
    violations = PowerShellApprovedVerbDetector().detect(
        context, PowerShellApprovedVerbConfig()
    )
    assert violations
