"""Zen-rule detectors for C++ code quality, safety, and modern idiom checks.

Each detector implements the Strategy pattern as a ``ViolationDetector``
subclass, targeting a specific C++ anti-pattern.  Modern C++ (C++11 through
C++23) provides RAII, smart pointers, ``constexpr``, range-based loops, and
``std::optional`` to replace error-prone C-era patterns; these detectors
enforce that transition.

See Also:
    ``CppAnalyzer``: Template Method analyzer that orchestrates these detectors.
"""

from __future__ import annotations

import re

from mcp_zen_of_languages.analyzers.base import (
    AnalysisContext,
    LocationHelperMixin,
    ViolationDetector,
)
from mcp_zen_of_languages.languages.configs import (
    CppAutoConfig,
    CppAvoidGlobalsConfig,
    CppConstCorrectnessConfig,
    CppCStyleCastConfig,
    CppManualAllocationConfig,
    CppMoveConfig,
    CppNullptrConfig,
    CppOptionalConfig,
    CppOverrideFinalConfig,
    CppRaiiConfig,
    CppRangeForConfig,
    CppRuleOfFiveConfig,
    CppSmartPointerConfig,
)
from mcp_zen_of_languages.models import Location, Violation


class CppSmartPointerDetector(
    ViolationDetector[CppSmartPointerConfig], LocationHelperMixin
):
    """Flags raw ``new``/``delete`` usage where smart pointers should be used.

    Manual ``new``/``delete`` is the leading cause of memory leaks, dangling
    pointers, and double-free vulnerabilities in C++ code.  ``std::unique_ptr``
    and ``std::shared_ptr`` provide deterministic, exception-safe ownership
    semantics that eliminate entire categories of runtime errors with zero
    overhead (for ``unique_ptr``) or minimal overhead (for ``shared_ptr``).
    """

    @property
    def name(self) -> str:
        """Return ``'cpp_smart_pointers'`` for registry wiring.

        Returns:
            str: Detector identifier for the smart-pointer rule.
        """
        return "cpp_smart_pointers"

    def detect(
        self, context: AnalysisContext, config: CppSmartPointerConfig
    ) -> list[Violation]:
        """Flag lines containing raw ``new`` or ``delete`` expressions.

        Args:
            context: Analysis context with C++ source text.
            config: Smart-pointer detection configuration.

        Returns:
            list[Violation]: Violations detected for the analyzed context.
        """
        violations: list[Violation] = [
            self.build_violation(
                config,
                contains="new",
                location=Location(line=idx, column=1),
                suggestion=(
                    "Prefer smart pointers and RAII over manual new/delete."
                ),
            )
            for idx, line in enumerate(context.code.splitlines(), start=1)
            if re.search(r"\bnew\b", line) or re.search(r"\bdelete\b", line)
        ]
        return violations


class CppNullptrDetector(ViolationDetector[CppNullptrConfig], LocationHelperMixin):
    """Flags legacy ``NULL`` macro usage instead of the type-safe ``nullptr`` literal.

    The ``NULL`` macro is a C holdover typically defined as ``0`` or
    ``(void*)0``, which participates in integer overload resolution and
    can silently select the wrong function overload.  ``nullptr`` introduced
    in C++11 has its own type (``std::nullptr_t``) that only converts to
    pointer types, preventing subtle overload-resolution bugs.
    """

    @property
    def name(self) -> str:
        """Return ``'cpp_nullptr'`` for registry wiring.

        Returns:
            str: Detector identifier for the nullptr rule.
        """
        return "cpp_nullptr"

    def detect(
        self, context: AnalysisContext, config: CppNullptrConfig
    ) -> list[Violation]:
        """Flag lines that reference the ``NULL`` macro.

        Args:
            context: Analysis context with C++ source text.
            config: Nullptr detection configuration.

        Returns:
            list[Violation]: Violations detected for the analyzed context.
        """
        violations: list[Violation] = [
            self.build_violation(
                config,
                contains="nullptr",
                location=Location(line=idx, column=1),
                suggestion="Use nullptr instead of NULL/0.",
            )
            for idx, line in enumerate(context.code.splitlines(), start=1)
            if re.search(r"\bNULL\b", line)
        ]
        return violations


class CppRaiiDetector(ViolationDetector[CppRaiiConfig], LocationHelperMixin):
    """Detects manual resource management that should use RAII wrappers.

    RAII (Resource Acquisition Is Initialization) is the cornerstone of
    safe C++ resource management.  Raw ``new``/``delete``, ``malloc``/``free``
    calls bypass destructor-based cleanup, leaving resources leaked when
    exceptions unwind the stack or early returns skip cleanup code.  Using
    RAII wrappers like ``std::unique_ptr``, ``std::lock_guard``, or custom
    scoped handles ensures deterministic release regardless of control flow.
    """

    @property
    def name(self) -> str:
        """Return ``'cpp-001'`` for registry wiring.

        Returns:
            str: Detector identifier for the RAII rule.
        """
        return "cpp-001"

    def detect(
        self, context: AnalysisContext, config: CppRaiiConfig
    ) -> list[Violation]:
        """Flag lines with ``new``/``delete``/``malloc``/``free`` that bypass RAII.

        Args:
            context: Analysis context with C++ source text.
            config: RAII detection configuration.

        Returns:
            list[Violation]: Violations detected for the analyzed context.
        """
        violations: list[Violation] = [
            self.build_violation(
                config,
                contains="RAII",
                location=Location(line=idx, column=1),
                suggestion="Prefer RAII wrappers instead of manual resource control.",
            )
            for idx, line in enumerate(context.code.splitlines(), start=1)
            if re.search(r"\bnew\b|\bdelete\b|malloc\(|free\(", line)
        ]
        return violations


class CppAutoDetector(ViolationDetector[CppAutoConfig], LocationHelperMixin):
    """Suggests ``auto`` type deduction where explicit ``std::`` types add verbosity.

    When the right-hand side of an assignment makes the type obvious
    (e.g., ``auto it = container.begin()``), spelling out the full type
    clutters code without adding information.  ``auto`` reduces visual noise,
    prevents narrowing-conversion surprises, and makes refactoring safer
    because the variable type tracks the expression automatically.

    Note:
        Lines already containing ``auto`` are skipped; only verbose ``std::``
        assignments are flagged.
    """

    @property
    def name(self) -> str:
        """Return ``'cpp-003'`` for registry wiring.

        Returns:
            str: Detector identifier for the auto-deduction rule.
        """
        return "cpp-003"

    def detect(
        self, context: AnalysisContext, config: CppAutoConfig
    ) -> list[Violation]:
        """Flag assignments with explicit ``std::`` types that could use ``auto``.

        Args:
            context: Analysis context with C++ source text.
            config: Auto-deduction detection configuration.

        Returns:
            list[Violation]: Violations detected for the analyzed context.
        """
        violations: list[Violation] = []
        for idx, line in enumerate(context.code.splitlines(), start=1):
            if "auto " in line:
                continue
            if "std::" in line and "=" in line:
                violations.append(
                    self.build_violation(
                        config,
                        contains="auto",
                        location=Location(line=idx, column=1),
                        suggestion="Use auto for obvious type deduction.",
                    )
                )
        return violations


class CppRangeForDetector(ViolationDetector[CppRangeForConfig], LocationHelperMixin):
    """Flags iterator-based ``for`` loops that should use range-based ``for``.

    C++11 range-based ``for`` loops (``for (auto& x : container)``) eliminate
    off-by-one errors, remove boilerplate ``.begin()``/``.end()`` calls, and
    express intent more clearly than manual iterator management.  They also
    compose better with structured bindings (C++17) for map iteration.
    """

    @property
    def name(self) -> str:
        """Return ``'cpp-005'`` for registry wiring.

        Returns:
            str: Detector identifier for the range-for rule.
        """
        return "cpp-005"

    def detect(
        self, context: AnalysisContext, config: CppRangeForConfig
    ) -> list[Violation]:
        """Flag ``for`` loops using explicit ``.begin()``/``.end()`` iterators.

        Args:
            context: Analysis context with C++ source text.
            config: Range-for detection configuration.

        Returns:
            list[Violation]: Violations detected for the analyzed context.
        """
        violations: list[Violation] = [
            self.build_violation(
                config,
                contains="range-for",
                location=Location(line=idx, column=1),
                suggestion="Prefer range-based for loops for iteration.",
            )
            for idx, line in enumerate(context.code.splitlines(), start=1)
            if "for" in line and (".begin()" in line or ".end()" in line)
        ]
        return violations


class CppManualAllocationDetector(
    ViolationDetector[CppManualAllocationConfig], LocationHelperMixin
):
    """Detects C-style heap allocation (``malloc``/``free``, ``new[]``/``delete[]``).

    Manual heap allocation requires exact pairing of allocate/deallocate calls
    and is inherently exception-unsafe.  Standard containers (``std::vector``,
    ``std::array``) and smart pointers manage memory automatically, provide
    bounds checking in debug builds, and integrate with move semantics for
    efficient transfers.  C-style allocation should be reserved for FFI
    boundaries or custom allocator implementations.
    """

    @property
    def name(self) -> str:
        """Return ``'cpp-006'`` for registry wiring.

        Returns:
            str: Detector identifier for the manual-allocation rule.
        """
        return "cpp-006"

    def detect(
        self, context: AnalysisContext, config: CppManualAllocationConfig
    ) -> list[Violation]:
        """Flag ``malloc``/``free`` and array ``new[]``/``delete[]`` usage.

        Args:
            context: Analysis context with C++ source text.
            config: Manual-allocation detection configuration.

        Returns:
            list[Violation]: Violations detected for the analyzed context.
        """
        violations: list[Violation] = [
            self.build_violation(
                config,
                contains="allocation",
                location=Location(line=idx, column=1),
                suggestion="Use standard containers or smart pointers.",
            )
            for idx, line in enumerate(context.code.splitlines(), start=1)
            if re.search(r"malloc\(|free\(|new\s+\w+\s*\[|delete\s*\[", line)
        ]
        return violations


class CppConstCorrectnessDetector(
    ViolationDetector[CppConstCorrectnessConfig], LocationHelperMixin
):
    """Flags non-const references where ``const`` qualification is appropriate.

    Const correctness is a compile-time contract that prevents accidental
    mutation.  Passing objects by non-const reference when the function does
    not modify them misleads readers, prevents the compiler from optimising,
    and can mask bugs where mutation was unintended.  Marking parameters
    and locals ``const`` wherever possible is a core C++ Core Guideline.
    """

    @property
    def name(self) -> str:
        """Return ``'cpp-007'`` for registry wiring.

        Returns:
            str: Detector identifier for the const-correctness rule.
        """
        return "cpp-007"

    def detect(
        self, context: AnalysisContext, config: CppConstCorrectnessConfig
    ) -> list[Violation]:
        """Flag reference parameters and variables missing ``const`` qualification.

        Args:
            context: Analysis context with C++ source text.
            config: Const-correctness detection configuration.

        Returns:
            list[Violation]: Violations detected for the analyzed context.
        """
        violations: list[Violation] = [
            self.build_violation(
                config,
                contains="const",
                location=Location(line=idx, column=1),
                suggestion="Mark references as const where applicable.",
            )
            for idx, line in enumerate(context.code.splitlines(), start=1)
            if "&" in line and "const" not in line
        ]
        return violations


class CppCStyleCastDetector(
    ViolationDetector[CppCStyleCastConfig], LocationHelperMixin
):
    """Detects C-style casts that should use ``static_cast``/``dynamic_cast``.

    C-style casts (``(int)x``) silently combine ``const_cast``,
    ``static_cast``, ``reinterpret_cast``, and even removing access
    protection in a single opaque syntax.  C++-style named casts make the
    programmer's intent explicit, are searchable in code, and trigger
    compiler diagnostics when the conversion is unsafe.
    """

    @property
    def name(self) -> str:
        """Return ``'cpp-008'`` for registry wiring.

        Returns:
            str: Detector identifier for the C-style-cast rule.
        """
        return "cpp-008"

    def detect(
        self, context: AnalysisContext, config: CppCStyleCastConfig
    ) -> list[Violation]:
        """Flag C-style cast syntax on lines not already using named casts.

        Args:
            context: Analysis context with C++ source text.
            config: C-style-cast detection configuration.

        Returns:
            list[Violation]: Violations detected for the analyzed context.
        """
        violations: list[Violation] = []
        for idx, line in enumerate(context.code.splitlines(), start=1):
            if "static_cast" in line or "dynamic_cast" in line:
                continue
            if re.search(r"\([A-Za-z_][A-Za-z0-9_:<>]*\)\s*\w", line):
                violations.append(
                    self.build_violation(
                        config,
                        contains="cast",
                        location=Location(line=idx, column=1),
                        suggestion="Use C++-style casts (static_cast, dynamic_cast).",
                    )
                )
        return violations


class CppRuleOfFiveDetector(
    ViolationDetector[CppRuleOfFiveConfig], LocationHelperMixin
):
    """Flags classes with destructors but missing copy/move special members.

    The Rule of Five states that if a class defines any of the destructor,
    copy constructor, copy assignment, move constructor, or move assignment,
    it should explicitly define or default all five.  Failing to do so risks
    shallow copies of owned resources, double-free on destruction, and
    silently deleted move operations that degrade performance.
    """

    @property
    def name(self) -> str:
        """Return ``'cpp-009'`` for registry wiring.

        Returns:
            str: Detector identifier for the Rule-of-Five rule.
        """
        return "cpp-009"

    def detect(
        self, context: AnalysisContext, config: CppRuleOfFiveConfig
    ) -> list[Violation]:
        """Flag classes with a destructor but no ``operator=`` definition.

        Args:
            context: Analysis context with C++ source text.
            config: Rule-of-Five detection configuration.

        Returns:
            list[Violation]: Violations detected for the analyzed context.
        """
        if re.search(r"~\w+\s*\(", context.code) and "operator=" not in context.code:
            return [
                self.build_violation(
                    config,
                    contains="rule of five",
                    suggestion="Define or default copy/move operations consistently.",
                )
            ]
        return []


class CppMoveDetector(ViolationDetector[CppMoveConfig], LocationHelperMixin):
    """Flags rvalue references (``&&``) without corresponding ``std::move``.

    Move semantics (C++11) enable zero-copy ownership transfer, but the
    benefit is only realised when ``std::move`` is used to cast lvalues to
    rvalue references.  Code that accepts ``&&`` parameters but copies
    instead of moving wastes the performance advantage and misleads readers
    about ownership intent.
    """

    @property
    def name(self) -> str:
        """Return ``'cpp-010'`` for registry wiring.

        Returns:
            str: Detector identifier for the move-semantics rule.
        """
        return "cpp-010"

    def detect(
        self, context: AnalysisContext, config: CppMoveConfig
    ) -> list[Violation]:
        """Flag code with ``&&`` references but no ``std::move`` usage.

        Args:
            context: Analysis context with C++ source text.
            config: Move-semantics detection configuration.

        Returns:
            list[Violation]: Violations detected for the analyzed context.
        """
        if "&&" in context.code and "std::move" not in context.code:
            return [
                self.build_violation(
                    config,
                    contains="std::move",
                    suggestion="Use std::move when transferring ownership.",
                )
            ]
        return []


class CppAvoidGlobalsDetector(
    ViolationDetector[CppAvoidGlobalsConfig], LocationHelperMixin
):
    """Detects mutable global and file-scope ``static``/``extern`` variables.

    Mutable globals introduce hidden coupling between translation units,
    create data races in multi-threaded programs, and make unit testing
    nearly impossible because state persists across test cases.  The C++
    Core Guidelines recommend scoped state managed through function
    parameters or dependency injection instead.

    Note:
        ``static_assert`` lines are excluded because they are compile-time
        checks, not mutable state.
    """

    @property
    def name(self) -> str:
        """Return ``'cpp-011'`` for registry wiring.

        Returns:
            str: Detector identifier for the avoid-globals rule.
        """
        return "cpp-011"

    def detect(
        self, context: AnalysisContext, config: CppAvoidGlobalsConfig
    ) -> list[Violation]:
        """Flag file-scope ``static`` or ``extern`` declarations (excluding ``static_assert``).

        Args:
            context: Analysis context with C++ source text.
            config: Global-avoidance detection configuration.

        Returns:
            list[Violation]: Violations detected for the analyzed context.
        """
        violations: list[Violation] = [
            self.build_violation(
                config,
                contains="global",
                location=Location(line=idx, column=1),
                suggestion="Avoid mutable globals; use scoped state.",
            )
            for idx, line in enumerate(context.code.splitlines(), start=1)
            if re.match(r"\s*(static|extern)\s+", line)
            and "static_assert" not in line
        ]
        return violations


class CppOverrideFinalDetector(
    ViolationDetector[CppOverrideFinalConfig], LocationHelperMixin
):
    """Flags ``virtual`` overrides missing the ``override`` or ``final`` specifier.

    Without ``override``, a typo in a virtual method signature silently
    creates a new function instead of overriding the base class version,
    a bug that is invisible until runtime.  ``override`` (C++11) turns this
    into a compile-time error.  ``final`` additionally prevents further
    overriding, enabling devirtualisation optimisations.
    """

    @property
    def name(self) -> str:
        """Return ``'cpp-012'`` for registry wiring.

        Returns:
            str: Detector identifier for the override/final rule.
        """
        return "cpp-012"

    def detect(
        self, context: AnalysisContext, config: CppOverrideFinalConfig
    ) -> list[Violation]:
        """Flag ``virtual`` methods lacking ``override`` or ``final`` specifiers.

        Args:
            context: Analysis context with C++ source text.
            config: Override/final detection configuration.

        Returns:
            list[Violation]: Violations detected for the analyzed context.
        """
        violations: list[Violation] = [
            self.build_violation(
                config,
                contains="override",
                location=Location(line=idx, column=1),
                suggestion="Add override/final to virtual overrides.",
            )
            for idx, line in enumerate(context.code.splitlines(), start=1)
            if "virtual" in line and "override" not in line and "final" not in line
        ]
        return violations


class CppOptionalDetector(ViolationDetector[CppOptionalConfig], LocationHelperMixin):
    """Suggests ``std::optional`` over nullable raw pointers for optional values.

    Using raw pointers to represent "maybe a value" conflates ownership,
    nullability, and optionality into a single ambiguous type.
    ``std::optional`` (C++17) is a value-semantic wrapper that makes the
    "no value" state explicit in the type system, prevents null-pointer
    dereferences at compile time (with ``value()``), and avoids heap
    allocation entirely.
    """

    @property
    def name(self) -> str:
        """Return ``'cpp-013'`` for registry wiring.

        Returns:
            str: Detector identifier for the std::optional rule.
        """
        return "cpp-013"

    def detect(
        self, context: AnalysisContext, config: CppOptionalConfig
    ) -> list[Violation]:
        """Flag pointer declarations where ``std::optional`` would express intent better.

        Args:
            context: Analysis context with C++ source text.
            config: Optional detection configuration.

        Returns:
            list[Violation]: Violations detected for the analyzed context.
        """
        if (
            re.search(r"\b\w+\s*\*\s*\w+", context.code)
            and "std::optional" not in context.code
        ):
            return [
                self.build_violation(
                    config,
                    contains="optional",
                    suggestion="Prefer std::optional over nullable pointers.",
                )
            ]
        return []


__all__ = [
    "CppAutoDetector",
    "CppAvoidGlobalsDetector",
    "CppCStyleCastDetector",
    "CppConstCorrectnessDetector",
    "CppManualAllocationDetector",
    "CppMoveDetector",
    "CppNullptrDetector",
    "CppOptionalDetector",
    "CppOverrideFinalDetector",
    "CppRaiiDetector",
    "CppRangeForDetector",
    "CppRuleOfFiveDetector",
    "CppSmartPointerDetector",
]
