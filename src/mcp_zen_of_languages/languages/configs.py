"""Pydantic configuration models for violation detectors across all supported languages.

Each model inherits from ``DetectorConfig`` and adds fields specific to a
single detector type.  The ``type`` literal acts as a discriminator so the
pipeline can deserialize heterogeneous detector configurations from
``zen-config.yaml`` into the correct Pydantic class.

See Also:
    [`mcp_zen_of_languages.analyzers.pipeline`][mcp_zen_of_languages.analyzers.pipeline]: Merges these configs with
    rule-derived defaults at analysis time.
"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class DetectorConfig(BaseModel):
    """Base configuration shared by every violation detector.

    Subclasses add detector-specific fields while inheriting common metadata
    like ``principle_id``, ``severity``, and ``violation_messages``.

    Attributes:
        type: Discriminator string that uniquely identifies the detector kind.
        principle_id: Optional zen principle identifier this detector enforces.
        principle: Human-readable name of the zen principle, used as a fallback
            violation message when no specific messages are configured.
        severity: Violation severity on a 1-10 scale (1 = informational,
            10 = critical).
        violation_messages: Ordered list of message templates; the first
            matching template is selected at report time.
        detectable_patterns: Literal strings or ``!``-prefixed required-absence
            patterns that the rule-pattern detector scans for.
        recommended_alternative: Suggestion text appended to violation reports
            when a better practice exists.
    """

    type: str = Field(..., description="Detector type discriminator")
    principle_id: str | None = None
    principle: str | None = None
    severity: int | None = Field(default=None, ge=1, le=10)
    violation_messages: list[str] | None = None
    detectable_patterns: list[str] | None = None
    recommended_alternative: str | None = None

    model_config = ConfigDict(extra="forbid")

    def select_violation_message(
        self,
        *,
        contains: str | None = None,
        index: int = 0,
    ) -> str:
        """Choose a violation message by substring match or positional index.

        When *contains* is given, the first message whose text includes that
        substring is returned.  Otherwise the message at *index* is used,
        falling back to the first message, the principle name, or the type
        discriminator if no messages are configured.

        Args:
            contains: Optional substring to match against available messages.
            index: Zero-based position selecting a message when no substring
                match is requested.

        Returns:
            str: The selected violation message text.
        """
        messages = self.violation_messages or []
        if contains:
            for message in messages:
                if contains in message:
                    return message
        if messages:
            return messages[index] if 0 <= index < len(messages) else messages[0]
        return self.principle or self.principle_id or self.type


class NameStyleConfig(DetectorConfig):
    """Naming convention enforcement settings.

    Attributes:
        naming_convention: Expected convention pattern (e.g. ``snake_case``).
        min_identifier_length: Shortest acceptable identifier length.
    """

    type: Literal["name_style"] = "name_style"
    naming_convention: str | None = None
    min_identifier_length: int | None = None


class SparseCodeConfig(DetectorConfig):
    """Code density and whitespace separation settings.

    Attributes:
        max_statements_per_line: Maximum statements allowed on a single line.
        min_blank_lines_between_defs: Minimum blank lines required between
            top-level definitions.
    """

    type: Literal["sparse_code"] = "sparse_code"
    max_statements_per_line: int = 1
    min_blank_lines_between_defs: int = 1


class ConsistencyConfig(DetectorConfig):
    """Naming-style consistency settings across a codebase.

    Attributes:
        max_naming_styles: Maximum distinct naming conventions allowed.
    """

    type: Literal["consistency"] = "consistency"
    max_naming_styles: int = 1


class ExplicitnessConfig(DetectorConfig):
    """Explicit type annotation enforcement settings.

    Attributes:
        require_type_hints: When ``True``, functions without type hints are flagged.
    """

    type: Literal["explicitness"] = "explicitness"
    require_type_hints: bool = True


class NamespaceConfig(DetectorConfig):
    """Namespace and top-level symbol density settings.

    Attributes:
        max_top_level_symbols: Maximum top-level names before flagging pollution.
        max_exports: Maximum public exports allowed from a module.
    """

    type: Literal["namespace_usage"] = "namespace_usage"
    max_top_level_symbols: int = 25
    max_exports: int = 20


class CyclomaticComplexityConfig(DetectorConfig):
    """Cyclomatic complexity threshold settings.

    Attributes:
        max_cyclomatic_complexity: Upper bound on per-function cyclomatic complexity.
    """

    type: Literal["cyclomatic_complexity"] = "cyclomatic_complexity"
    max_cyclomatic_complexity: int = 10


class NestingDepthConfig(DetectorConfig):
    """Control-flow nesting depth threshold settings.

    Attributes:
        max_nesting_depth: Maximum allowed indentation levels within a function.
    """

    type: Literal["nesting_depth"] = "nesting_depth"
    max_nesting_depth: int = 3


class LongFunctionConfig(DetectorConfig):
    """Function length threshold settings.

    Attributes:
        max_function_length: Maximum lines allowed in a single function body.
    """

    type: Literal["long_functions"] = "long_functions"
    max_function_length: int = 50


class GodClassConfig(DetectorConfig):
    """God-class detection threshold settings.

    Attributes:
        max_methods: Maximum methods per class before flagging.
        max_class_length: Maximum total lines in a class definition.
    """

    type: Literal["god_classes"] = "god_classes"
    max_methods: int = 10
    max_class_length: int = 300


class MagicMethodConfig(DetectorConfig):
    """Magic/dunder method count threshold settings.

    Attributes:
        max_magic_methods: Maximum dunder methods per class.
    """

    type: Literal["magic_methods"] = "magic_methods"
    max_magic_methods: int = 3


class CircularDependencyConfig(DetectorConfig):
    """Circular import/dependency detection settings."""

    type: Literal["circular_dependencies"] = "circular_dependencies"


class DeepInheritanceConfig(DetectorConfig):
    """Inheritance chain depth threshold settings.

    Attributes:
        max_depth: Maximum allowed inheritance levels.
    """

    type: Literal["deep_inheritance"] = "deep_inheritance"
    max_depth: int = 3


class FeatureEnvyConfig(DetectorConfig):
    """Feature envy detection settings.

    Attributes:
        min_occurrences: Minimum external attribute accesses to trigger a violation.
    """

    type: Literal["feature_envy"] = "feature_envy"
    min_occurrences: int = 3


class DuplicateImplementationConfig(DetectorConfig):
    """Duplicate code block detection settings."""

    type: Literal["duplicate_implementations"] = "duplicate_implementations"


class ClassSizeConfig(DetectorConfig):
    """Class size threshold settings.

    Attributes:
        max_class_length: Maximum total lines in a class definition.
    """

    type: Literal["class_size"] = "class_size"
    max_class_length: int = 300


class LineLengthConfig(DetectorConfig):
    """Line length threshold settings.

    Attributes:
        max_line_length: Maximum characters per source line.
    """

    type: Literal["line_length"] = "line_length"
    max_line_length: int = 88


class DocstringConfig(DetectorConfig):
    """Missing docstring detection settings."""

    type: Literal["docstrings"] = "docstrings"


class ContextManagerConfig(DetectorConfig):
    """Context manager (``with`` statement) usage detection settings."""

    type: Literal["context_manager"] = "context_manager"


class StarImportConfig(DetectorConfig):
    """Wildcard (``from x import *``) import detection settings."""

    type: Literal["star_imports"] = "star_imports"


class BareExceptConfig(DetectorConfig):
    """Bare ``except:`` clause detection settings."""

    type: Literal["bare_except"] = "bare_except"


class MagicNumberConfig(DetectorConfig):
    """Magic number literal detection settings.

    Attributes:
        max_magic_numbers: Maximum unnamed numeric literals allowed.
    """

    type: Literal["magic_number"] = "magic_number"
    max_magic_numbers: int = 0


class ComplexOneLinersConfig(DetectorConfig):
    """Complex one-liner comprehension detection settings.

    Attributes:
        max_for_clauses: Maximum ``for`` clauses in a single comprehension.
        max_line_length: Maximum line length for a comprehension expression.
    """

    type: Literal["complex_one_liners"] = "complex_one_liners"
    max_for_clauses: int = 1
    max_line_length: int = 120


class ShortVariableNamesConfig(DetectorConfig):
    """Short variable name detection settings.

    Attributes:
        min_identifier_length: Minimum characters for a variable name.
        allowed_loop_names: Names exempted from the length check (e.g., loop counters).
    """

    type: Literal["short_variable_names"] = "short_variable_names"
    min_identifier_length: int = 3
    allowed_loop_names: list[str] = Field(
        default_factory=lambda: ["i", "j", "k", "x", "y"],
    )


class TsAnyUsageConfig(DetectorConfig):
    """TypeScript ``any`` usage detection settings.

    Attributes:
        max_any_usages: Maximum permitted ``any`` annotations (default 0).
        detect_explicit_any: Flag explicit ``any`` type annotations.
        detect_assertions_any: Flag ``as any`` type assertions.
        detect_any_arrays: Flag ``any[]`` array types.
    """

    type: Literal["ts_any_usage"] = "ts_any_usage"
    max_any_usages: int = 0
    detect_explicit_any: bool = True
    detect_assertions_any: bool = True
    detect_any_arrays: bool = True


class TsStrictModeConfig(DetectorConfig):
    """TypeScript strict-mode compiler flag enforcement settings.

    Attributes:
        require_strict: Require the ``strict`` flag.
        require_no_implicit_any: Require ``noImplicitAny``.
        require_strict_null_checks: Require ``strictNullChecks``.
    """

    type: Literal["ts_strict_mode"] = "ts_strict_mode"
    require_strict: bool = True
    require_no_implicit_any: bool = True
    require_strict_null_checks: bool = True


class TsInterfacePreferenceConfig(DetectorConfig):
    """TypeScript interface-over-type-alias preference settings.

    Attributes:
        max_object_type_aliases: Maximum object-shape type aliases before a violation.
    """

    type: Literal["ts_interface_preference"] = "ts_interface_preference"
    max_object_type_aliases: int = 0


class TsReturnTypeConfig(DetectorConfig):
    """TypeScript explicit return-type annotation enforcement settings.

    Attributes:
        require_return_types: When ``True``, flag functions without return-type annotations.
    """

    type: Literal["ts_return_types"] = "ts_return_types"
    require_return_types: bool = True


class TsReadonlyConfig(DetectorConfig):
    """TypeScript ``readonly`` modifier enforcement settings.

    Attributes:
        require_readonly_properties: Require ``readonly`` on applicable properties.
        min_readonly_occurrences: Minimum expected ``readonly`` annotations.
    """

    type: Literal["ts_readonly"] = "ts_readonly"
    require_readonly_properties: bool = True
    min_readonly_occurrences: int = 1


class TsTypeGuardConfig(DetectorConfig):
    """TypeScript type-guard preference over type-assertion settings.

    Attributes:
        max_type_assertions: Maximum ``as`` type assertions allowed.
    """

    type: Literal["ts_type_guards"] = "ts_type_guards"
    max_type_assertions: int = 0


class TsUtilityTypesConfig(DetectorConfig):
    """TypeScript built-in utility-type usage enforcement settings.

    Attributes:
        min_utility_type_usage: Minimum expected utility-type references.
        min_object_type_aliases: Minimum object-type aliases before the rule activates.
    """

    type: Literal["ts_utility_types"] = "ts_utility_types"
    min_utility_type_usage: int = 1
    min_object_type_aliases: int = 2


class TsNonNullAssertionConfig(DetectorConfig):
    """TypeScript non-null assertion (``!``) detection settings.

    Attributes:
        max_non_null_assertions: Maximum allowed ``!`` postfix operators.
    """

    type: Literal["ts_non_null_assertions"] = "ts_non_null_assertions"
    max_non_null_assertions: int = 0


class TsEnumConstConfig(DetectorConfig):
    """TypeScript const-enum preference settings.

    Attributes:
        max_plain_enum_objects: Maximum non-const enums before a violation.
    """

    type: Literal["ts_enum_const"] = "ts_enum_const"
    max_plain_enum_objects: int = 0


class TsUnknownOverAnyConfig(DetectorConfig):
    """TypeScript ``unknown``-over-``any`` preference settings.

    Attributes:
        max_any_for_unknown: Maximum ``any`` usages where ``unknown`` is preferred.
    """

    type: Literal["ts_unknown_over_any"] = "ts_unknown_over_any"
    max_any_for_unknown: int = 0


class JsCallbackNestingConfig(DetectorConfig):
    """JavaScript callback-nesting depth enforcement settings.

    Attributes:
        max_callback_nesting: Maximum permitted callback nesting levels.
    """

    type: Literal["js_callback_nesting"] = "js_callback_nesting"
    max_callback_nesting: int = 2


class JsNoVarConfig(DetectorConfig):
    """JavaScript ``var`` keyword prohibition settings.

    Attributes:
        detect_var_usage: When ``True``, flag ``var`` declarations.
    """

    type: Literal["js_no_var"] = "js_no_var"
    detect_var_usage: bool = True


class JsStrictEqualityConfig(DetectorConfig):
    """JavaScript strict-equality operator (``===``) enforcement settings."""

    type: Literal["js_strict_equality"] = "js_strict_equality"


class JsAsyncErrorHandlingConfig(DetectorConfig):
    """JavaScript async/await error-handling detection settings."""

    type: Literal["js_async_error_handling"] = "js_async_error_handling"


class JsFunctionLengthConfig(DetectorConfig):
    """JavaScript function-length and parameter-count enforcement settings.

    Attributes:
        max_function_length: Maximum lines per function body.
        max_parameters: Maximum formal parameters per function (``None`` disables).
    """

    type: Literal["js_function_length"] = "js_function_length"
    max_function_length: int = 50
    max_parameters: int | None = None


class JsGlobalStateConfig(DetectorConfig):
    """JavaScript global-state usage detection settings."""

    type: Literal["js_global_state"] = "js_global_state"


class JsModernFeaturesConfig(DetectorConfig):
    """JavaScript modern-feature adoption detection settings."""

    type: Literal["js_modern_features"] = "js_modern_features"


class JsMagicNumbersConfig(DetectorConfig):
    """JavaScript magic-number detection settings."""

    type: Literal["js_magic_numbers"] = "js_magic_numbers"


class JsPureFunctionConfig(DetectorConfig):
    """JavaScript pure-function preference enforcement settings."""

    type: Literal["js_pure_functions"] = "js_pure_functions"


class BashStrictModeConfig(DetectorConfig):
    """Bash strict-mode (``set -euo pipefail``) enforcement settings."""

    type: Literal["bash_strict_mode"] = "bash_strict_mode"


class BashQuoteVariablesConfig(DetectorConfig):
    """Bash variable-quoting enforcement settings."""

    type: Literal["bash_quote_variables"] = "bash_quote_variables"


class BashEvalUsageConfig(DetectorConfig):
    """Bash ``eval`` usage detection settings."""

    type: Literal["bash_eval_usage"] = "bash_eval_usage"


class BashDoubleBracketsConfig(DetectorConfig):
    """Bash ``[[ ]]`` double-bracket preference settings."""

    type: Literal["bash_double_brackets"] = "bash_double_brackets"


class BashCommandSubstitutionConfig(DetectorConfig):
    """Bash ``$()`` command-substitution preference settings."""

    type: Literal["bash_command_substitution"] = "bash_command_substitution"


class BashReadonlyConstantsConfig(DetectorConfig):
    """Bash ``readonly`` constant enforcement settings."""

    type: Literal["bash_readonly_constants"] = "bash_readonly_constants"


class BashExitCodeConfig(DetectorConfig):
    """Bash meaningful exit-code enforcement settings."""

    type: Literal["bash-005"] = "bash-005"


class BashLocalVariablesConfig(DetectorConfig):
    """Bash ``local`` variable-scoping enforcement settings."""

    type: Literal["bash-007"] = "bash-007"


class BashArgumentValidationConfig(DetectorConfig):
    """Bash argument-validation enforcement settings."""

    type: Literal["bash-010"] = "bash-010"


class BashSignalHandlingConfig(DetectorConfig):
    """Bash signal-handler (``trap``) enforcement settings."""

    type: Literal["bash-012"] = "bash-012"


class BashArrayUsageConfig(DetectorConfig):
    """Bash proper array-usage enforcement settings."""

    type: Literal["bash-013"] = "bash-013"


class BashUsageInfoConfig(DetectorConfig):
    """Bash usage/help-message enforcement settings."""

    type: Literal["bash-014"] = "bash-014"


class PowerShellApprovedVerbConfig(DetectorConfig):
    """PowerShell approved-verb enforcement settings.

    Attributes:
        approved_verbs: Accepted verb prefixes for cmdlet names.
    """

    type: Literal["powershell_approved_verbs"] = "powershell_approved_verbs"
    approved_verbs: list[str] = [
        "get",
        "set",
        "new",
        "remove",
        "add",
        "clear",
        "start",
        "stop",
    ]


class PowerShellErrorHandlingConfig(DetectorConfig):
    """PowerShell error-handling enforcement settings."""

    type: Literal["powershell_error_handling"] = "powershell_error_handling"


class PowerShellPascalCaseConfig(DetectorConfig):
    """PowerShell PascalCase naming-convention enforcement settings.

    Attributes:
        naming_convention: Expected casing pattern (``None`` uses PascalCase default).
    """

    type: Literal["powershell_pascal_case"] = "powershell_pascal_case"
    naming_convention: str | None = None


class PowerShellCmdletBindingConfig(DetectorConfig):
    """PowerShell ``[CmdletBinding()]`` attribute enforcement settings."""

    type: Literal["powershell_cmdlet_binding"] = "powershell_cmdlet_binding"


class PowerShellVerboseDebugConfig(DetectorConfig):
    """PowerShell ``Write-Verbose``/``Write-Debug`` usage detection settings."""

    type: Literal["powershell_verbose_debug"] = "powershell_verbose_debug"


class PowerShellPositionalParamsConfig(DetectorConfig):
    """PowerShell positional-parameter prohibition settings."""

    type: Literal["powershell_positional_params"] = "powershell_positional_params"


class PowerShellPipelineUsageConfig(DetectorConfig):
    """PowerShell pipeline-usage preference settings."""

    type: Literal["powershell_pipeline_usage"] = "powershell_pipeline_usage"


class PowerShellShouldProcessConfig(DetectorConfig):
    """PowerShell ``ShouldProcess`` support enforcement settings."""

    type: Literal["powershell_should_process"] = "powershell_should_process"


class PowerShellSplattingConfig(DetectorConfig):
    """PowerShell parameter-splatting preference settings."""

    type: Literal["powershell_splatting"] = "powershell_splatting"


class PowerShellParameterValidationConfig(DetectorConfig):
    """PowerShell parameter-validation attribute enforcement settings."""

    type: Literal["powershell_parameter_validation"] = "powershell_parameter_validation"


class PowerShellCommentHelpConfig(DetectorConfig):
    """PowerShell comment-based help block enforcement settings."""

    type: Literal["powershell_comment_help"] = "powershell_comment_help"


class PowerShellAliasUsageConfig(DetectorConfig):
    """PowerShell alias-avoidance enforcement settings."""

    type: Literal["powershell_alias_usage"] = "powershell_alias_usage"


class PowerShellReturnObjectsConfig(DetectorConfig):
    """PowerShell structured-object return enforcement settings."""

    type: Literal["powershell_return_objects"] = "powershell_return_objects"


class PowerShellScopeUsageConfig(DetectorConfig):
    """PowerShell scope-modifier usage detection settings."""

    type: Literal["powershell_scope_usage"] = "powershell_scope_usage"


class PowerShellNullHandlingConfig(DetectorConfig):
    """PowerShell null-handling pattern enforcement settings."""

    type: Literal["powershell_null_handling"] = "powershell_null_handling"


class RubyNamingConventionConfig(DetectorConfig):
    """Ruby naming-convention enforcement settings.

    Attributes:
        naming_convention: Expected casing style (``None`` defaults to snake_case).
    """

    type: Literal["ruby_naming_convention"] = "ruby_naming_convention"
    naming_convention: str | None = None


class RubyMethodChainConfig(DetectorConfig):
    """Ruby method-chain length enforcement settings.

    Attributes:
        max_method_chain_length: Maximum chained method calls per expression.
    """

    type: Literal["ruby_method_chain"] = "ruby_method_chain"
    max_method_chain_length: int = 4


class RubyDryConfig(DetectorConfig):
    """Ruby DRY (Don't Repeat Yourself) enforcement settings."""

    type: Literal["ruby_dry"] = "ruby_dry"


class RubyBlockPreferenceConfig(DetectorConfig):
    """Ruby block-syntax preference (``do..end`` vs braces) settings."""

    type: Literal["ruby_block_preference"] = "ruby_block_preference"


class RubyMonkeyPatchConfig(DetectorConfig):
    """Ruby monkey-patching detection settings."""

    type: Literal["ruby_monkey_patch"] = "ruby_monkey_patch"


class RubyMethodNamingConfig(DetectorConfig):
    """Ruby method-naming convention detection settings."""

    type: Literal["ruby_method_naming"] = "ruby_method_naming"


class RubySymbolKeysConfig(DetectorConfig):
    """Ruby symbol-key preference over string-key settings."""

    type: Literal["ruby_symbol_keys"] = "ruby_symbol_keys"


class RubyGuardClauseConfig(DetectorConfig):
    """Ruby guard-clause preference over nested conditionals settings."""

    type: Literal["ruby_guard_clause"] = "ruby_guard_clause"


class RubyMetaprogrammingConfig(DetectorConfig):
    """Ruby excessive metaprogramming detection settings."""

    type: Literal["ruby_metaprogramming"] = "ruby_metaprogramming"


class RubyExpressiveSyntaxConfig(DetectorConfig):
    """Ruby expressive-syntax usage enforcement settings."""

    type: Literal["ruby_expressive_syntax"] = "ruby_expressive_syntax"


class RubyPreferFailConfig(DetectorConfig):
    """Ruby ``fail``-over-``raise`` preference settings."""

    type: Literal["ruby_prefer_fail"] = "ruby_prefer_fail"


class CppSmartPointerConfig(DetectorConfig):
    """C++ smart-pointer preference over raw-pointer settings."""

    type: Literal["cpp_smart_pointers"] = "cpp_smart_pointers"


class CppNullptrConfig(DetectorConfig):
    """C++ ``nullptr`` over ``NULL``/``0`` preference settings."""

    type: Literal["cpp_nullptr"] = "cpp_nullptr"


class CppRaiiConfig(DetectorConfig):
    """C++ RAII resource-management enforcement settings."""

    type: Literal["cpp-001"] = "cpp-001"


class CppAutoConfig(DetectorConfig):
    """C++ ``auto`` type-deduction preference settings."""

    type: Literal["cpp-003"] = "cpp-003"


class CppRangeForConfig(DetectorConfig):
    """C++ range-based ``for`` loop preference settings."""

    type: Literal["cpp-005"] = "cpp-005"


class CppManualAllocationConfig(DetectorConfig):
    """C++ manual ``new``/``delete`` avoidance settings."""

    type: Literal["cpp-006"] = "cpp-006"


class CppConstCorrectnessConfig(DetectorConfig):
    """C++ const-correctness enforcement settings."""

    type: Literal["cpp-007"] = "cpp-007"


class CppCStyleCastConfig(DetectorConfig):
    """C++ C-style cast avoidance settings."""

    type: Literal["cpp-008"] = "cpp-008"


class CppRuleOfFiveConfig(DetectorConfig):
    """C++ Rule of Five special-member enforcement settings."""

    type: Literal["cpp-009"] = "cpp-009"


class CppMoveConfig(DetectorConfig):
    """C++ move-semantics usage enforcement settings."""

    type: Literal["cpp-010"] = "cpp-010"


class CppAvoidGlobalsConfig(DetectorConfig):
    """C++ global-variable avoidance settings."""

    type: Literal["cpp-011"] = "cpp-011"


class CppOverrideFinalConfig(DetectorConfig):
    """C++ ``override``/``final`` keyword enforcement settings."""

    type: Literal["cpp-012"] = "cpp-012"


class CppOptionalConfig(DetectorConfig):
    """C++ ``std::optional`` usage enforcement settings."""

    type: Literal["cpp-013"] = "cpp-013"


class CSharpAsyncAwaitConfig(DetectorConfig):
    """C# async/await usage enforcement settings."""

    type: Literal["csharp_async_await"] = "csharp_async_await"


class CSharpStringInterpolationConfig(DetectorConfig):
    """C# string-interpolation preference settings."""

    type: Literal["csharp_string_interpolation"] = "csharp_string_interpolation"


class CSharpNullableConfig(DetectorConfig):
    """C# nullable reference-type enforcement settings."""

    type: Literal["cs-001"] = "cs-001"


class CSharpExpressionBodiedConfig(DetectorConfig):
    """C# expression-bodied member preference settings."""

    type: Literal["cs-002"] = "cs-002"


class CSharpVarConfig(DetectorConfig):
    """C# ``var`` implicit-typing preference settings."""

    type: Literal["cs-003"] = "cs-003"


class CSharpPatternMatchingConfig(DetectorConfig):
    """C# pattern-matching preference settings."""

    type: Literal["cs-005"] = "cs-005"


class CSharpCollectionExpressionConfig(DetectorConfig):
    """C# collection-expression syntax preference settings."""

    type: Literal["cs-007"] = "cs-007"


class CSharpDisposableConfig(DetectorConfig):
    """C# ``IDisposable`` usage enforcement settings."""

    type: Literal["cs-009"] = "cs-009"


class CSharpMagicNumberConfig(DetectorConfig):
    """C# magic-number detection settings."""

    type: Literal["cs-010"] = "cs-010"


class CSharpLinqConfig(DetectorConfig):
    """C# LINQ query preference settings."""

    type: Literal["cs-011"] = "cs-011"


class CSharpExceptionHandlingConfig(DetectorConfig):
    """C# exception-handling best-practice enforcement settings."""

    type: Literal["cs-012"] = "cs-012"


class CSharpRecordConfig(DetectorConfig):
    """C# record-type preference settings."""

    type: Literal["cs-013"] = "cs-013"


class YamlIndentationConfig(DetectorConfig):
    """YAML indentation width enforcement settings.

    Attributes:
        indent_size: Expected number of spaces per indentation level (default 2).
    """

    type: Literal["yaml-001"] = "yaml-001"
    indent_size: int = 2


class YamlNoTabsConfig(DetectorConfig):
    """YAML tab-character prohibition settings."""

    type: Literal["yaml-002"] = "yaml-002"


class YamlDuplicateKeysConfig(DetectorConfig):
    """YAML duplicate mapping-key detection settings."""

    type: Literal["yaml-003"] = "yaml-003"


class YamlLowercaseKeysConfig(DetectorConfig):
    """YAML lowercase-key enforcement settings."""

    type: Literal["yaml-004"] = "yaml-004"


class YamlKeyClarityConfig(DetectorConfig):
    """YAML minimum key-length enforcement settings.

    Attributes:
        min_key_length: Shortest acceptable mapping-key length (default 3).
    """

    type: Literal["yaml-005"] = "yaml-005"
    min_key_length: int = 3


class YamlConsistencyConfig(DetectorConfig):
    """YAML list-marker consistency enforcement settings.

    Attributes:
        allowed_list_markers: Permitted sequence indicators (default ``["-"]``).
    """

    type: Literal["yaml-006"] = "yaml-006"
    allowed_list_markers: list[str] = ["-"]


class YamlCommentIntentConfig(DetectorConfig):
    """YAML comment-coverage enforcement settings.

    Attributes:
        min_comment_lines: Minimum number of comment lines required.
        min_nonempty_lines: File must exceed this line count before the rule applies.
    """

    type: Literal["yaml-007"] = "yaml-007"
    min_comment_lines: int = 1
    min_nonempty_lines: int = 5


class YamlStringStyleConfig(DetectorConfig):
    """YAML string quoting enforcement settings.

    Attributes:
        require_quotes_for_specials: When ``True``, strings with spaces or
            special characters must be quoted.
    """

    type: Literal["yaml-008"] = "yaml-008"
    require_quotes_for_specials: bool = True


class TomlNoInlineTablesConfig(DetectorConfig):
    """TOML inline-table prohibition settings."""

    type: Literal["toml-001"] = "toml-001"


class TomlDuplicateKeysConfig(DetectorConfig):
    """TOML duplicate-key detection settings."""

    type: Literal["toml-002"] = "toml-002"


class TomlLowercaseKeysConfig(DetectorConfig):
    """TOML lowercase-key enforcement settings."""

    type: Literal["toml-003"] = "toml-003"


class TomlTrailingCommasConfig(DetectorConfig):
    """TOML trailing-comma detection settings."""

    type: Literal["toml-004"] = "toml-004"


class TomlCommentClarityConfig(DetectorConfig):
    """TOML comment-coverage enforcement settings.

    Attributes:
        min_comment_lines: Minimum number of comment lines before the rule passes.
    """

    type: Literal["toml-005"] = "toml-005"
    min_comment_lines: int = 1


class TomlOrderConfig(DetectorConfig):
    """TOML table-section ordering settings."""

    type: Literal["toml-006"] = "toml-006"


class TomlIsoDatetimeConfig(DetectorConfig):
    """TOML ISO 8601 datetime enforcement settings."""

    type: Literal["toml-007"] = "toml-007"


class TomlFloatIntegerConfig(DetectorConfig):
    """TOML float-vs-integer precision detection settings."""

    type: Literal["toml-008"] = "toml-008"


class JsonStrictnessConfig(DetectorConfig):
    """JSON/JSON5 strictness settings (trailing comma policy)."""

    type: Literal["json-001"] = "json-001"
    target_format: Literal["json", "json5"] = "json"
    allow_trailing_commas: bool = False


class JsonSchemaConsistencyConfig(DetectorConfig):
    """JSON deep-nesting detection settings."""

    type: Literal["json-002"] = "json-002"
    max_depth: int = 5


class JsonDuplicateKeyConfig(DetectorConfig):
    """JSON duplicate-key detection settings."""

    type: Literal["json-003"] = "json-003"


class JsonMagicStringConfig(DetectorConfig):
    """JSON magic-string repetition detection settings.

    Attributes:
        min_repetition: Minimum occurrences of a string value to flag it.
        min_length: Minimum string length to consider as a magic-string candidate.
    """

    type: Literal["json-004"] = "json-004"
    min_repetition: int = 3
    min_length: int = 4


class JsonKeyCasingConfig(DetectorConfig):
    """JSON key-casing consistency enforcement settings."""

    type: Literal["json-005"] = "json-005"


class JsonArrayOrderConfig(DetectorConfig):
    """JSON oversized-inline-array detection settings."""

    type: Literal["json-006"] = "json-006"
    max_inline_array_size: int = 20


class JsonNullSprawlConfig(DetectorConfig):
    """JSON null-sprawl detection settings.

    Attributes:
        max_null_values: Maximum total null values permitted across the document.
    """

    type: Literal["json-007"] = "json-007"
    max_null_values: int = 3


class JsonDateFormatConfig(DetectorConfig):
    """JSON ISO 8601 date-format enforcement settings.

    Attributes:
        common_date_keys: Key name fragments used to identify probable date fields.
    """

    type: Literal["json-008"] = "json-008"
    common_date_keys: list[str] = [
        "date",
        "time",
        "created",
        "updated",
        "modified",
        "timestamp",
        "expires",
        "published",
        "at",
    ]


class JsonNullHandlingConfig(DetectorConfig):
    """JSON top-level explicit-null detection settings.

    Attributes:
        max_top_level_nulls: Maximum number of top-level object keys allowed to
            be set explicitly to null before a violation is raised.
    """

    type: Literal["json-009"] = "json-009"
    max_top_level_nulls: int = 0


class XmlSemanticMarkupConfig(DetectorConfig):
    """XML semantic-vs-presentational markup detection settings."""

    type: Literal["xml-001"] = "xml-001"


class XmlAttributeUsageConfig(DetectorConfig):
    """XML oversized-attribute detection settings."""

    type: Literal["xml-002"] = "xml-002"


class XmlNamespaceConfig(DetectorConfig):
    """XML namespace declaration enforcement settings."""

    type: Literal["xml-003"] = "xml-003"


class XmlValidityConfig(DetectorConfig):
    """XML schema/DTD reference requirement settings."""

    type: Literal["xml-004"] = "xml-004"


class XmlHierarchyConfig(DetectorConfig):
    """XML element hierarchy and grouping detection settings."""

    type: Literal["xml-005"] = "xml-005"


class XmlClosingTagsConfig(DetectorConfig):
    """XML self-closing tag detection settings."""

    type: Literal["xml-006"] = "xml-006"


class GoErrorHandlingConfig(DetectorConfig):
    """Go error-handling enforcement settings.

    Attributes:
        max_ignored_errors: Maximum ``_``-discarded error returns.
    """

    type: Literal["go_error_handling"] = "go_error_handling"
    max_ignored_errors: int = 0


class GoInterfaceSizeConfig(DetectorConfig):
    """Go interface-size enforcement settings.

    Attributes:
        max_interface_methods: Maximum methods per interface.
    """

    type: Literal["go_interface_size"] = "go_interface_size"
    max_interface_methods: int = 3


class GoContextUsageConfig(DetectorConfig):
    """Go ``context.Context`` propagation enforcement settings.

    Attributes:
        require_context: Require ``context.Context`` as first parameter.
    """

    type: Literal["go_context_usage"] = "go_context_usage"
    require_context: bool = True


class GoDeferUsageConfig(DetectorConfig):
    """Go ``defer`` usage enforcement settings.

    Attributes:
        detect_defer_in_loop: Flag ``defer`` inside loops.
        detect_missing_defer: Flag resource opens without matching ``defer``.
    """

    type: Literal["go_defer_usage"] = "go_defer_usage"
    detect_defer_in_loop: bool = True
    detect_missing_defer: bool = True


class GoNamingConventionConfig(DetectorConfig):
    """Go naming-convention enforcement settings.

    Attributes:
        detect_long_names: Flag overly long identifier names.
    """

    type: Literal["go_naming_convention"] = "go_naming_convention"
    detect_long_names: bool = True


class GoInterfaceReturnConfig(DetectorConfig):
    """Go accept-interfaces-return-structs enforcement settings."""

    type: Literal["go_interface_return"] = "go_interface_return"


class GoZeroValueConfig(DetectorConfig):
    """Go zero-value initialization enforcement settings."""

    type: Literal["go_zero_value"] = "go_zero_value"


class GoInterfacePointerConfig(DetectorConfig):
    """Go interface-pointer avoidance settings."""

    type: Literal["go_interface_pointer"] = "go_interface_pointer"


class GoGoroutineLeakConfig(DetectorConfig):
    """Go goroutine-leak detection settings."""

    type: Literal["go_goroutine_leaks"] = "go_goroutine_leaks"


class GoPackageNamingConfig(DetectorConfig):
    """Go package-naming convention enforcement settings."""

    type: Literal["go_package_naming"] = "go_package_naming"


class GoPackageStateConfig(DetectorConfig):
    """Go package-level state avoidance settings."""

    type: Literal["go_package_state"] = "go_package_state"


class GoInitUsageConfig(DetectorConfig):
    """Go ``init()`` function usage detection settings."""

    type: Literal["go_init_usage"] = "go_init_usage"


class RustUnwrapUsageConfig(DetectorConfig):
    """Rust ``unwrap()`` avoidance settings.

    Attributes:
        max_unwraps: Maximum permitted ``unwrap()`` calls.
    """

    type: Literal["rust_unwrap_usage"] = "rust_unwrap_usage"
    max_unwraps: int = 0


class RustUnsafeBlocksConfig(DetectorConfig):
    """Rust ``unsafe`` block detection settings.

    Attributes:
        detect_unsafe_blocks: When ``True``, flag ``unsafe`` blocks.
    """

    type: Literal["rust_unsafe_blocks"] = "rust_unsafe_blocks"
    detect_unsafe_blocks: bool = True


class RustCloneOverheadConfig(DetectorConfig):
    """Rust excessive ``.clone()`` detection settings.

    Attributes:
        max_clone_calls: Maximum permitted ``.clone()`` calls.
    """

    type: Literal["rust_clone_overhead"] = "rust_clone_overhead"
    max_clone_calls: int = 0


class RustErrorHandlingConfig(DetectorConfig):
    """Rust error-handling enforcement settings.

    Attributes:
        detect_unhandled_results: Flag unhandled ``Result`` values.
        max_panics: Maximum permitted ``panic!`` invocations.
    """

    type: Literal["rust_error_handling"] = "rust_error_handling"
    detect_unhandled_results: bool = True
    max_panics: int = 0


class RustTypeSafetyConfig(DetectorConfig):
    """Rust newtype/type-safety preference settings.

    Attributes:
        primitive_types: Primitive types that should be wrapped in newtypes.
    """

    type: Literal["rust-002"] = "rust-002"
    primitive_types: list[str] = ["String", "i32", "u32", "i64", "u64", "bool"]


class RustIteratorPreferenceConfig(DetectorConfig):
    """Rust iterator-over-loop preference settings.

    Attributes:
        max_loops: Maximum ``for``/``while`` loops before suggesting iterators.
    """

    type: Literal["rust-003"] = "rust-003"
    max_loops: int = 0


class RustMustUseConfig(DetectorConfig):
    """Rust ``#[must_use]`` attribute enforcement settings."""

    type: Literal["rust-005"] = "rust-005"


class RustDebugDeriveConfig(DetectorConfig):
    """Rust ``#[derive(Debug)]`` enforcement settings."""

    type: Literal["rust-006"] = "rust-006"


class RustNewtypePatternConfig(DetectorConfig):
    """Rust newtype-pattern enforcement settings.

    Attributes:
        primitive_types: Types that should be wrapped as newtypes.
    """

    type: Literal["rust-007"] = "rust-007"
    primitive_types: list[str] = ["String", "i32", "u32", "i64", "u64", "bool"]


class RustStdTraitsConfig(DetectorConfig):
    """Rust standard-trait implementation enforcement settings."""

    type: Literal["rust-009"] = "rust-009"


class RustEnumOverBoolConfig(DetectorConfig):
    """Rust enum-over-boolean preference settings.

    Attributes:
        max_bool_fields: Maximum ``bool`` struct fields before suggesting an enum.
    """

    type: Literal["rust-010"] = "rust-010"
    max_bool_fields: int = 0


class RustLifetimeUsageConfig(DetectorConfig):
    """Rust explicit-lifetime minimization settings.

    Attributes:
        max_explicit_lifetimes: Maximum explicit lifetime annotations.
    """

    type: Literal["rust-011"] = "rust-011"
    max_explicit_lifetimes: int = 0


class RustInteriorMutabilityConfig(DetectorConfig):
    """Rust interior-mutability (``RefCell``/``Cell``) detection settings."""

    type: Literal["rust-012"] = "rust-012"


class Bash006Config(DetectorConfig):
    """Bash script-length-without-functions enforcement settings.

    Attributes:
        max_script_length_without_functions: Maximum line count before requiring
            function decomposition.
    """

    type: Literal["bash-006"] = "bash-006"
    max_script_length_without_functions: int | None = None


class Bash011Config(DetectorConfig):
    """Bash minimum variable-name-length enforcement settings.

    Attributes:
        min_variable_name_length: Shortest acceptable variable name.
    """

    type: Literal["bash-011"] = "bash-011"
    min_variable_name_length: int | None = None


class Js009Config(DetectorConfig):
    """JavaScript class inheritance-depth enforcement settings.

    Attributes:
        max_inheritance_depth: Maximum allowed ``extends`` chain depth.
    """

    type: Literal["js-009"] = "js-009"
    max_inheritance_depth: int | None = None


class Js011Config(DetectorConfig):
    """JavaScript minimum identifier-length enforcement settings.

    Attributes:
        min_identifier_length: Shortest acceptable identifier name.
    """

    type: Literal["js-011"] = "js-011"
    min_identifier_length: int | None = None


class Cs008Config(DetectorConfig):
    """C# public/private naming-convention enforcement settings.

    Attributes:
        public_naming: Expected naming style for public members.
        private_naming: Expected naming style for private members.
    """

    type: Literal["cs-008"] = "cs-008"
    public_naming: str | None = None
    private_naming: str | None = None


class GitHubActionsWorkflowConfig(DetectorConfig):
    """GitHub Actions workflow composite detector settings."""

    type: Literal["gha-workflow"] = "gha-workflow"


RULE_CONFIGS: dict[str, type[DetectorConfig]] = {
    "bash-006": Bash006Config,
    "bash-011": Bash011Config,
    "js-009": Js009Config,
    "js-011": Js011Config,
    "cs-008": Cs008Config,
}
