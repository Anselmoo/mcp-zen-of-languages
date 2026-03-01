from __future__ import annotations

from mcp_zen_of_languages.analyzers.base import AnalysisContext
from mcp_zen_of_languages.languages.configs import CSharpCollectionExpressionConfig
from mcp_zen_of_languages.languages.configs import CSharpDisposableConfig
from mcp_zen_of_languages.languages.configs import CSharpExceptionHandlingConfig
from mcp_zen_of_languages.languages.configs import CSharpExpressionBodiedConfig
from mcp_zen_of_languages.languages.configs import CSharpLinqConfig
from mcp_zen_of_languages.languages.configs import CSharpMagicNumberConfig
from mcp_zen_of_languages.languages.configs import CSharpNullableConfig
from mcp_zen_of_languages.languages.configs import CSharpPatternMatchingConfig
from mcp_zen_of_languages.languages.configs import CSharpRecordConfig
from mcp_zen_of_languages.languages.configs import CSharpVarConfig
from mcp_zen_of_languages.languages.configs import CppAutoConfig
from mcp_zen_of_languages.languages.configs import CppAvoidGlobalsConfig
from mcp_zen_of_languages.languages.configs import CppCStyleCastConfig
from mcp_zen_of_languages.languages.configs import CppConstCorrectnessConfig
from mcp_zen_of_languages.languages.configs import CppManualAllocationConfig
from mcp_zen_of_languages.languages.configs import CppMoveConfig
from mcp_zen_of_languages.languages.configs import CppOptionalConfig
from mcp_zen_of_languages.languages.configs import CppOverrideFinalConfig
from mcp_zen_of_languages.languages.configs import CppRaiiConfig
from mcp_zen_of_languages.languages.configs import CppRangeForConfig
from mcp_zen_of_languages.languages.configs import CppRuleOfFiveConfig
from mcp_zen_of_languages.languages.configs import Cs008Config
from mcp_zen_of_languages.languages.configs import CssColorLiteralConfig
from mcp_zen_of_languages.languages.configs import CssGodStylesheetConfig
from mcp_zen_of_languages.languages.configs import CssImportChainConfig
from mcp_zen_of_languages.languages.configs import CssMagicPixelsConfig
from mcp_zen_of_languages.languages.configs import CssMediaQueryScaleConfig
from mcp_zen_of_languages.languages.configs import CssSpecificityConfig
from mcp_zen_of_languages.languages.configs import CssVendorPrefixConfig
from mcp_zen_of_languages.languages.configs import CssZIndexScaleConfig
from mcp_zen_of_languages.languages.configs import GoGoroutineLeakConfig
from mcp_zen_of_languages.languages.configs import GoInitUsageConfig
from mcp_zen_of_languages.languages.configs import GoInterfacePointerConfig
from mcp_zen_of_languages.languages.configs import GoInterfaceReturnConfig
from mcp_zen_of_languages.languages.configs import GoPackageNamingConfig
from mcp_zen_of_languages.languages.configs import GoPackageStateConfig
from mcp_zen_of_languages.languages.configs import GoZeroValueConfig
from mcp_zen_of_languages.languages.configs import Js009Config
from mcp_zen_of_languages.languages.configs import Js011Config
from mcp_zen_of_languages.languages.configs import JsGlobalStateConfig
from mcp_zen_of_languages.languages.configs import JsMagicNumbersConfig
from mcp_zen_of_languages.languages.configs import JsModernFeaturesConfig
from mcp_zen_of_languages.languages.configs import JsPureFunctionConfig
from mcp_zen_of_languages.languages.configs import JsonArrayOrderConfig
from mcp_zen_of_languages.languages.configs import JsonDateFormatConfig
from mcp_zen_of_languages.languages.configs import JsonDuplicateKeyConfig
from mcp_zen_of_languages.languages.configs import JsonKeyCasingConfig
from mcp_zen_of_languages.languages.configs import JsonMagicStringConfig
from mcp_zen_of_languages.languages.configs import JsonNullHandlingConfig
from mcp_zen_of_languages.languages.configs import JsonNullSprawlConfig
from mcp_zen_of_languages.languages.configs import JsonSchemaConsistencyConfig
from mcp_zen_of_languages.languages.configs import JsonStrictnessConfig
from mcp_zen_of_languages.languages.configs import PowerShellAliasUsageConfig
from mcp_zen_of_languages.languages.configs import PowerShellCmdletBindingConfig
from mcp_zen_of_languages.languages.configs import PowerShellCommentHelpConfig
from mcp_zen_of_languages.languages.configs import PowerShellNullHandlingConfig
from mcp_zen_of_languages.languages.configs import PowerShellParameterValidationConfig
from mcp_zen_of_languages.languages.configs import PowerShellPipelineUsageConfig
from mcp_zen_of_languages.languages.configs import PowerShellPositionalParamsConfig
from mcp_zen_of_languages.languages.configs import PowerShellReturnObjectsConfig
from mcp_zen_of_languages.languages.configs import PowerShellScopeUsageConfig
from mcp_zen_of_languages.languages.configs import PowerShellShouldProcessConfig
from mcp_zen_of_languages.languages.configs import PowerShellSplattingConfig
from mcp_zen_of_languages.languages.configs import PowerShellVerboseDebugConfig
from mcp_zen_of_languages.languages.configs import RubyBlockPreferenceConfig
from mcp_zen_of_languages.languages.configs import RubyDryConfig
from mcp_zen_of_languages.languages.configs import RubyExpressiveSyntaxConfig
from mcp_zen_of_languages.languages.configs import RubyGuardClauseConfig
from mcp_zen_of_languages.languages.configs import RubyMetaprogrammingConfig
from mcp_zen_of_languages.languages.configs import RubyMethodNamingConfig
from mcp_zen_of_languages.languages.configs import RubyMonkeyPatchConfig
from mcp_zen_of_languages.languages.configs import RubyPreferFailConfig
from mcp_zen_of_languages.languages.configs import RubySymbolKeysConfig
from mcp_zen_of_languages.languages.configs import TomlCommentClarityConfig
from mcp_zen_of_languages.languages.configs import TomlDuplicateKeysConfig
from mcp_zen_of_languages.languages.configs import TomlFloatIntegerConfig
from mcp_zen_of_languages.languages.configs import TomlIsoDatetimeConfig
from mcp_zen_of_languages.languages.configs import TomlLowercaseKeysConfig
from mcp_zen_of_languages.languages.configs import TomlNoInlineTablesConfig
from mcp_zen_of_languages.languages.configs import TomlOrderConfig
from mcp_zen_of_languages.languages.configs import TomlTrailingCommasConfig
from mcp_zen_of_languages.languages.configs import XmlAttributeUsageConfig
from mcp_zen_of_languages.languages.configs import XmlClosingTagsConfig
from mcp_zen_of_languages.languages.configs import XmlHierarchyConfig
from mcp_zen_of_languages.languages.configs import XmlNamespaceConfig
from mcp_zen_of_languages.languages.configs import XmlSemanticMarkupConfig
from mcp_zen_of_languages.languages.configs import XmlValidityConfig
from mcp_zen_of_languages.languages.configs import YamlCommentIntentConfig
from mcp_zen_of_languages.languages.configs import YamlConsistencyConfig
from mcp_zen_of_languages.languages.configs import YamlDuplicateKeysConfig
from mcp_zen_of_languages.languages.configs import YamlIndentationConfig
from mcp_zen_of_languages.languages.configs import YamlKeyClarityConfig
from mcp_zen_of_languages.languages.configs import YamlLowercaseKeysConfig
from mcp_zen_of_languages.languages.configs import YamlNoTabsConfig
from mcp_zen_of_languages.languages.configs import YamlStringStyleConfig
from mcp_zen_of_languages.languages.cpp.detectors import CppAutoDetector
from mcp_zen_of_languages.languages.cpp.detectors import CppAvoidGlobalsDetector
from mcp_zen_of_languages.languages.cpp.detectors import CppCStyleCastDetector
from mcp_zen_of_languages.languages.cpp.detectors import CppConstCorrectnessDetector
from mcp_zen_of_languages.languages.cpp.detectors import CppManualAllocationDetector
from mcp_zen_of_languages.languages.cpp.detectors import CppMoveDetector
from mcp_zen_of_languages.languages.cpp.detectors import CppOptionalDetector
from mcp_zen_of_languages.languages.cpp.detectors import CppOverrideFinalDetector
from mcp_zen_of_languages.languages.cpp.detectors import CppRaiiDetector
from mcp_zen_of_languages.languages.cpp.detectors import CppRangeForDetector
from mcp_zen_of_languages.languages.cpp.detectors import CppRuleOfFiveDetector
from mcp_zen_of_languages.languages.csharp.detectors import (
    CSharpCollectionExpressionDetector,
)
from mcp_zen_of_languages.languages.csharp.detectors import CSharpDisposableDetector
from mcp_zen_of_languages.languages.csharp.detectors import (
    CSharpExceptionHandlingDetector,
)
from mcp_zen_of_languages.languages.csharp.detectors import (
    CSharpExpressionBodiedDetector,
)
from mcp_zen_of_languages.languages.csharp.detectors import CSharpLinqDetector
from mcp_zen_of_languages.languages.csharp.detectors import CSharpMagicNumberDetector
from mcp_zen_of_languages.languages.csharp.detectors import (
    CSharpNamingConventionDetector,
)
from mcp_zen_of_languages.languages.csharp.detectors import CSharpNullableDetector
from mcp_zen_of_languages.languages.csharp.detectors import (
    CSharpPatternMatchingDetector,
)
from mcp_zen_of_languages.languages.csharp.detectors import CSharpRecordDetector
from mcp_zen_of_languages.languages.csharp.detectors import CSharpVarDetector
from mcp_zen_of_languages.languages.css.detectors import CssColorLiteralDetector
from mcp_zen_of_languages.languages.css.detectors import CssGodStylesheetDetector
from mcp_zen_of_languages.languages.css.detectors import CssImportChainDetector
from mcp_zen_of_languages.languages.css.detectors import CssMagicPixelsDetector
from mcp_zen_of_languages.languages.css.detectors import CssMediaQueryScaleDetector
from mcp_zen_of_languages.languages.css.detectors import CssSpecificityDetector
from mcp_zen_of_languages.languages.css.detectors import CssVendorPrefixDetector
from mcp_zen_of_languages.languages.css.detectors import CssZIndexScaleDetector
from mcp_zen_of_languages.languages.go.detectors import GoContextUsageDetector
from mcp_zen_of_languages.languages.go.detectors import GoDeferUsageDetector
from mcp_zen_of_languages.languages.go.detectors import GoErrorHandlingDetector
from mcp_zen_of_languages.languages.go.detectors import GoGoroutineLeakDetector
from mcp_zen_of_languages.languages.go.detectors import GoInitUsageDetector
from mcp_zen_of_languages.languages.go.detectors import GoInterfacePointerDetector
from mcp_zen_of_languages.languages.go.detectors import GoInterfaceReturnDetector
from mcp_zen_of_languages.languages.go.detectors import GoInterfaceSizeDetector
from mcp_zen_of_languages.languages.go.detectors import GoNamingConventionDetector
from mcp_zen_of_languages.languages.go.detectors import GoPackageNamingDetector
from mcp_zen_of_languages.languages.go.detectors import GoPackageStateDetector
from mcp_zen_of_languages.languages.go.detectors import GoZeroValueDetector
from mcp_zen_of_languages.languages.javascript.detectors import (
    JsAsyncErrorHandlingDetector,
)
from mcp_zen_of_languages.languages.javascript.detectors import (
    JsCallbackNestingDetector,
)
from mcp_zen_of_languages.languages.javascript.detectors import JsFunctionLengthDetector
from mcp_zen_of_languages.languages.javascript.detectors import JsGlobalStateDetector
from mcp_zen_of_languages.languages.javascript.detectors import (
    JsInheritanceDepthDetector,
)
from mcp_zen_of_languages.languages.javascript.detectors import JsMagicNumbersDetector
from mcp_zen_of_languages.languages.javascript.detectors import (
    JsMeaningfulNamesDetector,
)
from mcp_zen_of_languages.languages.javascript.detectors import JsModernFeaturesDetector
from mcp_zen_of_languages.languages.javascript.detectors import JsNoVarDetector
from mcp_zen_of_languages.languages.javascript.detectors import JsPureFunctionDetector
from mcp_zen_of_languages.languages.javascript.detectors import JsStrictEqualityDetector
from mcp_zen_of_languages.languages.json.detectors import JsonArrayOrderDetector
from mcp_zen_of_languages.languages.json.detectors import JsonDateFormatDetector
from mcp_zen_of_languages.languages.json.detectors import JsonDuplicateKeyDetector
from mcp_zen_of_languages.languages.json.detectors import JsonKeyCasingDetector
from mcp_zen_of_languages.languages.json.detectors import JsonMagicStringDetector
from mcp_zen_of_languages.languages.json.detectors import JsonNullHandlingDetector
from mcp_zen_of_languages.languages.json.detectors import JsonNullSprawlDetector
from mcp_zen_of_languages.languages.json.detectors import JsonSchemaConsistencyDetector
from mcp_zen_of_languages.languages.json.detectors import JsonStrictnessDetector
from mcp_zen_of_languages.languages.powershell.detectors import (
    PowerShellAliasUsageDetector,
)
from mcp_zen_of_languages.languages.powershell.detectors import (
    PowerShellCmdletBindingDetector,
)
from mcp_zen_of_languages.languages.powershell.detectors import (
    PowerShellCommentHelpDetector,
)
from mcp_zen_of_languages.languages.powershell.detectors import (
    PowerShellNullHandlingDetector,
)
from mcp_zen_of_languages.languages.powershell.detectors import (
    PowerShellParameterValidationDetector,
)
from mcp_zen_of_languages.languages.powershell.detectors import (
    PowerShellPipelineUsageDetector,
)
from mcp_zen_of_languages.languages.powershell.detectors import (
    PowerShellPositionalParamsDetector,
)
from mcp_zen_of_languages.languages.powershell.detectors import (
    PowerShellReturnObjectsDetector,
)
from mcp_zen_of_languages.languages.powershell.detectors import (
    PowerShellScopeUsageDetector,
)
from mcp_zen_of_languages.languages.powershell.detectors import (
    PowerShellShouldProcessDetector,
)
from mcp_zen_of_languages.languages.powershell.detectors import (
    PowerShellSplattingDetector,
)
from mcp_zen_of_languages.languages.powershell.detectors import (
    PowerShellVerboseDebugDetector,
)
from mcp_zen_of_languages.languages.ruby.detectors import RubyBlockPreferenceDetector
from mcp_zen_of_languages.languages.ruby.detectors import RubyDryDetector
from mcp_zen_of_languages.languages.ruby.detectors import RubyExpressiveSyntaxDetector
from mcp_zen_of_languages.languages.ruby.detectors import RubyGuardClauseDetector
from mcp_zen_of_languages.languages.ruby.detectors import RubyMetaprogrammingDetector
from mcp_zen_of_languages.languages.ruby.detectors import RubyMethodNamingDetector
from mcp_zen_of_languages.languages.ruby.detectors import RubyMonkeyPatchDetector
from mcp_zen_of_languages.languages.ruby.detectors import RubyPreferFailDetector
from mcp_zen_of_languages.languages.ruby.detectors import RubySymbolKeysDetector
from mcp_zen_of_languages.languages.toml.detectors import TomlCommentClarityDetector
from mcp_zen_of_languages.languages.toml.detectors import TomlDuplicateKeysDetector
from mcp_zen_of_languages.languages.toml.detectors import TomlFloatIntegerDetector
from mcp_zen_of_languages.languages.toml.detectors import TomlIsoDatetimeDetector
from mcp_zen_of_languages.languages.toml.detectors import TomlLowercaseKeysDetector
from mcp_zen_of_languages.languages.toml.detectors import TomlNoInlineTablesDetector
from mcp_zen_of_languages.languages.toml.detectors import TomlOrderDetector
from mcp_zen_of_languages.languages.toml.detectors import TomlTrailingCommasDetector
from mcp_zen_of_languages.languages.xml.detectors import XmlAttributeUsageDetector
from mcp_zen_of_languages.languages.xml.detectors import XmlClosingTagsDetector
from mcp_zen_of_languages.languages.xml.detectors import XmlHierarchyDetector
from mcp_zen_of_languages.languages.xml.detectors import XmlNamespaceDetector
from mcp_zen_of_languages.languages.xml.detectors import XmlSemanticMarkupDetector
from mcp_zen_of_languages.languages.xml.detectors import XmlValidityDetector
from mcp_zen_of_languages.languages.yaml.detectors import YamlCommentIntentDetector
from mcp_zen_of_languages.languages.yaml.detectors import YamlConsistencyDetector
from mcp_zen_of_languages.languages.yaml.detectors import YamlDuplicateKeysDetector
from mcp_zen_of_languages.languages.yaml.detectors import YamlIndentationDetector
from mcp_zen_of_languages.languages.yaml.detectors import YamlKeyClarityDetector
from mcp_zen_of_languages.languages.yaml.detectors import YamlLowercaseKeysDetector
from mcp_zen_of_languages.languages.yaml.detectors import YamlNoTabsDetector
from mcp_zen_of_languages.languages.yaml.detectors import YamlStringStyleDetector


def run_detector(detector, code: str, language: str, config):
    context = AnalysisContext(code=code, language=language)
    assert detector.name
    return detector.detect(context, config)


def test_go_additional_detectors_cover_paths():
    assert run_detector(
        GoInterfaceReturnDetector(),
        "package main\nfunc Make() interface{} { return nil }",
        "go",
        GoInterfaceReturnConfig(),
    )
    assert run_detector(
        GoZeroValueDetector(),
        "package main\nfunc NewWidget() *Widget { return &Widget{} }",
        "go",
        GoZeroValueConfig(),
    )
    assert run_detector(
        GoInterfacePointerDetector(),
        "package main\nvar target *interface{}",
        "go",
        GoInterfacePointerConfig(),
    )
    assert run_detector(
        GoGoroutineLeakDetector(),
        "package main\nfunc Run(){ go func() { }() }",
        "go",
        GoGoroutineLeakConfig(),
    )
    assert run_detector(
        GoPackageNamingDetector(),
        "package foos\nfunc Run() {}",
        "go",
        GoPackageNamingConfig(),
    )
    assert run_detector(
        GoPackageStateDetector(),
        "package main\nvar state int",
        "go",
        GoPackageStateConfig(),
    )
    assert run_detector(
        GoInitUsageDetector(),
        "package main\nfunc init() {}",
        "go",
        GoInitUsageConfig(),
    )


def test_js_additional_detectors_cover_paths():
    assert JsCallbackNestingDetector().name == "js_callback_nesting"
    assert JsNoVarDetector().name == "js_no_var"
    assert JsStrictEqualityDetector().name == "js_strict_equality"
    assert JsAsyncErrorHandlingDetector().name == "js_async_error_handling"
    assert JsFunctionLengthDetector().name == "js_function_length"
    assert run_detector(
        JsGlobalStateDetector(),
        "window.state = 1;",
        "javascript",
        JsGlobalStateConfig(),
    )
    assert run_detector(
        JsModernFeaturesDetector(),
        "function() {}",
        "javascript",
        JsModernFeaturesConfig(),
    )
    assert run_detector(
        JsModernFeaturesDetector(),
        "const message = 'Hello ' + name;",
        "javascript",
        JsModernFeaturesConfig(),
    )
    assert run_detector(
        JsMagicNumbersDetector(),
        "const total = 42;",
        "javascript",
        JsMagicNumbersConfig(),
    )
    assert run_detector(
        JsPureFunctionDetector(),
        "const items = []; items.push(1);",
        "javascript",
        JsPureFunctionConfig(),
    )
    assert run_detector(
        JsInheritanceDepthDetector(),
        "class A extends B {}\nclass B extends C {}\n",
        "javascript",
        Js009Config().model_copy(update={"max_inheritance_depth": 1}),
    )
    assert run_detector(
        JsMeaningfulNamesDetector(),
        "const a = 1;",
        "javascript",
        Js011Config().model_copy(update={"min_identifier_length": 4}),
    )


def test_powershell_additional_detectors_cover_paths():
    assert run_detector(
        PowerShellCmdletBindingDetector(),
        "function Test-Thing { param($foo) }",
        "powershell",
        PowerShellCmdletBindingConfig(),
    )
    assert run_detector(
        PowerShellVerboseDebugDetector(),
        "Write-Host 'log'",
        "powershell",
        PowerShellVerboseDebugConfig(),
    )
    assert run_detector(
        PowerShellPositionalParamsDetector(),
        "$args",
        "powershell",
        PowerShellPositionalParamsConfig(),
    )
    assert run_detector(
        PowerShellPipelineUsageDetector(),
        "foreach ($item in $items) { $item }",
        "powershell",
        PowerShellPipelineUsageConfig(),
    )
    assert run_detector(
        PowerShellShouldProcessDetector(),
        "Remove-Item $path",
        "powershell",
        PowerShellShouldProcessConfig(),
    )
    assert run_detector(
        PowerShellSplattingDetector(),
        "Get-Item -Path x -Filter y -Force -Recurse",
        "powershell",
        PowerShellSplattingConfig(),
    )
    assert run_detector(
        PowerShellParameterValidationDetector(),
        "function Test-Thing { param($foo) }",
        "powershell",
        PowerShellParameterValidationConfig(),
    )
    assert run_detector(
        PowerShellCommentHelpDetector(),
        "function Test-Thing { }\n",
        "powershell",
        PowerShellCommentHelpConfig(),
    )
    assert run_detector(
        PowerShellAliasUsageDetector(),
        "gci $path",
        "powershell",
        PowerShellAliasUsageConfig(),
    )
    assert run_detector(
        PowerShellReturnObjectsDetector(),
        "Format-Table",
        "powershell",
        PowerShellReturnObjectsConfig(),
    )
    assert run_detector(
        PowerShellScopeUsageDetector(),
        "$global:thing = 1",
        "powershell",
        PowerShellScopeUsageConfig(),
    )
    assert run_detector(
        PowerShellNullHandlingDetector(),
        "function Test-Thing { param($foo) }",
        "powershell",
        PowerShellNullHandlingConfig(),
    )


def test_ruby_additional_detectors_cover_paths():
    assert run_detector(
        RubyDryDetector(),
        "puts 'hi'\nputs 'hi'\nputs 'hi'\n",
        "ruby",
        RubyDryConfig(),
    )
    assert run_detector(
        RubyBlockPreferenceDetector(),
        "lambda { |x| x }\n",
        "ruby",
        RubyBlockPreferenceConfig(),
    )
    assert run_detector(
        RubyMonkeyPatchDetector(),
        "class String\nend\n",
        "ruby",
        RubyMonkeyPatchConfig(),
    )
    assert run_detector(
        RubyMethodNamingDetector(),
        "def isReady\nend\n",
        "ruby",
        RubyMethodNamingConfig(),
    )
    assert run_detector(
        RubySymbolKeysDetector(),
        '{ "foo" => "bar" }\n',
        "ruby",
        RubySymbolKeysConfig(),
    )
    assert not run_detector(
        RubySymbolKeysDetector(),
        "{ foo: 'bar' }\n",
        "ruby",
        RubySymbolKeysConfig(),
    )
    assert run_detector(
        RubyGuardClauseDetector(),
        "if ready\n  work\nend\n",
        "ruby",
        RubyGuardClauseConfig(),
    )
    assert run_detector(
        RubyMetaprogrammingDetector(),
        "define_method(:foo) { }\n",
        "ruby",
        RubyMetaprogrammingConfig(),
    )
    assert run_detector(
        RubyExpressiveSyntaxDetector(),
        "for item in items\nend\n",
        "ruby",
        RubyExpressiveSyntaxConfig(),
    )
    assert run_detector(
        RubyPreferFailDetector(),
        "raise 'boom'\n",
        "ruby",
        RubyPreferFailConfig(),
    )


def test_cpp_detectors_cover_paths():
    assert run_detector(
        CppRaiiDetector(),
        "int* ptr = new int;",
        "cpp",
        CppRaiiConfig(),
    )
    assert run_detector(
        CppAutoDetector(),
        "std::vector<int> items = {};",
        "cpp",
        CppAutoConfig(),
    )
    assert run_detector(
        CppRangeForDetector(),
        "for (auto it = items.begin(); it != items.end(); ++it) {}",
        "cpp",
        CppRangeForConfig(),
    )
    assert run_detector(
        CppManualAllocationDetector(),
        "auto ptr = new int[10];",
        "cpp",
        CppManualAllocationConfig(),
    )
    assert run_detector(
        CppConstCorrectnessDetector(),
        "void foo(std::string& name) {}",
        "cpp",
        CppConstCorrectnessConfig(),
    )
    assert run_detector(
        CppCStyleCastDetector(),
        "int x = (int)foo;",
        "cpp",
        CppCStyleCastConfig(),
    )
    assert run_detector(
        CppRuleOfFiveDetector(),
        "class Foo { ~Foo(); };",
        "cpp",
        CppRuleOfFiveConfig(),
    )
    assert run_detector(
        CppMoveDetector(),
        "Foo&& value = get();",
        "cpp",
        CppMoveConfig(),
    )
    assert run_detector(
        CppAvoidGlobalsDetector(),
        "static int g_state = 1;",
        "cpp",
        CppAvoidGlobalsConfig(),
    )
    assert run_detector(
        CppOverrideFinalDetector(),
        "virtual void Run();",
        "cpp",
        CppOverrideFinalConfig(),
    )
    assert run_detector(
        CppOptionalDetector(),
        "Widget* maybe = nullptr;",
        "cpp",
        CppOptionalConfig(),
    )


def test_csharp_detectors_cover_paths():
    assert run_detector(
        CSharpNullableDetector(),
        "public class Foo {}",
        "csharp",
        CSharpNullableConfig(),
    )
    assert run_detector(
        CSharpExpressionBodiedDetector(),
        "int Value { get { return 1; } }",
        "csharp",
        CSharpExpressionBodiedConfig(),
    )
    assert run_detector(
        CSharpVarDetector(),
        "int value = 1;",
        "csharp",
        CSharpVarConfig(),
    )
    assert run_detector(
        CSharpPatternMatchingDetector(),
        "if (obj is Foo) {}",
        "csharp",
        CSharpPatternMatchingConfig(),
    )
    assert run_detector(
        CSharpCollectionExpressionDetector(),
        "var items = new List<int>();",
        "csharp",
        CSharpCollectionExpressionConfig(),
    )
    assert run_detector(
        CSharpNamingConventionDetector(),
        "public class foo {}",
        "csharp",
        Cs008Config().model_copy(update={"public_naming": "PascalCase"}),
    )
    assert run_detector(
        CSharpDisposableDetector(),
        "IDisposable item; item.Dispose();",
        "csharp",
        CSharpDisposableConfig(),
    )
    assert run_detector(
        CSharpMagicNumberDetector(),
        "const int Limit = 42;",
        "csharp",
        CSharpMagicNumberConfig(),
    )
    assert run_detector(
        CSharpLinqDetector(),
        "foreach (var item in items) { }",
        "csharp",
        CSharpLinqConfig(),
    )
    assert run_detector(
        CSharpExceptionHandlingDetector(),
        "try {} catch (Exception) {}",
        "csharp",
        CSharpExceptionHandlingConfig(),
    )
    assert run_detector(
        CSharpRecordDetector(),
        "class Person { public string Name { get; set; } }",
        "csharp",
        CSharpRecordConfig(),
    )


def test_yaml_detectors_cover_paths():
    assert run_detector(
        YamlIndentationDetector(),
        "root:\n   child: value\n",
        "yaml",
        YamlIndentationConfig().model_copy(update={"indent_size": 2}),
    )
    assert run_detector(
        YamlNoTabsDetector(),
        "root:\n\tchild: value\n",
        "yaml",
        YamlNoTabsConfig(),
    )
    assert run_detector(
        YamlDuplicateKeysDetector(),
        "root: 1\nroot: 2\n",
        "yaml",
        YamlDuplicateKeysConfig(),
    )
    assert run_detector(
        YamlLowercaseKeysDetector(),
        "Root: 1\n",
        "yaml",
        YamlLowercaseKeysConfig(),
    )
    assert run_detector(
        YamlKeyClarityDetector(),
        "r: 1\n",
        "yaml",
        YamlKeyClarityConfig().model_copy(update={"min_key_length": 3}),
    )
    assert run_detector(
        YamlConsistencyDetector(),
        "- item\n* other\n",
        "yaml",
        YamlConsistencyConfig().model_copy(update={"allowed_list_markers": ["-"]}),
    )
    assert run_detector(
        YamlCommentIntentDetector(),
        "root: 1\nchild: 2\nleaf: 3\nnode: 4\nvalue: 5\n",
        "yaml",
        YamlCommentIntentConfig().model_copy(update={"min_nonempty_lines": 3}),
    )
    assert run_detector(
        YamlStringStyleDetector(),
        "title: hello world\n",
        "yaml",
        YamlStringStyleConfig(),
    )


def test_css_detectors_cover_paths():
    assert run_detector(
        CssSpecificityDetector(),
        ".a { .b { .c { .d { color: red !important; } } } }\n",
        "css",
        CssSpecificityConfig().model_copy(
            update={"max_selector_nesting": 3, "max_important_usages": 0},
        ),
    )
    assert run_detector(
        CssSpecificityDetector(),
        ".button { color: red ! Important; }\n",
        "css",
        CssSpecificityConfig().model_copy(
            update={"max_selector_nesting": 10, "max_important_usages": 0},
        ),
    )
    assert run_detector(
        CssMagicPixelsDetector(),
        ".a { padding: 12px; }\n",
        "css",
        CssMagicPixelsConfig(),
    )
    assert run_detector(
        CssMagicPixelsDetector(),
        ".a { border-width: 0px; margin: 0.5px; }\n",
        "css",
        CssMagicPixelsConfig().model_copy(update={"max_raw_pixel_literals": 0}),
    )
    assert run_detector(
        CssColorLiteralDetector(),
        ".a { color: #ff00aa; }\n",
        "css",
        CssColorLiteralConfig(),
    )
    assert run_detector(
        CssGodStylesheetDetector(),
        ".a {}\n.b {}\n.c {}\n",
        "css",
        CssGodStylesheetConfig().model_copy(update={"max_stylesheet_lines": 1}),
    )
    assert run_detector(
        CssImportChainDetector(),
        "@import 'base';\n",
        "css",
        CssImportChainConfig(),
    )
    assert run_detector(
        CssZIndexScaleDetector(),
        ".modal { z-index: 9999; }\n",
        "css",
        CssZIndexScaleConfig().model_copy(update={"allowed_z_index_values": [0, 10]}),
    )
    assert run_detector(
        CssVendorPrefixDetector(),
        ".btn { -webkit-user-select: none; }\n",
        "css",
        CssVendorPrefixConfig(),
    )
    assert run_detector(
        CssMediaQueryScaleDetector(),
        "@media screen and\n(min-width: 990px) {\n  .x { display: block; }\n}\n",
        "css",
        CssMediaQueryScaleConfig(),
    )


def test_toml_detectors_cover_paths():
    assert run_detector(
        TomlNoInlineTablesDetector(),
        'root = { key = "value" }',
        "toml",
        TomlNoInlineTablesConfig(),
    )
    assert run_detector(
        TomlDuplicateKeysDetector(),
        'root = "value"\nroot = "value2"\n',
        "toml",
        TomlDuplicateKeysConfig(),
    )
    assert run_detector(
        TomlLowercaseKeysDetector(),
        'Root = "value"\n',
        "toml",
        TomlLowercaseKeysConfig(),
    )
    assert run_detector(
        TomlTrailingCommasDetector(),
        "items = [1, 2, ]\n",
        "toml",
        TomlTrailingCommasConfig(),
    )
    assert run_detector(
        TomlCommentClarityDetector(),
        "value = 42\n",
        "toml",
        TomlCommentClarityConfig().model_copy(update={"min_comment_lines": 1}),
    )
    assert run_detector(
        TomlOrderDetector(),
        "[first]\nvalue = 1\n\n\n\n\n\n\n\n\n\n[second]\nvalue = 2\n",
        "toml",
        TomlOrderConfig(),
    )
    assert run_detector(
        TomlIsoDatetimeDetector(),
        'date = "01/02/2024"\n',
        "toml",
        TomlIsoDatetimeConfig(),
    )
    assert run_detector(
        TomlFloatIntegerDetector(),
        "count = 4.0\n",
        "toml",
        TomlFloatIntegerConfig(),
    )


def test_json_detectors_cover_paths():
    assert run_detector(
        JsonStrictnessDetector(),
        '{ "name": "x", }\n',
        "json",
        JsonStrictnessConfig(),
    )
    assert run_detector(
        JsonSchemaConsistencyDetector(),
        '{"a":{"b":{"c":{"d":{"e":{"f":1}}}}}}',
        "json",
        JsonSchemaConsistencyConfig(),
    )
    assert run_detector(
        JsonDuplicateKeyDetector(),
        '{"a": 1, "a": 2}',
        "json",
        JsonDuplicateKeyConfig(),
    )
    assert run_detector(
        JsonMagicStringDetector(),
        '{"status":"active","state":"active","mode":"active"}',
        "json",
        JsonMagicStringConfig(min_repetition=3),
    )
    assert run_detector(
        JsonDateFormatDetector(),
        '{"created_at": "03/15/2024"}',
        "json",
        JsonDateFormatConfig(),
    )
    assert run_detector(
        JsonNullHandlingDetector(),
        '{"name": "test", "config": null}',
        "json",
        JsonNullHandlingConfig(max_top_level_nulls=0),
    )
    assert run_detector(
        JsonKeyCasingDetector(),
        '{"Key": 1, "value": 2}',
        "json",
        JsonKeyCasingConfig(),
    )
    assert run_detector(
        JsonArrayOrderDetector(),
        '{"items": [1,2,3,4,5]}',
        "json",
        JsonArrayOrderConfig(max_inline_array_size=4),
    )
    assert run_detector(
        JsonNullSprawlDetector(),
        '{"a": null, "b": null, "c": null, "d": null}',
        "json",
        JsonNullSprawlConfig(),
    )


def test_xml_detectors_cover_paths():
    assert run_detector(
        XmlSemanticMarkupDetector(),
        "<font>hi</font>",
        "xml",
        XmlSemanticMarkupConfig(),
    )
    assert run_detector(
        XmlAttributeUsageDetector(),
        '<item description="This is a very long attribute value that should be element data"></item>',
        "xml",
        XmlAttributeUsageConfig(),
    )
    assert run_detector(
        XmlNamespaceDetector(),
        "<x:root><x:item /></x:root>",
        "xml",
        XmlNamespaceConfig(),
    )
    assert run_detector(
        XmlValidityDetector(),
        "<root><child /></root>",
        "xml",
        XmlValidityConfig(),
    )
    assert run_detector(
        XmlHierarchyDetector(),
        "<root><item></item><item></item><item></item></root>",
        "xml",
        XmlHierarchyConfig(),
    )
    assert run_detector(
        XmlClosingTagsDetector(),
        "<item />",
        "xml",
        XmlClosingTagsConfig(),
    )


def test_go_detector_names_cover_paths():
    assert GoErrorHandlingDetector().name == "go_error_handling"
    assert GoInterfaceSizeDetector().name == "go_interface_size"
    assert GoContextUsageDetector().name == "go_context_usage"
    assert GoDeferUsageDetector().name == "go_defer_usage"
    assert GoNamingConventionDetector().name == "go_naming_convention"
