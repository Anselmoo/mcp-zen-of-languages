from __future__ import annotations

from mcp_zen_of_languages.analyzers.base import AnalysisContext
from mcp_zen_of_languages.languages.configs import (
    CppAutoConfig,
    CppAvoidGlobalsConfig,
    CppConstCorrectnessConfig,
    CppCStyleCastConfig,
    CppManualAllocationConfig,
    CppMoveConfig,
    CppOptionalConfig,
    CppOverrideFinalConfig,
    CppRaiiConfig,
    CppRangeForConfig,
    CppRuleOfFiveConfig,
    Cs008Config,
    CSharpCollectionExpressionConfig,
    CSharpDisposableConfig,
    CSharpExceptionHandlingConfig,
    CSharpExpressionBodiedConfig,
    CSharpLinqConfig,
    CSharpMagicNumberConfig,
    CSharpNullableConfig,
    CSharpPatternMatchingConfig,
    CSharpRecordConfig,
    CSharpVarConfig,
    CssColorLiteralConfig,
    CssGodStylesheetConfig,
    CssImportChainConfig,
    CssMagicPixelsConfig,
    CssMediaQueryScaleConfig,
    CssSpecificityConfig,
    CssVendorPrefixConfig,
    CssZIndexScaleConfig,
    GoGoroutineLeakConfig,
    GoInitUsageConfig,
    GoInterfacePointerConfig,
    GoInterfaceReturnConfig,
    GoPackageNamingConfig,
    GoPackageStateConfig,
    GoZeroValueConfig,
    Js009Config,
    Js011Config,
    JsGlobalStateConfig,
    JsMagicNumbersConfig,
    JsModernFeaturesConfig,
    JsonArrayOrderConfig,
    JsonDateFormatConfig,
    JsonDuplicateKeyConfig,
    JsonKeyCasingConfig,
    JsonMagicStringConfig,
    JsonNullHandlingConfig,
    JsonNullSprawlConfig,
    JsonSchemaConsistencyConfig,
    JsonStrictnessConfig,
    JsPureFunctionConfig,
    PowerShellAliasUsageConfig,
    PowerShellCmdletBindingConfig,
    PowerShellCommentHelpConfig,
    PowerShellNullHandlingConfig,
    PowerShellParameterValidationConfig,
    PowerShellPipelineUsageConfig,
    PowerShellPositionalParamsConfig,
    PowerShellReturnObjectsConfig,
    PowerShellScopeUsageConfig,
    PowerShellShouldProcessConfig,
    PowerShellSplattingConfig,
    PowerShellVerboseDebugConfig,
    RubyBlockPreferenceConfig,
    RubyDryConfig,
    RubyExpressiveSyntaxConfig,
    RubyGuardClauseConfig,
    RubyMetaprogrammingConfig,
    RubyMethodNamingConfig,
    RubyMonkeyPatchConfig,
    RubyPreferFailConfig,
    RubySymbolKeysConfig,
    TomlCommentClarityConfig,
    TomlDuplicateKeysConfig,
    TomlFloatIntegerConfig,
    TomlIsoDatetimeConfig,
    TomlLowercaseKeysConfig,
    TomlNoInlineTablesConfig,
    TomlOrderConfig,
    TomlTrailingCommasConfig,
    XmlAttributeUsageConfig,
    XmlClosingTagsConfig,
    XmlHierarchyConfig,
    XmlNamespaceConfig,
    XmlSemanticMarkupConfig,
    XmlValidityConfig,
    YamlCommentIntentConfig,
    YamlConsistencyConfig,
    YamlDuplicateKeysConfig,
    YamlIndentationConfig,
    YamlKeyClarityConfig,
    YamlLowercaseKeysConfig,
    YamlNoTabsConfig,
    YamlStringStyleConfig,
)
from mcp_zen_of_languages.languages.cpp.detectors import (
    CppAutoDetector,
    CppAvoidGlobalsDetector,
    CppConstCorrectnessDetector,
    CppCStyleCastDetector,
    CppManualAllocationDetector,
    CppMoveDetector,
    CppOptionalDetector,
    CppOverrideFinalDetector,
    CppRaiiDetector,
    CppRangeForDetector,
    CppRuleOfFiveDetector,
)
from mcp_zen_of_languages.languages.csharp.detectors import (
    CSharpCollectionExpressionDetector,
    CSharpDisposableDetector,
    CSharpExceptionHandlingDetector,
    CSharpExpressionBodiedDetector,
    CSharpLinqDetector,
    CSharpMagicNumberDetector,
    CSharpNamingConventionDetector,
    CSharpNullableDetector,
    CSharpPatternMatchingDetector,
    CSharpRecordDetector,
    CSharpVarDetector,
)
from mcp_zen_of_languages.languages.css.detectors import (
    CssColorLiteralDetector,
    CssGodStylesheetDetector,
    CssImportChainDetector,
    CssMagicPixelsDetector,
    CssMediaQueryScaleDetector,
    CssSpecificityDetector,
    CssVendorPrefixDetector,
    CssZIndexScaleDetector,
)
from mcp_zen_of_languages.languages.go.detectors import (
    GoContextUsageDetector,
    GoDeferUsageDetector,
    GoErrorHandlingDetector,
    GoGoroutineLeakDetector,
    GoInitUsageDetector,
    GoInterfacePointerDetector,
    GoInterfaceReturnDetector,
    GoInterfaceSizeDetector,
    GoNamingConventionDetector,
    GoPackageNamingDetector,
    GoPackageStateDetector,
    GoZeroValueDetector,
)
from mcp_zen_of_languages.languages.javascript.detectors import (
    JsAsyncErrorHandlingDetector,
    JsCallbackNestingDetector,
    JsFunctionLengthDetector,
    JsGlobalStateDetector,
    JsInheritanceDepthDetector,
    JsMagicNumbersDetector,
    JsMeaningfulNamesDetector,
    JsModernFeaturesDetector,
    JsNoVarDetector,
    JsPureFunctionDetector,
    JsStrictEqualityDetector,
)
from mcp_zen_of_languages.languages.json.detectors import (
    JsonArrayOrderDetector,
    JsonDateFormatDetector,
    JsonDuplicateKeyDetector,
    JsonKeyCasingDetector,
    JsonMagicStringDetector,
    JsonNullHandlingDetector,
    JsonNullSprawlDetector,
    JsonSchemaConsistencyDetector,
    JsonStrictnessDetector,
)
from mcp_zen_of_languages.languages.powershell.detectors import (
    PowerShellAliasUsageDetector,
    PowerShellCmdletBindingDetector,
    PowerShellCommentHelpDetector,
    PowerShellNullHandlingDetector,
    PowerShellParameterValidationDetector,
    PowerShellPipelineUsageDetector,
    PowerShellPositionalParamsDetector,
    PowerShellReturnObjectsDetector,
    PowerShellScopeUsageDetector,
    PowerShellShouldProcessDetector,
    PowerShellSplattingDetector,
    PowerShellVerboseDebugDetector,
)
from mcp_zen_of_languages.languages.ruby.detectors import (
    RubyBlockPreferenceDetector,
    RubyDryDetector,
    RubyExpressiveSyntaxDetector,
    RubyGuardClauseDetector,
    RubyMetaprogrammingDetector,
    RubyMethodNamingDetector,
    RubyMonkeyPatchDetector,
    RubyPreferFailDetector,
    RubySymbolKeysDetector,
)
from mcp_zen_of_languages.languages.toml.detectors import (
    TomlCommentClarityDetector,
    TomlDuplicateKeysDetector,
    TomlFloatIntegerDetector,
    TomlIsoDatetimeDetector,
    TomlLowercaseKeysDetector,
    TomlNoInlineTablesDetector,
    TomlOrderDetector,
    TomlTrailingCommasDetector,
)
from mcp_zen_of_languages.languages.xml.detectors import (
    XmlAttributeUsageDetector,
    XmlClosingTagsDetector,
    XmlHierarchyDetector,
    XmlNamespaceDetector,
    XmlSemanticMarkupDetector,
    XmlValidityDetector,
)
from mcp_zen_of_languages.languages.yaml.detectors import (
    YamlCommentIntentDetector,
    YamlConsistencyDetector,
    YamlDuplicateKeysDetector,
    YamlIndentationDetector,
    YamlKeyClarityDetector,
    YamlLowercaseKeysDetector,
    YamlNoTabsDetector,
    YamlStringStyleDetector,
)


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
        CssMagicPixelsDetector(),
        ".a { padding: 12px; }\n",
        "css",
        CssMagicPixelsConfig(),
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
        "@media (min-width: 990px) { .x { display: block; } }\n",
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
