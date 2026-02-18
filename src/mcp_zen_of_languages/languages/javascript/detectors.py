"""Rule detectors for JavaScript code quality and idiomatic best-practice checks.

Each detector in this module targets a specific JavaScript anti-pattern —
from legacy ``var`` declarations and loose equality to callback hell and
unhandled promise rejections.  Detectors scan source lines with regex
patterns because no Python-native JavaScript AST is currently integrated.

See Also:
    ``JavaScriptAnalyzer``:
    The analyzer that wires these detectors into its pipeline.
"""

from __future__ import annotations

import re

from mcp_zen_of_languages.analyzers.base import (
    AnalysisContext,
    LocationHelperMixin,
    ViolationDetector,
)
from mcp_zen_of_languages.languages.configs import (
    Js009Config,
    Js011Config,
    JsAsyncErrorHandlingConfig,
    JsCallbackNestingConfig,
    JsFunctionLengthConfig,
    JsGlobalStateConfig,
    JsMagicNumbersConfig,
    JsModernFeaturesConfig,
    JsNoVarConfig,
    JsPureFunctionConfig,
    JsStrictEqualityConfig,
)
from mcp_zen_of_languages.models import Location, Violation


class JsCallbackNestingDetector(
    ViolationDetector[JsCallbackNestingConfig], LocationHelperMixin
):
    """Detect deeply nested callbacks that create "callback hell".

    JavaScript's event-driven model often leads to pyramids of nested
    ``function`` or ``=>`` callbacks, making control flow hard to follow
    and errors easy to swallow.  This detector tracks nesting depth by
    counting callback openings vs. closing braces and flags files that
    exceed the configured threshold.

    Note:
        Modern code should prefer ``async``/``await`` or chained Promises
        to keep nesting shallow and readable.
    """

    @property
    def name(self) -> str:
        """Return the detector identifier used by registry wiring.

        Returns:
            str: Identifier string consumed by callers.
        """
        return "js_callback_nesting"

    def detect(
        self, context: AnalysisContext, config: JsCallbackNestingConfig
    ) -> list[Violation]:
        """Detect violations for the current analysis context.

        Args:
            context (AnalysisContext): Analysis context containing source text and intermediate metrics.
            config (JsCallbackNestingConfig): Typed detector or analyzer configuration that controls thresholds.

        Returns:
            list[Violation]: Violations detected for the analyzed context.
        """
        max_nesting = config.max_callback_nesting
        code = context.code
        nesting = 0
        max_seen = 0
        for line in code.splitlines():
            if "function" in line or "=>" in line:
                nesting += 1
                max_seen = max(max_seen, nesting)
            if "}" in line:
                nesting = max(nesting - 1, 0)
        if max_seen > max_nesting:
            return [
                self.build_violation(
                    config,
                    contains="callback",
                    suggestion=(
                        "Reduce nested callbacks by using async/await or Promises."
                    ),
                )
            ]
        return []


class JsNoVarDetector(ViolationDetector[JsNoVarConfig], LocationHelperMixin):
    r"""Detect usage of the legacy ``var`` keyword for variable declarations.

    ``var`` has function scope rather than block scope, which leads to subtle
    hoisting bugs and accidental variable leaks in loops and conditionals.
    This detector scans every line for the ``\\bvar\\b`` pattern and reports
    each occurrence with its exact line and column position.

    Note:
        ``const`` (for immutable bindings) and ``let`` (for mutable bindings)
        are block-scoped and should always be preferred over ``var``.
    """

    @property
    def name(self) -> str:
        """Return the detector identifier used by registry wiring.

        Returns:
            str: Identifier string consumed by callers.
        """
        return "js_no_var"

    def detect(
        self, context: AnalysisContext, config: JsNoVarConfig
    ) -> list[Violation]:
        """Detect violations for the current analysis context.

        Args:
            context (AnalysisContext): Analysis context containing source text and intermediate metrics.
            config (JsNoVarConfig): Typed detector or analyzer configuration that controls thresholds.

        Returns:
            list[Violation]: Violations detected for the analyzed context.
        """
        violations: list[Violation] = [
            self.build_violation(
                config,
                contains="var",
                location=Location(line=idx, column=line.find("var") + 1),
                suggestion="Use const/let instead of var.",
            )
            for idx, line in enumerate(context.code.splitlines(), start=1)
            if re.search(r"\bvar\b", line)
        ]
        return violations


class JsStrictEqualityDetector(
    ViolationDetector[JsStrictEqualityConfig], LocationHelperMixin
):
    """Detect loose equality operators (``==`` / ``!=``) in JavaScript.

    JavaScript's abstract equality algorithm performs type coercion before
    comparison, producing counter-intuitive results such as ``0 == ""``
    evaluating to ``true``.  This detector scans for ``==`` and ``!=`` while
    skipping their strict counterparts (``===`` / ``!==``), reporting the
    exact column of each offending operator.

    Note:
        Strict equality (``===`` / ``!==``) avoids implicit coercion and is
        the standard recommendation in ESLint's ``eqeqeq`` rule.
    """

    @property
    def name(self) -> str:
        """Return the detector identifier used by registry wiring.

        Returns:
            str: Identifier string consumed by callers.
        """
        return "js_strict_equality"

    def detect(
        self, context: AnalysisContext, config: JsStrictEqualityConfig
    ) -> list[Violation]:
        """Detect violations for the current analysis context.

        Args:
            context (AnalysisContext): Analysis context containing source text and intermediate metrics.
            config (JsStrictEqualityConfig): Typed detector or analyzer configuration that controls thresholds.

        Returns:
            list[Violation]: Violations detected for the analyzed context.
        """
        violations: list[Violation] = []
        for idx, line in enumerate(context.code.splitlines(), start=1):
            if "==" in line or "!=" in line:
                if "===" in line or "!==" in line:
                    continue
                if match := re.search(r"(!=|==)", line):
                    violations.append(
                        self.build_violation(
                            config,
                            contains="==",
                            location=Location(line=idx, column=match.start() + 1),
                            suggestion="Use === or !== instead of ==/!=.",
                        )
                    )
        return violations


class JsAsyncErrorHandlingDetector(
    ViolationDetector[JsAsyncErrorHandlingConfig], LocationHelperMixin
):
    """Detect async functions and promise chains with missing error handling.

    Unhandled promise rejections crash Node.js processes (since v15+) and
    silently swallow errors in browsers.  This detector raises a violation
    when an ``async`` function body contains no ``try``/``catch`` or
    ``.catch()`` call, and when ``.then()`` chains lack a trailing
    ``.catch()`` within a four-line look-ahead window.

    Note:
        Every ``async`` call path should terminate in a ``catch`` clause
        to prevent unhandled-rejection crashes in production.
    """

    @property
    def name(self) -> str:
        """Return the detector identifier used by registry wiring.

        Returns:
            str: Identifier string consumed by callers.
        """
        return "js_async_error_handling"

    def detect(
        self, context: AnalysisContext, config: JsAsyncErrorHandlingConfig
    ) -> list[Violation]:
        """Detect violations for the current analysis context.

        Args:
            context (AnalysisContext): Analysis context containing source text and intermediate metrics.
            config (JsAsyncErrorHandlingConfig): Typed detector or analyzer configuration that controls thresholds.

        Returns:
            list[Violation]: Violations detected for the analyzed context.
        """
        code = context.code
        violations: list[Violation] = []
        if "async " in code and "try" not in code and ".catch" not in code:
            violations.append(
                self.build_violation(
                    config,
                    contains="catch",
                    suggestion="Handle async errors with try/catch or .catch().",
                )
            )
        lines = code.splitlines()
        for idx, line in enumerate(lines):
            if ".then" not in line:
                continue
            window = "\n".join(lines[idx : idx + 4])
            if ".catch" in window:
                continue
            violations.append(
                self.build_violation(
                    config,
                    contains="catch",
                    suggestion="Always terminate promise chains with .catch().",
                )
            )
            break
        return violations


class JsFunctionLengthDetector(
    ViolationDetector[JsFunctionLengthConfig], LocationHelperMixin
):
    """Detect JavaScript functions that exceed a configurable line-count limit.

    Long functions violate the single-responsibility principle and are harder
    to test, review, and maintain.  This detector finds ``function`` keyword
    declarations, counts lines until the closing brace, and flags any that
    exceed ``max_function_length``.

    Note:
        Arrow functions and method shorthand are not currently matched;
        the detector focuses on classic ``function`` declarations.
    """

    @property
    def name(self) -> str:
        """Return the detector identifier used by registry wiring.

        Returns:
            str: Identifier string consumed by callers.
        """
        return "js_function_length"

    def detect(
        self, context: AnalysisContext, config: JsFunctionLengthConfig
    ) -> list[Violation]:
        """Detect violations for the current analysis context.

        Args:
            context (AnalysisContext): Analysis context containing source text and intermediate metrics.
            config (JsFunctionLengthConfig): Typed detector or analyzer configuration that controls thresholds.

        Returns:
            list[Violation]: Violations detected for the analyzed context.
        """
        limit = config.max_function_length
        violations: list[Violation] = []
        lines = context.code.splitlines()
        for idx, line in enumerate(lines, start=1):
            if line.strip().startswith("function "):
                length = 0
                for sub in lines[idx:]:
                    if sub.strip().startswith("}"):
                        break
                    length += 1
                if length > limit:
                    violations.append(
                        self.build_violation(
                            config,
                            contains="function",
                            location=Location(line=idx, column=1),
                            suggestion=f"Keep functions <= {limit} lines.",
                        )
                    )
        return violations


class JsGlobalStateDetector(
    ViolationDetector[JsGlobalStateConfig], LocationHelperMixin
):
    """Detect direct access to global mutable state via ``window``, ``globalThis``, or ``global``.

    Relying on global state creates hidden coupling between modules, makes
    code non-deterministic, and breaks in environments where the expected
    global object differs (e.g., ``window`` is undefined in Node.js workers).
    This detector flags lines that reference any of the three common global
    accessors.

    Note:
        Prefer dependency injection or module-scoped state to keep functions
        pure and testable.
    """

    @property
    def name(self) -> str:
        """Return the detector identifier used by registry wiring.

        Returns:
            str: Identifier string consumed by callers.
        """
        return "js_global_state"

    def detect(
        self, context: AnalysisContext, config: JsGlobalStateConfig
    ) -> list[Violation]:
        """Detect violations for the current analysis context.

        Args:
            context (AnalysisContext): Analysis context containing source text and intermediate metrics.
            config (JsGlobalStateConfig): Typed detector or analyzer configuration that controls thresholds.

        Returns:
            list[Violation]: Violations detected for the analyzed context.
        """
        violations: list[Violation] = [
            self.build_violation(
                config,
                contains="global",
                location=Location(line=idx, column=1),
                suggestion="Avoid global mutable state.",
            )
            for idx, line in enumerate(context.code.splitlines(), start=1)
            if "window." in line or "globalThis." in line or "global." in line
        ]
        return violations


class JsModernFeaturesDetector(
    ViolationDetector[JsModernFeaturesConfig], LocationHelperMixin
):
    """Detect opportunities to adopt modern ES6+ language features.

    Legacy patterns like anonymous ``function()`` expressions, string
    concatenation with ``+``, and repeated property access without
    destructuring are harder to read and more error-prone.  This detector
    checks for each pattern independently and suggests arrow functions,
    template literals, or destructuring as replacements.

    Note:
        All modern browsers and Node.js 14+ support these features
        natively — there is no reason to avoid them in new code.
    """

    @property
    def name(self) -> str:
        """Return the detector identifier used by registry wiring.

        Returns:
            str: Identifier string consumed by callers.
        """
        return "js_modern_features"

    def detect(
        self, context: AnalysisContext, config: JsModernFeaturesConfig
    ) -> list[Violation]:
        """Detect violations for the current analysis context.

        Args:
            context (AnalysisContext): Analysis context containing source text and intermediate metrics.
            config (JsModernFeaturesConfig): Typed detector or analyzer configuration that controls thresholds.

        Returns:
            list[Violation]: Violations detected for the analyzed context.
        """
        violations: list[Violation] = []
        code = context.code
        if "function(" in code:
            violations.append(
                self.build_violation(
                    config,
                    contains="arrow functions",
                    index=0,
                    suggestion="Prefer arrow functions and other modern syntax.",
                )
            )
        if re.search(r"['\"][^'\"]+['\"]\s*\+|\+\s*['\"][^'\"]+['\"]", code):
            violations.append(
                self.build_violation(
                    config,
                    contains="template literals",
                    index=0,
                    suggestion="Use template literals instead of string concatenation.",
                )
            )
        for line in code.splitlines():
            matches = re.findall(r"\b(\w+)\.\w+", line)
            if any(matches.count(name) >= 2 for name in set(matches)):
                violations.append(
                    self.build_violation(
                        config,
                        contains="destructuring",
                        index=0,
                        suggestion="Use object destructuring for repeated property access.",
                    )
                )
                break
        return violations


class JsMagicNumbersDetector(
    ViolationDetector[JsMagicNumbersConfig], LocationHelperMixin
):
    """Detect unexplained numeric literals (magic numbers) in JavaScript code.

    Magic numbers obscure intent — a reader cannot tell whether ``86400``
    means "seconds in a day" or an unrelated constant.  This detector
    uses a regex to find integer literals ≥ 2 that are not assigned to
    a named constant, and recommends extracting them into descriptive
    ``const`` declarations.

    Note:
        Common trivial values like ``0`` and ``1`` are intentionally excluded
        from detection to reduce false positives.
    """

    @property
    def name(self) -> str:
        """Return the detector identifier used by registry wiring.

        Returns:
            str: Identifier string consumed by callers.
        """
        return "js_magic_numbers"

    def detect(
        self, context: AnalysisContext, config: JsMagicNumbersConfig
    ) -> list[Violation]:
        """Detect violations for the current analysis context.

        Args:
            context (AnalysisContext): Analysis context containing source text and intermediate metrics.
            config (JsMagicNumbersConfig): Typed detector or analyzer configuration that controls thresholds.

        Returns:
            list[Violation]: Violations detected for the analyzed context.
        """
        if re.search(r"\b[2-9]\d*\b", context.code):
            return [
                self.build_violation(
                    config,
                    contains="magic numbers",
                    suggestion="Use named constants instead of magic numbers.",
                )
            ]
        return []


class JsInheritanceDepthDetector(ViolationDetector[Js009Config], LocationHelperMixin):
    """Detect class hierarchies that exceed a maximum inheritance depth.

    Deep ``extends`` chains tightly couple subclasses to ancestor
    implementations, making refactoring fragile and debugging painful.
    This detector builds a parent-child map from ``class X extends Y``
    declarations, walks each chain, and flags any that exceed the
    configured ``max_inheritance_depth``.

    Note:
        Composition (injecting behaviour via constructor parameters or
        mixins) is generally preferred over deep inheritance in JavaScript.
    """

    @property
    def name(self) -> str:
        """Return the detector identifier used by registry wiring.

        Returns:
            str: Identifier string consumed by callers.
        """
        return "js-009"

    def detect(self, context: AnalysisContext, config: Js009Config) -> list[Violation]:
        """Detect violations for the current analysis context.

        Args:
            context (AnalysisContext): Analysis context containing source text and intermediate metrics.
            config (Js009Config): Typed detector or analyzer configuration that controls thresholds.

        Returns:
            list[Violation]: Violations detected for the analyzed context.
        """
        max_depth = config.max_inheritance_depth or 0
        parents: dict[str, str] = {}
        for match in re.finditer(r"class\s+(\w+)\s+extends\s+(\w+)", context.code):
            parents[match.group(1)] = match.group(2)

        def chain_depth(name: str) -> int:
            """Compute the inheritance chain depth for a given class name.

            Args:
                name: Class name whose ancestor chain is walked.

            Returns:
                int: Number of ``extends`` hops from *name* to the root class.
            """
            depth = 0
            seen: set[str] = set()
            while name in parents and name not in seen:
                seen.add(name)
                name = parents[name]
                depth += 1
            return depth

        for child in parents:
            if chain_depth(child) > max_depth:
                return [
                    self.build_violation(
                        config,
                        contains="extends",
                        suggestion="Prefer composition over deep inheritance chains.",
                    )
                ]
        return []


class JsPureFunctionDetector(
    ViolationDetector[JsPureFunctionConfig], LocationHelperMixin
):
    """Detect in-place array mutations that break functional programming principles.

    Methods like ``push``, ``pop``, ``splice``, ``shift``, and ``unshift``
    mutate arrays in place, producing side effects that make functions impure
    and harder to reason about.  This detector scans for these method calls
    and recommends immutable alternatives such as spread syntax, ``concat``,
    ``filter``, or ``slice``.

    Note:
        Pure functions with immutable data structures are easier to test,
        cache, and parallelize in both browser and server environments.
    """

    @property
    def name(self) -> str:
        """Return the detector identifier used by registry wiring.

        Returns:
            str: Identifier string consumed by callers.
        """
        return "js_pure_functions"

    def detect(
        self, context: AnalysisContext, config: JsPureFunctionConfig
    ) -> list[Violation]:
        """Detect violations for the current analysis context.

        Args:
            context (AnalysisContext): Analysis context containing source text and intermediate metrics.
            config (JsPureFunctionConfig): Typed detector or analyzer configuration that controls thresholds.

        Returns:
            list[Violation]: Violations detected for the analyzed context.
        """
        if re.search(r"\b(push|splice|pop|shift|unshift)\s*\(", context.code):
            return [
                self.build_violation(
                    config,
                    contains="mutation",
                    suggestion="Prefer pure functions and immutable operations.",
                )
            ]
        return []


class JsMeaningfulNamesDetector(ViolationDetector[Js011Config], LocationHelperMixin):
    """Detect overly short or cryptic identifiers in JavaScript declarations.

    Single-character names like ``x`` or ``d`` outside of loop counters
    (``i``, ``j``, ``k``) harm readability and make code searches
    unreliable.  This detector extracts names from ``const``, ``let``,
    ``var``, ``function``, and ``class`` declarations and flags any
    shorter than ``min_identifier_length``.

    Note:
        Descriptive names serve as inline documentation and reduce the need
        for explanatory comments.
    """

    @property
    def name(self) -> str:
        """Return the detector identifier used by registry wiring.

        Returns:
            str: Identifier string consumed by callers.
        """
        return "js-011"

    def detect(self, context: AnalysisContext, config: Js011Config) -> list[Violation]:
        """Detect violations for the current analysis context.

        Args:
            context (AnalysisContext): Analysis context containing source text and intermediate metrics.
            config (Js011Config): Typed detector or analyzer configuration that controls thresholds.

        Returns:
            list[Violation]: Violations detected for the analyzed context.
        """
        min_length = config.min_identifier_length or 0
        pattern = re.compile(r"\b(?:const|let|var|function|class)\s+([A-Za-z_]\w*)")
        for idx, line in enumerate(context.code.splitlines(), start=1):
            for match in pattern.finditer(line):
                name = match.group(1)
                if len(name) < min_length and name not in {"i", "j", "k"}:
                    return [
                        self.build_violation(
                            config,
                            contains=name,
                            location=Location(line=idx, column=match.start(1) + 1),
                            suggestion="Use clearer, longer identifiers.",
                        )
                    ]
        return []


__all__ = [
    "JsAsyncErrorHandlingDetector",
    "JsCallbackNestingDetector",
    "JsFunctionLengthDetector",
    "JsGlobalStateDetector",
    "JsInheritanceDepthDetector",
    "JsMagicNumbersDetector",
    "JsMeaningfulNamesDetector",
    "JsModernFeaturesDetector",
    "JsNoVarDetector",
    "JsPureFunctionDetector",
    "JsStrictEqualityDetector",
]
