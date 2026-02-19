from __future__ import annotations

from mcp_zen_of_languages.analyzers.base import AnalysisContext
from mcp_zen_of_languages.languages.bash.detectors import (
    BashArgumentValidationDetector,
    BashArrayUsageDetector,
    BashCommandSubstitutionDetector,
    BashDoubleBracketsDetector,
    BashExitCodeChecksDetector,
    BashFunctionUsageDetector,
    BashLocalVariablesDetector,
    BashMeaningfulNamesDetector,
    BashQuoteVariablesDetector,
    BashReadonlyConstantsDetector,
    BashSignalHandlingDetector,
    BashStrictModeDetector,
    BashUsageInfoDetector,
)
from mcp_zen_of_languages.languages.configs import (
    Bash006Config,
    Bash011Config,
    BashArgumentValidationConfig,
    BashArrayUsageConfig,
    BashCommandSubstitutionConfig,
    BashDoubleBracketsConfig,
    BashExitCodeConfig,
    BashLocalVariablesConfig,
    BashQuoteVariablesConfig,
    BashReadonlyConstantsConfig,
    BashSignalHandlingConfig,
    BashStrictModeConfig,
    BashUsageInfoConfig,
    CppNullptrConfig,
    CppSmartPointerConfig,
    CSharpAsyncAwaitConfig,
    CSharpStringInterpolationConfig,
    GoContextUsageConfig,
    GoDeferUsageConfig,
    GoErrorHandlingConfig,
    GoInterfaceSizeConfig,
    GoNamingConventionConfig,
    JsAsyncErrorHandlingConfig,
    JsCallbackNestingConfig,
    JsFunctionLengthConfig,
    JsNoVarConfig,
    JsStrictEqualityConfig,
    PowerShellApprovedVerbConfig,
    PowerShellErrorHandlingConfig,
    PowerShellPascalCaseConfig,
    RubyMethodChainConfig,
    RubyNamingConventionConfig,
    RustCloneOverheadConfig,
    RustErrorHandlingConfig,
    RustTypeSafetyConfig,
    RustUnsafeBlocksConfig,
    RustUnwrapUsageConfig,
    TsAnyUsageConfig,
    TsEnumConstConfig,
    TsInterfacePreferenceConfig,
    TsNonNullAssertionConfig,
    TsReadonlyConfig,
    TsReturnTypeConfig,
    TsStrictModeConfig,
    TsTypeGuardConfig,
    TsUnknownOverAnyConfig,
    TsUtilityTypesConfig,
)
from mcp_zen_of_languages.languages.cpp.detectors import (
    CppNullptrDetector,
    CppSmartPointerDetector,
)
from mcp_zen_of_languages.languages.csharp.detectors import (
    CSharpAsyncAwaitDetector,
    CSharpStringInterpolationDetector,
)
from mcp_zen_of_languages.languages.go.detectors import (
    GoContextUsageDetector,
    GoDeferUsageDetector,
    GoErrorHandlingDetector,
    GoInterfaceSizeDetector,
    GoNamingConventionDetector,
)
from mcp_zen_of_languages.languages.javascript.detectors import (
    JsAsyncErrorHandlingDetector,
    JsCallbackNestingDetector,
    JsFunctionLengthDetector,
    JsNoVarDetector,
    JsStrictEqualityDetector,
)
from mcp_zen_of_languages.languages.powershell.detectors import (
    PowerShellApprovedVerbDetector,
    PowerShellErrorHandlingDetector,
    PowerShellPascalCaseDetector,
)
from mcp_zen_of_languages.languages.ruby.detectors import (
    RubyMethodChainDetector,
    RubyNamingConventionDetector,
)
from mcp_zen_of_languages.languages.rust.detectors import (
    RustCloneOverheadDetector,
    RustErrorHandlingDetector,
    RustTypeSafetyDetector,
    RustUnsafeBlocksDetector,
    RustUnwrapUsageDetector,
)
from mcp_zen_of_languages.languages.typescript.detectors import (
    TsAnyUsageDetector,
    TsEnumConstDetector,
    TsInterfacePreferenceDetector,
    TsNonNullAssertionDetector,
    TsReadonlyDetector,
    TsReturnTypeDetector,
    TsStrictModeDetector,
    TsTypeGuardDetector,
    TsUnknownOverAnyDetector,
    TsUtilityTypesDetector,
)


def test_other_language_detectors_cover_paths():
    assert BashExitCodeChecksDetector().name == "bash-005"
    assert BashFunctionUsageDetector().name == "bash-006"
    assert BashLocalVariablesDetector().name == "bash-007"
    assert BashArgumentValidationDetector().name == "bash-010"
    assert BashMeaningfulNamesDetector().name == "bash-011"
    assert BashSignalHandlingDetector().name == "bash-012"
    assert BashArrayUsageDetector().name == "bash-013"
    assert BashUsageInfoDetector().name == "bash-014"
    bash_context = AnalysisContext(code="echo $foo", language="bash")
    assert BashStrictModeDetector().detect(bash_context, BashStrictModeConfig())
    assert BashQuoteVariablesDetector().detect(bash_context, BashQuoteVariablesConfig())
    bash_brackets = AnalysisContext(
        code="if [ -f file ]; then echo ok; fi",
        language="bash",
    )
    assert BashDoubleBracketsDetector().detect(
        bash_brackets,
        BashDoubleBracketsConfig(),
    )
    bash_sub = AnalysisContext(code="output=`echo hi`", language="bash")
    assert BashCommandSubstitutionDetector().detect(
        bash_sub,
        BashCommandSubstitutionConfig(),
    )
    bash_readonly = AnalysisContext(code="FOO=bar", language="bash")
    assert BashReadonlyConstantsDetector().detect(
        bash_readonly,
        BashReadonlyConstantsConfig(),
    )
    bash_exit = AnalysisContext(code="rm file", language="bash")
    assert BashExitCodeChecksDetector().detect(bash_exit, BashExitCodeConfig())
    bash_long = AnalysisContext(code="echo 1\n" * 3, language="bash")
    length_cfg = Bash006Config().model_copy(
        update={"max_script_length_without_functions": 1},
    )
    assert BashFunctionUsageDetector().detect(bash_long, length_cfg)
    bash_local = AnalysisContext(code="foo() {\n  value=1\n}\n", language="bash")
    assert BashLocalVariablesDetector().detect(bash_local, BashLocalVariablesConfig())
    bash_args = AnalysisContext(code="echo $1\n", language="bash")
    assert BashArgumentValidationDetector().detect(
        bash_args,
        BashArgumentValidationConfig(),
    )
    bash_names = AnalysisContext(code="a=1\n", language="bash")
    name_cfg = Bash011Config().model_copy(update={"min_variable_name_length": 3})
    assert BashMeaningfulNamesDetector().detect(bash_names, name_cfg)
    bash_signal = AnalysisContext(code="tmp=$(mktemp)\n", language="bash")
    assert BashSignalHandlingDetector().detect(bash_signal, BashSignalHandlingConfig())
    bash_array = AnalysisContext(
        code="for item in $items; do echo $item; done\n",
        language="bash",
    )
    assert BashArrayUsageDetector().detect(bash_array, BashArrayUsageConfig())
    bash_usage = AnalysisContext(code="echo 'hi'\n", language="bash")
    assert BashUsageInfoDetector().detect(bash_usage, BashUsageInfoConfig())

    cpp_context = AnalysisContext(code="int* x = new int;\n", language="cpp")
    assert CppSmartPointerDetector().detect(cpp_context, CppSmartPointerConfig())
    cpp_null = AnalysisContext(code="if (ptr == NULL) {}\n", language="cpp")
    assert CppNullptrDetector().detect(cpp_null, CppNullptrConfig())

    csharp_context = AnalysisContext(code="task.Result;\n", language="csharp")
    assert CSharpAsyncAwaitDetector().detect(csharp_context, CSharpAsyncAwaitConfig())
    csharp_str = AnalysisContext(code="String.Format('x', y);\n", language="csharp")
    assert CSharpStringInterpolationDetector().detect(
        csharp_str,
        CSharpStringInterpolationConfig(),
    )

    go_context = AnalysisContext(code="panic('x')\n", language="go")
    assert GoErrorHandlingDetector().detect(go_context, GoErrorHandlingConfig())
    go_iface = AnalysisContext(
        code="type Foo interface {\n A()\n B()\n C()\n}\n",
        language="go",
    )
    iface_cfg = GoInterfaceSizeConfig().model_copy(update={"max_interface_methods": 1})
    assert GoInterfaceSizeDetector().detect(go_iface, iface_cfg)
    go_ctx = AnalysisContext(code="package main\n", language="go")
    assert GoContextUsageDetector().detect(go_ctx, GoContextUsageConfig())
    go_loop = AnalysisContext(
        code="for i := 0; i < 1; i++ { defer foo() }",
        language="go",
    )
    assert GoDeferUsageDetector().detect(go_loop, GoDeferUsageConfig())
    go_name = AnalysisContext(
        code="var this_is_a_super_long_variable_name int\n",
        language="go",
    )
    assert GoNamingConventionDetector().detect(go_name, GoNamingConventionConfig())

    js_context = AnalysisContext(
        code="function foo() { var x = 1; }",
        language="javascript",
    )
    assert JsNoVarDetector().detect(js_context, JsNoVarConfig())
    assert JsStrictEqualityDetector().detect(
        AnalysisContext(code="if (a == b) {}", language="javascript"),
        JsStrictEqualityConfig(),
    )
    callback_cfg = JsCallbackNestingConfig().model_copy(
        update={"max_callback_nesting": 0},
    )
    assert JsCallbackNestingDetector().detect(
        AnalysisContext(
            code="function foo() { function bar() {} }",
            language="javascript",
        ),
        callback_cfg,
    )
    assert JsAsyncErrorHandlingDetector().detect(
        AnalysisContext(
            code="async function foo() { return 1 }",
            language="javascript",
        ),
        JsAsyncErrorHandlingConfig(),
    )
    js_long = AnalysisContext(
        code="function foo() {\n" + "x\n" * 10 + "}\n",
        language="javascript",
    )
    js_cfg = JsFunctionLengthConfig().model_copy(update={"max_function_length": 1})
    assert JsFunctionLengthDetector().detect(js_long, js_cfg)

    ps_context = AnalysisContext(code="function bad-Name {}\n", language="powershell")
    assert PowerShellApprovedVerbDetector().detect(
        ps_context,
        PowerShellApprovedVerbConfig(),
    )
    assert PowerShellErrorHandlingDetector().detect(
        ps_context,
        PowerShellErrorHandlingConfig(),
    )
    assert PowerShellPascalCaseDetector().detect(
        ps_context,
        PowerShellPascalCaseConfig(),
    )

    ruby_context = AnalysisContext(
        code="def BadName\n  foo.bar.baz.qux.quux\nend\n",
        language="ruby",
    )
    assert RubyNamingConventionDetector().detect(
        ruby_context,
        RubyNamingConventionConfig(),
    )
    chain_cfg = RubyMethodChainConfig().model_copy(
        update={"max_method_chain_length": 1},
    )
    assert RubyMethodChainDetector().detect(ruby_context, chain_cfg)

    rust_context = AnalysisContext(code="let x = foo().unwrap();\n", language="rust")
    assert RustUnwrapUsageDetector().detect(rust_context, RustUnwrapUsageConfig())
    assert RustUnsafeBlocksDetector().detect(
        AnalysisContext(code="unsafe { }", language="rust"),
        RustUnsafeBlocksConfig(),
    )
    assert RustCloneOverheadDetector().detect(
        AnalysisContext(code="x.clone();", language="rust"),
        RustCloneOverheadConfig(),
    )
    assert RustErrorHandlingDetector().detect(
        AnalysisContext(code="fn foo() -> Result<i32, i32> { Ok(1) }", language="rust"),
        RustErrorHandlingConfig(),
    )
    assert RustTypeSafetyDetector().detect(
        AnalysisContext(code="struct User { id: i32 }\n", language="rust"),
        RustTypeSafetyConfig(),
    )

    ts_context = AnalysisContext(code="let x: any;", language="typescript")
    assert TsAnyUsageDetector().detect(ts_context, TsAnyUsageConfig())
    assert TsStrictModeDetector().detect(ts_context, TsStrictModeConfig())
    ts_interface = AnalysisContext(
        code="type Foo = { a: string };",
        language="typescript",
    )
    assert TsInterfacePreferenceDetector().detect(
        ts_interface,
        TsInterfacePreferenceConfig(),
    )
    ts_return = AnalysisContext(
        code="export function foo() { return 1 }",
        language="typescript",
    )
    assert TsReturnTypeDetector().detect(ts_return, TsReturnTypeConfig())
    assert TsReadonlyDetector().detect(ts_context, TsReadonlyConfig())
    ts_guard_context = AnalysisContext(code="foo as Bar", language="typescript")
    assert TsTypeGuardDetector().detect(ts_guard_context, TsTypeGuardConfig())
    ts_util = AnalysisContext(code="type Foo = { a: string };", language="typescript")
    util_cfg = TsUtilityTypesConfig().model_copy(
        update={"min_utility_type_usage": 1, "min_object_type_aliases": 0},
    )
    assert TsUtilityTypesDetector().detect(ts_util, util_cfg)
    ts_nonnull = AnalysisContext(code="const x = foo!;", language="typescript")
    assert TsNonNullAssertionDetector().detect(ts_nonnull, TsNonNullAssertionConfig())
    ts_enum = AnalysisContext(code="const Foo = { A: 1 }", language="typescript")
    assert TsEnumConstDetector().detect(ts_enum, TsEnumConstConfig())
    ts_unknown = AnalysisContext(code="let x: any;", language="typescript")
    unknown_cfg = TsUnknownOverAnyConfig().model_copy(update={"max_any_for_unknown": 0})
    assert TsUnknownOverAnyDetector().detect(ts_unknown, unknown_cfg)
