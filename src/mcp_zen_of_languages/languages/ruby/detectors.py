"""Zen-rule detectors for Ruby code quality, naming, and architecture checks.

Each detector implements the Strategy pattern as a ``ViolationDetector``
subclass, targeting a specific Ruby anti-pattern.  Ruby's dynamic runtime
and convention-driven culture make disciplined naming, restrained
metaprogramming, and idiomatic block usage essential for maintainable code.

See Also:
    ``RubyAnalyzer``: Template Method analyzer that orchestrates these detectors.
"""

from __future__ import annotations

import re

from mcp_zen_of_languages.analyzers.base import (
    AnalysisContext,
    LocationHelperMixin,
    ViolationDetector,
)
from mcp_zen_of_languages.languages.configs import (
    RubyBlockPreferenceConfig,
    RubyDryConfig,
    RubyExpressiveSyntaxConfig,
    RubyGuardClauseConfig,
    RubyMetaprogrammingConfig,
    RubyMethodChainConfig,
    RubyMethodNamingConfig,
    RubyMonkeyPatchConfig,
    RubyNamingConventionConfig,
    RubyPreferFailConfig,
    RubySymbolKeysConfig,
)
from mcp_zen_of_languages.models import Location, Violation

# Minimum number of identical lines before flagging as duplication
MIN_DUPLICATE_LINE_COUNT = 3


class RubyNamingConventionDetector(
    ViolationDetector[RubyNamingConventionConfig],
    LocationHelperMixin,
):
    """Flags Ruby methods defined with non-snake_case names.

    Ruby's community universally expects ``snake_case`` for method and variable
    names.  A method starting with an uppercase letter looks like a constant or
    class reference, breaking the readability contract that Rubyists rely on
    when scanning code without explicit type annotations.

    Note:
        Only catches ``def UpperCase`` patterns; does not inspect local variables.
    """

    @property
    def name(self) -> str:
        """Return ``'ruby_naming_convention'`` for registry wiring.

        Returns:
            str: Detector identifier for the naming-convention rule.
        """
        return "ruby_naming_convention"

    def detect(
        self,
        context: AnalysisContext,
        config: RubyNamingConventionConfig,
    ) -> list[Violation]:
        """Scan method definitions for non-snake_case names.

        Args:
            context: Analysis context with Ruby source text.
            config: Threshold configuration for naming conventions.

        Returns:
            list[Violation]: One violation per method using non-snake_case naming.
        """
        violations: list[Violation] = [
            self.build_violation(
                config,
                contains="snake_case",
                location=Location(line=idx, column=1),
                suggestion="Use snake_case for method names.",
            )
            for idx, line in enumerate(context.code.splitlines(), start=1)
            if re.search(r"def\s+[A-Z]", line)
        ]
        return violations


class RubyMethodChainDetector(
    ViolationDetector[RubyMethodChainConfig],
    LocationHelperMixin,
):
    """Detects excessively long method chains that reduce readability.

    Ruby's fluent API style encourages chaining, but overly long chains
    become hard to debug and produce cryptic ``NoMethodError`` traces.
    Breaking chains into named intermediate variables clarifies intent
    and makes each transformation step independently testable.
    """

    @property
    def name(self) -> str:
        """Return ``'ruby_method_chain'`` for registry wiring.

        Returns:
            str: Detector identifier for the method-chain-length rule.
        """
        return "ruby_method_chain"

    def detect(
        self,
        context: AnalysisContext,
        config: RubyMethodChainConfig,
    ) -> list[Violation]:
        """Flag lines where the number of chained method calls exceeds the threshold.

        Args:
            context: Analysis context with Ruby source text.
            config: Contains ``max_method_chain_length`` threshold.

        Returns:
            list[Violation]: Violations detected for the analyzed context.
        """
        max_chain = config.max_method_chain_length
        violations: list[Violation] = [
            self.build_violation(
                config,
                contains="chain",
                location=Location(line=idx, column=1),
                suggestion=f"Limit method chains to <= {max_chain} calls.",
            )
            for idx, line in enumerate(context.code.splitlines(), start=1)
            if line.count(".") > max_chain
        ]
        return violations


class RubyDryDetector(ViolationDetector[RubyDryConfig], LocationHelperMixin):
    """Identifies duplicated code lines that violate Don't Repeat Yourself (DRY).

    Repeated non-trivial lines signal copy-paste programming, a common anti-pattern
    in Ruby projects that grow without refactoring.  Extracting shared logic
    into methods, modules, or concerns keeps Ruby codebases concise and
    aligned with the principle that every piece of knowledge should have a
    single authoritative representation.
    """

    @property
    def name(self) -> str:
        """Return ``'ruby_dry'`` for registry wiring.

        Returns:
            str: Detector identifier for the DRY rule.
        """
        return "ruby_dry"

    def detect(
        self,
        context: AnalysisContext,
        config: RubyDryConfig,
    ) -> list[Violation]:
        """Flag source files containing three or more identical non-blank lines.

        Args:
            context: Analysis context with Ruby source text.
            config: DRY threshold configuration.

        Returns:
            list[Violation]: Violations detected for the analyzed context.
        """
        counts: dict[str, int] = {}
        for line in context.code.splitlines():
            stripped = line.strip()
            if not stripped or stripped.startswith("#"):
                continue
            counts[stripped] = counts.get(stripped, 0) + 1
            if counts[stripped] >= MIN_DUPLICATE_LINE_COUNT:
                return [
                    self.build_violation(
                        config,
                        contains="duplication",
                        suggestion="Extract repeated code into methods or modules.",
                    ),
                ]
        return []


class RubyBlockPreferenceDetector(
    ViolationDetector[RubyBlockPreferenceConfig],
    LocationHelperMixin,
):
    """Flags use of ``lambda``/``Proc.new`` where idiomatic blocks would suffice.

    Ruby blocks (``do...end`` / ``{...}``) are the idiomatic way to pass
    closures for iteration and callbacks.  Reaching for ``lambda`` or
    ``Proc.new`` when a simple block works adds unnecessary ceremony and
    confuses readers who expect the conventional block form in everyday
    enumerable pipelines.

    Note:
        ``lambda`` is appropriate for stored callables; this detector targets
        cases where a block would be more natural.
    """

    @property
    def name(self) -> str:
        """Return ``'ruby_block_preference'`` for registry wiring.

        Returns:
            str: Detector identifier for the block-preference rule.
        """
        return "ruby_block_preference"

    def detect(
        self,
        context: AnalysisContext,
        config: RubyBlockPreferenceConfig,
    ) -> list[Violation]:
        """Flag files that use ``lambda`` or ``Proc.new`` instead of blocks.

        Args:
            context: Analysis context with Ruby source text.
            config: Block-preference threshold configuration.

        Returns:
            list[Violation]: Violations detected for the analyzed context.
        """
        if "lambda" in context.code or "Proc.new" in context.code:
            return [
                self.build_violation(
                    config,
                    contains="lambda",
                    suggestion="Prefer blocks for simple iterations and callbacks.",
                ),
            ]
        return []


class RubyMonkeyPatchDetector(
    ViolationDetector[RubyMonkeyPatchConfig],
    LocationHelperMixin,
):
    """Detects reopening of core Ruby classes (monkey patching).

    Monkey patching ``String``, ``Array``, ``Hash``, or numeric classes
    silently mutates shared global state, creating action-at-a-distance
    bugs that are notoriously difficult to diagnose.  In Ruby's open-class
    system any gem or initializer can redefine core behaviour, leading to
    conflicts between libraries and unpredictable runtime failures.

    Note:
        Refinements (``Module#refine``) are the safe alternative for scoped
        extensions to core classes.
    """

    @property
    def name(self) -> str:
        """Return ``'ruby_monkey_patch'`` for registry wiring.

        Returns:
            str: Detector identifier for the monkey-patching rule.
        """
        return "ruby_monkey_patch"

    def detect(
        self,
        context: AnalysisContext,
        config: RubyMonkeyPatchConfig,
    ) -> list[Violation]:
        """Flag class reopenings of built-in Ruby types like String or Array.

        Args:
            context: Analysis context with Ruby source text.
            config: Monkey-patch detection configuration.

        Returns:
            list[Violation]: Violations detected for the analyzed context.
        """
        violations: list[Violation] = []
        pattern = re.compile(r"^\s*class\s+(String|Array|Hash|Integer|Float)\b")
        violations.extend(
            self.build_violation(
                config,
                contains="monkey patch",
                location=Location(line=idx, column=1),
                suggestion="Avoid monkey-patching Ruby core classes.",
            )
            for idx, line in enumerate(context.code.splitlines(), start=1)
            if pattern.search(line)
        )
        return violations


class RubyMethodNamingDetector(
    ViolationDetector[RubyMethodNamingConfig],
    LocationHelperMixin,
):
    """Flags boolean-style methods that lack the conventional trailing ``?``.

    Ruby convention dictates that predicate methods end with ``?``
    (e.g., ``empty?``, ``valid?``).  A method named ``is_active`` or
    ``has_items`` without the ``?`` suffix breaks the expectation of every
    Ruby developer, making boolean intent invisible at call sites and
    undermining Ruby's expressive readability.
    """

    @property
    def name(self) -> str:
        """Return ``'ruby_method_naming'`` for registry wiring.

        Returns:
            str: Detector identifier for the boolean-method naming rule.
        """
        return "ruby_method_naming"

    def detect(
        self,
        context: AnalysisContext,
        config: RubyMethodNamingConfig,
    ) -> list[Violation]:
        """Flag methods starting with ``is``/``has`` that are missing a ``?`` suffix.

        Args:
            context: Analysis context with Ruby source text.
            config: Method-naming threshold configuration.

        Returns:
            list[Violation]: Violations detected for the analyzed context.
        """
        violations: list[Violation] = []
        for idx, line in enumerate(context.code.splitlines(), start=1):
            match = re.search(r"\bdef\s+([a-zA-Z_]\w*)", line)
            if not match:
                continue
            name = match[1]
            if name.startswith(("is", "has")) and not name.endswith("?"):
                violations.append(
                    self.build_violation(
                        config,
                        contains=name,
                        location=Location(line=idx, column=match.start(1) + 1),
                        suggestion="Boolean methods should end with ?.",
                    ),
                )
        return violations


class RubySymbolKeysDetector(
    ViolationDetector[RubySymbolKeysConfig],
    LocationHelperMixin,
):
    """Flags hash literals using string keys instead of idiomatic symbol keys.

    Symbols are immutable, interned identifiers that are cheaper to compare
    and allocate than strings.  Using ``'key' => value`` instead of
    ``key: value`` wastes memory in long-lived hashes and signals
    unfamiliarity with Ruby's modern hash syntax introduced in Ruby 1.9.
    """

    @property
    def name(self) -> str:
        """Return ``'ruby_symbol_keys'`` for registry wiring.

        Returns:
            str: Detector identifier for the symbol-keys rule.
        """
        return "ruby_symbol_keys"

    def detect(
        self,
        context: AnalysisContext,
        config: RubySymbolKeysConfig,
    ) -> list[Violation]:
        """Flag hash literals that use quoted string keys with ``=>`` syntax.

        Args:
            context: Analysis context with Ruby source text.
            config: Symbol-keys detection configuration.

        Returns:
            list[Violation]: Violations detected for the analyzed context.
        """
        violations: list[Violation] = [
            self.build_violation(
                config,
                contains="string keys",
                location=Location(line=idx, column=1),
                suggestion="Use symbols for hash keys.",
            )
            for idx, line in enumerate(context.code.splitlines(), start=1)
            if re.search(r"['\"][^'\"]+['\"]\s*=>", line)
        ]
        return violations


class RubyGuardClauseDetector(
    ViolationDetector[RubyGuardClauseConfig],
    LocationHelperMixin,
):
    """Detects methods that could benefit from guard clauses to reduce nesting.

    Deeply nested ``if`` blocks obscure the happy path.  Ruby's
    ``return if`` / ``return unless`` guard clauses let methods exit early,
    keeping the main logic at the top indentation level and making methods
    dramatically easier to read and maintain.
    """

    @property
    def name(self) -> str:
        """Return ``'ruby_guard_clause'`` for registry wiring.

        Returns:
            str: Detector identifier for the guard-clause rule.
        """
        return "ruby_guard_clause"

    def detect(
        self,
        context: AnalysisContext,
        config: RubyGuardClauseConfig,
    ) -> list[Violation]:
        """Flag code with ``if`` blocks that lack ``return if/unless`` guard clauses.

        Args:
            context: Analysis context with Ruby source text.
            config: Guard-clause detection configuration.

        Returns:
            list[Violation]: Violations detected for the analyzed context.
        """
        code = context.code
        if "if " in code and not re.search(r"\breturn\s+(if|unless)\b", code):
            return [
                self.build_violation(
                    config,
                    contains="guard clause",
                    suggestion="Use guard clauses (return if/unless) to reduce nesting.",
                ),
            ]
        return []


class RubyMetaprogrammingDetector(
    ViolationDetector[RubyMetaprogrammingConfig],
    LocationHelperMixin,
):
    """Flags dangerous metaprogramming constructs like ``method_missing`` and ``eval``.

    Ruby's metaprogramming power—``define_method``, ``method_missing``,
    ``class_eval``, ``instance_eval``, and dynamic ``send``—can make code
    impossible to trace statically, defeats IDE navigation, and hides
    method signatures from documentation tools.  Unrestricted use turns a
    codebase into a maze where any object may respond to any message at
    runtime, making debugging and security auditing extremely difficult.

    Note:
        Metaprogramming is acceptable in DSL frameworks; this detector
        highlights it so teams can make conscious, documented decisions.
    """

    @property
    def name(self) -> str:
        """Return ``'ruby_metaprogramming'`` for registry wiring.

        Returns:
            str: Detector identifier for the metaprogramming-restraint rule.
        """
        return "ruby_metaprogramming"

    def detect(
        self,
        context: AnalysisContext,
        config: RubyMetaprogrammingConfig,
    ) -> list[Violation]:
        """Flag code containing dynamic dispatch or runtime method generation.

        Args:
            context: Analysis context with Ruby source text.
            config: Metaprogramming detection configuration.

        Returns:
            list[Violation]: Violations detected for the analyzed context.
        """
        return next(
            (
                [
                    self.build_violation(
                        config,
                        contains=token,
                        suggestion="Avoid metaprogramming unless strictly necessary.",
                    ),
                ]
                for token in (
                    "define_method",
                    "method_missing",
                    "class_eval",
                    "instance_eval",
                    "send(",
                    "public_send(",
                )
                if token in context.code
            ),
            [],
        )


class RubyExpressiveSyntaxDetector(
    ViolationDetector[RubyExpressiveSyntaxConfig],
    LocationHelperMixin,
):
    """Flags non-idiomatic control flow like C-style ``for`` loops and ``unless !``.

    Ruby provides ``each``, ``map``, ``select``, and other Enumerable
    methods that are more expressive and less error-prone than ``for...in``
    loops.  Similarly, ``unless !condition`` is a double-negative that should
    be written as ``if condition``.  Using these non-idiomatic constructs
    signals unfamiliarity with Ruby's expressive design philosophy.
    """

    @property
    def name(self) -> str:
        """Return ``'ruby_expressive_syntax'`` for registry wiring.

        Returns:
            str: Detector identifier for the expressive-syntax rule.
        """
        return "ruby_expressive_syntax"

    def detect(
        self,
        context: AnalysisContext,
        config: RubyExpressiveSyntaxConfig,
    ) -> list[Violation]:
        """Flag ``for...in`` loops and ``unless !`` double-negatives.

        Args:
            context: Analysis context with Ruby source text.
            config: Expressive-syntax detection configuration.

        Returns:
            list[Violation]: Violations detected for the analyzed context.
        """
        return next(
            (
                [
                    self.build_violation(
                        config,
                        contains="expressive syntax",
                        location=Location(line=idx, column=1),
                        suggestion="Prefer each/if over for/unless !.",
                    ),
                ]
                for idx, line in enumerate(context.code.splitlines(), start=1)
                if re.search(r"^\s*for\s+\w+\s+in\s+", line) or "unless !" in line
            ),
            [],
        )


class RubyPreferFailDetector(
    ViolationDetector[RubyPreferFailConfig],
    LocationHelperMixin,
):
    """Flags use of ``raise`` where ``fail`` is the preferred convention for programmer errors.

    The Ruby community convention (popularized by RuboCop) reserves ``fail``
    for signalling programmer errors in methods and ``raise`` for re-raising
    exceptions in rescue blocks.  Consistent use of ``fail`` for initial
    error signalling makes it immediately obvious whether an exception is
    being raised for the first time or re-raised after partial handling.
    """

    @property
    def name(self) -> str:
        """Return ``'ruby_prefer_fail'`` for registry wiring.

        Returns:
            str: Detector identifier for the prefer-fail rule.
        """
        return "ruby_prefer_fail"

    def detect(
        self,
        context: AnalysisContext,
        config: RubyPreferFailConfig,
    ) -> list[Violation]:
        """Flag files that use ``raise`` without any corresponding ``fail`` calls.

        Args:
            context: Analysis context with Ruby source text.
            config: Prefer-fail detection configuration.

        Returns:
            list[Violation]: Violations detected for the analyzed context.
        """
        if "raise " in context.code and "fail " not in context.code:
            return [
                self.build_violation(
                    config,
                    contains="raise",
                    suggestion="Use fail for programmer errors.",
                ),
            ]
        return []


__all__ = [
    "RubyBlockPreferenceDetector",
    "RubyDryDetector",
    "RubyExpressiveSyntaxDetector",
    "RubyGuardClauseDetector",
    "RubyMetaprogrammingDetector",
    "RubyMethodChainDetector",
    "RubyMethodNamingDetector",
    "RubyMonkeyPatchDetector",
    "RubyNamingConventionDetector",
    "RubyPreferFailDetector",
    "RubySymbolKeysDetector",
]
