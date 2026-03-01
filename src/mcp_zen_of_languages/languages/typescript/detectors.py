"""Rule detectors for typescript code quality and architecture checks."""

from __future__ import annotations

import re

from typing import TYPE_CHECKING

from mcp_zen_of_languages.analyzers.base import AnalysisContext
from mcp_zen_of_languages.analyzers.base import LocationHelperMixin
from mcp_zen_of_languages.analyzers.base import ViolationDetector
from mcp_zen_of_languages.languages.configs import TsAnyUsageConfig
from mcp_zen_of_languages.languages.configs import TsCatchAllTypeConfig
from mcp_zen_of_languages.languages.configs import TsConsoleUsageConfig
from mcp_zen_of_languages.languages.configs import TsDefaultExportConfig
from mcp_zen_of_languages.languages.configs import TsEnumConstConfig
from mcp_zen_of_languages.languages.configs import TsIndexLoopConfig
from mcp_zen_of_languages.languages.configs import TsInterfacePreferenceConfig
from mcp_zen_of_languages.languages.configs import TsNonNullAssertionConfig
from mcp_zen_of_languages.languages.configs import TsOptionalChainingConfig
from mcp_zen_of_languages.languages.configs import TsPromiseChainConfig
from mcp_zen_of_languages.languages.configs import TsReadonlyConfig
from mcp_zen_of_languages.languages.configs import TsRequireImportConfig
from mcp_zen_of_languages.languages.configs import TsReturnTypeConfig
from mcp_zen_of_languages.languages.configs import TsStrictModeConfig
from mcp_zen_of_languages.languages.configs import TsStringConcatConfig
from mcp_zen_of_languages.languages.configs import TsTypeGuardConfig
from mcp_zen_of_languages.languages.configs import TsUnknownOverAnyConfig
from mcp_zen_of_languages.languages.configs import TsUtilityTypesConfig
from mcp_zen_of_languages.rules.detections import detect_ts_any_usage
from mcp_zen_of_languages.rules.detections import detect_ts_catch_all_types
from mcp_zen_of_languages.rules.detections import detect_ts_console_usage
from mcp_zen_of_languages.rules.detections import detect_ts_default_exports
from mcp_zen_of_languages.rules.detections import detect_ts_index_loops
from mcp_zen_of_languages.rules.detections import detect_ts_missing_return_types
from mcp_zen_of_languages.rules.detections import detect_ts_non_null_assertions
from mcp_zen_of_languages.rules.detections import detect_ts_object_type_aliases
from mcp_zen_of_languages.rules.detections import detect_ts_optional_chaining
from mcp_zen_of_languages.rules.detections import detect_ts_plain_enum_objects
from mcp_zen_of_languages.rules.detections import detect_ts_promise_chains
from mcp_zen_of_languages.rules.detections import detect_ts_readonly_usage
from mcp_zen_of_languages.rules.detections import detect_ts_require_imports
from mcp_zen_of_languages.rules.detections import detect_ts_string_concats
from mcp_zen_of_languages.rules.detections import detect_ts_type_assertions
from mcp_zen_of_languages.rules.detections import detect_ts_unknown_over_any
from mcp_zen_of_languages.rules.detections import detect_ts_utility_types


if TYPE_CHECKING:
    from mcp_zen_of_languages.models import Violation


class TsAnyUsageDetector(ViolationDetector[TsAnyUsageConfig], LocationHelperMixin):
    """Detects excessive use of the ``any`` type that undermines TypeScript's value.

    The ``any`` type disables all type checking for a value, silently
    propagating unsafety through every expression it touches.  This
    detector counts ``any`` annotations via ``detect_ts_any_usage`` and
    flags files that exceed the configured threshold, encouraging the use
    of ``unknown``, generics, or concrete types instead.
    """

    @property
    def name(self) -> str:
        """Return the detector identifier used by registry wiring.

        Returns:
            str: Identifier string consumed by callers.
        """
        return "ts_any_usage"

    def detect(
        self,
        context: AnalysisContext,
        config: TsAnyUsageConfig,
    ) -> list[Violation]:
        """Detect violations for the current analysis context.

        Args:
            context (AnalysisContext): Analysis context containing source text and intermediate metrics.
            config (TsAnyUsageConfig): Typed detector or analyzer configuration that controls thresholds.

        Returns:
            list[Violation]: Violations detected for the analyzed context.
        """
        violations: list[Violation] = []
        finding = detect_ts_any_usage(context.code)
        if finding.count > config.max_any_usages:
            violations.append(
                self.build_violation(
                    config,
                    contains="any",
                    index=0,
                    suggestion="Use unknown or specific types instead of any.",
                ),
            )
        return violations


class TsStrictModeDetector(ViolationDetector[TsStrictModeConfig]):
    """Checks whether strict compiler options are enabled in the project.

    TypeScript's ``strict`` flag activates ``strictNullChecks``,
    ``noImplicitAny``, and other safety options that catch common bugs at
    compile time.  Without strict mode, TypeScript behaves almost like
    plain JavaScript, making the type system advisory rather than
    enforced.  This detector raises a violation when strict mode is
    required by configuration but not detected in the source.
    """

    @property
    def name(self) -> str:
        """Return the detector identifier used by registry wiring.

        Returns:
            str: Identifier string consumed by callers.
        """
        return "ts_strict_mode"

    def detect(
        self,
        _context: AnalysisContext,
        config: TsStrictModeConfig,
    ) -> list[Violation]:
        """Detect violations for the current analysis context.

        Args:
            _context (AnalysisContext): Analysis context containing source text and intermediate metrics.
            config (TsStrictModeConfig): Typed detector or analyzer configuration that controls thresholds.

        Returns:
            list[Violation]: Violations detected for the analyzed context.
        """
        violations: list[Violation] = []
        if config.require_strict:
            violations.append(
                self.build_violation(
                    config,
                    contains="strict",
                    index=0,
                    suggestion="Enable strict compiler options in tsconfig.",
                ),
            )
        return violations


class TsInterfacePreferenceDetector(
    ViolationDetector[TsInterfacePreferenceConfig],
    LocationHelperMixin,
):
    """Flags object-shaped type aliases that should be interfaces instead.

    In TypeScript, ``interface`` declarations are open for extension via
    declaration merging and produce clearer error messages than ``type``
    aliases for object shapes.  This detector uses
    ``detect_ts_object_type_aliases`` to count ``type Foo = { ... }``
    patterns and flags files that exceed the configured limit,
    encouraging the use of ``interface`` for plain object contracts.
    """

    @property
    def name(self) -> str:
        """Return the detector identifier used by registry wiring.

        Returns:
            str: Identifier string consumed by callers.
        """
        return "ts_interface_preference"

    def detect(
        self,
        context: AnalysisContext,
        config: TsInterfacePreferenceConfig,
    ) -> list[Violation]:
        """Detect violations for the current analysis context.

        Args:
            context (AnalysisContext): Analysis context containing source text and intermediate metrics.
            config (TsInterfacePreferenceConfig): Typed detector or analyzer configuration that controls thresholds.

        Returns:
            list[Violation]: Violations detected for the analyzed context.
        """
        violations: list[Violation] = []
        finding = detect_ts_object_type_aliases(context.code)
        if finding.count > config.max_object_type_aliases:
            violations.append(
                self.build_violation(
                    config,
                    contains="Type aliases",
                    index=0,
                    suggestion="Prefer interfaces for object shapes.",
                ),
            )
        return violations


class TsReturnTypeDetector(ViolationDetector[TsReturnTypeConfig], LocationHelperMixin):
    """Flags exported functions that lack explicit return type annotations.

    When functions omit return types, TypeScript infers them, which can
    silently widen the contract and break callers after refactoring.
    Explicit return types serve as documentation and a stability
    guarantee at API boundaries.  This detector uses
    ``detect_ts_missing_return_types`` to scan for exported functions
    without a declared return type.
    """

    @property
    def name(self) -> str:
        """Return the detector identifier used by registry wiring.

        Returns:
            str: Identifier string consumed by callers.
        """
        return "ts_return_types"

    def detect(
        self,
        context: AnalysisContext,
        config: TsReturnTypeConfig,
    ) -> list[Violation]:
        """Detect violations for the current analysis context.

        Args:
            context (AnalysisContext): Analysis context containing source text and intermediate metrics.
            config (TsReturnTypeConfig): Typed detector or analyzer configuration that controls thresholds.

        Returns:
            list[Violation]: Violations detected for the analyzed context.
        """
        if not config.require_return_types:
            return []
        violations: list[Violation] = []
        finding = detect_ts_missing_return_types(context.code)
        if finding.count > 0:
            violations.append(
                self.build_violation(
                    config,
                    contains="return type",
                    index=0,
                    suggestion="Add explicit return types for exported functions.",
                ),
            )
        return violations


class TsReadonlyDetector(ViolationDetector[TsReadonlyConfig], LocationHelperMixin):
    """Detects insufficient use of ``readonly`` for immutable properties and arrays.

    Marking properties and array types as ``readonly`` prevents
    accidental mutation, a common source of bugs in shared state.  This
    detector counts ``readonly`` annotations via
    ``detect_ts_readonly_usage`` and flags files where the count falls
    below the configured minimum, nudging authors toward immutability by
    default.
    """

    @property
    def name(self) -> str:
        """Return the detector identifier used by registry wiring.

        Returns:
            str: Identifier string consumed by callers.
        """
        return "ts_readonly"

    def detect(
        self,
        context: AnalysisContext,
        config: TsReadonlyConfig,
    ) -> list[Violation]:
        """Detect violations for the current analysis context.

        Args:
            context (AnalysisContext): Analysis context containing source text and intermediate metrics.
            config (TsReadonlyConfig): Typed detector or analyzer configuration that controls thresholds.

        Returns:
            list[Violation]: Violations detected for the analyzed context.
        """
        violations: list[Violation] = []
        finding = detect_ts_readonly_usage(context.code)
        if (
            config.require_readonly_properties
            and finding.count < config.min_readonly_occurrences
        ):
            violations.append(
                self.build_violation(
                    config,
                    contains="readonly",
                    index=0,
                    suggestion="Use readonly for immutable properties and arrays.",
                ),
            )
        return violations


class TsTypeGuardDetector(ViolationDetector[TsTypeGuardConfig], LocationHelperMixin):
    """Flags overuse of type assertions (``as T``) instead of user-defined type guards.

    Type assertions bypass the compiler's narrowing logic and can mask
    runtime type mismatches.  User-defined type guards (``x is Foo``)
    let TypeScript narrow types safely within conditional branches.
    This detector uses ``detect_ts_type_assertions`` to count ``as``
    casts and flags files that exceed the configured ceiling.
    """

    @property
    def name(self) -> str:
        """Return the detector identifier used by registry wiring.

        Returns:
            str: Identifier string consumed by callers.
        """
        return "ts_type_guards"

    def detect(
        self,
        context: AnalysisContext,
        config: TsTypeGuardConfig,
    ) -> list[Violation]:
        """Detect violations for the current analysis context.

        Args:
            context (AnalysisContext): Analysis context containing source text and intermediate metrics.
            config (TsTypeGuardConfig): Typed detector or analyzer configuration that controls thresholds.

        Returns:
            list[Violation]: Violations detected for the analyzed context.
        """
        violations: list[Violation] = []
        finding = detect_ts_type_assertions(context.code)
        if finding.count > config.max_type_assertions:
            violations.append(
                self.build_violation(
                    config,
                    contains="assertions",
                    index=0,
                    suggestion="Prefer user-defined type guards over assertions.",
                ),
            )
        return violations


class TsUtilityTypesDetector(
    ViolationDetector[TsUtilityTypesConfig],
    LocationHelperMixin,
):
    """Detects missed opportunities to use built-in utility types like ``Partial`` or ``Pick``.

    TypeScript ships with utility types (``Partial<T>``, ``Readonly<T>``,
    ``Pick<T, K>``, etc.) that express common type transformations
    concisely.  When a codebase defines many object type aliases but
    rarely uses utility types, authors are likely duplicating structure
    that could be derived.  This detector cross-checks utility-type
    usage against object-alias counts and flags the gap.
    """

    @property
    def name(self) -> str:
        """Return the detector identifier used by registry wiring.

        Returns:
            str: Identifier string consumed by callers.
        """
        return "ts_utility_types"

    def detect(
        self,
        context: AnalysisContext,
        config: TsUtilityTypesConfig,
    ) -> list[Violation]:
        """Detect violations for the current analysis context.

        Args:
            context (AnalysisContext): Analysis context containing source text and intermediate metrics.
            config (TsUtilityTypesConfig): Typed detector or analyzer configuration that controls thresholds.

        Returns:
            list[Violation]: Violations detected for the analyzed context.
        """
        violations: list[Violation] = []
        utility = detect_ts_utility_types(context.code)
        object_aliases = detect_ts_object_type_aliases(context.code)
        if (
            utility.count < config.min_utility_type_usage
            and object_aliases.count >= config.min_object_type_aliases
        ):
            violations.append(
                self.build_violation(
                    config,
                    contains="utility",
                    index=0,
                    suggestion="Use built-in utility types for transformations.",
                ),
            )
        return violations


class TsNonNullAssertionDetector(
    ViolationDetector[TsNonNullAssertionConfig],
    LocationHelperMixin,
):
    """Flags excessive non-null assertion operators (``!``) that silence null safety.

    The postfix ``!`` operator tells TypeScript to trust that a value is
    neither ``null`` nor ``undefined``, but it offers no runtime
    protection.  Chained assertions like ``obj!.prop!`` are especially
    dangerous.  This detector combines results from
    ``detect_ts_non_null_assertions`` with a regex scan for chained
    patterns and flags files that exceed the configured limit.
    """

    @property
    def name(self) -> str:
        """Return the detector identifier used by registry wiring.

        Returns:
            str: Identifier string consumed by callers.
        """
        return "ts_non_null_assertions"

    def detect(
        self,
        context: AnalysisContext,
        config: TsNonNullAssertionConfig,
    ) -> list[Violation]:
        """Detect violations for the current analysis context.

        Args:
            context (AnalysisContext): Analysis context containing source text and intermediate metrics.
            config (TsNonNullAssertionConfig): Typed detector or analyzer configuration that controls thresholds.

        Returns:
            list[Violation]: Violations detected for the analyzed context.
        """
        violations: list[Violation] = []
        finding = detect_ts_non_null_assertions(context.code)
        chain_count = len(re.findall(r"\w+!\.\w+!", context.code))
        if finding.count + chain_count > config.max_non_null_assertions:
            violations.append(
                self.build_violation(
                    config,
                    contains="Non-null",
                    index=1,
                    suggestion="Handle null/undefined via checks instead of non-null assertions.",
                ),
            )
        return violations


class TsEnumConstDetector(ViolationDetector[TsEnumConstConfig], LocationHelperMixin):
    """Detects plain object literals used as constants instead of enums or ``as const``.

    Plain objects masquerading as enumerations lose TypeScript's
    exhaustiveness checking and allow arbitrary string or number values
    to slip through.  Using ``enum`` or ``as const`` assertions gives
    the compiler a closed set of values it can verify at every usage
    site.  This detector uses ``detect_ts_plain_enum_objects`` to count
    constant-like object patterns and flags files above the threshold.
    """

    @property
    def name(self) -> str:
        """Return the detector identifier used by registry wiring.

        Returns:
            str: Identifier string consumed by callers.
        """
        return "ts_enum_const"

    def detect(
        self,
        context: AnalysisContext,
        config: TsEnumConstConfig,
    ) -> list[Violation]:
        """Detect violations for the current analysis context.

        Args:
            context (AnalysisContext): Analysis context containing source text and intermediate metrics.
            config (TsEnumConstConfig): Typed detector or analyzer configuration that controls thresholds.

        Returns:
            list[Violation]: Violations detected for the analyzed context.
        """
        violations: list[Violation] = []
        finding = detect_ts_plain_enum_objects(context.code)
        if finding.count > config.max_plain_enum_objects:
            violations.append(
                self.build_violation(
                    config,
                    contains="Plain objects",
                    index=0,
                    suggestion="Use enums or const assertions for constants.",
                ),
            )
        return violations


class TsUnknownOverAnyDetector(
    ViolationDetector[TsUnknownOverAnyConfig],
    LocationHelperMixin,
):
    """Flags codebases that use ``any`` without ever using the safer ``unknown`` alternative.

    ``unknown`` is the type-safe counterpart of ``any``: it accepts
    every value but requires narrowing before use, catching mistakes
    that ``any`` would silently allow.  This detector checks whether
    ``any`` annotations appear above the configured ceiling while
    ``unknown`` is entirely absent, indicating that authors may not be
    aware of the safer option.
    """

    @property
    def name(self) -> str:
        """Return the detector identifier used by registry wiring.

        Returns:
            str: Identifier string consumed by callers.
        """
        return "ts_unknown_over_any"

    def detect(
        self,
        context: AnalysisContext,
        config: TsUnknownOverAnyConfig,
    ) -> list[Violation]:
        """Detect violations for the current analysis context.

        Args:
            context (AnalysisContext): Analysis context containing source text and intermediate metrics.
            config (TsUnknownOverAnyConfig): Typed detector or analyzer configuration that controls thresholds.

        Returns:
            list[Violation]: Violations detected for the analyzed context.
        """
        violations: list[Violation] = []
        finding = detect_ts_unknown_over_any(context.code)
        if (
            finding.any_count > config.max_any_for_unknown
            and finding.unknown_count == 0
        ):
            violations.append(
                self.build_violation(
                    config,
                    contains="any",
                    index=0,
                    suggestion="Prefer unknown for uncertain types.",
                ),
            )
        return violations


class TsOptionalChainingDetector(
    ViolationDetector[TsOptionalChainingConfig],
    LocationHelperMixin,
):
    """Detects manual null-check chains replaceable by optional chaining (``?.``)."""

    @property
    def name(self) -> str:
        """Return the detector identifier.

        Returns:
            str: Identifier string.
        """
        return "ts_optional_chaining"

    def detect(
        self,
        context: AnalysisContext,
        config: TsOptionalChainingConfig,
    ) -> list[Violation]:
        """Detect manual null-check chain violations.

        Args:
            context (AnalysisContext): Analysis context.
            config (TsOptionalChainingConfig): Detector configuration.

        Returns:
            list[Violation]: Violations found.
        """
        violations: list[Violation] = []
        finding = detect_ts_optional_chaining(context.code)
        if finding.count > config.max_manual_null_checks:
            violations.append(
                self.build_violation(
                    config,
                    contains="&&",
                    index=0,
                    suggestion="Use optional chaining (?.) instead of manual null checks.",
                ),
            )
        return violations


class TsIndexLoopDetector(
    ViolationDetector[TsIndexLoopConfig],
    LocationHelperMixin,
):
    """Detects C-style index-based ``for`` loops replaceable by ``for-of`` or array methods."""

    @property
    def name(self) -> str:
        """Return the detector identifier.

        Returns:
            str: Identifier string.
        """
        return "ts_index_loops"

    def detect(
        self,
        context: AnalysisContext,
        config: TsIndexLoopConfig,
    ) -> list[Violation]:
        """Detect index-loop violations.

        Args:
            context (AnalysisContext): Analysis context.
            config (TsIndexLoopConfig): Detector configuration.

        Returns:
            list[Violation]: Violations found.
        """
        violations: list[Violation] = []
        finding = detect_ts_index_loops(context.code)
        if finding.count > config.max_index_loops:
            violations.append(
                self.build_violation(
                    config,
                    contains="for",
                    index=0,
                    suggestion="Prefer for-of or array methods over index loops.",
                ),
            )
        return violations


class TsPromiseChainDetector(
    ViolationDetector[TsPromiseChainConfig],
    LocationHelperMixin,
):
    """Detects raw ``.then()`` promise chains replaceable by async/await."""

    @property
    def name(self) -> str:
        """Return the detector identifier.

        Returns:
            str: Identifier string.
        """
        return "ts_promise_chains"

    def detect(
        self,
        context: AnalysisContext,
        config: TsPromiseChainConfig,
    ) -> list[Violation]:
        """Detect promise chain violations.

        Args:
            context (AnalysisContext): Analysis context.
            config (TsPromiseChainConfig): Detector configuration.

        Returns:
            list[Violation]: Violations found.
        """
        violations: list[Violation] = []
        finding = detect_ts_promise_chains(context.code)
        if finding.count > config.max_promise_chains:
            violations.append(
                self.build_violation(
                    config,
                    contains=".then(",
                    index=0,
                    suggestion="Prefer async/await over raw promise chains.",
                ),
            )
        return violations


class TsDefaultExportDetector(
    ViolationDetector[TsDefaultExportConfig],
    LocationHelperMixin,
):
    """Detects ``export default`` statements encouraging named exports instead."""

    @property
    def name(self) -> str:
        """Return the detector identifier.

        Returns:
            str: Identifier string.
        """
        return "ts_default_exports"

    def detect(
        self,
        context: AnalysisContext,
        config: TsDefaultExportConfig,
    ) -> list[Violation]:
        """Detect default export violations.

        Args:
            context (AnalysisContext): Analysis context.
            config (TsDefaultExportConfig): Detector configuration.

        Returns:
            list[Violation]: Violations found.
        """
        violations: list[Violation] = []
        finding = detect_ts_default_exports(context.code)
        if finding.count > config.max_default_exports:
            violations.append(
                self.build_violation(
                    config,
                    contains="export default",
                    index=0,
                    suggestion="Prefer named exports for better refactoring support.",
                ),
            )
        return violations


class TsCatchAllTypeDetector(
    ViolationDetector[TsCatchAllTypeConfig],
    LocationHelperMixin,
):
    """Detects catch-all type annotations (``Object``, ``object``, ``{}``)."""

    @property
    def name(self) -> str:
        """Return the detector identifier.

        Returns:
            str: Identifier string.
        """
        return "ts_catch_all_types"

    def detect(
        self,
        context: AnalysisContext,
        config: TsCatchAllTypeConfig,
    ) -> list[Violation]:
        """Detect catch-all type violations.

        Args:
            context (AnalysisContext): Analysis context.
            config (TsCatchAllTypeConfig): Detector configuration.

        Returns:
            list[Violation]: Violations found.
        """
        violations: list[Violation] = []
        finding = detect_ts_catch_all_types(context.code)
        if finding.count > config.max_catch_all_types:
            violations.append(
                self.build_violation(
                    config,
                    contains="Object",
                    index=0,
                    suggestion="Use precise types instead of Object, object, or {}.",
                ),
            )
        return violations


class TsConsoleUsageDetector(
    ViolationDetector[TsConsoleUsageConfig],
    LocationHelperMixin,
):
    """Detects ``console.*`` calls in TypeScript production code."""

    @property
    def name(self) -> str:
        """Return the detector identifier.

        Returns:
            str: Identifier string.
        """
        return "ts_console_usage"

    def detect(
        self,
        context: AnalysisContext,
        config: TsConsoleUsageConfig,
    ) -> list[Violation]:
        """Detect console usage violations.

        Args:
            context (AnalysisContext): Analysis context.
            config (TsConsoleUsageConfig): Detector configuration.

        Returns:
            list[Violation]: Violations found.
        """
        violations: list[Violation] = []
        finding = detect_ts_console_usage(context.code)
        if finding.count > config.max_console_usages:
            violations.append(
                self.build_violation(
                    config,
                    contains="console.",
                    index=0,
                    suggestion="Use a proper logging framework instead of console.",
                ),
            )
        return violations


class TsRequireImportDetector(
    ViolationDetector[TsRequireImportConfig],
    LocationHelperMixin,
):
    """Detects ``require()`` calls encouraging ES module imports instead."""

    @property
    def name(self) -> str:
        """Return the detector identifier.

        Returns:
            str: Identifier string.
        """
        return "ts_require_imports"

    def detect(
        self,
        context: AnalysisContext,
        config: TsRequireImportConfig,
    ) -> list[Violation]:
        """Detect require import violations.

        Args:
            context (AnalysisContext): Analysis context.
            config (TsRequireImportConfig): Detector configuration.

        Returns:
            list[Violation]: Violations found.
        """
        violations: list[Violation] = []
        finding = detect_ts_require_imports(context.code)
        if finding.count > config.max_require_calls:
            violations.append(
                self.build_violation(
                    config,
                    contains="require(",
                    index=0,
                    suggestion="Use ES module import/export syntax instead of require().",
                ),
            )
        return violations


class TsStringConcatDetector(
    ViolationDetector[TsStringConcatConfig],
    LocationHelperMixin,
):
    """Detects string concatenation patterns encouraging template literals."""

    @property
    def name(self) -> str:
        """Return the detector identifier.

        Returns:
            str: Identifier string.
        """
        return "ts_string_concats"

    def detect(
        self,
        context: AnalysisContext,
        config: TsStringConcatConfig,
    ) -> list[Violation]:
        """Detect string concatenation violations.

        Args:
            context (AnalysisContext): Analysis context.
            config (TsStringConcatConfig): Detector configuration.

        Returns:
            list[Violation]: Violations found.
        """
        violations: list[Violation] = []
        finding = detect_ts_string_concats(context.code)
        if finding.count > config.max_string_concats:
            violations.append(
                self.build_violation(
                    config,
                    contains="+",
                    index=0,
                    suggestion="Use template literals instead of string concatenation.",
                ),
            )
        return violations


__all__ = [
    "TsAnyUsageDetector",
    "TsCatchAllTypeDetector",
    "TsConsoleUsageDetector",
    "TsDefaultExportDetector",
    "TsEnumConstDetector",
    "TsIndexLoopDetector",
    "TsInterfacePreferenceDetector",
    "TsNonNullAssertionDetector",
    "TsOptionalChainingDetector",
    "TsPromiseChainDetector",
    "TsReadonlyDetector",
    "TsRequireImportDetector",
    "TsReturnTypeDetector",
    "TsStrictModeDetector",
    "TsStringConcatDetector",
    "TsTypeGuardDetector",
    "TsUnknownOverAnyDetector",
    "TsUtilityTypesDetector",
]
