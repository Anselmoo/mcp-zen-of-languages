"""Zen-rule detectors for C# code quality, .NET idiom, and type-safety checks.

Each detector implements the Strategy pattern as a ``ViolationDetector``
subclass, targeting a specific C# anti-pattern.  Modern C# (8–12) provides
nullable reference types, pattern matching, records, and async/await to
replace legacy patterns; these detectors enforce that adoption.

See Also:
    ``CSharpAnalyzer``: Template Method analyzer that orchestrates these detectors.
"""

from __future__ import annotations

import re

from mcp_zen_of_languages.analyzers.base import (
    AnalysisContext,
    LocationHelperMixin,
    ViolationDetector,
)
from mcp_zen_of_languages.languages.configs import (
    Cs008Config,
    CSharpAsyncAwaitConfig,
    CSharpCollectionExpressionConfig,
    CSharpDisposableConfig,
    CSharpExceptionHandlingConfig,
    CSharpExpressionBodiedConfig,
    CSharpLinqConfig,
    CSharpMagicNumberConfig,
    CSharpNullableConfig,
    CSharpPatternMatchingConfig,
    CSharpRecordConfig,
    CSharpStringInterpolationConfig,
    CSharpVarConfig,
)
from mcp_zen_of_languages.models import Location, Violation


class CSharpAsyncAwaitDetector(
    ViolationDetector[CSharpAsyncAwaitConfig], LocationHelperMixin
):
    """Flags synchronous blocking on tasks via ``.Result`` or ``.Wait()``.

    Calling ``.Result`` or ``.Wait()`` on a ``Task`` blocks the calling
    thread and can deadlock in UI or ASP.NET synchronization contexts where
    the continuation needs the same thread that is now blocked.  Using
    ``await`` instead yields the thread back to the pool, preventing
    deadlocks and keeping the application responsive under load.
    """

    @property
    def name(self) -> str:
        """Return ``'csharp_async_await'`` for registry wiring.

        Returns:
            str: Detector identifier for the async/await rule.
        """
        return "csharp_async_await"

    def detect(
        self, context: AnalysisContext, config: CSharpAsyncAwaitConfig
    ) -> list[Violation]:
        """Flag lines that block on tasks with ``.Result`` or ``.Wait()``.

        Args:
            context: Analysis context with C# source text.
            config: Async/await detection configuration.

        Returns:
            list[Violation]: Violations detected for the analyzed context.
        """
        violations: list[Violation] = []
        for idx, line in enumerate(context.code.splitlines(), start=1):
            if ".Result" in line or ".Wait()" in line:
                violations.append(
                    self.build_violation(
                        config,
                        contains="async",
                        location=Location(line=idx, column=1),
                        suggestion="Avoid blocking on tasks; use async/await.",
                    )
                )
        return violations


class CSharpStringInterpolationDetector(
    ViolationDetector[CSharpStringInterpolationConfig], LocationHelperMixin
):
    """Flags ``String.Format`` usage where string interpolation is cleaner.

    ``String.Format`` requires positional index placeholders (``{0}``, ``{1}``)
    that are error-prone and hard to read.  C# 6+ string interpolation
    (``$"Hello {name}"``) embeds expressions inline, is checked at compile
    time, and allocates fewer intermediate strings on the managed heap.
    """

    @property
    def name(self) -> str:
        """Return ``'csharp_string_interpolation'`` for registry wiring.

        Returns:
            str: Detector identifier for the string-interpolation rule.
        """
        return "csharp_string_interpolation"

    def detect(
        self, context: AnalysisContext, config: CSharpStringInterpolationConfig
    ) -> list[Violation]:
        """Flag calls to ``String.Format`` that should use interpolation.

        Args:
            context: Analysis context with C# source text.
            config: String-interpolation detection configuration.

        Returns:
            list[Violation]: Violations detected for the analyzed context.
        """
        violations: list[Violation] = []
        for idx, line in enumerate(context.code.splitlines(), start=1):
            if "String.Format" in line:
                violations.append(
                    self.build_violation(
                        config,
                        contains="String.Format",
                        location=Location(line=idx, column=1),
                        suggestion=(
                            'Use string interpolation ($"...") instead of String.Format.'
                        ),
                    )
                )
        return violations


class CSharpNullableDetector(
    ViolationDetector[CSharpNullableConfig], LocationHelperMixin
):
    """Detects files missing ``#nullable enable`` for nullable reference types.

    C# 8 nullable reference types turn ``NullReferenceException`` from a
    runtime surprise into a compile-time warning.  Without ``#nullable enable``,
    the compiler cannot distinguish nullable from non-nullable references,
    leaving the most common .NET exception class unguarded and forcing
    defensive null checks throughout the codebase.
    """

    @property
    def name(self) -> str:
        """Return ``'cs-001'`` for registry wiring.

        Returns:
            str: Detector identifier for the nullable-reference-types rule.
        """
        return "cs-001"

    def detect(
        self, context: AnalysisContext, config: CSharpNullableConfig
    ) -> list[Violation]:
        """Flag files that do not contain a ``#nullable enable`` directive.

        Args:
            context: Analysis context with C# source text.
            config: Nullable detection configuration.

        Returns:
            list[Violation]: Violations detected for the analyzed context.
        """
        if "#nullable enable" not in context.code:
            return [
                self.build_violation(
                    config,
                    contains="nullable",
                    suggestion="Enable nullable reference types with #nullable enable.",
                )
            ]
        return []


class CSharpExpressionBodiedDetector(
    ViolationDetector[CSharpExpressionBodiedConfig], LocationHelperMixin
):
    """Flags verbose property getters that should use expression-bodied members.

    Expression-bodied members (``=> expression;``) introduced in C# 6
    eliminate brace-and-return boilerplate for single-expression getters
    and methods, reducing visual noise and making the class surface area
    immediately scannable.
    """

    @property
    def name(self) -> str:
        """Return ``'cs-002'`` for registry wiring.

        Returns:
            str: Detector identifier for the expression-bodied-member rule.
        """
        return "cs-002"

    def detect(
        self, context: AnalysisContext, config: CSharpExpressionBodiedConfig
    ) -> list[Violation]:
        """Flag ``get { return ... }`` patterns that could be expression-bodied.

        Args:
            context: Analysis context with C# source text.
            config: Expression-bodied detection configuration.

        Returns:
            list[Violation]: Violations detected for the analyzed context.
        """
        for idx, line in enumerate(context.code.splitlines(), start=1):
            if re.search(r"\bget\s*\{\s*return", line):
                return [
                    self.build_violation(
                        config,
                        contains="expression-bodied",
                        location=Location(line=idx, column=1),
                        suggestion="Use expression-bodied members for simple getters.",
                    )
                ]
        return []


class CSharpVarDetector(ViolationDetector[CSharpVarConfig], LocationHelperMixin):
    """Flags explicit primitive type declarations where ``var`` improves readability.

    When the right-hand side of an assignment makes the type obvious
    (e.g., ``new List<string>()``), repeating ``List<string>`` on the left
    adds redundancy without clarity.  ``var`` reduces line length and keeps
    the focus on the variable name and its initial value, following the
    .NET coding convention for obvious-type assignments.
    """

    @property
    def name(self) -> str:
        """Return ``'cs-003'`` for registry wiring.

        Returns:
            str: Detector identifier for the var-usage rule.
        """
        return "cs-003"

    def detect(
        self, context: AnalysisContext, config: CSharpVarConfig
    ) -> list[Violation]:
        """Flag assignments with explicit primitive types that could use ``var``.

        Args:
            context: Analysis context with C# source text.
            config: Var-usage detection configuration.

        Returns:
            list[Violation]: Violations detected for the analyzed context.
        """
        violations: list[Violation] = []
        pattern = re.compile(r"\b(int|string|bool|double|float|decimal)\s+\w+\s*=")
        for idx, line in enumerate(context.code.splitlines(), start=1):
            if pattern.search(line):
                violations.append(
                    self.build_violation(
                        config,
                        contains="var",
                        location=Location(line=idx, column=1),
                        suggestion="Use var when the type is obvious.",
                    )
                )
        return violations


class CSharpPatternMatchingDetector(
    ViolationDetector[CSharpPatternMatchingConfig], LocationHelperMixin
):
    """Suggests pattern matching (``is``/``switch`` expressions) over explicit casts.

    C# 7+ pattern matching combines type testing and variable declaration
    in a single expression, eliminating the need for separate ``is`` checks
    followed by casts.  This reduces boxing for value types and prevents
    ``InvalidCastException`` by making the type check and extraction atomic.
    """

    @property
    def name(self) -> str:
        """Return ``'cs-005'`` for registry wiring.

        Returns:
            str: Detector identifier for the pattern-matching rule.
        """
        return "cs-005"

    def detect(
        self, context: AnalysisContext, config: CSharpPatternMatchingConfig
    ) -> list[Violation]:
        """Flag ``is`` type checks that could leverage pattern matching.

        Args:
            context: Analysis context with C# source text.
            config: Pattern-matching detection configuration.

        Returns:
            list[Violation]: Violations detected for the analyzed context.
        """
        for idx, line in enumerate(context.code.splitlines(), start=1):
            if "is " in line and "switch" not in line:
                return [
                    self.build_violation(
                        config,
                        contains="pattern",
                        location=Location(line=idx, column=1),
                        suggestion="Use pattern matching (is/expression) instead of casts.",
                    )
                ]
        return []


class CSharpCollectionExpressionDetector(
    ViolationDetector[CSharpCollectionExpressionConfig], LocationHelperMixin
):
    """Flags verbose ``new List`` or ``new T[]`` where collection expressions work.

    C# 12 collection expressions (``[a, b, c]``) provide a concise,
    target-typed syntax for initialising lists, arrays, and spans.  They
    reduce boilerplate, improve readability, and allow the compiler to
    choose the optimal backing storage based on the target type.
    """

    @property
    def name(self) -> str:
        """Return ``'cs-007'`` for registry wiring.

        Returns:
            str: Detector identifier for the collection-expression rule.
        """
        return "cs-007"

    def detect(
        self, context: AnalysisContext, config: CSharpCollectionExpressionConfig
    ) -> list[Violation]:
        """Flag ``new List`` or ``new T[]`` initialisations that could use ``[]``.

        Args:
            context: Analysis context with C# source text.
            config: Collection-expression detection configuration.

        Returns:
            list[Violation]: Violations detected for the analyzed context.
        """
        for idx, line in enumerate(context.code.splitlines(), start=1):
            if re.search(r"new\s+List|new\s+\w+\[\]", line):
                return [
                    self.build_violation(
                        config,
                        contains="collection",
                        location=Location(line=idx, column=1),
                        suggestion="Prefer collection expressions ([]) for simple lists.",
                    )
                ]
        return []


class CSharpNamingConventionDetector(
    ViolationDetector[Cs008Config], LocationHelperMixin
):
    """Enforces .NET naming conventions for public and private members.

    The .NET Framework Design Guidelines prescribe PascalCase for public
    members and camelCase (optionally ``_``-prefixed) for private fields.
    Consistent naming enables developers to infer visibility from the
    identifier alone, which is critical in large codebases where navigating
    by convention replaces navigating by access modifiers.
    """

    @property
    def name(self) -> str:
        """Return ``'cs-008'`` for registry wiring.

        Returns:
            str: Detector identifier for the naming-convention rule.
        """
        return "cs-008"

    def detect(self, context: AnalysisContext, config: Cs008Config) -> list[Violation]:
        """Flag public/private members that violate configured naming styles.

        Args:
            context: Analysis context with C# source text.
            config: Contains ``public_naming`` and ``private_naming`` style rules.

        Returns:
            list[Violation]: Violations detected for the analyzed context.
        """

        def matches_style(name: str, style: str) -> bool:
            """Check whether a symbol name conforms to the given casing style.

            Args:
                name: Symbol name to validate (e.g., ``myField``, ``MyProperty``).
                style: Casing convention to match—``PascalCase`` or ``camelCase``.

            Returns:
                bool: ``True`` when the name matches the expected casing style.
            """
            style_lower = style.lower()
            if "pascal" in style_lower:
                return bool(re.match(r"^[A-Z][A-Za-z0-9]*$", name))
            if "camel" in style_lower:
                return bool(re.match(r"^_?[a-z][A-Za-z0-9]*$", name))
            return True

        for idx, line in enumerate(context.code.splitlines(), start=1):
            match = re.search(r"\bpublic\s+\w[\w<>,\s]*\s+([A-Za-z_]\w*)", line)
            if match and config.public_naming:
                name = match.group(1)
                if not matches_style(name, config.public_naming):
                    return [
                        self.build_violation(
                            config,
                            contains=name,
                            location=Location(line=idx, column=match.start(1) + 1),
                            suggestion=f"Use {config.public_naming} for public members.",
                        )
                    ]
            match = re.search(r"\bprivate\s+\w[\w<>,\s]*\s+([A-Za-z_]\w*)", line)
            if match and config.private_naming:
                name = match.group(1)
                if not matches_style(name, config.private_naming):
                    return [
                        self.build_violation(
                            config,
                            contains=name,
                            location=Location(line=idx, column=match.start(1) + 1),
                            suggestion=f"Use {config.private_naming} for private members.",
                        )
                    ]
        return []


class CSharpDisposableDetector(
    ViolationDetector[CSharpDisposableConfig], LocationHelperMixin
):
    """Detects ``IDisposable`` resources not wrapped in ``using`` statements.

    .NET's deterministic disposal pattern requires ``IDisposable`` objects
    (database connections, file handles, HTTP clients) to be wrapped in
    ``using`` blocks or declarations.  Without ``using``, the ``Dispose()``
    call depends on the garbage collector's finaliser queue, leading to
    resource exhaustion under load—connection pool starvation is the most
    common symptom.
    """

    @property
    def name(self) -> str:
        """Return ``'cs-009'`` for registry wiring.

        Returns:
            str: Detector identifier for the disposable-resource rule.
        """
        return "cs-009"

    def detect(
        self, context: AnalysisContext, config: CSharpDisposableConfig
    ) -> list[Violation]:
        """Flag code referencing ``IDisposable``/``Dispose()`` without ``using``.

        Args:
            context: Analysis context with C# source text.
            config: Disposable detection configuration.

        Returns:
            list[Violation]: Violations detected for the analyzed context.
        """
        code = context.code
        if ("IDisposable" in code or "Dispose()" in code) and "using" not in code:
            return [
                self.build_violation(
                    config,
                    contains="using",
                    suggestion="Wrap disposable resources in using statements.",
                )
            ]
        return []


class CSharpMagicNumberDetector(
    ViolationDetector[CSharpMagicNumberConfig], LocationHelperMixin
):
    """Flags hard-coded numeric literals (magic numbers) in business logic.

    Magic numbers embedded in code hide domain intent and make maintenance
    hazardous—changing a threshold means finding every occurrence of the
    same literal across the codebase.  Named constants (``const`` or
    ``static readonly``) provide self-documenting, single-source-of-truth
    values that the JIT compiler can inline just as efficiently.
    """

    @property
    def name(self) -> str:
        """Return ``'cs-010'`` for registry wiring.

        Returns:
            str: Detector identifier for the magic-number rule.
        """
        return "cs-010"

    def detect(
        self, context: AnalysisContext, config: CSharpMagicNumberConfig
    ) -> list[Violation]:
        """Flag multi-digit numeric literals that should be named constants.

        Args:
            context: Analysis context with C# source text.
            config: Magic-number detection configuration.

        Returns:
            list[Violation]: Violations detected for the analyzed context.
        """
        if re.search(r"\b\d{2,}\b", context.code):
            return [
                self.build_violation(
                    config,
                    contains="magic number",
                    suggestion="Replace magic numbers with named constants.",
                )
            ]
        return []


class CSharpLinqDetector(ViolationDetector[CSharpLinqConfig], LocationHelperMixin):
    """Suggests LINQ methods (``Select``/``Where``) over manual ``foreach`` loops.

    LINQ provides a declarative, composable query syntax that expresses
    *what* to compute rather than *how* to iterate.  Replacing imperative
    ``foreach`` accumulation with ``Select``, ``Where``, and ``Aggregate``
    reduces mutable state, enables deferred execution, and aligns with
    the functional programming features built into the .NET runtime.
    """

    @property
    def name(self) -> str:
        """Return ``'cs-011'`` for registry wiring.

        Returns:
            str: Detector identifier for the LINQ-preference rule.
        """
        return "cs-011"

    def detect(
        self, context: AnalysisContext, config: CSharpLinqConfig
    ) -> list[Violation]:
        """Flag ``foreach`` loops that lack corresponding LINQ method calls.

        Args:
            context: Analysis context with C# source text.
            config: LINQ detection configuration.

        Returns:
            list[Violation]: Violations detected for the analyzed context.
        """
        code = context.code
        if "foreach" in code and ".Select" not in code and ".Where" not in code:
            return [
                self.build_violation(
                    config,
                    contains="LINQ",
                    suggestion="Use LINQ methods like Select/Where for collections.",
                )
            ]
        return []


class CSharpExceptionHandlingDetector(
    ViolationDetector[CSharpExceptionHandlingConfig], LocationHelperMixin
):
    """Flags overly broad ``catch (Exception)`` or empty ``catch`` blocks.

    Catching the base ``Exception`` type swallows ``OutOfMemoryException``,
    ``StackOverflowException``, and other critical failures that should
    crash the process.  Empty catch blocks silently discard errors, making
    production debugging impossible.  Best practice is to catch the most
    specific exception type and log or re-throw with context.
    """

    @property
    def name(self) -> str:
        """Return ``'cs-012'`` for registry wiring.

        Returns:
            str: Detector identifier for the exception-handling rule.
        """
        return "cs-012"

    def detect(
        self, context: AnalysisContext, config: CSharpExceptionHandlingConfig
    ) -> list[Violation]:
        """Flag ``catch (Exception)`` and bare ``catch`` blocks.

        Args:
            context: Analysis context with C# source text.
            config: Exception-handling detection configuration.

        Returns:
            list[Violation]: Violations detected for the analyzed context.
        """
        if (
            re.search(r"catch\s*\(\s*Exception", context.code)
            or "catch {" in context.code
        ):
            return [
                self.build_violation(
                    config,
                    contains="catch",
                    suggestion="Catch specific exceptions and avoid empty handlers.",
                )
            ]
        return []


class CSharpRecordDetector(ViolationDetector[CSharpRecordConfig], LocationHelperMixin):
    """Suggests ``record`` types for immutable data-transfer objects (DTOs).

    C# 9 ``record`` types provide value-based equality, immutability via
    ``init``-only setters, built-in ``ToString()``, and ``with``-expression
    cloning—all of which must be hand-written for plain ``class`` DTOs.
    Using ``class`` with ``get; set;`` properties for data carriers wastes
    boilerplate and invites accidental mutation of shared state.
    """

    @property
    def name(self) -> str:
        """Return ``'cs-013'`` for registry wiring.

        Returns:
            str: Detector identifier for the record-type rule.
        """
        return "cs-013"

    def detect(
        self, context: AnalysisContext, config: CSharpRecordConfig
    ) -> list[Violation]:
        """Flag ``class`` definitions with ``get; set;`` that could be records.

        Args:
            context: Analysis context with C# source text.
            config: Record-type detection configuration.

        Returns:
            list[Violation]: Violations detected for the analyzed context.
        """
        code = context.code
        if "class " in code and "record " not in code and "get; set;" in code:
            return [
                self.build_violation(
                    config,
                    contains="record",
                    suggestion="Prefer records for immutable DTOs.",
                )
            ]
        return []


__all__ = [
    "CSharpAsyncAwaitDetector",
    "CSharpCollectionExpressionDetector",
    "CSharpDisposableDetector",
    "CSharpExceptionHandlingDetector",
    "CSharpExpressionBodiedDetector",
    "CSharpLinqDetector",
    "CSharpMagicNumberDetector",
    "CSharpNamingConventionDetector",
    "CSharpNullableDetector",
    "CSharpPatternMatchingDetector",
    "CSharpRecordDetector",
    "CSharpStringInterpolationDetector",
    "CSharpVarDetector",
]
