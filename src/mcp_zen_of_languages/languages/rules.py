"""Generic pattern-matching detector for rules that rely on text-scanning heuristics.

This module provides [`RulePatternDetector`][RulePatternDetector], a multi-strategy detector that
applies configurable text patterns, script-length checks, variable-name-length
rules, inheritance-depth analysis, identifier-length enforcement, and naming-
convention validation.  It serves as the catch-all detector for rules that do
not warrant a dedicated detector class.

See Also:
    [`mcp_zen_of_languages.languages.configs`][mcp_zen_of_languages.languages.configs]: Configuration models consumed
    by the sub-detection methods.
"""

from __future__ import annotations

import re

from mcp_zen_of_languages.analyzers.base import (
    AnalysisContext,
    LocationHelperMixin,
    ViolationDetector,
)
from mcp_zen_of_languages.languages.configs import DetectorConfig
from mcp_zen_of_languages.models import Location, Violation


class RulePatternDetector(ViolationDetector[DetectorConfig], LocationHelperMixin):
    """Multi-strategy detector that applies configurable text patterns and structural checks.

    Combines six independent sub-detections into a single pass: literal or
    required-absence pattern matching, script length without functions,
    variable name length, class inheritance depth, identifier length, and
    public/private naming conventions.  Each sub-detection activates only when
    the corresponding config field is present, making this detector reusable
    across languages that share common heuristics.
    """

    @property
    def name(self) -> str:
        """Return ``'rule_pattern'`` identifying the generic pattern detector.

        Returns:
            str: The ``'rule_pattern'`` identifier.
        """
        return "rule_pattern"

    def detect(
        self, context: AnalysisContext, config: DetectorConfig
    ) -> list[Violation]:
        """Run all sub-detection strategies and aggregate their violations.

        Args:
            context: Analysis context holding the source text to scan.
            config: Detector configuration whose optional fields activate
                individual sub-detections (patterns, script length, naming, etc.).

        Returns:
            list[Violation]: Combined violations from all activated sub-detections.
        """
        violations: list[Violation] = []
        violations.extend(self._detect_patterns(context, config))
        violations.extend(self._detect_script_length(context, config))
        violations.extend(self._detect_variable_name_length(context, config))
        violations.extend(self._detect_inheritance_depth(context, config))
        violations.extend(self._detect_identifier_length(context, config))
        violations.extend(self._detect_naming_conventions(context, config))
        return violations

    def _detect_patterns(
        self, context: AnalysisContext, config: DetectorConfig
    ) -> list[Violation]:
        """Match literal text patterns and required-absence patterns from ``detectable_patterns``.

        Args:
            context: Analysis context holding the source text.
            config: Config whose ``detectable_patterns`` list drives the scan.

        Returns:
            list[Violation]: Violations for each matched or missing pattern.
        """
        violations: list[Violation] = []
        patterns = config.detectable_patterns or []
        for pattern in patterns:
            if not pattern:
                continue
            is_required = pattern.startswith("!")
            needle = pattern[1:] if is_required else pattern
            if not needle:
                continue
            if is_required:
                if needle not in context.code:
                    violations.append(
                        self.build_violation(
                            config,
                            contains=needle,
                            suggestion=config.recommended_alternative,
                        )
                    )
                continue
            for idx, line in enumerate(context.code.splitlines(), start=1):
                if needle in line:
                    violations.append(
                        self.build_violation(
                            config,
                            contains=needle,
                            location=Location(line=idx, column=line.find(needle) + 1),
                            suggestion=config.recommended_alternative,
                        )
                    )
                    break
        return violations

    def _detect_script_length(
        self, context: AnalysisContext, config: DetectorConfig
    ) -> list[Violation]:
        """Flag scripts exceeding a line-count threshold that lack function definitions.

        Args:
            context: Analysis context holding the source text.
            config: Config with optional ``max_script_length_without_functions`` field.

        Returns:
            list[Violation]: A single violation when the script is too long and has no functions.
        """
        max_length = getattr(config, "max_script_length_without_functions", None)
        if max_length is None:
            return []
        lines = context.code.splitlines()
        has_function = re.search(
            r"^\s*(function\s+\w+|\w+\s*\(\)\s*\{)", context.code, re.MULTILINE
        )
        if len(lines) > max_length and not has_function:
            return [
                self.build_violation(
                    config,
                    contains="function",
                    suggestion="Extract reusable logic into functions.",
                )
            ]
        return []

    def _detect_variable_name_length(
        self, context: AnalysisContext, config: DetectorConfig
    ) -> list[Violation]:
        """Flag shell-style variable assignments with names shorter than a minimum length.

        Args:
            context: Analysis context holding the source text.
            config: Config with optional ``min_variable_name_length`` field.

        Returns:
            list[Violation]: A single violation for the first overly short variable name.
        """
        min_length = getattr(config, "min_variable_name_length", None)
        if min_length is None:
            return []
        for idx, line in enumerate(context.code.splitlines(), start=1):
            match = re.match(r"\s*([a-zA-Z_][a-zA-Z0-9_]*)=", line)
            if not match:
                continue
            name = match[1]
            if len(name) < min_length and name not in {"i", "j", "k"}:
                return [
                    self.build_violation(
                        config,
                        contains=name,
                        location=Location(line=idx, column=1),
                        suggestion="Use more descriptive variable names.",
                    )
                ]
        return []

    def _detect_inheritance_depth(
        self, context: AnalysisContext, config: DetectorConfig
    ) -> list[Violation]:
        """Flag class hierarchies whose ``extends`` chains exceed a configurable depth.

        Args:
            context: Analysis context holding the source text.
            config: Config with optional ``max_inheritance_depth`` field.

        Returns:
            list[Violation]: A single violation when any inheritance chain is too deep.
        """
        max_depth = getattr(config, "max_inheritance_depth", None)
        if max_depth is None:
            return []
        parents: dict[str, str] = {}
        for match in re.finditer(r"class\s+(\w+)\s+extends\s+(\w+)", context.code):
            parents[match.group(1)] = match.group(2)

        def chain_depth(name: str) -> int:
            """Walk the parent map to measure the depth of the inheritance chain for *name*.

            Args:
                name: Class name whose ancestor chain is traced.

            Returns:
                int: Number of ``extends`` links from *name* to the root.
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

    def _detect_identifier_length(
        self, context: AnalysisContext, config: DetectorConfig
    ) -> list[Violation]:
        """Flag JavaScript-style identifiers (``const``, ``let``, ``var``, etc.) shorter than a minimum.

        Args:
            context: Analysis context holding the source text.
            config: Config with optional ``min_identifier_length`` field.

        Returns:
            list[Violation]: A single violation for the first overly short identifier.
        """
        min_length = getattr(config, "min_identifier_length", None)
        if min_length is None:
            return []
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
                            suggestion="Use clearer, longer identifiers for readability.",
                        )
                    ]
        return []

    def _detect_naming_conventions(
        self, context: AnalysisContext, config: DetectorConfig
    ) -> list[Violation]:
        """Enforce PascalCase or camelCase conventions on public and private members.

        Args:
            context: Analysis context holding the source text.
            config: Config with optional ``public_naming`` and ``private_naming`` fields.

        Returns:
            list[Violation]: A single violation for the first non-conforming member name.
        """
        public_naming = getattr(config, "public_naming", None)
        private_naming = getattr(config, "private_naming", None)
        if public_naming is None and private_naming is None:
            return []

        def matches_style(name: str, style: str) -> bool:
            """Check whether *name* conforms to the given naming *style* (PascalCase or camelCase).

            Args:
                name: Identifier to validate.
                style: Convention string containing ``pascal`` or ``camel`` (case-insensitive).

            Returns:
                bool: ``True`` when *name* matches the expected pattern.
            """
            style_lower = style.lower()
            if "pascal" in style_lower:
                return bool(re.match(r"^[A-Z][A-Za-z0-9]*$", name))
            if "camel" in style_lower:
                return bool(re.match(r"^_?[a-z][A-Za-z0-9]*$", name))
            return True

        for idx, line in enumerate(context.code.splitlines(), start=1):
            if public_naming:
                match = re.search(r"\bpublic\s+\w[\w<>,\s]*\s+([A-Za-z_]\w*)", line)
                if match and not matches_style(match[1], public_naming):
                    return [
                        self.build_violation(
                            config,
                            contains=match[1],
                            location=Location(line=idx, column=match.start(1) + 1),
                            suggestion=f"Use {public_naming} for public members.",
                        )
                    ]
            if private_naming:
                match = re.search(r"\bprivate\s+\w[\w<>,\s]*\s+([A-Za-z_]\w*)", line)
                if match and not matches_style(match.group(1), private_naming):
                    return [
                        self.build_violation(
                            config,
                            contains=match.group(1),
                            location=Location(line=idx, column=match.start(1) + 1),
                            suggestion=f"Use {private_naming} for private members.",
                        )
                    ]
        return []


__all__ = ["RulePatternDetector"]
