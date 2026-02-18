"""Rule detectors for PowerShell code quality and automation best-practice checks.

Each detector in this module targets a specific PowerShell anti-pattern — from
alias usage in scripts and ``Write-Host`` misuse to global scope pollution and
missing ``CmdletBinding``.  Detectors scan source lines with regex patterns
because no Python-native PowerShell AST is currently integrated.

See Also:
    ``PowerShellAnalyzer``:
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
    PowerShellAliasUsageConfig,
    PowerShellApprovedVerbConfig,
    PowerShellCmdletBindingConfig,
    PowerShellCommentHelpConfig,
    PowerShellErrorHandlingConfig,
    PowerShellNullHandlingConfig,
    PowerShellParameterValidationConfig,
    PowerShellPascalCaseConfig,
    PowerShellPipelineUsageConfig,
    PowerShellPositionalParamsConfig,
    PowerShellReturnObjectsConfig,
    PowerShellScopeUsageConfig,
    PowerShellShouldProcessConfig,
    PowerShellSplattingConfig,
    PowerShellVerboseDebugConfig,
)
from mcp_zen_of_languages.models import Location, Violation


class PowerShellApprovedVerbDetector(
    ViolationDetector[PowerShellApprovedVerbConfig], LocationHelperMixin
):
    """Detect function names that use unapproved PowerShell verbs.

    PowerShell mandates a standard set of verbs (``Get``, ``Set``, ``New``,
    ``Remove``, etc.) for the ``Verb-Noun`` naming convention.  Using
    non-standard verbs like ``Fetch-Data`` or ``Grab-Item`` triggers import
    warnings, breaks discoverability in ``Get-Command``, and violates the
    PowerShell module publishing guidelines.

    Note:
        Run ``Get-Verb`` in a PowerShell session to see the full list of
        approved verbs and their expected usage groups.
    """

    @property
    def name(self) -> str:
        """Return the detector identifier used by registry wiring.

        Returns:
            str: Identifier string consumed by callers.
        """
        return "powershell_approved_verbs"

    def detect(
        self, context: AnalysisContext, config: PowerShellApprovedVerbConfig
    ) -> list[Violation]:
        """Detect violations for the current analysis context.

        Args:
            context (AnalysisContext): Analysis context containing source text and intermediate metrics.
            config (PowerShellApprovedVerbConfig): Typed detector or analyzer configuration that controls thresholds.

        Returns:
            list[Violation]: Violations detected for the analyzed context.
        """
        violations: list[Violation] = []
        for idx, line in enumerate(context.code.splitlines(), start=1):
            match = re.search(r"function\s+(\w+)-", line, re.IGNORECASE)
            if match and match[1].lower() not in config.approved_verbs:
                violations.append(
                    self.build_violation(
                        config,
                        contains="verb",
                        location=Location(line=idx, column=match.start(1) + 1),
                        suggestion=(
                            "Use approved PowerShell verbs (Get/Set/New/Remove/etc.)."
                        ),
                    )
                )
        return violations


class PowerShellErrorHandlingDetector(
    ViolationDetector[PowerShellErrorHandlingConfig], LocationHelperMixin
):
    """Detect scripts that lack any form of error handling.

    PowerShell's default ``Continue`` error action silently moves past
    non-terminating errors, allowing scripts to report success despite
    partial failures.  This detector flags scripts that contain no
    ``try``/``catch`` blocks and no ``-ErrorAction`` parameters.

    Note:
        Use ``$ErrorActionPreference = 'Stop'`` at the script level or
        ``-ErrorAction Stop`` per cmdlet to promote errors to terminating
        exceptions that ``try``/``catch`` can handle.
    """

    @property
    def name(self) -> str:
        """Return the detector identifier used by registry wiring.

        Returns:
            str: Identifier string consumed by callers.
        """
        return "powershell_error_handling"

    def detect(
        self, context: AnalysisContext, config: PowerShellErrorHandlingConfig
    ) -> list[Violation]:
        """Detect violations for the current analysis context.

        Args:
            context (AnalysisContext): Analysis context containing source text and intermediate metrics.
            config (PowerShellErrorHandlingConfig): Typed detector or analyzer configuration that controls thresholds.

        Returns:
            list[Violation]: Violations detected for the analyzed context.
        """
        code = context.code
        if "try" not in code and "catch" not in code and "-ErrorAction" not in code:
            return [
                self.build_violation(
                    config,
                    contains="error",
                    suggestion="Add try/catch or -ErrorAction to handle errors.",
                )
            ]
        return []


class PowerShellPascalCaseDetector(
    ViolationDetector[PowerShellPascalCaseConfig], LocationHelperMixin
):
    """Detect function names that violate PascalCase naming conventions.

    PowerShell's ecosystem expects ``Verb-Noun`` function names in PascalCase
    (e.g., ``Get-ChildItem``).  Functions named ``get_data`` or ``fetchItems``
    break tab-completion expectations, look foreign alongside built-in
    cmdlets, and confuse users accustomed to the standard naming pattern.

    Note:
        The regex validates both standalone PascalCase names and hyphenated
        ``Verb-Noun`` pairs to accommodate advanced functions and modules.
    """

    @property
    def name(self) -> str:
        """Return the detector identifier used by registry wiring.

        Returns:
            str: Identifier string consumed by callers.
        """
        return "powershell_pascal_case"

    def detect(
        self, context: AnalysisContext, config: PowerShellPascalCaseConfig
    ) -> list[Violation]:
        """Detect violations for the current analysis context.

        Args:
            context (AnalysisContext): Analysis context containing source text and intermediate metrics.
            config (PowerShellPascalCaseConfig): Typed detector or analyzer configuration that controls thresholds.

        Returns:
            list[Violation]: Violations detected for the analyzed context.
        """
        violations: list[Violation] = []
        for idx, line in enumerate(context.code.splitlines(), start=1):
            if match := re.search(r"function\s+(\w+)", line, re.IGNORECASE):
                name = match[1]
                if not re.match(r"^[A-Z][A-Za-z0-9]*(-[A-Z][A-Za-z0-9]*)?$", name):
                    violations.append(
                        self.build_violation(
                            config,
                            contains="PascalCase",
                            location=Location(line=idx, column=match.start(1) + 1),
                            suggestion="Use PascalCase for function names.",
                        )
                    )
        return violations


class PowerShellCmdletBindingDetector(
    ViolationDetector[PowerShellCmdletBindingConfig], LocationHelperMixin
):
    """Detect advanced functions missing ``[CmdletBinding()]`` and ``param()``.

    Without ``[CmdletBinding()]``, a function cannot participate in the
    common-parameter ecosystem (``-Verbose``, ``-Debug``, ``-ErrorAction``,
    ``-WhatIf``).  Scripts that define functions but omit the attribute
    lose access to PowerShell's built-in safety and diagnostics features.

    Note:
        ``[CmdletBinding()]`` paired with a ``param()`` block is the minimum
        requirement for production-quality advanced functions.
    """

    @property
    def name(self) -> str:
        """Return the detector identifier used by registry wiring.

        Returns:
            str: Identifier string consumed by callers.
        """
        return "powershell_cmdlet_binding"

    def detect(
        self, context: AnalysisContext, config: PowerShellCmdletBindingConfig
    ) -> list[Violation]:
        """Detect violations for the current analysis context.

        Args:
            context (AnalysisContext): Analysis context containing source text and intermediate metrics.
            config (PowerShellCmdletBindingConfig): Typed detector or analyzer configuration that controls thresholds.

        Returns:
            list[Violation]: Violations detected for the analyzed context.
        """
        code = context.code
        if "function" not in code:
            return []
        if "CmdletBinding" not in code or "param(" not in code:
            return [
                self.build_violation(
                    config,
                    contains="CmdletBinding",
                    suggestion="Add [CmdletBinding()] and a param() block.",
                )
            ]
        return []


class PowerShellVerboseDebugDetector(
    ViolationDetector[PowerShellVerboseDebugConfig], LocationHelperMixin
):
    """Detect ``Write-Host`` calls that should use ``Write-Verbose`` or ``Write-Debug``.

    ``Write-Host`` writes directly to the console host, bypassing
    PowerShell's output streams.  Its output cannot be captured, redirected,
    or suppressed — making scripts unusable in automated pipelines, remoting
    sessions, and CI/CD environments.  This detector flags every
    ``Write-Host`` occurrence.

    Note:
        Use ``Write-Verbose`` for operational messages, ``Write-Debug`` for
        developer diagnostics, and ``Write-Output`` for pipeline data.
    """

    @property
    def name(self) -> str:
        """Return the detector identifier used by registry wiring.

        Returns:
            str: Identifier string consumed by callers.
        """
        return "powershell_verbose_debug"

    def detect(
        self, context: AnalysisContext, config: PowerShellVerboseDebugConfig
    ) -> list[Violation]:
        """Detect violations for the current analysis context.

        Args:
            context (AnalysisContext): Analysis context containing source text and intermediate metrics.
            config (PowerShellVerboseDebugConfig): Typed detector or analyzer configuration that controls thresholds.

        Returns:
            list[Violation]: Violations detected for the analyzed context.
        """
        violations: list[Violation] = [
            self.build_violation(
                config,
                contains="Write-Host",
                location=Location(line=idx, column=line.find("Write-Host") + 1),
                suggestion=(
                    "Use Write-Verbose or Write-Debug for logging output."
                ),
            )
            for idx, line in enumerate(context.code.splitlines(), start=1)
            if "Write-Host" in line
        ]
        return violations


class PowerShellPositionalParamsDetector(
    ViolationDetector[PowerShellPositionalParamsConfig], LocationHelperMixin
):
    """Detect reliance on ``$args`` for positional parameter access.

    Using the automatic ``$args`` variable instead of a typed ``param()``
    block sacrifices type validation, tab completion, mandatory-parameter
    enforcement, and pipeline binding.  This detector scans for ``$args``
    references and recommends named parameters.

    Note:
        Define explicit ``[Parameter()]`` attributes with types and
        validation to make functions self-documenting and IDE-friendly.
    """

    @property
    def name(self) -> str:
        """Return the detector identifier used by registry wiring.

        Returns:
            str: Identifier string consumed by callers.
        """
        return "powershell_positional_params"

    def detect(
        self, context: AnalysisContext, config: PowerShellPositionalParamsConfig
    ) -> list[Violation]:
        """Detect violations for the current analysis context.

        Args:
            context (AnalysisContext): Analysis context containing source text and intermediate metrics.
            config (PowerShellPositionalParamsConfig): Typed detector or analyzer configuration that controls thresholds.

        Returns:
            list[Violation]: Violations detected for the analyzed context.
        """
        violations: list[Violation] = [
            self.build_violation(
                config,
                contains="$args",
                location=Location(line=idx, column=line.find("$args") + 1),
                suggestion="Prefer named parameters over positional arguments.",
            )
            for idx, line in enumerate(context.code.splitlines(), start=1)
            if "$args" in line
        ]
        return violations


class PowerShellPipelineUsageDetector(
    ViolationDetector[PowerShellPipelineUsageConfig], LocationHelperMixin
):
    """Detect ``ForEach-Object`` or ``foreach`` loops that should use pipelines.

    PowerShell's pipeline streams objects one at a time, enabling memory-
    efficient processing of large datasets.  Explicit ``foreach`` loops
    without a pipeline accumulate entire collections in memory and miss
    the composability benefits of chaining cmdlets with ``|``.

    Note:
        Pipeline-aware code like ``Get-Process | Where-Object CPU -gt 50``
        is both more idiomatic and more memory-efficient than loop-based
        equivalents.
    """

    @property
    def name(self) -> str:
        """Return the detector identifier used by registry wiring.

        Returns:
            str: Identifier string consumed by callers.
        """
        return "powershell_pipeline_usage"

    def detect(
        self, context: AnalysisContext, config: PowerShellPipelineUsageConfig
    ) -> list[Violation]:
        """Detect violations for the current analysis context.

        Args:
            context (AnalysisContext): Analysis context containing source text and intermediate metrics.
            config (PowerShellPipelineUsageConfig): Typed detector or analyzer configuration that controls thresholds.

        Returns:
            list[Violation]: Violations detected for the analyzed context.
        """
        code = context.code
        if "|" in code:
            return []
        if re.search(r"\bForEach-Object\b", code, re.IGNORECASE) or re.search(
            r"\bforeach\b", code, re.IGNORECASE
        ):
            return [
                self.build_violation(
                    config,
                    contains="pipeline",
                    suggestion="Prefer pipeline operations for object processing.",
                )
            ]
        return []


class PowerShellShouldProcessDetector(
    ViolationDetector[PowerShellShouldProcessConfig], LocationHelperMixin
):
    """Detect destructive cmdlet verbs missing ``SupportsShouldProcess``.

    Functions that ``Remove``, ``Set``, ``Stop``, ``Clear``, ``Restart``,
    ``Disable``, or ``Enable`` resources should declare
    ``[CmdletBinding(SupportsShouldProcess)]`` so that callers can pass
    ``-WhatIf`` for dry-run confirmation and ``-Confirm`` for interactive
    safety.  This detector flags destructive verbs without the attribute.

    Note:
        Always call ``$PSCmdlet.ShouldProcess()`` before performing the
        destructive action to honour ``-WhatIf`` and ``-Confirm`` flags.
    """

    @property
    def name(self) -> str:
        """Return the detector identifier used by registry wiring.

        Returns:
            str: Identifier string consumed by callers.
        """
        return "powershell_should_process"

    def detect(
        self, context: AnalysisContext, config: PowerShellShouldProcessConfig
    ) -> list[Violation]:
        """Detect violations for the current analysis context.

        Args:
            context (AnalysisContext): Analysis context containing source text and intermediate metrics.
            config (PowerShellShouldProcessConfig): Typed detector or analyzer configuration that controls thresholds.

        Returns:
            list[Violation]: Violations detected for the analyzed context.
        """
        code = context.code
        if "SupportsShouldProcess" in code:
            return []
        if re.search(r"\b(Remove|Set|Stop|Clear|Restart|Disable|Enable)-", code):
            return [
                self.build_violation(
                    config,
                    contains="SupportsShouldProcess",
                    suggestion="Add [CmdletBinding(SupportsShouldProcess)] for safety.",
                )
            ]
        return []


class PowerShellSplattingDetector(
    ViolationDetector[PowerShellSplattingConfig], LocationHelperMixin
):
    """Detect cmdlet calls with many inline parameters that should use splatting.

    Lines passing four or more ``-Parameter Value`` pairs become hard to
    read, impossible to diff cleanly, and error-prone to maintain.
    Splatting (``@params``) moves parameters into a hashtable variable,
    improving readability and enabling parameter reuse.  This detector
    counts ``-`` prefixed tokens per line, skipping lines already using ``@``.

    Note:
        Splatting also simplifies conditional parameter inclusion by letting
        you build the hashtable dynamically before the call.
    """

    @property
    def name(self) -> str:
        """Return the detector identifier used by registry wiring.

        Returns:
            str: Identifier string consumed by callers.
        """
        return "powershell_splatting"

    def detect(
        self, context: AnalysisContext, config: PowerShellSplattingConfig
    ) -> list[Violation]:
        """Detect violations for the current analysis context.

        Args:
            context (AnalysisContext): Analysis context containing source text and intermediate metrics.
            config (PowerShellSplattingConfig): Typed detector or analyzer configuration that controls thresholds.

        Returns:
            list[Violation]: Violations detected for the analyzed context.
        """
        violations: list[Violation] = []
        for idx, line in enumerate(context.code.splitlines(), start=1):
            if "@" in line:
                continue
            param_count = len(re.findall(r"\s-\w+", line))
            if param_count >= 4:
                violations.append(
                    self.build_violation(
                        config,
                        contains="splatting",
                        location=Location(line=idx, column=1),
                        suggestion="Use splatting for long parameter lists.",
                    )
                )
        return violations


class PowerShellParameterValidationDetector(
    ViolationDetector[PowerShellParameterValidationConfig], LocationHelperMixin
):
    """Detect ``param()`` blocks that lack ``[Validate*]`` attributes.

    PowerShell's validation attributes (``[ValidateNotNullOrEmpty()]``,
    ``[ValidateRange()]``, ``[ValidateSet()]``, etc.) enforce input
    constraints before the function body runs, producing clear error
    messages without manual guard clauses.  This detector flags ``param()``
    blocks that omit all validation attributes.

    Note:
        Declarative validation is preferred over manual ``if`` checks
        because it integrates with ``Get-Help`` and IDE tooling.
    """

    @property
    def name(self) -> str:
        """Return the detector identifier used by registry wiring.

        Returns:
            str: Identifier string consumed by callers.
        """
        return "powershell_parameter_validation"

    def detect(
        self, context: AnalysisContext, config: PowerShellParameterValidationConfig
    ) -> list[Violation]:
        """Detect violations for the current analysis context.

        Args:
            context (AnalysisContext): Analysis context containing source text and intermediate metrics.
            config (PowerShellParameterValidationConfig): Typed detector or analyzer configuration that controls thresholds.

        Returns:
            list[Violation]: Violations detected for the analyzed context.
        """
        code = context.code
        if "param(" in code and "[Validate" not in code:
            return [
                self.build_violation(
                    config,
                    contains="Validate",
                    suggestion="Add [Validate*] attributes for parameters.",
                )
            ]
        return []


class PowerShellCommentHelpDetector(
    ViolationDetector[PowerShellCommentHelpConfig], LocationHelperMixin
):
    """Detect functions missing comment-based help with ``.SYNOPSIS``.

    PowerShell's ``Get-Help`` system relies on structured comment blocks
    containing ``.SYNOPSIS``, ``.DESCRIPTION``, ``.PARAMETER``, and
    ``.EXAMPLE`` sections.  Without them, users cannot discover how to
    use a function without reading its source code.  This detector flags
    the absence of ``.SYNOPSIS`` in the file.

    Note:
        Comment-based help also enables ``-?`` and tab-completion of
        parameter descriptions in the console.
    """

    @property
    def name(self) -> str:
        """Return the detector identifier used by registry wiring.

        Returns:
            str: Identifier string consumed by callers.
        """
        return "powershell_comment_help"

    def detect(
        self, context: AnalysisContext, config: PowerShellCommentHelpConfig
    ) -> list[Violation]:
        """Detect violations for the current analysis context.

        Args:
            context (AnalysisContext): Analysis context containing source text and intermediate metrics.
            config (PowerShellCommentHelpConfig): Typed detector or analyzer configuration that controls thresholds.

        Returns:
            list[Violation]: Violations detected for the analyzed context.
        """
        if ".SYNOPSIS" not in context.code:
            return [
                self.build_violation(
                    config,
                    contains=".SYNOPSIS",
                    suggestion="Add comment-based help with .SYNOPSIS and examples.",
                )
            ]
        return []


class PowerShellAliasUsageDetector(
    ViolationDetector[PowerShellAliasUsageConfig], LocationHelperMixin
):
    """Detect built-in aliases (``gci``, ``ls``, ``%``, ``?``) used in scripts.

    Aliases like ``gci``, ``ls``, ``dir``, ``cat``, ``%``, and ``?`` vary
    across platforms (``ls`` maps to ``Get-ChildItem`` on Windows but to
    ``/bin/ls`` on Linux) and are not guaranteed to exist in constrained
    environments like JEA endpoints.  This detector scans for common alias
    tokens and recommends full cmdlet names for portability.

    Note:
        Aliases are fine for interactive sessions but should never appear
        in shared scripts, modules, or CI/CD automation.
    """

    @property
    def name(self) -> str:
        """Return the detector identifier used by registry wiring.

        Returns:
            str: Identifier string consumed by callers.
        """
        return "powershell_alias_usage"

    def detect(
        self, context: AnalysisContext, config: PowerShellAliasUsageConfig
    ) -> list[Violation]:
        """Detect violations for the current analysis context.

        Args:
            context (AnalysisContext): Analysis context containing source text and intermediate metrics.
            config (PowerShellAliasUsageConfig): Typed detector or analyzer configuration that controls thresholds.

        Returns:
            list[Violation]: Violations detected for the analyzed context.
        """
        violations: list[Violation] = []
        alias_pattern = re.compile(r"(?<!\w)(gci|ls|dir|cat|%|\?)(?!\w)")
        for idx, line in enumerate(context.code.splitlines(), start=1):
            if match := alias_pattern.search(line):
                violations.append(
                    self.build_violation(
                        config,
                        contains=match[1],
                        location=Location(line=idx, column=match.start(1) + 1),
                        suggestion="Use full cmdlet names instead of aliases.",
                    )
                )
        return violations


class PowerShellReturnObjectsDetector(
    ViolationDetector[PowerShellReturnObjectsConfig], LocationHelperMixin
):
    """Detect functions that return formatted text instead of objects.

    Using ``Format-Table`` or ``Out-String`` inside a function bakes a
    specific display format into the output, preventing downstream
    cmdlets from filtering, sorting, or exporting the data.  PowerShell
    functions should return rich objects and let the caller choose the
    presentation format.

    Note:
        Reserve ``Format-*`` cmdlets for the final display step in the
        console, never inside reusable functions or modules.
    """

    @property
    def name(self) -> str:
        """Return the detector identifier used by registry wiring.

        Returns:
            str: Identifier string consumed by callers.
        """
        return "powershell_return_objects"

    def detect(
        self, context: AnalysisContext, config: PowerShellReturnObjectsConfig
    ) -> list[Violation]:
        """Detect violations for the current analysis context.

        Args:
            context (AnalysisContext): Analysis context containing source text and intermediate metrics.
            config (PowerShellReturnObjectsConfig): Typed detector or analyzer configuration that controls thresholds.

        Returns:
            list[Violation]: Violations detected for the analyzed context.
        """
        return next(
            (
                [
                    self.build_violation(
                        config,
                        contains=token,
                        suggestion="Return objects instead of formatted text.",
                    )
                ]
                for token in ("Format-Table", "Out-String")
                if token in context.code
            ),
            [],
        )


class PowerShellScopeUsageDetector(
    ViolationDetector[PowerShellScopeUsageConfig], LocationHelperMixin
):
    """Detect explicit ``$global:`` and ``$script:`` scope modifiers.

    Accessing ``$global:`` or ``$script:`` variables creates hidden
    coupling between functions, makes testing difficult (state leaks
    between test runs), and can introduce race conditions in parallel
    execution.  This detector flags any use of these scope prefixes.

    Note:
        Prefer passing state through parameters and return values to keep
        functions self-contained and testable in isolation.
    """

    @property
    def name(self) -> str:
        """Return the detector identifier used by registry wiring.

        Returns:
            str: Identifier string consumed by callers.
        """
        return "powershell_scope_usage"

    def detect(
        self, context: AnalysisContext, config: PowerShellScopeUsageConfig
    ) -> list[Violation]:
        """Detect violations for the current analysis context.

        Args:
            context (AnalysisContext): Analysis context containing source text and intermediate metrics.
            config (PowerShellScopeUsageConfig): Typed detector or analyzer configuration that controls thresholds.

        Returns:
            list[Violation]: Violations detected for the analyzed context.
        """
        if "$global:" in context.code or "$script:" in context.code:
            return [
                self.build_violation(
                    config,
                    contains="scope",
                    suggestion="Be explicit and minimize scope usage.",
                )
            ]
        return []


class PowerShellNullHandlingDetector(
    ViolationDetector[PowerShellNullHandlingConfig], LocationHelperMixin
):
    """Detect functions and param blocks that never check for ``$null``.

    PowerShell treats ``$null`` differently from empty strings and empty
    collections, and cmdlets can return ``$null`` unexpectedly when no
    objects match a filter.  Functions that process pipeline input or
    optional parameters without ``$null`` guards risk ``NullReference``
    errors at runtime.  This detector flags scripts containing
    ``function`` or ``param()`` declarations with no ``$null`` check.

    Note:
        Use ``if ($null -ne $value)`` (with ``$null`` on the left) to avoid
        PowerShell's counter-intuitive collection comparison behaviour.
    """

    @property
    def name(self) -> str:
        """Return the detector identifier used by registry wiring.

        Returns:
            str: Identifier string consumed by callers.
        """
        return "powershell_null_handling"

    def detect(
        self, context: AnalysisContext, config: PowerShellNullHandlingConfig
    ) -> list[Violation]:
        """Detect violations for the current analysis context.

        Args:
            context (AnalysisContext): Analysis context containing source text and intermediate metrics.
            config (PowerShellNullHandlingConfig): Typed detector or analyzer configuration that controls thresholds.

        Returns:
            list[Violation]: Violations detected for the analyzed context.
        """
        code = context.code
        if ("function" in code or "param(" in code) and "$null" not in code:
            return [
                self.build_violation(
                    config,
                    contains="$null",
                    suggestion="Add explicit $null checks for safety.",
                )
            ]
        return []


__all__ = [
    "PowerShellApprovedVerbDetector",
    "PowerShellAliasUsageDetector",
    "PowerShellCmdletBindingDetector",
    "PowerShellCommentHelpDetector",
    "PowerShellErrorHandlingDetector",
    "PowerShellNullHandlingDetector",
    "PowerShellParameterValidationDetector",
    "PowerShellPascalCaseDetector",
    "PowerShellPipelineUsageDetector",
    "PowerShellPositionalParamsDetector",
    "PowerShellReturnObjectsDetector",
    "PowerShellScopeUsageDetector",
    "PowerShellShouldProcessDetector",
    "PowerShellSplattingDetector",
    "PowerShellVerboseDebugDetector",
]
