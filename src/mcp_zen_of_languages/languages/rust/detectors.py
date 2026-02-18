"""Rule detectors for rust code quality and architecture checks."""

from __future__ import annotations

import re

from mcp_zen_of_languages.analyzers.base import AnalysisContext, ViolationDetector
from mcp_zen_of_languages.languages.configs import (
    RustCloneOverheadConfig,
    RustDebugDeriveConfig,
    RustEnumOverBoolConfig,
    RustErrorHandlingConfig,
    RustInteriorMutabilityConfig,
    RustIteratorPreferenceConfig,
    RustLifetimeUsageConfig,
    RustMustUseConfig,
    RustNewtypePatternConfig,
    RustStdTraitsConfig,
    RustTypeSafetyConfig,
    RustUnsafeBlocksConfig,
    RustUnwrapUsageConfig,
)
from mcp_zen_of_languages.models import Violation


class RustUnwrapUsageDetector(ViolationDetector[RustUnwrapUsageConfig]):
    """Flags excessive ``unwrap()`` and ``expect()`` calls that bypass Rust's error model.

    Rust's ``Result`` and ``Option`` types encode fallibility in the type
    system, but ``unwrap()`` and ``expect()`` short-circuit that safety
    by panicking on ``Err`` or ``None``.  In library code, panics are
    unrecoverable by callers.  This detector uses a regex to count
    ``.unwrap(`` and ``.expect(`` occurrences and flags files that
    exceed the configured maximum.
    """

    @property
    def name(self) -> str:
        """Return the detector identifier used by registry wiring.

        Returns:
            str: Identifier string consumed by callers.
        """
        return "rust_unwrap_usage"

    def detect(
        self, context: AnalysisContext, config: RustUnwrapUsageConfig
    ) -> list[Violation]:
        """Detect violations for the current analysis context.

        Args:
            context (AnalysisContext): Analysis context containing source text and intermediate metrics.
            config (RustUnwrapUsageConfig): Typed detector or analyzer configuration that controls thresholds.

        Returns:
            list[Violation]: Violations detected for the analyzed context.
        """
        violations: list[Violation] = []
        count = len(re.findall(r"\.unwrap\s*\(|\.expect\s*\(", context.code))
        if count > config.max_unwraps:
            violations.append(
                self.build_violation(
                    config,
                    contains="unwrap",
                    index=0,
                    suggestion="Use ? or match with proper error handling instead of unwrap/expect.",
                )
            )
        return violations


class RustUnsafeBlocksDetector(ViolationDetector[RustUnsafeBlocksConfig]):
    """Ensures every ``unsafe`` block is preceded by a ``// SAFETY:`` comment.

    Rust allows opting out of borrow-checker guarantees with ``unsafe``,
    but the Rust community convention requires a ``// SAFETY:`` comment
    explaining why the invariants hold.  This detector scans each line
    containing the ``unsafe`` keyword and checks the preceding two lines
    for the required safety justification, skipping commented-out code.
    """

    @property
    def name(self) -> str:
        """Return the detector identifier used by registry wiring.

        Returns:
            str: Identifier string consumed by callers.
        """
        return "rust_unsafe_blocks"

    def detect(
        self, context: AnalysisContext, config: RustUnsafeBlocksConfig
    ) -> list[Violation]:
        """Detect violations for the current analysis context.

        Args:
            context (AnalysisContext): Analysis context containing source text and intermediate metrics.
            config (RustUnsafeBlocksConfig): Typed detector or analyzer configuration that controls thresholds.

        Returns:
            list[Violation]: Violations detected for the analyzed context.
        """
        if not config.detect_unsafe_blocks:
            return []
        violations: list[Violation] = []
        lines = context.code.splitlines()
        for idx, line in enumerate(lines):
            if not re.search(r"\bunsafe\b", line):
                continue
            if line.strip().startswith("//"):
                continue
            has_comment = any(
                "// SAFETY:" in lines[back] for back in range(max(0, idx - 2), idx)
            )
            if not has_comment:
                violations.append(
                    self.build_violation(
                        config,
                        contains="safety comments",
                        index=0,
                        suggestion=(
                            "Document invariants with // SAFETY: before unsafe blocks."
                        ),
                    )
                )
        return violations


class RustCloneOverheadDetector(ViolationDetector[RustCloneOverheadConfig]):
    """Detects excessive ``.clone()`` calls that undermine Rust's zero-cost abstraction goal.

    Cloning performs a deep copy, which can be expensive for heap-allocated
    types like ``String`` or ``Vec``.  Idiomatic Rust prefers borrowing or
    ``Cow<T>`` to avoid unnecessary allocations.  This detector counts
    ``.clone()`` invocations via regex and flags files that exceed the
    configured ceiling.
    """

    @property
    def name(self) -> str:
        """Return the detector identifier used by registry wiring.

        Returns:
            str: Identifier string consumed by callers.
        """
        return "rust_clone_overhead"

    def detect(
        self, context: AnalysisContext, config: RustCloneOverheadConfig
    ) -> list[Violation]:
        """Detect violations for the current analysis context.

        Args:
            context (AnalysisContext): Analysis context containing source text and intermediate metrics.
            config (RustCloneOverheadConfig): Typed detector or analyzer configuration that controls thresholds.

        Returns:
            list[Violation]: Violations detected for the analyzed context.
        """
        violations: list[Violation] = []
        count = len(re.findall(r"\.clone\s*\(", context.code))
        if count > config.max_clone_calls:
            violations.append(
                self.build_violation(
                    config,
                    contains="clone",
                    index=0,
                    suggestion="Prefer borrowing or Cow<T> over cloning in hot paths.",
                )
            )
        return violations


class RustErrorHandlingDetector(ViolationDetector[RustErrorHandlingConfig]):
    """Flags functions that use ``Result`` without propagating errors and detects ``panic!`` abuse.

    Rust's error model relies on ``Result<T, E>`` with the ``?`` operator
    for ergonomic propagation.  Functions that declare ``Result`` returns
    but never use ``?`` likely swallow errors silently.  Additionally,
    ``panic!`` in library code is an anti-pattern because callers cannot
    recover.  This detector checks both conditions via regex scans.
    """

    @property
    def name(self) -> str:
        """Return the detector identifier used by registry wiring.

        Returns:
            str: Identifier string consumed by callers.
        """
        return "rust_error_handling"

    def detect(
        self, context: AnalysisContext, config: RustErrorHandlingConfig
    ) -> list[Violation]:
        """Detect violations for the current analysis context.

        Args:
            context (AnalysisContext): Analysis context containing source text and intermediate metrics.
            config (RustErrorHandlingConfig): Typed detector or analyzer configuration that controls thresholds.

        Returns:
            list[Violation]: Violations detected for the analyzed context.
        """
        violations: list[Violation] = []
        if (
            config.detect_unhandled_results
            and re.search(r"\bResult<", context.code)
            and not re.search(r"\?", context.code)
        ):
            violations.append(
                self.build_violation(
                    config,
                    contains="Result",
                    index=0,
                    suggestion="Propagate errors with ? or handle Result explicitly.",
                )
            )
        panic_count = len(re.findall(r"\bpanic!\s*\(", context.code))
        if panic_count > config.max_panics:
            violations.append(
                self.build_violation(
                    config,
                    contains="panic",
                    index=0,
                    suggestion="Avoid panic! in library code; return Result instead.",
                )
            )
        return violations


class RustTypeSafetyDetector(ViolationDetector[RustTypeSafetyConfig]):
    """Flags structs that use raw primitive types instead of domain-specific newtypes.

    Rust's type system is strong enough to prevent entire categories of
    bugs via newtypes (e.g., ``struct UserId(u64)`` instead of bare
    ``u64``).  Raw primitives in struct fields lose semantic meaning and
    allow accidental mixing of unrelated values.  This detector scans
    struct bodies for configured primitive types and suggests wrapping
    them in dedicated newtypes or enums.
    """

    @property
    def name(self) -> str:
        """Return the detector identifier used by registry wiring.

        Returns:
            str: Identifier string consumed by callers.
        """
        return "rust-002"

    def detect(
        self, context: AnalysisContext, config: RustTypeSafetyConfig
    ) -> list[Violation]:
        """Detect violations for the current analysis context.

        Args:
            context (AnalysisContext): Analysis context containing source text and intermediate metrics.
            config (RustTypeSafetyConfig): Typed detector or analyzer configuration that controls thresholds.

        Returns:
            list[Violation]: Violations detected for the analyzed context.
        """
        violations: list[Violation] = []
        types_pattern = "|".join(re.escape(t) for t in config.primitive_types)
        if not types_pattern:
            return violations
        struct_pattern = re.compile(r"struct\s+\w+\s*\{(?P<body>[^}]*)\}", re.S)
        for match in struct_pattern.finditer(context.code):
            body = match.group("body")
            if type_match := re.search(rf":\s*(?P<typ>{types_pattern})\b", body):
                violations.append(
                    self.build_violation(
                        config,
                        contains=type_match["typ"],
                        index=0,
                        suggestion=(
                            "Introduce newtypes or enums for domain-specific values instead "
                            "of raw primitives."
                        ),
                    )
                )
                break
        return violations


class RustIteratorPreferenceDetector(ViolationDetector[RustIteratorPreferenceConfig]):
    """Flags excessive manual loops where iterator adapters would be more idiomatic.

    Rust's iterator combinators (``map``, ``filter``, ``fold``, etc.)
    are zero-cost abstractions that the compiler can optimize as well as
    hand-written loops, while being more expressive and less error-prone.
    This detector counts ``for`` and ``while`` loops and flags files
    that exceed the configured maximum, encouraging iterator-based
    transformations instead.
    """

    @property
    def name(self) -> str:
        """Return the detector identifier used by registry wiring.

        Returns:
            str: Identifier string consumed by callers.
        """
        return "rust-003"

    def detect(
        self, context: AnalysisContext, config: RustIteratorPreferenceConfig
    ) -> list[Violation]:
        """Detect violations for the current analysis context.

        Args:
            context (AnalysisContext): Analysis context containing source text and intermediate metrics.
            config (RustIteratorPreferenceConfig): Typed detector or analyzer configuration that controls thresholds.

        Returns:
            list[Violation]: Violations detected for the analyzed context.
        """
        loop_count = len(re.findall(r"\bfor\s+\w+\s+in\b", context.code)) + len(
            re.findall(r"\bwhile\b", context.code)
        )
        if loop_count > config.max_loops:
            return [
                self.build_violation(
                    config,
                    contains="for",
                    index=0,
                    suggestion="Prefer iterator adapters (map/filter) over manual loops.",
                )
            ]
        return []


class RustMustUseDetector(ViolationDetector[RustMustUseConfig]):
    """Detects ``Result``-returning code that omits the ``#[must_use]`` attribute.

    When a function returns ``Result`` but the caller ignores the return
    value, errors are silently discarded.  The ``#[must_use]`` attribute
    causes a compiler warning when a return value is unused, making
    neglected errors visible at build time.  This detector flags files
    that contain ``Result<`` without any ``#[must_use]`` annotation.
    """

    @property
    def name(self) -> str:
        """Return the detector identifier used by registry wiring.

        Returns:
            str: Identifier string consumed by callers.
        """
        return "rust-005"

    def detect(
        self, context: AnalysisContext, config: RustMustUseConfig
    ) -> list[Violation]:
        """Detect violations for the current analysis context.

        Args:
            context (AnalysisContext): Analysis context containing source text and intermediate metrics.
            config (RustMustUseConfig): Typed detector or analyzer configuration that controls thresholds.

        Returns:
            list[Violation]: Violations detected for the analyzed context.
        """
        if "Result<" in context.code and "#[must_use]" not in context.code:
            return [
                self.build_violation(
                    config,
                    contains="Result",
                    index=0,
                    suggestion="Annotate important return types with #[must_use].",
                )
            ]
        return []


class RustDebugDeriveDetector(ViolationDetector[RustDebugDeriveConfig]):
    """Ensures public structs derive ``Debug`` for ergonomic logging and diagnostics.

    In Rust, ``#[derive(Debug)]`` enables ``{:?}`` formatting, which is
    essential for logging, test assertions, and interactive debugging.
    Public structs without ``Debug`` force consumers to work blindly
    with opaque values.  This detector checks whether files containing
    ``pub struct`` also include ``#[derive(Debug)]`` somewhere.
    """

    @property
    def name(self) -> str:
        """Return the detector identifier used by registry wiring.

        Returns:
            str: Identifier string consumed by callers.
        """
        return "rust-006"

    def detect(
        self, context: AnalysisContext, config: RustDebugDeriveConfig
    ) -> list[Violation]:
        """Detect violations for the current analysis context.

        Args:
            context (AnalysisContext): Analysis context containing source text and intermediate metrics.
            config (RustDebugDeriveConfig): Typed detector or analyzer configuration that controls thresholds.

        Returns:
            list[Violation]: Violations detected for the analyzed context.
        """
        if "pub struct" in context.code and "#[derive(Debug)]" not in context.code:
            return [
                self.build_violation(
                    config,
                    contains="Debug",
                    index=0,
                    suggestion="Derive Debug for public structs with #[derive(Debug)].",
                )
            ]
        return []


class RustNewtypePatternDetector(ViolationDetector[RustNewtypePatternConfig]):
    """Flags type aliases to primitives that should be tuple-struct newtypes.

    A ``type Alias = u64`` creates a transparent synonym with no type
    safety: a ``UserId`` and a ``PostId`` are freely interchangeable.
    A tuple-struct newtype (``struct UserId(u64)``) is a distinct type
    the compiler enforces at every call site.  This detector scans for
    ``type X = <primitive>`` patterns and suggests newtypes instead.
    """

    @property
    def name(self) -> str:
        """Return the detector identifier used by registry wiring.

        Returns:
            str: Identifier string consumed by callers.
        """
        return "rust-007"

    def detect(
        self, context: AnalysisContext, config: RustNewtypePatternConfig
    ) -> list[Violation]:
        """Detect violations for the current analysis context.

        Args:
            context (AnalysisContext): Analysis context containing source text and intermediate metrics.
            config (RustNewtypePatternConfig): Typed detector or analyzer configuration that controls thresholds.

        Returns:
            list[Violation]: Violations detected for the analyzed context.
        """
        if types_pattern := "|".join(re.escape(t) for t in config.primitive_types):
            return (
                [
                    self.build_violation(
                        config,
                        contains="type",
                        index=0,
                        suggestion="Prefer tuple struct newtypes over type aliases.",
                    )
                ]
                if re.search(rf"type\s+\w+\s*=\s*(?:{types_pattern})\b", context.code)
                else []
            )
        return []


class RustStdTraitsDetector(ViolationDetector[RustStdTraitsConfig]):
    """Detects structs that lack standard trait implementations like ``From`` or ``Display``.

    Implementing standard library traits (``From``, ``Into``,
    ``Default``, ``Display``) lets a struct participate in Rust's
    ecosystem idioms — conversions, default construction, and
    user-facing formatting — without custom methods.  This detector
    flags files containing ``struct`` definitions that have no ``impl``
    blocks for any of these key traits.
    """

    @property
    def name(self) -> str:
        """Return the detector identifier used by registry wiring.

        Returns:
            str: Identifier string consumed by callers.
        """
        return "rust-009"

    def detect(
        self, context: AnalysisContext, config: RustStdTraitsConfig
    ) -> list[Violation]:
        """Detect violations for the current analysis context.

        Args:
            context (AnalysisContext): Analysis context containing source text and intermediate metrics.
            config (RustStdTraitsConfig): Typed detector or analyzer configuration that controls thresholds.

        Returns:
            list[Violation]: Violations detected for the analyzed context.
        """
        if "struct" in context.code and not re.search(
            r"impl\s+(From|Into|Default|Display)", context.code
        ):
            return [
                self.build_violation(
                    config,
                    contains="impl",
                    index=0,
                    suggestion="Implement standard traits like From, Default, or Display.",
                )
            ]
        return []


class RustEnumOverBoolDetector(ViolationDetector[RustEnumOverBoolConfig]):
    """Flags structs with too many boolean fields that should be expressed as enums.

    Multiple ``bool`` fields in a struct create combinatorial state
    explosions and make call sites confusing (``new(true, false, true)``).
    An enum with named variants (``enum Mode { Read, Write }``) is
    self-documenting and the compiler can verify exhaustive matching.
    This detector counts ``: bool`` annotations and flags files that
    exceed the configured maximum.
    """

    @property
    def name(self) -> str:
        """Return the detector identifier used by registry wiring.

        Returns:
            str: Identifier string consumed by callers.
        """
        return "rust-010"

    def detect(
        self, context: AnalysisContext, config: RustEnumOverBoolConfig
    ) -> list[Violation]:
        """Detect violations for the current analysis context.

        Args:
            context (AnalysisContext): Analysis context containing source text and intermediate metrics.
            config (RustEnumOverBoolConfig): Typed detector or analyzer configuration that controls thresholds.

        Returns:
            list[Violation]: Violations detected for the analyzed context.
        """
        bool_fields = len(re.findall(r":\s*bool\b", context.code))
        if bool_fields > config.max_bool_fields:
            return [
                self.build_violation(
                    config,
                    contains="bool",
                    index=0,
                    suggestion="Use enums instead of boolean flags for state.",
                )
            ]
        return []


class RustLifetimeUsageDetector(ViolationDetector[RustLifetimeUsageConfig]):
    """Flags excessive explicit lifetime annotations where elision would suffice.

    Rust's lifetime elision rules handle the majority of borrow cases
    automatically.  Overusing explicit lifetimes (``'a``, ``'static``)
    adds visual noise and cognitive overhead without improving safety.
    This detector counts explicit lifetime parameters and ``'static``
    annotations via regex and flags files that exceed the configured
    threshold.
    """

    @property
    def name(self) -> str:
        """Return the detector identifier used by registry wiring.

        Returns:
            str: Identifier string consumed by callers.
        """
        return "rust-011"

    def detect(
        self, context: AnalysisContext, config: RustLifetimeUsageConfig
    ) -> list[Violation]:
        """Detect violations for the current analysis context.

        Args:
            context (AnalysisContext): Analysis context containing source text and intermediate metrics.
            config (RustLifetimeUsageConfig): Typed detector or analyzer configuration that controls thresholds.

        Returns:
            list[Violation]: Violations detected for the analyzed context.
        """
        lifetimes = len(re.findall(r"<\s*'\w+", context.code)) + len(
            re.findall(r"'static", context.code)
        )
        if lifetimes > config.max_explicit_lifetimes:
            return [
                self.build_violation(
                    config,
                    contains="lifetime",
                    index=0,
                    suggestion="Prefer elided lifetimes unless explicit ones are required.",
                )
            ]
        return []


class RustInteriorMutabilityDetector(ViolationDetector[RustInteriorMutabilityConfig]):
    """Detects ``Rc<RefCell<T>>`` and ``Arc<Mutex<T>>`` patterns that signal design issues.

    Interior mutability types let you mutate data behind shared
    references, but ``Rc<RefCell<T>>`` panics on borrow violations at
    runtime and ``Arc<Mutex<T>>`` risks deadlocks.  Frequent use of
    these wrappers often indicates that ownership boundaries need
    rethinking.  This detector scans for both patterns via regex and
    flags their presence.
    """

    @property
    def name(self) -> str:
        """Return the detector identifier used by registry wiring.

        Returns:
            str: Identifier string consumed by callers.
        """
        return "rust-012"

    def detect(
        self, context: AnalysisContext, config: RustInteriorMutabilityConfig
    ) -> list[Violation]:
        """Detect violations for the current analysis context.

        Args:
            context (AnalysisContext): Analysis context containing source text and intermediate metrics.
            config (RustInteriorMutabilityConfig): Typed detector or analyzer configuration that controls thresholds.

        Returns:
            list[Violation]: Violations detected for the analyzed context.
        """
        if re.search(r"Rc<\s*RefCell|Arc<\s*Mutex", context.code):
            return [
                self.build_violation(
                    config,
                    contains="RefCell",
                    index=0,
                    suggestion="Avoid Rc<RefCell> or Arc<Mutex> unless required.",
                )
            ]
        return []


__all__ = [
    "RustUnwrapUsageDetector",
    "RustUnsafeBlocksDetector",
    "RustCloneOverheadDetector",
    "RustErrorHandlingDetector",
    "RustTypeSafetyDetector",
    "RustIteratorPreferenceDetector",
    "RustMustUseDetector",
    "RustDebugDeriveDetector",
    "RustNewtypePatternDetector",
    "RustStdTraitsDetector",
    "RustEnumOverBoolDetector",
    "RustLifetimeUsageDetector",
    "RustInteriorMutabilityDetector",
]
