"""Rule detectors for Bash/shell code quality and robustness checks.

Each detector in this module targets a specific shell scripting anti-pattern —
from missing ``set -euo pipefail`` and unquoted variable expansions to legacy
backtick syntax and absent signal handlers.  Detectors scan source lines with
regex patterns because no Python-native Bash AST is currently integrated.

See Also:
    ``BashAnalyzer``:
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
    Bash006Config,
    Bash011Config,
    BashArgumentValidationConfig,
    BashArrayUsageConfig,
    BashCommandSubstitutionConfig,
    BashDoubleBracketsConfig,
    BashEvalUsageConfig,
    BashExitCodeConfig,
    BashLocalVariablesConfig,
    BashQuoteVariablesConfig,
    BashReadonlyConstantsConfig,
    BashSignalHandlingConfig,
    BashStrictModeConfig,
    BashUsageInfoConfig,
)
from mcp_zen_of_languages.models import Location, Violation


class BashStrictModeDetector(
    ViolationDetector[BashStrictModeConfig],
    LocationHelperMixin,
):
    """Detect scripts missing the unofficial Bash strict mode header.

    Without ``set -euo pipefail``, a script silently continues after command
    failures (``-e``), uses undefined variables without error (``-u``), and
    masks failures in pipelines (``pipefail``).  This is the number-one cause
    of "it worked on my machine" CI failures.  The detector searches the
    entire file content for the exact pragma string.

    Note:
        Place ``set -euo pipefail`` immediately after the shebang line so
        that every subsequent command runs under strict error handling.
    """

    @property
    def name(self) -> str:
        """Return the detector identifier used by registry wiring.

        Returns:
            str: Identifier string consumed by callers.
        """
        return "bash_strict_mode"

    def detect(
        self,
        context: AnalysisContext,
        config: BashStrictModeConfig,
    ) -> list[Violation]:
        """Detect violations for the current analysis context.

        Args:
            context (AnalysisContext): Analysis context containing source text and intermediate metrics.
            config (BashStrictModeConfig): Typed detector or analyzer configuration that controls thresholds.

        Returns:
            list[Violation]: Violations detected for the analyzed context.
        """
        if "set -euo pipefail" not in context.code:
            return [
                self.build_violation(
                    config,
                    contains="set -euo pipefail",
                    suggestion="Add 'set -euo pipefail' near the top of the script.",
                ),
            ]
        return []


class BashQuoteVariablesDetector(
    ViolationDetector[BashQuoteVariablesConfig],
    LocationHelperMixin,
):
    """Detect unquoted variable expansions that cause word-splitting bugs.

    When ``$var`` appears outside double quotes, the shell performs word
    splitting and pathname expansion on its value.  A filename containing
    spaces or glob characters can silently break ``rm``, ``mv``, or loop
    logic.  This detector flags lines containing ``$`` variable references
    that lack surrounding double quotes.

    Note:
        Always write ``"$var"`` instead of bare ``$var`` to prevent word
        splitting and globbing surprises.
    """

    @property
    def name(self) -> str:
        """Return the detector identifier used by registry wiring.

        Returns:
            str: Identifier string consumed by callers.
        """
        return "bash_quote_variables"

    def detect(
        self,
        context: AnalysisContext,
        config: BashQuoteVariablesConfig,
    ) -> list[Violation]:
        """Detect violations for the current analysis context.

        Args:
            context (AnalysisContext): Analysis context containing source text and intermediate metrics.
            config (BashQuoteVariablesConfig): Typed detector or analyzer configuration that controls thresholds.

        Returns:
            list[Violation]: Violations detected for the analyzed context.
        """
        violations: list[Violation] = [
            self.build_violation(
                config,
                contains="quote",
                location=Location(line=idx, column=1),
                suggestion='Quote variable expansions like "$var".',
            )
            for idx, line in enumerate(context.code.splitlines(), start=1)
            if re.search(r"\$\w+", line) and '"' not in line
        ]
        return violations


class BashEvalUsageDetector(
    ViolationDetector[BashEvalUsageConfig],
    LocationHelperMixin,
):
    """Detect usage of ``eval`` which enables code injection attacks.

    ``eval`` re-parses its arguments as shell commands, making scripts
    vulnerable to injection when any part of the evaluated string comes
    from user input, environment variables, or external files.  This
    detector scans every line for the ``eval`` keyword and reports its
    exact position.

    Note:
        Replace ``eval`` with arrays for dynamic command construction or
        ``case`` statements for dispatching, both of which are injection-safe.
    """

    @property
    def name(self) -> str:
        """Return the detector identifier used by registry wiring.

        Returns:
            str: Identifier string consumed by callers.
        """
        return "bash_eval_usage"

    def detect(
        self,
        context: AnalysisContext,
        config: BashEvalUsageConfig,
    ) -> list[Violation]:
        """Detect violations for the current analysis context.

        Args:
            context (AnalysisContext): Analysis context containing source text and intermediate metrics.
            config (BashEvalUsageConfig): Typed detector or analyzer configuration that controls thresholds.

        Returns:
            list[Violation]: Violations detected for the analyzed context.
        """
        violations: list[Violation] = [
            self.build_violation(
                config,
                contains="eval",
                location=Location(line=idx, column=line.find("eval") + 1),
                suggestion="Avoid eval; use arrays or case statements instead.",
            )
            for idx, line in enumerate(context.code.splitlines(), start=1)
            if "eval" in line
        ]
        return violations


class BashDoubleBracketsDetector(
    ViolationDetector[BashDoubleBracketsConfig],
    LocationHelperMixin,
):
    """Detect single-bracket ``[ ]`` test expressions that should use ``[[ ]]``.

    The POSIX ``[`` command is an external binary with surprising parsing
    rules — unquoted variables inside ``[ ]`` can cause syntax errors when
    empty, and pattern matching is unavailable.  Bash's built-in ``[[ ]]``
    handles empty strings safely, supports ``=~`` regex matching, and does
    not perform word splitting on variables.

    Note:
        ``[[ ]]`` is a Bash extension.  If POSIX portability is required,
        quote all variables inside ``[ ]`` instead.
    """

    @property
    def name(self) -> str:
        """Return the detector identifier used by registry wiring.

        Returns:
            str: Identifier string consumed by callers.
        """
        return "bash_double_brackets"

    def detect(
        self,
        context: AnalysisContext,
        config: BashDoubleBracketsConfig,
    ) -> list[Violation]:
        """Detect violations for the current analysis context.

        Args:
            context (AnalysisContext): Analysis context containing source text and intermediate metrics.
            config (BashDoubleBracketsConfig): Typed detector or analyzer configuration that controls thresholds.

        Returns:
            list[Violation]: Violations detected for the analyzed context.
        """
        violations: list[Violation] = [
            self.build_violation(
                config,
                contains="[",
                location=Location(line=idx, column=1),
                suggestion="Prefer [[ ]] over [ ] for conditionals.",
            )
            for idx, line in enumerate(context.code.splitlines(), start=1)
            if re.search(r"\[[^\\[]", line) and "[[" not in line
        ]
        return violations


class BashCommandSubstitutionDetector(
    ViolationDetector[BashCommandSubstitutionConfig],
    LocationHelperMixin,
):
    """Detect legacy backtick command substitution syntax.

    Backtick-delimited command substitution (````cmd````) cannot be nested
    without cumbersome escaping, is visually ambiguous with single quotes in
    some fonts, and is considered deprecated in modern shell style guides.
    This detector flags every backtick occurrence and recommends the
    ``$(cmd)`` form, which nests cleanly and is universally supported.

    Note:
        ``$(...)`` is supported by all POSIX-compliant shells and should be
        the default choice for command substitution.
    """

    @property
    def name(self) -> str:
        """Return the detector identifier used by registry wiring.

        Returns:
            str: Identifier string consumed by callers.
        """
        return "bash_command_substitution"

    def detect(
        self,
        context: AnalysisContext,
        config: BashCommandSubstitutionConfig,
    ) -> list[Violation]:
        """Detect violations for the current analysis context.

        Args:
            context (AnalysisContext): Analysis context containing source text and intermediate metrics.
            config (BashCommandSubstitutionConfig): Typed detector or analyzer configuration that controls thresholds.

        Returns:
            list[Violation]: Violations detected for the analyzed context.
        """
        violations: list[Violation] = [
            self.build_violation(
                config,
                contains="`",
                location=Location(line=idx, column=line.find("`") + 1),
                suggestion="Use $(...) instead of backticks.",
            )
            for idx, line in enumerate(context.code.splitlines(), start=1)
            if "`" in line
        ]
        return violations


class BashReadonlyConstantsDetector(
    ViolationDetector[BashReadonlyConstantsConfig],
    LocationHelperMixin,
):
    """Detect ALL_CAPS assignments that are not declared ``readonly``.

    Shell constants (paths, configuration values, magic strings) are
    conventionally named in ALL_CAPS but remain mutable unless explicitly
    declared with ``readonly``.  Accidental reassignment of a constant
    deep in a script can produce silent, hard-to-debug failures.  This
    detector flags top-level ALL_CAPS assignments lacking ``readonly``.

    Note:
        Use ``readonly MY_CONST="value"`` or ``declare -r`` to make
        constants truly immutable.
    """

    @property
    def name(self) -> str:
        """Return the detector identifier used by registry wiring.

        Returns:
            str: Identifier string consumed by callers.
        """
        return "bash_readonly_constants"

    def detect(
        self,
        context: AnalysisContext,
        config: BashReadonlyConstantsConfig,
    ) -> list[Violation]:
        """Detect violations for the current analysis context.

        Args:
            context (AnalysisContext): Analysis context containing source text and intermediate metrics.
            config (BashReadonlyConstantsConfig): Typed detector or analyzer configuration that controls thresholds.

        Returns:
            list[Violation]: Violations detected for the analyzed context.
        """
        violations: list[Violation] = [
            self.build_violation(
                config,
                contains="readonly",
                location=Location(line=idx, column=1),
                suggestion="Declare constants with readonly.",
            )
            for idx, line in enumerate(context.code.splitlines(), start=1)
            if re.match(r"^[A-Z][A-Z0-9_]*=", line) and "readonly" not in line
        ]
        return violations


class BashExitCodeChecksDetector(
    ViolationDetector[BashExitCodeConfig],
    LocationHelperMixin,
):
    """Detect external commands whose exit codes are silently ignored.

    Even with ``set -e``, some command failures can slip through (e.g.,
    commands on the left side of ``&&`` or inside ``if`` conditions).
    This detector identifies standalone command invocations that are not
    guarded by ``||``, ``&&``, or explicit ``$?`` checks, flagging the
    first unguarded command it finds.

    Note:
        Guard critical commands with ``cmd || handle_error`` or check
        ``$?`` immediately after execution.
    """

    @property
    def name(self) -> str:
        """Return the detector identifier used by registry wiring.

        Returns:
            str: Identifier string consumed by callers.
        """
        return "bash-005"

    def detect(
        self,
        context: AnalysisContext,
        config: BashExitCodeConfig,
    ) -> list[Violation]:
        """Detect violations for the current analysis context.

        Args:
            context (AnalysisContext): Analysis context containing source text and intermediate metrics.
            config (BashExitCodeConfig): Typed detector or analyzer configuration that controls thresholds.

        Returns:
            list[Violation]: Violations detected for the analyzed context.
        """
        violations: list[Violation] = []
        lines = context.code.splitlines()
        for idx, line in enumerate(lines, start=1):
            stripped = line.strip()
            if not stripped or stripped.startswith("#"):
                continue
            if re.match(r"^[A-Za-z_][A-Za-z0-9_]*=", stripped):
                continue
            if stripped.startswith("export ") and "=" in stripped:
                continue
            if re.match(r"^\w+\s*\(\)\s*\{", stripped):
                continue
            if re.match(
                r"^(if|then|elif|else|fi|for|while|until|case|select|do|done)\b",
                stripped,
            ):
                continue
            if stripped.startswith(("set ", "{", "}")):
                continue
            if re.match(r"^(return|exit)\b", stripped):
                continue
            if "||" in stripped or "&&" in stripped or "$?" in stripped:
                continue
            next_line = lines[idx] if idx < len(lines) else ""
            if "$?" in next_line:
                continue
            if re.match(r"^[A-Za-z0-9_./-]+", stripped):
                violations.append(
                    self.build_violation(
                        config,
                        contains="exit code",
                        location=Location(line=idx, column=1),
                        suggestion=(
                            "Check exit codes with `||`, `&&`, or explicit `$?` tests."
                        ),
                    ),
                )
                break
        return violations


class BashFunctionUsageDetector(ViolationDetector[Bash006Config], LocationHelperMixin):
    """Detect long scripts that lack function decomposition.

    A linear Bash script without functions becomes unreadable and
    un-testable as it grows.  This detector counts non-comment, non-blank
    lines and flags scripts exceeding ``max_script_length_without_functions``
    when no ``function`` or ``name()`` declaration is present.

    Note:
        Extract repeated or logically distinct blocks into named functions
        so each unit can be tested, logged, and reused independently.
    """

    @property
    def name(self) -> str:
        """Return the detector identifier used by registry wiring.

        Returns:
            str: Identifier string consumed by callers.
        """
        return "bash-006"

    def detect(
        self,
        context: AnalysisContext,
        config: Bash006Config,
    ) -> list[Violation]:
        """Detect violations for the current analysis context.

        Args:
            context (AnalysisContext): Analysis context containing source text and intermediate metrics.
            config (Bash006Config): Typed detector or analyzer configuration that controls thresholds.

        Returns:
            list[Violation]: Violations detected for the analyzed context.
        """
        lines = [
            line
            for line in context.code.splitlines()
            if line.strip() and not line.strip().startswith("#")
        ]
        has_function = any(
            re.match(r"^\s*(?:function\s+)?\w+\s*\(\)\s*\{", line) for line in lines
        )
        max_len = config.max_script_length_without_functions or 50
        if not has_function and len(lines) > max_len:
            return [
                self.build_violation(
                    config,
                    contains="function",
                    location=Location(line=1, column=1),
                    suggestion="Extract reusable logic into functions.",
                ),
            ]
        return []


class BashLocalVariablesDetector(
    ViolationDetector[BashLocalVariablesConfig],
    LocationHelperMixin,
):
    """Detect function-scoped variables missing the ``local`` keyword.

    Bash variables are global by default — assigning ``name=value`` inside
    a function pollutes the caller's namespace and can overwrite unrelated
    variables.  This detector tracks whether the script is inside a function
    body and flags variable assignments that omit ``local``.

    Note:
        Always prefix function-internal assignments with ``local`` to prevent
        accidental namespace collisions.
    """

    @property
    def name(self) -> str:
        """Return the detector identifier used by registry wiring.

        Returns:
            str: Identifier string consumed by callers.
        """
        return "bash-007"

    def detect(
        self,
        context: AnalysisContext,
        config: BashLocalVariablesConfig,
    ) -> list[Violation]:
        """Detect violations for the current analysis context.

        Args:
            context (AnalysisContext): Analysis context containing source text and intermediate metrics.
            config (BashLocalVariablesConfig): Typed detector or analyzer configuration that controls thresholds.

        Returns:
            list[Violation]: Violations detected for the analyzed context.
        """
        violations: list[Violation] = []
        in_function = False
        for idx, line in enumerate(context.code.splitlines(), start=1):
            stripped = line.strip()
            if re.match(r"^\s*(?:function\s+)?\w+\s*\(\)\s*\{", line):
                in_function = True
                continue
            if in_function and stripped.startswith("}"):
                in_function = False
                continue
            if not in_function:
                continue
            if re.match(
                r"^[A-Za-z_][A-Za-z0-9_]*=",
                stripped,
            ) and not stripped.startswith("local "):
                violations.append(
                    self.build_violation(
                        config,
                        contains="local",
                        location=Location(line=idx, column=1),
                        suggestion="Declare function variables with local.",
                    ),
                )
                break
        return violations


class BashArgumentValidationDetector(
    ViolationDetector[BashArgumentValidationConfig],
    LocationHelperMixin,
):
    """Detect scripts that use positional arguments without validation.

    Scripts referencing ``$1``, ``$@``, or ``$*`` without checking ``$#``
    or using ``getopts`` will produce cryptic errors — or worse, silently
    operate on empty values — when invoked with missing arguments.  This
    detector flags the absence of argument-count guards.

    Note:
        Validate arguments early with ``if [[ $# -lt N ]]`` or use
        ``getopts`` for option parsing to fail fast with a clear message.
    """

    @property
    def name(self) -> str:
        """Return the detector identifier used by registry wiring.

        Returns:
            str: Identifier string consumed by callers.
        """
        return "bash-010"

    def detect(
        self,
        context: AnalysisContext,
        config: BashArgumentValidationConfig,
    ) -> list[Violation]:
        """Detect violations for the current analysis context.

        Args:
            context (AnalysisContext): Analysis context containing source text and intermediate metrics.
            config (BashArgumentValidationConfig): Typed detector or analyzer configuration that controls thresholds.

        Returns:
            list[Violation]: Violations detected for the analyzed context.
        """
        code = context.code
        uses_args = bool(re.search(r"\$(?:[1-9]|@|\*)", code))
        has_validation = "$#" in code or "getopts" in code
        if uses_args and not has_validation:
            return [
                self.build_violation(
                    config,
                    contains="$#",
                    location=Location(line=1, column=1),
                    suggestion="Validate arguments with `$#` checks or getopts.",
                ),
            ]
        return []


class BashMeaningfulNamesDetector(
    ViolationDetector[Bash011Config],
    LocationHelperMixin,
):
    """Detect overly short or cryptic variable names in shell scripts.

    Single-character names like ``x`` or ``t`` outside of loop counters
    (``i``, ``j``, ``k``) and ALL_CAPS constants make scripts harder to
    maintain.  This detector extracts variable assignments, skips uppercase
    constants and conventional loop vars, and flags names shorter than
    ``min_variable_name_length``.

    Note:
        Descriptive names like ``log_dir`` instead of ``d`` turn the script
        into self-documenting code.
    """

    @property
    def name(self) -> str:
        """Return the detector identifier used by registry wiring.

        Returns:
            str: Identifier string consumed by callers.
        """
        return "bash-011"

    def detect(
        self,
        context: AnalysisContext,
        config: Bash011Config,
    ) -> list[Violation]:
        """Detect violations for the current analysis context.

        Args:
            context (AnalysisContext): Analysis context containing source text and intermediate metrics.
            config (Bash011Config): Typed detector or analyzer configuration that controls thresholds.

        Returns:
            list[Violation]: Violations detected for the analyzed context.
        """
        violations: list[Violation] = []
        min_len = config.min_variable_name_length or 3
        for idx, line in enumerate(context.code.splitlines(), start=1):
            match = re.match(r"^\s*([A-Za-z_][A-Za-z0-9_]*)=", line)
            if not match:
                continue
            name = match[1]
            if name.isupper() or name in {"i", "j", "k"}:
                continue
            if len(name) < min_len:
                violations.append(
                    self.build_violation(
                        config,
                        contains=name,
                        location=Location(line=idx, column=1),
                        suggestion="Use descriptive variable names.",
                    ),
                )
                break
        return violations


class BashSignalHandlingDetector(
    ViolationDetector[BashSignalHandlingConfig],
    LocationHelperMixin,
):
    """Detect scripts that lack ``trap`` handlers for cleanup on exit or signals.

    Scripts that create temporary files, acquire locks, or start background
    processes must clean up on ``EXIT``, ``INT``, and ``TERM`` signals.
    Without a ``trap`` handler, an interrupted script leaves stale temp
    files, dangling lock files, or orphaned child processes.

    Note:
        Add ``trap cleanup EXIT`` near the top of the script to guarantee
        that cleanup runs regardless of how the script terminates.
    """

    @property
    def name(self) -> str:
        """Return the detector identifier used by registry wiring.

        Returns:
            str: Identifier string consumed by callers.
        """
        return "bash-012"

    def detect(
        self,
        context: AnalysisContext,
        config: BashSignalHandlingConfig,
    ) -> list[Violation]:
        """Detect violations for the current analysis context.

        Args:
            context (AnalysisContext): Analysis context containing source text and intermediate metrics.
            config (BashSignalHandlingConfig): Typed detector or analyzer configuration that controls thresholds.

        Returns:
            list[Violation]: Violations detected for the analyzed context.
        """
        if "trap " not in context.code:
            return [
                self.build_violation(
                    config,
                    contains="trap",
                    location=Location(line=1, column=1),
                    suggestion="Add trap handlers for cleanup and signals.",
                ),
            ]
        return []


class BashArrayUsageDetector(
    ViolationDetector[BashArrayUsageConfig],
    LocationHelperMixin,
):
    """Detect IFS-based string splitting used instead of proper Bash arrays.

    Setting ``IFS`` to split a string into tokens and iterating over
    unquoted ``$var`` is fragile — it breaks when values contain the
    delimiter character and does not preserve empty fields.  This detector
    flags ``IFS=`` assignments and ``for x in $var`` patterns, recommending
    Bash arrays with ``"${array[@]}"`` iteration instead.

    Note:
        Bash arrays handle whitespace-containing elements correctly and
        should be preferred over IFS-splitting for list-like data.
    """

    @property
    def name(self) -> str:
        """Return the detector identifier used by registry wiring.

        Returns:
            str: Identifier string consumed by callers.
        """
        return "bash-013"

    def detect(
        self,
        context: AnalysisContext,
        config: BashArrayUsageConfig,
    ) -> list[Violation]:
        """Detect violations for the current analysis context.

        Args:
            context (AnalysisContext): Analysis context containing source text and intermediate metrics.
            config (BashArrayUsageConfig): Typed detector or analyzer configuration that controls thresholds.

        Returns:
            list[Violation]: Violations detected for the analyzed context.
        """
        if re.search(r"\bIFS=|\bfor\s+\w+\s+in\s+\$", context.code):
            return [
                self.build_violation(
                    config,
                    contains="array",
                    location=Location(line=1, column=1),
                    suggestion='Prefer arrays and iterate with "${array[@]}".',
                ),
            ]
        return []


class BashUsageInfoDetector(
    ViolationDetector[BashUsageInfoConfig],
    LocationHelperMixin,
):
    """Detect scripts lacking a ``usage`` function or ``--help``/``-h`` flag.

    A script without built-in help forces users to read the source code to
    understand its arguments and options.  This detector checks for the
    presence of a ``usage`` keyword or ``--help``/``-h`` string and flags
    scripts that provide neither.

    Note:
        Even minimal scripts benefit from a ``usage()`` function that prints
        expected arguments and exits with a non-zero code on misuse.
    """

    @property
    def name(self) -> str:
        """Return the detector identifier used by registry wiring.

        Returns:
            str: Identifier string consumed by callers.
        """
        return "bash-014"

    def detect(
        self,
        context: AnalysisContext,
        config: BashUsageInfoConfig,
    ) -> list[Violation]:
        """Detect violations for the current analysis context.

        Args:
            context (AnalysisContext): Analysis context containing source text and intermediate metrics.
            config (BashUsageInfoConfig): Typed detector or analyzer configuration that controls thresholds.

        Returns:
            list[Violation]: Violations detected for the analyzed context.
        """
        if not re.search(r"\busage\b", context.code) and not re.search(
            r"--help|-h",
            context.code,
        ):
            return [
                self.build_violation(
                    config,
                    contains="usage",
                    location=Location(line=1, column=1),
                    suggestion="Provide a usage function or -h/--help flag.",
                ),
            ]
        return []


__all__ = [
    "BashArgumentValidationDetector",
    "BashArrayUsageDetector",
    "BashCommandSubstitutionDetector",
    "BashDoubleBracketsDetector",
    "BashEvalUsageDetector",
    "BashExitCodeChecksDetector",
    "BashFunctionUsageDetector",
    "BashLocalVariablesDetector",
    "BashMeaningfulNamesDetector",
    "BashQuoteVariablesDetector",
    "BashReadonlyConstantsDetector",
    "BashSignalHandlingDetector",
    "BashStrictModeDetector",
    "BashUsageInfoDetector",
]
