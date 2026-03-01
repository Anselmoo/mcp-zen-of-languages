"""Rule detectors for go code quality and architecture checks."""

from __future__ import annotations

import re

from typing import TYPE_CHECKING

from mcp_zen_of_languages.analyzers.base import AnalysisContext
from mcp_zen_of_languages.analyzers.base import ViolationDetector
from mcp_zen_of_languages.languages.configs import GoBenchmarkConfig
from mcp_zen_of_languages.languages.configs import GoConcurrencyCallerConfig
from mcp_zen_of_languages.languages.configs import GoContextUsageConfig
from mcp_zen_of_languages.languages.configs import GoDeferUsageConfig
from mcp_zen_of_languages.languages.configs import GoEarlyReturnConfig
from mcp_zen_of_languages.languages.configs import GoErrorHandlingConfig
from mcp_zen_of_languages.languages.configs import GoGoroutineLeakConfig
from mcp_zen_of_languages.languages.configs import GoInitUsageConfig
from mcp_zen_of_languages.languages.configs import GoInterfacePointerConfig
from mcp_zen_of_languages.languages.configs import GoInterfaceReturnConfig
from mcp_zen_of_languages.languages.configs import GoInterfaceSizeConfig
from mcp_zen_of_languages.languages.configs import GoMaintainabilityConfig
from mcp_zen_of_languages.languages.configs import GoModerationConfig
from mcp_zen_of_languages.languages.configs import GoNamingConventionConfig
from mcp_zen_of_languages.languages.configs import GoPackageNamingConfig
from mcp_zen_of_languages.languages.configs import GoPackageStateConfig
from mcp_zen_of_languages.languages.configs import GoSimplicityConfig
from mcp_zen_of_languages.languages.configs import GoSinglePurposePackageConfig
from mcp_zen_of_languages.languages.configs import GoTestPresenceConfig
from mcp_zen_of_languages.languages.configs import GoZeroValueConfig


if TYPE_CHECKING:
    from mcp_zen_of_languages.models import Violation


class GoErrorHandlingDetector(ViolationDetector[GoErrorHandlingConfig]):
    """Flags ignored errors, unchecked ``err`` variables, and ``panic()`` calls in Go code.

    Go's explicit ``if err != nil`` pattern is the language's primary
    safety mechanism — there are no exceptions.  Assigning errors to
    ``_``, calling ``panic()`` in library code, or leaving ``err``
    unchecked silently discards failure information.  This detector uses
    regex to count all three anti-patterns and flags files whose
    combined total exceeds the configured threshold.
    """

    @property
    def name(self) -> str:
        """Return the detector identifier used by registry wiring.

        Returns:
            str: Identifier string consumed by callers.
        """
        return "go_error_handling"

    def detect(
        self,
        context: AnalysisContext,
        config: GoErrorHandlingConfig,
    ) -> list[Violation]:
        """Detect violations for the current analysis context.

        Args:
            context (AnalysisContext): Analysis context containing source text and intermediate metrics.
            config (GoErrorHandlingConfig): Typed detector or analyzer configuration that controls thresholds.

        Returns:
            list[Violation]: Violations detected for the analyzed context.
        """
        violations: list[Violation] = []
        code = context.code
        counts = {
            "panic": len(re.findall(r"\bpanic\s*\(", code)),
            "ignored": len(re.findall(r"\b_,\s*err\s*:=", code)),
            "unchecked": len(re.findall(r"\berr\s*:=", code)),
        }
        total = counts["panic"] + counts["ignored"] + counts["unchecked"]
        if total > config.max_ignored_errors:
            violations.append(
                self.build_violation(
                    config,
                    contains="error",
                    index=0,
                    suggestion=(
                        "Check errors explicitly; avoid panic or ignored errors in "
                        "libraries."
                    ),
                ),
            )
        return violations


class GoInterfaceSizeDetector(ViolationDetector[GoInterfaceSizeConfig]):
    """Detects oversized interfaces that violate Go's preference for small, composable contracts.

    Go proverb: "The bigger the interface, the weaker the abstraction."
    Interfaces with many methods are hard to implement, hard to mock in
    tests, and tightly couple consumers to a single implementation.
    This detector parses interface bodies via regex, counts non-comment
    method lines, and flags interfaces that exceed the configured
    maximum.
    """

    @property
    def name(self) -> str:
        """Return the detector identifier used by registry wiring.

        Returns:
            str: Identifier string consumed by callers.
        """
        return "go_interface_size"

    def detect(
        self,
        context: AnalysisContext,
        config: GoInterfaceSizeConfig,
    ) -> list[Violation]:
        """Detect violations for the current analysis context.

        Args:
            context (AnalysisContext): Analysis context containing source text and intermediate metrics.
            config (GoInterfaceSizeConfig): Typed detector or analyzer configuration that controls thresholds.

        Returns:
            list[Violation]: Violations detected for the analyzed context.
        """
        violations: list[Violation] = []
        if not re.search(r"\binterface\b", context.code):
            return violations
        max_methods = config.max_interface_methods
        for match in re.finditer(
            r"type\s+(\w+)\s+interface\s*\{([\s\S]*?)\}",
            context.code,
        ):
            body = match.group(2)
            methods = [
                line
                for line in body.splitlines()
                if line.strip() and not line.strip().startswith("//")
            ]
            if len(methods) > max_methods:
                violations.append(
                    self.build_violation(
                        config,
                        contains="interfaces",
                        index=0,
                        suggestion="Split large interfaces into smaller ones.",
                    ),
                )
        return violations


class GoContextUsageDetector(ViolationDetector[GoContextUsageConfig]):
    """Flags code that lacks ``context.Context`` for cancellation and deadline propagation.

    In Go, ``context.Context`` is the standard mechanism for
    cancellation, timeouts, and request-scoped values across goroutine
    boundaries.  Long-running or network-bound operations without a
    context parameter cannot be cancelled gracefully.  This detector
    checks whether the source mentions ``context.Context`` at all and
    flags its absence when required by configuration.
    """

    @property
    def name(self) -> str:
        """Return the detector identifier used by registry wiring.

        Returns:
            str: Identifier string consumed by callers.
        """
        return "go_context_usage"

    def detect(
        self,
        context: AnalysisContext,
        config: GoContextUsageConfig,
    ) -> list[Violation]:
        """Detect violations for the current analysis context.

        Args:
            context (AnalysisContext): Analysis context containing source text and intermediate metrics.
            config (GoContextUsageConfig): Typed detector or analyzer configuration that controls thresholds.

        Returns:
            list[Violation]: Violations detected for the analyzed context.
        """
        violations: list[Violation] = []
        if config.require_context and "context.Context" not in context.code:
            violations.append(
                self.build_violation(
                    config,
                    contains="context",
                    index=0,
                    suggestion=(
                        "Pass context.Context to long-running or cancellable "
                        "operations."
                    ),
                ),
            )
        return violations


class GoDeferUsageDetector(ViolationDetector[GoDeferUsageConfig]):
    """Detects ``defer`` misuse inside loops and missing ``defer`` for resource cleanup.

    ``defer`` in Go schedules a call to run when the enclosing function
    returns, making it ideal for releasing resources like file handles
    and locks.  However, ``defer`` inside a loop defers until function
    exit — not loop iteration — causing resource leaks.  This detector
    also scans for ``.Close()`` and ``.Unlock()`` calls that are not
    deferred, flagging forgotten cleanup.
    """

    @property
    def name(self) -> str:
        """Return the detector identifier used by registry wiring.

        Returns:
            str: Identifier string consumed by callers.
        """
        return "go_defer_usage"

    def detect(
        self,
        context: AnalysisContext,
        config: GoDeferUsageConfig,
    ) -> list[Violation]:
        """Detect violations for the current analysis context.

        Args:
            context (AnalysisContext): Analysis context containing source text and intermediate metrics.
            config (GoDeferUsageConfig): Typed detector or analyzer configuration that controls thresholds.

        Returns:
            list[Violation]: Violations detected for the analyzed context.
        """
        violations: list[Violation] = []
        code = context.code
        if config.detect_defer_in_loop and re.search(
            r"for\s+.+\{[\s\S]*?\bdefer\b",
            code,
        ):
            violations.append(
                self.build_violation(
                    config,
                    contains="defer",
                    index=0,
                    suggestion=(
                        "Avoid defers inside tight loops; defer outside or manage "
                        "resources explicitly."
                    ),
                ),
            )
        if not config.detect_missing_defer:
            return violations
        lines = code.splitlines()
        close_pattern = re.compile(r"\b(\w+(?:\.\w+)*)\.(Close|Unlock)\s*\(\)")
        for idx, line in enumerate(lines, start=1):
            match = close_pattern.search(line)
            if not match:
                continue
            if "defer" in line:
                continue
            prev_line = lines[idx - 2] if idx > 1 else ""
            if "defer" in prev_line:
                continue
            method = match[2]
            contains = "Unlock" if method == "Unlock" else "Close"
            violations.append(
                self.build_violation(
                    config,
                    contains=contains,
                    index=0,
                    suggestion="Defer cleanup immediately after acquiring the resource.",
                ),
            )
        return violations


class GoNamingConventionDetector(ViolationDetector[GoNamingConventionConfig]):
    """Flags overly long variable names that violate Go's brevity conventions.

    Go favors short, context-driven names — ``r`` for a reader, ``ctx``
    for a context — because the language's small function scopes make
    long names redundant.  This detector uses a regex to find ``var``
    declarations with identifiers exceeding 24 characters and suggests
    shorter, more idiomatic alternatives.
    """

    @property
    def name(self) -> str:
        """Return the detector identifier used by registry wiring.

        Returns:
            str: Identifier string consumed by callers.
        """
        return "go_naming_convention"

    def detect(
        self,
        context: AnalysisContext,
        config: GoNamingConventionConfig,
    ) -> list[Violation]:
        """Detect violations for the current analysis context.

        Args:
            context (AnalysisContext): Analysis context containing source text and intermediate metrics.
            config (GoNamingConventionConfig): Typed detector or analyzer configuration that controls thresholds.

        Returns:
            list[Violation]: Violations detected for the analyzed context.
        """
        violations: list[Violation] = []
        if not config.detect_long_names:
            return violations
        for _ in re.finditer(r"\bvar\s+(\w{25,})\b", context.code):
            violations.append(
                self.build_violation(
                    config,
                    contains="variable names",
                    index=0,
                    suggestion="Use short, contextual variable names in local scopes.",
                ),
            )
            break
        return violations


class GoInterfaceReturnDetector(ViolationDetector[GoInterfaceReturnConfig]):
    """Flags functions that return interface types instead of concrete structs.

    Go idiom: "Accept interfaces, return structs."  Returning an
    interface hides the concrete type from callers, preventing them
    from accessing type-specific methods or embedding the struct.  It
    also makes it harder to discover what a function actually produces.
    This detector uses a regex to find function signatures that return
    ``interface{`` and suggests returning concrete types instead.
    """

    @property
    def name(self) -> str:
        """Return the detector identifier used by registry wiring.

        Returns:
            str: Identifier string consumed by callers.
        """
        return "go_interface_return"

    def detect(
        self,
        context: AnalysisContext,
        config: GoInterfaceReturnConfig,
    ) -> list[Violation]:
        """Detect violations for the current analysis context.

        Args:
            context (AnalysisContext): Analysis context containing source text and intermediate metrics.
            config (GoInterfaceReturnConfig): Typed detector or analyzer configuration that controls thresholds.

        Returns:
            list[Violation]: Violations detected for the analyzed context.
        """
        if re.search(r"func\s+\w+\([^)]*\)\s+interface\s*\{", context.code):
            return [
                self.build_violation(
                    config,
                    contains="interface",
                    suggestion="Accept interfaces, return concrete structs.",
                ),
            ]
        return []


class GoZeroValueDetector(ViolationDetector[GoZeroValueConfig]):
    """Flags ``New*`` constructor functions where making the zero value usable would be simpler.

    Go's zero-value philosophy means a ``var x MyStruct`` should be
    ready to use without initialization.  When a package exports
    ``NewFoo()`` constructors, callers must remember to call them,
    and forgetting leads to nil-pointer panics.  This detector scans
    for ``func New*`` patterns and suggests designing structs so their
    zero values are valid.
    """

    @property
    def name(self) -> str:
        """Return the detector identifier used by registry wiring.

        Returns:
            str: Identifier string consumed by callers.
        """
        return "go_zero_value"

    def detect(
        self,
        context: AnalysisContext,
        config: GoZeroValueConfig,
    ) -> list[Violation]:
        """Detect violations for the current analysis context.

        Args:
            context (AnalysisContext): Analysis context containing source text and intermediate metrics.
            config (GoZeroValueConfig): Typed detector or analyzer configuration that controls thresholds.

        Returns:
            list[Violation]: Violations detected for the analyzed context.
        """
        if re.search(r"\bfunc\s+New\w+\b", context.code):
            return [
                self.build_violation(
                    config,
                    contains="New",
                    suggestion="Prefer making zero values usable without constructors.",
                ),
            ]
        return []


class GoInterfacePointerDetector(ViolationDetector[GoInterfacePointerConfig]):
    """Detects pointers to interfaces, which are almost always a mistake in Go.

    Interfaces in Go are already reference-like values (a type-pointer
    plus a data-pointer), so ``*MyInterface`` adds an unnecessary level
    of indirection that confuses the type system and prevents
    interface satisfaction.  This detector scans for ``*<name>Interface``
    and ``*interface{`` patterns via regex.
    """

    @property
    def name(self) -> str:
        """Return the detector identifier used by registry wiring.

        Returns:
            str: Identifier string consumed by callers.
        """
        return "go_interface_pointer"

    def detect(
        self,
        context: AnalysisContext,
        config: GoInterfacePointerConfig,
    ) -> list[Violation]:
        """Detect violations for the current analysis context.

        Args:
            context (AnalysisContext): Analysis context containing source text and intermediate metrics.
            config (GoInterfacePointerConfig): Typed detector or analyzer configuration that controls thresholds.

        Returns:
            list[Violation]: Violations detected for the analyzed context.
        """
        if re.search(r"\*\w+Interface\b|\*interface\s*\{", context.code):
            return [
                self.build_violation(
                    config,
                    contains="*interface",
                    suggestion="Avoid pointers to interfaces.",
                ),
            ]
        return []


class GoGoroutineLeakDetector(ViolationDetector[GoGoroutineLeakConfig]):
    """Flags goroutines launched without cancellation support and unclosed channels.

    Goroutine leaks are among the most insidious Go bugs: a goroutine
    blocked on a channel or network call with no way to cancel
    accumulates silently until the process runs out of memory.  This
    detector checks for ``go func`` invocations that lack a
    ``context.Context`` cancellation path and ``make(chan ...)``
    allocations without a corresponding ``close()`` call.
    """

    @property
    def name(self) -> str:
        """Return the detector identifier used by registry wiring.

        Returns:
            str: Identifier string consumed by callers.
        """
        return "go_goroutine_leaks"

    def detect(
        self,
        context: AnalysisContext,
        config: GoGoroutineLeakConfig,
    ) -> list[Violation]:
        """Detect violations for the current analysis context.

        Args:
            context (AnalysisContext): Analysis context containing source text and intermediate metrics.
            config (GoGoroutineLeakConfig): Typed detector or analyzer configuration that controls thresholds.

        Returns:
            list[Violation]: Violations detected for the analyzed context.
        """
        code = context.code
        violations: list[Violation] = []
        if "go func" in code and "context.Context" not in code:
            violations.append(
                self.build_violation(
                    config,
                    contains="goroutine",
                    suggestion="Ensure goroutines can terminate (context/cancel).",
                ),
            )
        if re.search(r"make\s*\(\s*chan\b", code) and "close(" not in code:
            violations.append(
                self.build_violation(
                    config,
                    contains="close",
                    suggestion="Close channels to signal completion and avoid leaks.",
                ),
            )
        return violations


class GoPackageNamingDetector(ViolationDetector[GoPackageNamingConfig]):
    """Flags package names that violate Go's singular, lowercase naming convention.

    The Go specification and community style guides require package
    names to be short, lowercase, singular nouns — no underscores, no
    ``mixedCaps``, no plurals.  A package named ``utils`` or
    ``string_helpers`` signals poor cohesion.  This detector extracts
    the ``package`` declaration and checks for trailing ``s`` or
    embedded underscores.
    """

    @property
    def name(self) -> str:
        """Return the detector identifier used by registry wiring.

        Returns:
            str: Identifier string consumed by callers.
        """
        return "go_package_naming"

    def detect(
        self,
        context: AnalysisContext,
        config: GoPackageNamingConfig,
    ) -> list[Violation]:
        """Detect violations for the current analysis context.

        Args:
            context (AnalysisContext): Analysis context containing source text and intermediate metrics.
            config (GoPackageNamingConfig): Typed detector or analyzer configuration that controls thresholds.

        Returns:
            list[Violation]: Violations detected for the analyzed context.
        """
        if match := re.search(r"^\s*package\s+(\w+)", context.code, re.MULTILINE):
            name = match[1]
            if name.endswith("s") or "_" in name:
                return [
                    self.build_violation(
                        config,
                        contains=name,
                        suggestion="Use singular, lowercase package names.",
                    ),
                ]
        return []


class GoPackageStateDetector(ViolationDetector[GoPackageStateConfig]):
    """Flags mutable package-level variables that introduce hidden global state.

    Package-level ``var`` declarations are effectively globals: they
    create implicit coupling between functions, make testing difficult,
    and introduce data races in concurrent programs.  Go encourages
    passing dependencies explicitly via function arguments or struct
    fields.  This detector scans for top-level ``var`` declarations
    and flags their presence.
    """

    @property
    def name(self) -> str:
        """Return the detector identifier used by registry wiring.

        Returns:
            str: Identifier string consumed by callers.
        """
        return "go_package_state"

    def detect(
        self,
        context: AnalysisContext,
        config: GoPackageStateConfig,
    ) -> list[Violation]:
        """Detect violations for the current analysis context.

        Args:
            context (AnalysisContext): Analysis context containing source text and intermediate metrics.
            config (GoPackageStateConfig): Typed detector or analyzer configuration that controls thresholds.

        Returns:
            list[Violation]: Violations detected for the analyzed context.
        """
        if re.search(r"^\s*var\s+\w+", context.code, re.MULTILINE):
            return [
                self.build_violation(
                    config,
                    contains="package state",
                    suggestion="Avoid mutable package-level state.",
                ),
            ]
        return []


class GoInitUsageDetector(ViolationDetector[GoInitUsageConfig]):
    """Flags ``func init()`` usage that hides initialization logic from callers.

    Go's ``init()`` functions run automatically at package load time,
    creating invisible side effects that make testing and dependency
    ordering unpredictable.  Explicit initialization via exported
    functions gives callers control over when and how setup happens.
    This detector simply checks for the presence of ``func init(``
    in the source.
    """

    @property
    def name(self) -> str:
        """Return the detector identifier used by registry wiring.

        Returns:
            str: Identifier string consumed by callers.
        """
        return "go_init_usage"

    def detect(
        self,
        context: AnalysisContext,
        config: GoInitUsageConfig,
    ) -> list[Violation]:
        """Detect violations for the current analysis context.

        Args:
            context (AnalysisContext): Analysis context containing source text and intermediate metrics.
            config (GoInitUsageConfig): Typed detector or analyzer configuration that controls thresholds.

        Returns:
            list[Violation]: Violations detected for the analyzed context.
        """
        if "func init(" in context.code:
            return [
                self.build_violation(
                    config,
                    contains="init",
                    suggestion="Prefer explicit initialization over init().",
                ),
            ]
        return []


class GoOrganizeResponsibilityDetector(ViolationDetector[GoSinglePurposePackageConfig]):
    """Detects catch-all package names like util, common, or helper.

    "Each package fulfils a single purpose" — generic package names
    indicate a grab-bag of unrelated functionality.
    """

    @property
    def name(self) -> str:
        """Return detector identifier.

        Returns:
            str: Identifier string.
        """
        return "go_single_purpose_package"

    def detect(
        self,
        context: AnalysisContext,
        config: GoSinglePurposePackageConfig,
    ) -> list[Violation]:
        """Detect catch-all Go package names.

        Args:
            context (AnalysisContext): Analysis context with source code.
            config (GoSinglePurposePackageConfig): Detector configuration.

        Returns:
            list[Violation]: Detected violations.
        """
        if re.search(
            r"^package\s+(util|utils|common|helper|helpers|misc|shared)\b",
            context.code,
            re.MULTILINE,
        ):
            return [
                self.build_violation(
                    config,
                    contains="package",
                    suggestion="Each package should fulfil a single purpose.",
                ),
            ]
        return []


class GoEarlyReturnDetector(ViolationDetector[GoEarlyReturnConfig]):
    """Flags ``err == nil`` guards that nest the happy path instead of returning early.

    Go convention favours returning errors immediately to keep the
    main logic at the top indentation level.
    """

    @property
    def name(self) -> str:
        """Return detector identifier.

        Returns:
            str: Identifier string.
        """
        return "go_early_return"

    def detect(
        self,
        context: AnalysisContext,
        config: GoEarlyReturnConfig,
    ) -> list[Violation]:
        """Detect ``err == nil`` nesting anti-pattern.

        Args:
            context (AnalysisContext): Analysis context with source code.
            config (GoEarlyReturnConfig): Detector configuration.

        Returns:
            list[Violation]: Detected violations.
        """
        if re.search(r"if\s+err\s*==\s*nil\s*\{", context.code):
            return [
                self.build_violation(
                    config,
                    contains="err == nil",
                    suggestion="Return early rather than nesting deeply.",
                ),
            ]
        return []


class GoConcurrencyCallerDetector(ViolationDetector[GoConcurrencyCallerConfig]):
    """Flags functions that spawn goroutines internally.

    Go proverb: leave concurrency decisions to the caller so that
    library code remains composable and testable.
    """

    @property
    def name(self) -> str:
        """Return detector identifier.

        Returns:
            str: Identifier string.
        """
        return "go_concurrency_caller"

    def detect(
        self,
        context: AnalysisContext,
        config: GoConcurrencyCallerConfig,
    ) -> list[Violation]:
        """Detect internal goroutine spawning.

        Args:
            context (AnalysisContext): Analysis context with source code.
            config (GoConcurrencyCallerConfig): Detector configuration.

        Returns:
            list[Violation]: Detected violations.
        """
        if re.search(r"\bgo\s+func\b|\bgo\s+\w+\(", context.code):
            return [
                self.build_violation(
                    config,
                    contains="go ",
                    suggestion="Leave concurrency to the caller.",
                ),
            ]
        return []


class GoSimplicityDetector(ViolationDetector[GoSimplicityConfig]):
    """Flags empty interface usage that weakens type safety.

    ``interface{}`` (or ``any``) discards compile-time type
    information.  Prefer specific types or small interfaces.
    """

    @property
    def name(self) -> str:
        """Return detector identifier.

        Returns:
            str: Identifier string.
        """
        return "go_simplicity"

    def detect(
        self,
        context: AnalysisContext,
        config: GoSimplicityConfig,
    ) -> list[Violation]:
        """Detect empty interface usage.

        Args:
            context (AnalysisContext): Analysis context with source code.
            config (GoSimplicityConfig): Detector configuration.

        Returns:
            list[Violation]: Detected violations.
        """
        if re.search(r"\binterface\s*\{\s*\}", context.code):
            return [
                self.build_violation(
                    config,
                    contains="interface{}",
                    suggestion="Prefer specific types over empty interfaces; simplicity matters.",
                ),
            ]
        return []


class GoTestPresenceDetector(ViolationDetector[GoTestPresenceConfig]):
    """Flags exported functions without accompanying test functions.

    Every exported API surface should have tests to lock in
    expected behaviour and prevent regressions.
    """

    @property
    def name(self) -> str:
        """Return detector identifier.

        Returns:
            str: Identifier string.
        """
        return "go_test_presence"

    def detect(
        self,
        context: AnalysisContext,
        config: GoTestPresenceConfig,
    ) -> list[Violation]:
        """Detect exported functions without tests.

        Args:
            context (AnalysisContext): Analysis context with source code.
            config (GoTestPresenceConfig): Detector configuration.

        Returns:
            list[Violation]: Detected violations.
        """
        has_exported = re.search(r"func\s+[A-Z]", context.code)
        has_tests = re.search(r"func\s+Test", context.code)
        if has_exported and not has_tests:
            return [
                self.build_violation(
                    config,
                    contains="exported function",
                    suggestion="Write tests to lock in API behaviour.",
                ),
            ]
        return []


class GoBenchmarkDetector(ViolationDetector[GoBenchmarkConfig]):
    """Flags optimisation primitives used without benchmark proof.

    ``sync.Pool`` and ``unsafe.Pointer`` are advanced optimisations
    that should be justified by benchmark results.
    """

    @property
    def name(self) -> str:
        """Return detector identifier.

        Returns:
            str: Identifier string.
        """
        return "go_benchmark"

    def detect(
        self,
        context: AnalysisContext,
        config: GoBenchmarkConfig,
    ) -> list[Violation]:
        """Detect optimisation without benchmarks.

        Args:
            context (AnalysisContext): Analysis context with source code.
            config (GoBenchmarkConfig): Detector configuration.

        Returns:
            list[Violation]: Detected violations.
        """
        has_optim = re.search(r"sync\.Pool|unsafe\.Pointer", context.code)
        has_bench = re.search(r"func\s+Benchmark", context.code)
        if has_optim and not has_bench:
            return [
                self.build_violation(
                    config,
                    contains="optimization",
                    suggestion="Prove it's slow with a benchmark before optimizing.",
                ),
            ]
        return []


class GoModerationDetector(ViolationDetector[GoModerationConfig]):
    """Flags excessive goroutine spawning within a single file.

    Moderation is a virtue — too many ``go`` statements in one file
    suggest uncontrolled concurrency that is hard to reason about.
    """

    @property
    def name(self) -> str:
        """Return detector identifier.

        Returns:
            str: Identifier string.
        """
        return "go_moderation"

    def detect(
        self,
        context: AnalysisContext,
        config: GoModerationConfig,
    ) -> list[Violation]:
        """Detect goroutine proliferation.

        Args:
            context (AnalysisContext): Analysis context with source code.
            config (GoModerationConfig): Detector configuration.

        Returns:
            list[Violation]: Detected violations.
        """
        count = len(re.findall(r"\bgo\s+", context.code))
        if count > config.max_goroutine_spawns:
            return [
                self.build_violation(
                    config,
                    contains="goroutine",
                    suggestion="Moderation is a virtue; limit goroutine proliferation.",
                ),
            ]
        return []


class GoMaintainabilityDetector(ViolationDetector[GoMaintainabilityConfig]):
    """Flags exported functions missing godoc comments.

    Go convention requires every exported symbol to have a comment
    starting with the symbol name for ``go doc`` to render correctly.
    """

    @property
    def name(self) -> str:
        """Return detector identifier.

        Returns:
            str: Identifier string.
        """
        return "go_maintainability"

    def detect(
        self,
        context: AnalysisContext,
        config: GoMaintainabilityConfig,
    ) -> list[Violation]:
        """Detect exported functions without godoc comments.

        Args:
            context (AnalysisContext): Analysis context with source code.
            config (GoMaintainabilityConfig): Detector configuration.

        Returns:
            list[Violation]: Detected violations.
        """
        lines = context.code.splitlines()
        for idx, line in enumerate(lines):
            if re.match(r"func\s+[A-Z]\w*\(", line):
                prev = lines[idx - 1].strip() if idx > 0 else ""
                if not prev.startswith("//"):
                    return [
                        self.build_violation(
                            config,
                            contains="exported function",
                            suggestion="Add godoc comments for exported functions.",
                        ),
                    ]
        return []


__all__ = [
    "GoBenchmarkDetector",
    "GoConcurrencyCallerDetector",
    "GoContextUsageDetector",
    "GoDeferUsageDetector",
    "GoEarlyReturnDetector",
    "GoErrorHandlingDetector",
    "GoGoroutineLeakDetector",
    "GoInitUsageDetector",
    "GoInterfacePointerDetector",
    "GoInterfaceReturnDetector",
    "GoInterfaceSizeDetector",
    "GoMaintainabilityDetector",
    "GoModerationDetector",
    "GoNamingConventionDetector",
    "GoOrganizeResponsibilityDetector",
    "GoPackageNamingDetector",
    "GoPackageStateDetector",
    "GoSimplicityDetector",
    "GoTestPresenceDetector",
    "GoZeroValueDetector",
]
