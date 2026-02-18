"""Rule detectors for typescript code quality and architecture checks."""

from __future__ import annotations

import re

from mcp_zen_of_languages.analyzers.base import (
    AnalysisContext,
    LocationHelperMixin,
    ViolationDetector,
)
from mcp_zen_of_languages.languages.configs import (
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
from mcp_zen_of_languages.rules.detections import (
    detect_ts_any_usage,
    detect_ts_missing_return_types,
    detect_ts_non_null_assertions,
    detect_ts_object_type_aliases,
    detect_ts_plain_enum_objects,
    detect_ts_readonly_usage,
    detect_ts_type_assertions,
    detect_ts_unknown_over_any,
    detect_ts_utility_types,
)
from typing import TYPE_CHECKING

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
        self, context: AnalysisContext, config: TsAnyUsageConfig
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
                )
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
        self, context: AnalysisContext, config: TsStrictModeConfig
    ) -> list[Violation]:
        """Detect violations for the current analysis context.

        Args:
            context (AnalysisContext): Analysis context containing source text and intermediate metrics.
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
                )
            )
        return violations


class TsInterfacePreferenceDetector(
    ViolationDetector[TsInterfacePreferenceConfig], LocationHelperMixin
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
        self, context: AnalysisContext, config: TsInterfacePreferenceConfig
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
                )
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
        self, context: AnalysisContext, config: TsReturnTypeConfig
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
                )
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
        self, context: AnalysisContext, config: TsReadonlyConfig
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
                )
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
        self, context: AnalysisContext, config: TsTypeGuardConfig
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
                )
            )
        return violations


class TsUtilityTypesDetector(
    ViolationDetector[TsUtilityTypesConfig], LocationHelperMixin
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
        self, context: AnalysisContext, config: TsUtilityTypesConfig
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
                )
            )
        return violations


class TsNonNullAssertionDetector(
    ViolationDetector[TsNonNullAssertionConfig], LocationHelperMixin
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
        self, context: AnalysisContext, config: TsNonNullAssertionConfig
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
                )
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
        self, context: AnalysisContext, config: TsEnumConstConfig
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
                )
            )
        return violations


class TsUnknownOverAnyDetector(
    ViolationDetector[TsUnknownOverAnyConfig], LocationHelperMixin
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
        self, context: AnalysisContext, config: TsUnknownOverAnyConfig
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
                )
            )
        return violations


__all__ = [
    "TsAnyUsageDetector",
    "TsEnumConstDetector",
    "TsInterfacePreferenceDetector",
    "TsNonNullAssertionDetector",
    "TsReadonlyDetector",
    "TsReturnTypeDetector",
    "TsStrictModeDetector",
    "TsTypeGuardDetector",
    "TsUnknownOverAnyDetector",
    "TsUtilityTypesDetector",
]
