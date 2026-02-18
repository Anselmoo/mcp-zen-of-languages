"""Python-specific violation detectors implementing the Strategy pattern.

Each detector class encapsulates a single zen-principle check against Python
source code.  Detectors are instantiated by the registry, wired into a
``DetectionPipeline``, and executed during ``PythonAnalyzer.analyze()``.

Detectors fall into two categories:

* **Syntactic detectors** — operate directly on source lines or the stdlib
  ``ast`` tree (e.g. ``StarImportDetector``, ``BareExceptDetector``).
* **Metric-gated detectors** — rely on pre-computed metrics stored in
  ``AnalysisContext`` (e.g. ``CyclomaticComplexityDetector`` reads
  ``context.cyclomatic_summary``).
"""

from __future__ import annotations

import ast
import re

from mcp_zen_of_languages.analyzers.base import (
    AnalysisContext,
    LocationHelperMixin,
    ViolationDetector,
)
from mcp_zen_of_languages.languages.configs import (
    BareExceptConfig,
    CircularDependencyConfig,
    ClassSizeConfig,
    ComplexOneLinersConfig,
    ConsistencyConfig,
    ContextManagerConfig,
    CyclomaticComplexityConfig,
    DeepInheritanceConfig,
    DetectorConfig,
    DocstringConfig,
    DuplicateImplementationConfig,
    ExplicitnessConfig,
    FeatureEnvyConfig,
    GodClassConfig,
    LineLengthConfig,
    LongFunctionConfig,
    MagicMethodConfig,
    MagicNumberConfig,
    NamespaceConfig,
    NameStyleConfig,
    NestingDepthConfig,
    ShortVariableNamesConfig,
    SparseCodeConfig,
    StarImportConfig,
)
from mcp_zen_of_languages.models import Location, ParserResult, Violation
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Iterable


def _principle_text(config: DetectorConfig) -> str:
    """Extract the human-readable principle name from a detector config.

    Falls back through ``principle`` → ``principle_id`` → ``type`` so that
    violation records always carry a meaningful label.

    Args:
        config: Detector configuration to extract the principle label from.

    Returns:
        str: The most descriptive principle label available.
    """
    return config.principle or config.principle_id or config.type


def _severity_level(config: DetectorConfig, fallback: int = 5) -> int:
    """Resolve the severity level from a detector config.

    Returns the explicit severity when set, otherwise falls back to a
    sensible default so that violations are never created without a
    severity rating.

    Args:
        config: Detector configuration potentially carrying an explicit severity.
        fallback: Default severity returned when the config has no override.

    Returns:
        int: Severity level in the range 1 (informational) to 9 (critical).
    """
    return config.severity if config.severity is not None else fallback


def _violation_message(
    config: DetectorConfig,
    *,
    contains: str | None = None,
    index: int = 0,
) -> str:
    """Select a violation message template from a detector config.

    Zen rules may define several violation message variants.  This helper
    delegates to ``config.select_violation_message`` using an optional
    substring filter and positional index to pick the best match.

    Args:
        config: Detector configuration carrying the rule's message variants.
        contains: Optional substring to filter candidate messages before
            selecting by index.
        index: Zero-based index into the (possibly filtered) message list.

    Returns:
        str: The resolved violation message text.
    """
    return config.select_violation_message(contains=contains, index=index)


class StarImportDetector(ViolationDetector[StarImportConfig], LocationHelperMixin):
    """Detect wildcard ``from X import *`` statements that pollute the module namespace.

    Star imports pull every public name from the target module into the
    current namespace, making it impossible to tell where a name originated
    from by reading the source alone.  They also defeat static analysis tools
    and IDE auto-complete, and create subtle bugs when two star-imported
    modules export the same name.

    Implements the *"Namespaces are one honking great idea"* zen principle:
    explicit imports keep namespaces clean and traceable.

    The detector scans raw source lines with a regex rather than walking the
    AST, because ``import *`` is a lexical pattern that is faster to match
    textually and does not require a successful parse.
    """

    @property
    def name(self) -> str:
        """Return ``"star_imports"`` for detector registry lookup.

        Returns:
            str: Registry key used to wire this detector to its rule config.
        """
        return "star_imports"

    def detect(
        self, context: AnalysisContext, config: StarImportConfig
    ) -> list[Violation]:
        """Scan source lines for ``from X import *`` patterns.

        Each matching line produces a violation pinpointed to the ``import``
        keyword column so that editors can jump straight to the offending
        statement.

        Args:
            context: Analysis context carrying the source text to scan.
            config: Star-import detector thresholds and rule metadata.

        Returns:
            list[Violation]: One violation per wildcard import found.
        """
        violations: list[Violation] = []
        message = config.select_violation_message(index=3)
        for i, line in enumerate(context.code.splitlines(), start=1):
            if re.match(r"^\s*from\s+\S+\s+import\s+\*", line):
                loc = Location(line=i, column=line.find("import") + 1)
                violations.append(
                    Violation(
                        principle=config.principle
                        or config.principle_id
                        or config.type,
                        severity=config.severity or 4,
                        message=message,
                        location=loc,
                        suggestion=(
                            "Import explicit names to avoid namespace pollution."
                        ),
                    )
                )
        return violations


class BareExceptDetector(ViolationDetector[BareExceptConfig], LocationHelperMixin):
    """Detect bare ``except:`` clauses and silently swallowed exceptions.

    A bare ``except:`` catches *everything* — including ``KeyboardInterrupt``
    and ``SystemExit`` — making it nearly impossible to interrupt or terminate
    the process cleanly.  Empty handlers (``except SomeError: pass``) are
    equally dangerous because they hide real failures and turn bugs into
    silent data corruption.

    Implements the *"Errors should never pass silently"* zen principle:
    exceptions must be caught specifically and handled meaningfully.

    Detection works on raw source lines using regex matching, covering three
    patterns: bare ``except:``, inline ``except X: pass``, and multi-line
    ``except X:`` followed by a ``pass``/``...`` body.
    """

    @property
    def name(self) -> str:
        """Return ``"bare_except"`` for detector registry lookup.

        Returns:
            str: Registry key used to wire this detector to its rule config.
        """
        return "bare_except"

    def detect(
        self, context: AnalysisContext, config: BareExceptConfig
    ) -> list[Violation]:
        """Scan source lines for bare excepts and empty exception handlers.

        Three patterns are checked in order for each line:

        1. ``except:`` with no exception type.
        2. Inline ``except SomeError: pass`` or ``except SomeError: ...``.
        3. ``except SomeError:`` on one line followed by ``pass``/``...`` on
           the next.

        Args:
            context: Analysis context with the source code to inspect.
            config: Bare-except detector thresholds and rule metadata.

        Returns:
            list[Violation]: One violation per offending ``except`` clause.
        """
        violations: list[Violation] = []
        lines = context.code.splitlines()
        for i, line in enumerate(lines, start=1):
            stripped = line.strip()
            if stripped == "except:" or stripped.startswith("except: "):
                loc = Location(line=i, column=line.find("except") + 1)
                violations.append(
                    Violation(
                        principle=config.principle
                        or config.principle_id
                        or config.type,
                        severity=config.severity or 5,
                        message=config.select_violation_message(
                            contains="Bare", index=0
                        ),
                        location=loc,
                        suggestion=(
                            "Catch specific exceptions or re-raise after logging."
                        ),
                    )
                )
                continue
            if re.match(
                r"except\s+\w+(?:\s+as\s+\w+)?\s*:\s*(pass|\.\.\.)\s*$",
                stripped,
            ):
                loc = Location(line=i, column=line.find("except") + 1)
                violations.append(
                    Violation(
                        principle=config.principle
                        or config.principle_id
                        or config.type,
                        severity=config.severity or 5,
                        message=config.select_violation_message(
                            contains="Empty", index=0
                        ),
                        location=loc,
                        suggestion=(
                            "Handle the exception or re-raise; avoid empty except blocks."
                        ),
                    )
                )
                continue
            if re.match(r"except\s+\w+(?:\s+as\s+\w+)?\s*:\s*$", stripped):
                next_line = lines[i] if i < len(lines) else ""
                if next_line.strip() in {"pass", "..."}:
                    loc = Location(line=i, column=line.find("except") + 1)
                    violations.append(
                        Violation(
                            principle=config.principle
                            or config.principle_id
                            or config.type,
                            severity=config.severity or 5,
                            message=config.select_violation_message(
                                contains="Empty", index=0
                            ),
                            location=loc,
                            suggestion=(
                                "Handle the exception or re-raise; avoid empty except blocks."
                            ),
                        )
                    )
        return violations


class MagicNumberDetector(ViolationDetector[MagicNumberConfig], LocationHelperMixin):
    """Detect excessive use of unexplained numeric literals (magic numbers).

    Numeric literals scattered through code obscure intent — a reader seeing
    ``if retries > 3`` cannot tell whether ``3`` is an arbitrary guess, a
    business rule, or a protocol limit.  Named constants (``MAX_RETRIES = 3``)
    make the code self-documenting and centralise change points.

    Implements the *"Readability counts"* zen principle: every value should
    communicate its purpose through a descriptive name.

    The detector regex-scans each line for integers ≥ 2 and non-integer
    floats, skipping comments, blank lines, and ``ALL_CAPS = …`` constant
    assignments.  A violation fires only when the total count exceeds the
    configured ``max_magic_numbers`` threshold.
    """

    @property
    def name(self) -> str:
        """Return ``"magic_number"`` for detector registry lookup.

        Returns:
            str: Registry key used to wire this detector to its rule config.
        """
        return "magic_number"

    def detect(
        self, context: AnalysisContext, config: MagicNumberConfig
    ) -> list[Violation]:
        """Count numeric literals across non-trivial lines and flag when too many.

        Lines that are blank, comments, or ``ALL_CAPS`` constant assignments
        are excluded.  The location of the *first* match is reported to guide
        the developer to the most likely starting point for refactoring.

        Args:
            context: Analysis context carrying the source text.
            config: Magic-number detector thresholds (``max_magic_numbers``).

        Returns:
            list[Violation]: At most one violation when the count exceeds the
                configured threshold.
        """
        violations: list[Violation] = []
        pattern = re.compile(r"\b(?:[2-9]\d*|1\.\d+)\b")
        count = 0
        first_match: tuple[int, int] | None = None
        for idx, line in enumerate(context.code.splitlines(), start=1):
            stripped = line.strip()
            if not stripped or stripped.startswith("#"):
                continue
            if re.match(r"^[A-Z][A-Z0-9_]*\s*=", stripped):
                continue
            for match in pattern.finditer(line):
                count += 1
                if first_match is None:
                    first_match = (idx, match.start() + 1)
        if count > config.max_magic_numbers:
            location = (
                Location(line=first_match[0], column=first_match[1])
                if first_match
                else None
            )
            violations.append(
                self.build_violation(
                    config,
                    contains="Magic numbers",
                    index=0,
                    location=location,
                    suggestion="Use named constants instead of magic numbers.",
                )
            )
        return violations


class ComplexOneLinersDetector(
    ViolationDetector[ComplexOneLinersConfig], LocationHelperMixin
):
    """Detect overly dense one-liner expressions that sacrifice readability.

    Deeply nested comprehensions and long ternary chains pack too much logic
    into a single line, making code hard to debug and impossible to set
    breakpoints inside.  Splitting them into named intermediate steps
    improves clarity without sacrificing performance.

    Implements the *"Simple is better than complex"* zen principle: favour
    straightforward multi-line code over clever one-liners.

    Two heuristics are applied per line:

    1. Count of ``for`` keywords exceeding ``max_for_clauses`` flags nested
       comprehensions.
    2. Lines longer than ``max_line_length`` containing both ``if`` and
       ``else`` flag complex ternary expressions.
    """

    @property
    def name(self) -> str:
        """Return ``"complex_one_liners"`` for detector registry lookup.

        Returns:
            str: Registry key used to wire this detector to its rule config.
        """
        return "complex_one_liners"

    def detect(
        self, context: AnalysisContext, config: ComplexOneLinersConfig
    ) -> list[Violation]:
        """Scan each line for nested comprehensions or complex ternary chains.

        Blank lines and comments are skipped.  Each offending line produces
        exactly one violation, choosing the most specific message variant
        (comprehension vs. generic one-liner).

        Args:
            context: Analysis context carrying the source text.
            config: One-liner detector thresholds (``max_for_clauses``,
                ``max_line_length``).

        Returns:
            list[Violation]: One violation per line that exceeds the
                complexity heuristics.
        """
        violations: list[Violation] = []
        for idx, line in enumerate(context.code.splitlines(), start=1):
            stripped = line.strip()
            if not stripped or stripped.startswith("#"):
                continue
            for_count = len(re.findall(r"\bfor\b", line))
            if for_count > config.max_for_clauses:
                violations.append(
                    self.build_violation(
                        config,
                        contains="comprehensions",
                        index=0,
                        location=Location(line=idx, column=1),
                        suggestion="Split nested comprehensions into named steps.",
                    )
                )
                continue
            if (
                len(line) > config.max_line_length
                and " if " in line
                and " else " in line
            ):
                violations.append(
                    self.build_violation(
                        config,
                        contains="Complex one-liners",
                        index=0,
                        location=Location(line=idx, column=1),
                        suggestion="Break complex expressions into multiple lines.",
                    )
                )
        return violations


class ContextManagerDetector(
    ViolationDetector[ContextManagerConfig], LocationHelperMixin
):
    """Detect ``open()`` calls not wrapped in a ``with`` context manager.

    File handles opened without a context manager risk resource leaks if an
    exception occurs before ``.close()`` is called.  The ``with`` statement
    guarantees cleanup even under error conditions.

    Implements the *"Explicit is better than implicit"* zen principle:
    resource lifetime should be governed by a visible scope, not by garbage
    collection timing.

    Detection walks the stdlib ``ast`` tree looking for ``Call`` nodes whose
    function name is ``open``.  For each match, a surrounding snippet is
    checked for ``with open`` to avoid false positives on properly managed
    handles.
    """

    @property
    def name(self) -> str:
        """Return ``"context_manager"`` for detector registry lookup.

        Returns:
            str: Registry key used to wire this detector to its rule config.
        """
        return "context_manager"

    def detect(
        self, context: AnalysisContext, config: ContextManagerConfig
    ) -> list[Violation]:
        """Walk the AST for ``open()`` calls and verify ``with`` wrapping.

        For each ``open()`` call node, a small surrounding snippet (±2 lines)
        is checked for ``with open``.  This avoids false positives on handles
        that are already managed by a context manager.

        Args:
            context: Analysis context with source text and (optionally) a
                pre-parsed AST.
            config: Context-manager detector thresholds and rule metadata.

        Returns:
            list[Violation]: One violation per ``open()`` call that is not
                wrapped in a ``with`` block.
        """
        violations: list[Violation] = []
        message = config.select_violation_message(contains="context managers", index=2)
        try:
            tree = ast.parse(context.code)
        except SyntaxError:
            return violations

        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                func = node.func
                func_name = None
                if isinstance(func, ast.Name):
                    func_name = func.id
                elif isinstance(func, ast.Attribute):
                    func_name = func.attr

                if func_name == "open":
                    lineno = getattr(node, "lineno", None)
                    col = getattr(node, "col_offset", None)
                    if lineno is not None:
                        loc = Location(line=lineno, column=(col or 0) + 1)
                        lines = context.code.splitlines()
                        start = max(0, lineno - 3)
                        end = min(len(lines), lineno + 2)
                        snippet = "\n".join(lines[start:end])
                        prev_line = lines[lineno - 2] if lineno >= 2 else ""
                        if (
                            "with open" not in snippet
                            and not prev_line.strip().startswith("with")
                        ):
                            violations.append(
                                Violation(
                                    principle=config.principle
                                    or config.principle_id
                                    or config.type,
                                    severity=config.severity or 4,
                                    message=message,
                                    location=loc,
                                    suggestion=(
                                        "Use 'with open(...) as f' to ensure proper resource cleanup."
                                    ),
                                )
                            )
        return violations


class DocstringDetector(ViolationDetector[DocstringConfig], LocationHelperMixin):
    """Detect top-level functions and classes missing a docstring.

    Public APIs without docstrings force consumers to read source code to
    understand behaviour, parameter expectations, and return semantics.
    Even a one-line docstring dramatically improves discoverability and
    IDE tooltip support.

    Implements the *"Readability counts"* zen principle: every public
    interface should document its contract.

    Detection uses ``ast.iter_child_nodes`` on the module root so that only
    module-level (top-level) definitions are checked — private helpers nested
    inside other functions are intentionally excluded.
    """

    @property
    def name(self) -> str:
        """Return ``"docstrings"`` for detector registry lookup.

        Returns:
            str: Registry key used to wire this detector to its rule config.
        """
        return "docstrings"

    def detect(
        self, context: AnalysisContext, config: DocstringConfig
    ) -> list[Violation]:
        """Parse the module AST and flag top-level defs lacking a docstring.

        Iterates only immediate children of the module node via
        ``ast.iter_child_nodes``.  ``FunctionDef`` and ``ClassDef`` nodes are
        checked with ``ast.get_docstring``; classes receive a higher severity
        because they typically represent broader public contracts.

        Args:
            context: Analysis context with source text to inspect.
            config: Docstring detector thresholds and rule metadata.

        Returns:
            list[Violation]: One violation per undocumented top-level
                function or class.
        """
        violations: list[Violation] = []
        message = config.select_violation_message(
            contains="Missing docstrings", index=3
        )
        try:
            tree = ast.parse(context.code)
        except SyntaxError:
            return violations

        for node in ast.iter_child_nodes(tree):
            if isinstance(node, ast.FunctionDef):
                if ast.get_docstring(node) is None:
                    loc = self.find_location_by_substring(
                        context.code, f"def {node.name}"
                    )
                    violations.append(
                        Violation(
                            principle=config.principle
                            or config.principle_id
                            or config.type,
                            severity=config.severity or 3,
                            message=message,
                            location=loc,
                            suggestion=(
                                "Add a brief docstring describing purpose and args."
                            ),
                        )
                    )
            elif isinstance(node, ast.ClassDef) and ast.get_docstring(node) is None:
                loc = self.find_location_by_substring(
                    context.code, f"class {node.name}"
                )
                violations.append(
                    Violation(
                        principle=config.principle
                        or config.principle_id
                        or config.type,
                        severity=config.severity or 4,
                        message=message,
                        location=loc,
                        suggestion=("Add class docstring describing responsibilities."),
                    )
                )
        return violations


class LineLengthDetector(ViolationDetector[LineLengthConfig], LocationHelperMixin):
    """Detect source lines that exceed a configured character limit.

    Overly long lines force horizontal scrolling in editors, break side-by-
    side diffs in code review, and often signal that a statement is doing too
    much at once.  PEP 8 recommends 79 characters; most modern projects
    settle on 88–120.

    Implements the *"Beautiful is better than ugly"* zen principle:
    consistent line length produces a visually uniform codebase.
    """

    @property
    def name(self) -> str:
        """Return ``"line_length"`` for detector registry lookup.

        Returns:
            str: Registry key used to wire this detector to its rule config.
        """
        return "line_length"

    def detect(
        self, context: AnalysisContext, config: LineLengthConfig
    ) -> list[Violation]:
        """Iterate source lines and emit a violation for each exceeding ``max_line_length``.

        The violation location column is set to ``max_len + 1`` so that
        editors highlight exactly where the overflow begins.

        Args:
            context: Analysis context carrying the source text.
            config: Line-length detector thresholds (``max_line_length``).

        Returns:
            list[Violation]: One violation per over-long line.
        """
        violations: list[Violation] = []
        max_len = config.max_line_length
        principle = config.principle or config.principle_id or config.type
        severity = config.severity or 2
        message = config.select_violation_message(contains="whitespace", index=2)

        for i, line in enumerate(context.code.splitlines(), start=1):
            if len(line) > max_len:
                loc = Location(line=i, column=max_len + 1)
                violations.append(
                    Violation(
                        principle=principle,
                        severity=severity,
                        message=message,
                        location=loc,
                        suggestion=(
                            f"Wrap or refactor to keep line <= {max_len} characters."
                        ),
                    )
                )
        return violations


class ClassSizeDetector(ViolationDetector[ClassSizeConfig], LocationHelperMixin):
    """Detect classes whose line count exceeds the configured maximum.

    Classes that grow beyond a few hundred lines tend to accumulate unrelated
    responsibilities, making them hard to understand, test, and extend.
    Splitting oversized classes into smaller, cohesive units improves
    modularity and keeps each unit within a developer's working memory.

    Implements the *"Simple is better than complex"* zen principle: small
    classes with clear responsibility boundaries are easier to reason about.

    Detection walks the AST for ``ClassDef`` nodes and measures each class
    by the span from its ``lineno`` to the ``lineno`` of its last body
    statement.
    """

    @property
    def name(self) -> str:
        """Return ``"class_size"`` for detector registry lookup.

        Returns:
            str: Registry key used to wire this detector to its rule config.
        """
        return "class_size"

    def detect(
        self, context: AnalysisContext, config: ClassSizeConfig
    ) -> list[Violation]:
        """Walk the AST and flag classes whose line span exceeds ``max_class_length``.

        Falls back to ``ast.parse`` when the pre-built ``context.ast_tree``
        is unavailable or not a stdlib ``ast.AST``.

        Args:
            context: Analysis context with source text and parsed tree.
            config: Class-size detector thresholds (``max_class_length``).

        Returns:
            list[Violation]: One violation per oversized class.
        """
        violations: list[Violation] = []
        max_lines = config.max_class_length
        principle = config.principle or config.principle_id or config.type
        severity = config.severity or 5
        message = config.select_violation_message(contains="Classes longer", index=1)

        ast_root = None
        try:
            ast_root = (
                context.ast_tree.tree
                if isinstance(context.ast_tree, ParserResult)
                else context.ast_tree
            )
        except AttributeError:
            ast_root = context.ast_tree

        if not isinstance(ast_root, ast.AST):
            try:
                ast_root = ast.parse(context.code)
            except SyntaxError:
                return violations

        for node in ast.walk(ast_root):
            if isinstance(node, ast.ClassDef):
                start = getattr(node, "lineno", None)
                end = None
                if node.body:
                    last = node.body[-1]
                    end = getattr(last, "lineno", None)
                if start is None or end is None:
                    continue

                length = end - start + 1
                if length > max_lines:
                    loc = self.ast_node_to_location(context.ast_tree, node)
                    violations.append(
                        Violation(
                            principle=principle,
                            severity=severity,
                            message=message,
                            location=loc,
                            suggestion="Split large classes into smaller cohesive units.",
                        )
                    )

        return violations


class NameStyleDetector(ViolationDetector[NameStyleConfig], LocationHelperMixin):
    """Detect function and variable names that violate Python's ``snake_case`` convention.

    PEP 8 mandates ``snake_case`` for functions and variables.  Mixing
    ``camelCase`` or other styles within a Python module confuses readers
    and clashes with the standard library's consistent naming.

    Implements the *"There should be one obvious way to do it"* zen principle:
    a single naming convention removes cognitive overhead and keeps style
    debates out of code review.

    The primary path walks the stdlib ``ast`` tree to find ``FunctionDef``
    and ``Assign`` nodes.  When parsing fails (e.g. partial code snippets),
    a regex-based heuristic fallback extracts ``def`` and assignment names
    directly from source text.
    """

    @property
    def name(self) -> str:
        """Return ``"name_style"`` for detector registry lookup.

        Returns:
            str: Registry key used to wire this detector to its rule config.
        """
        return "name_style"

    def detect(
        self, context: AnalysisContext, config: NameStyleConfig
    ) -> list[Violation]:
        """Walk the AST for non-snake_case function and variable names.

        ``FunctionDef`` nodes and ``Assign`` targets are checked against a
        ``snake_case`` regex.  ``ALL_CAPS`` constant assignments are
        intentionally skipped.  Tuple/list unpacking targets are flattened
        before checking.

        Falls back to ``_heuristic_detect`` when the AST cannot be built.

        Args:
            context: Analysis context with source text and parsed tree.
            config: Name-style detector thresholds and rule metadata.

        Returns:
            list[Violation]: One violation per non-conforming name.
        """
        violations: list[Violation] = []

        tree = None
        try:
            if context.ast_tree is not None:
                maybe_tree = getattr(context.ast_tree, "tree", context.ast_tree)
                if isinstance(maybe_tree, ast.AST):
                    tree = maybe_tree
                else:
                    tree = getattr(maybe_tree, "tree", None)
                    if tree is None:
                        tree = ast.parse(context.code)
            else:
                tree = ast.parse(context.code)
        except (AttributeError, SyntaxError):
            return self._heuristic_detect(context, config)

        principle = config.principle or config.principle_id or config.type
        severity = config.severity or 3
        message = config.select_violation_message(index=1)
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and not self._is_snake_case(node.name):
                loc = self.ast_node_to_location(
                    context.ast_tree, node
                ) or self.find_location_by_substring(context.code, f"def {node.name}")
                violations.append(
                    Violation(
                        principle=principle,
                        severity=severity,
                        message=message,
                        location=loc,
                        suggestion="Rename to snake_case to match Python conventions.",
                    )
                )

            if isinstance(node, ast.Assign):
                for target in self._iter_assignment_targets(node.targets):
                    if isinstance(target, ast.Name):
                        name = target.id
                        if name.isupper():
                            continue
                        if not self._is_snake_case(name):
                            loc = self.ast_node_to_location(
                                context.ast_tree, target
                            ) or self.find_location_by_substring(
                                context.code, f"{name} ="
                            )
                            violations.append(
                                Violation(
                                    principle=principle,
                                    severity=severity,
                                    message=message,
                                    location=loc,
                                    suggestion="Use snake_case for variable names.",
                                )
                            )

        return violations

    def _iter_assignment_targets(
        self, targets: Iterable[ast.expr]
    ) -> Iterable[ast.expr]:
        """Flatten compound assignment targets into individual ``ast.Name`` nodes.

        Handles tuple and list unpacking so that ``a, b = 1, 2`` checks both
        ``a`` and ``b`` independently.

        Args:
            targets: Top-level assignment target nodes from an ``ast.Assign``.

        Returns:
            Iterable[ast.expr]: Stream of leaf target nodes.
        """
        for t in targets:
            if isinstance(t, (ast.Tuple, ast.List)):
                yield from getattr(t, "elts", [])
            else:
                yield t

    def _heuristic_detect(
        self, context: AnalysisContext, config: NameStyleConfig
    ) -> list[Violation]:
        """Regex fallback for name-style checking when AST parsing fails.

        Scans raw source text for ``def`` declarations and top-level
        assignments, applying the same ``snake_case`` validation as the
        AST-based path.

        Args:
            context: Analysis context with the (unparseable) source text.
            config: Name-style detector thresholds and rule metadata.

        Returns:
            list[Violation]: Violations found via heuristic matching.
        """
        violations: list[Violation] = []
        principle = config.principle or config.principle_id or config.type
        severity = config.severity or 3
        message = config.select_violation_message(index=1)
        for m in re.finditer(r"^def\s+([A-Za-z0-9_]+)", context.code, flags=re.M):
            name = m.group(1)
            if not self._is_snake_case(name):
                loc = self.find_location_by_substring(context.code, f"def {name}")
                violations.append(
                    Violation(
                        principle=principle,
                        severity=severity,
                        message=message,
                        location=loc,
                        suggestion="Rename to snake_case to match Python conventions.",
                    )
                )

        for m in re.finditer(r"^([A-Za-z0-9_]+)\s*=", context.code, flags=re.M):
            name = m.group(1)
            if name.isupper():
                continue
            if not self._is_snake_case(name):
                loc = self.find_location_by_substring(context.code, f"{name} =")
                violations.append(
                    Violation(
                        principle=principle,
                        severity=severity,
                        message=message,
                        location=loc,
                        suggestion="Use snake_case for variable names.",
                    )
                )

        return violations

    def _is_snake_case(self, name: str) -> bool:
        """Test whether *name* matches the ``_?[a-z][a-z0-9_]*`` snake_case pattern.

        Args:
            name: Identifier string to validate.

        Returns:
            bool: ``True`` when *name* is valid snake_case.
        """
        return bool(re.match(r"^_?[a-z][a-z0-9_]*$", name))


class ShortVariableNamesDetector(
    ViolationDetector[ShortVariableNamesConfig], LocationHelperMixin
):
    """Detect variables and loop targets with names shorter than the configured minimum.

    Single-letter variables like ``x``, ``d``, or ``n`` obscure intent and
    make grep-based navigation unreliable.  Descriptive names (``index``,
    ``data``, ``count``) are self-documenting and reduce the need for
    inline comments.

    Implements the *"Readability counts"* zen principle: code is read far
    more often than it is written, so names should communicate purpose.

    Detection walks the AST for ``Assign``, ``AnnAssign``, ``AugAssign``,
    ``For``, and ``AsyncFor`` nodes.  ``ALL_CAPS`` constants and a
    configurable allow-list of conventional loop names (``i``, ``j``, ``k``,
    ``_``) are excluded.  Falls back to regex heuristics on parse failure.
    """

    @property
    def name(self) -> str:
        """Return ``"short_variable_names"`` for detector registry lookup.

        Returns:
            str: Registry key used to wire this detector to its rule config.
        """
        return "short_variable_names"

    def detect(
        self, context: AnalysisContext, config: ShortVariableNamesConfig
    ) -> list[Violation]:
        """Walk the AST and flag identifiers shorter than ``min_identifier_length``.

        Assignment targets (including tuple/list unpacking), annotated
        assignments, augmented assignments, and ``for``/``async for`` loop
        variables are all inspected.  ``ALL_CAPS`` constants and names in
        ``allowed_loop_names`` are skipped.

        Args:
            context: Analysis context with source text and parsed tree.
            config: Short-name detector thresholds (``min_identifier_length``,
                ``allowed_loop_names``).

        Returns:
            list[Violation]: One violation per overly short identifier.
        """
        violations: list[Violation] = []
        min_len = config.min_identifier_length
        allowed_loop_names = set(config.allowed_loop_names)
        try:
            tree = (
                context.ast_tree.tree
                if isinstance(context.ast_tree, ParserResult)
                else context.ast_tree
            )
            if not isinstance(tree, ast.AST):
                tree = ast.parse(context.code)
        except (AttributeError, SyntaxError):
            return self._heuristic_detect(context, config)

        for node in ast.walk(tree):
            if isinstance(node, (ast.Assign, ast.AnnAssign, ast.AugAssign)):
                targets = []
                if isinstance(node, ast.Assign):
                    targets = list(self._iter_assignment_targets(node.targets))
                else:
                    targets = [getattr(node, "target", None)]
                for target in targets:
                    if isinstance(target, ast.Name):
                        name = target.id
                        if name.isupper():
                            continue
                        if len(name) < min_len:
                            loc = self.ast_node_to_location(
                                context.ast_tree, target
                            ) or self.find_location_by_substring(
                                context.code, f"{name} ="
                            )
                            violations.append(
                                self.build_violation(
                                    config,
                                    contains=name,
                                    index=0,
                                    location=loc,
                                    suggestion=(
                                        "Use descriptive variable names for readability."
                                    ),
                                )
                            )
            elif isinstance(node, (ast.For, ast.AsyncFor)):
                target = node.target
                if isinstance(target, ast.Name):
                    name = target.id
                    if name.isupper() or name in allowed_loop_names:
                        continue
                    if len(name) < min_len:
                        loc = self.ast_node_to_location(context.ast_tree, target)
                        violations.append(
                            self.build_violation(
                                config,
                                contains=name,
                                index=0,
                                location=loc,
                                suggestion=(
                                    "Use descriptive loop variables instead of short names."
                                ),
                            )
                        )
        return violations

    def _heuristic_detect(
        self, context: AnalysisContext, config: ShortVariableNamesConfig
    ) -> list[Violation]:
        """Regex fallback for short-name detection when AST parsing fails.

        Matches top-level ``name = …`` assignments and applies the same
        length check, skipping ``ALL_CAPS`` constants.

        Args:
            context: Analysis context with the (unparseable) source text.
            config: Short-name detector thresholds.

        Returns:
            list[Violation]: Violations found via heuristic matching.
        """
        violations: list[Violation] = []
        min_len = config.min_identifier_length
        for match in re.finditer(r"^(\w+)\s*=", context.code, flags=re.M):
            name = match.group(1)
            if name.isupper() or len(name) >= min_len:
                continue
            loc = self.find_location_by_substring(context.code, f"{name} =")
            violations.append(
                self.build_violation(
                    config,
                    contains=name,
                    index=0,
                    location=loc,
                    suggestion="Use descriptive variable names for readability.",
                )
            )
        return violations

    def _iter_assignment_targets(
        self, targets: Iterable[ast.expr]
    ) -> Iterable[ast.expr]:
        """Flatten compound assignment targets for short-name checking.

        Unpacks ``ast.Tuple`` and ``ast.List`` nodes so that each element
        is evaluated individually.

        Args:
            targets: Top-level assignment target nodes from an ``ast.Assign``.

        Returns:
            Iterable[ast.expr]: Stream of leaf target nodes.
        """
        for t in targets:
            if isinstance(t, (ast.Tuple, ast.List)):
                yield from getattr(t, "elts", [])
            else:
                yield t


class CyclomaticComplexityDetector(
    ViolationDetector[CyclomaticComplexityConfig], LocationHelperMixin
):
    """Detect functions whose cyclomatic complexity exceeds the configured threshold.

    Cyclomatic complexity counts the number of independent execution paths
    through a function.  High values correlate strongly with bug density and
    make unit testing exponentially harder because each path requires at
    least one test case.

    Implements the *"Simple is better than complex"* zen principle:
    functions with low branching are easier to read, test, and maintain.

    Detection reads the pre-computed ``context.cyclomatic_summary`` (populated
    by radon via ``MetricsCollector``).  Both the module-wide average *and*
    individual function blocks are checked.  Per-block severity is scaled by
    how far the complexity exceeds the threshold.
    """

    @property
    def name(self) -> str:
        """Return ``"cyclomatic_complexity"`` for detector registry lookup.

        Returns:
            str: Registry key used to wire this detector to its rule config.
        """
        return "cyclomatic_complexity"

    def detect(
        self, context: AnalysisContext, config: CyclomaticComplexityConfig
    ) -> list[Violation]:
        """Check module-wide average and per-function cyclomatic complexity.

        When the module average exceeds ``max_cyclomatic_complexity``, a
        violation is emitted at the first ``def`` location.  Individual
        function blocks that exceed the threshold also produce violations
        with severity scaled proportionally to the overshoot.

        Args:
            context: Analysis context with a pre-computed
                ``cyclomatic_summary``.
            config: Cyclomatic-complexity detector thresholds.

        Returns:
            list[Violation]: One violation per over-complex function, plus
                optionally one for the module-wide average.
        """
        violations: list[Violation] = []

        if context.cyclomatic_summary is None:
            return violations

        avg = context.cyclomatic_summary.average
        max_allowed = config.max_cyclomatic_complexity
        principle = _principle_text(config)
        base_severity = _severity_level(config)

        if avg > max_allowed:
            location = self._find_first_function_location(context)
            violations.append(
                Violation(
                    principle=principle,
                    severity=base_severity,
                    message=_violation_message(config, contains="cyclomatic", index=0),
                    location=location,
                    suggestion="Reduce branching and split complex functions into smaller units.",
                )
            )

        for block in context.cyclomatic_summary.blocks or []:
            if block.complexity > max_allowed:
                loc = Location(line=block.lineno, column=1)
                delta = max(block.complexity - max_allowed, 0)
                severity = min(9, base_severity + delta)
                violations.append(
                    Violation(
                        principle=principle,
                        severity=severity,
                        message=_violation_message(
                            config, contains="cyclomatic", index=0
                        ),
                        location=loc,
                        suggestion="Consider refactoring this function to reduce branching.",
                    )
                )

        return violations

    def _find_first_function_location(self, context: AnalysisContext) -> Location:
        """Locate the first ``def`` statement for module-level violation reporting.

        Attempts AST-based lookup first, falling back to a substring scan
        for ``def `` in the raw source.

        Args:
            context: Analysis context with source text and parsed tree.

        Returns:
            Location: Source location of the first function definition.
        """
        if context.ast_tree:
            try:
                tree = (
                    context.ast_tree.tree
                    if isinstance(context.ast_tree, ParserResult)
                    else context.ast_tree
                )

                if isinstance(tree, ast.AST):
                    for node in ast.walk(tree):
                        if isinstance(node, ast.FunctionDef) and (
                            loc := self.ast_node_to_location(context.ast_tree, node)
                        ):
                            return loc
            except (AttributeError, TypeError):
                pass

        return self.find_location_by_substring(context.code, "def ")


class NestingDepthDetector(ViolationDetector[NestingDepthConfig], LocationHelperMixin):
    """Detect code blocks with excessive indentation depth and nested loops.

    Deeply nested code forces readers to maintain a large mental stack of
    conditions and scopes.  Beyond three levels, bugs hide in corner cases
    that are nearly impossible to reason about during review.

    Implements the *"Flat is better than nested"* zen principle: early
    returns, guard clauses, and helper functions keep nesting shallow.

    Two checks are performed:

    1. Indentation-based nesting depth via ``detect_deep_nesting``.
    2. AST-based loop nesting depth — nested ``for``/``while`` loops beyond
       depth 1 are flagged separately.
    """

    @property
    def name(self) -> str:
        """Return ``"nesting_depth"`` for detector registry lookup.

        Returns:
            str: Registry key used to wire this detector to its rule config.
        """
        return "nesting_depth"

    def detect(
        self, context: AnalysisContext, config: NestingDepthConfig
    ) -> list[Violation]:
        """Check indentation depth and loop nesting against thresholds.

        First delegates to ``detect_deep_nesting`` for an indentation-based
        measurement.  Then separately computes the maximum loop nesting depth
        via AST traversal and flags anything beyond depth 1.

        Args:
            context: Analysis context with source text and parsed tree.
            config: Nesting-depth detector thresholds (``max_nesting_depth``).

        Returns:
            list[Violation]: Up to two violations — one for general nesting,
                one for loop nesting.
        """
        from mcp_zen_of_languages.rules.detections import detect_deep_nesting

        violations: list[Violation] = []
        max_allowed = config.max_nesting_depth
        principle = _principle_text(config)
        severity = _severity_level(config)

        is_deep, _depth = detect_deep_nesting(context.code, max_allowed)
        if is_deep:
            location = self._find_nested_location(context)
            violations.append(
                Violation(
                    principle=principle,
                    severity=severity,
                    message=_violation_message(
                        config, contains="Nesting depth", index=0
                    ),
                    location=location,
                    suggestion=(
                        "Refactor deeply nested blocks into smaller functions or use early returns."
                    ),
                )
            )
        loop_depth = self._max_loop_depth(context)
        if loop_depth > 1:
            location = self.find_location_by_substring(
                context.code, "for "
            ) or self.find_location_by_substring(context.code, "while ")
            violations.append(
                Violation(
                    principle=principle,
                    severity=severity,
                    message=_violation_message(
                        config, contains="nested loops", index=0
                    ),
                    location=location,
                    suggestion="Flatten nested loops or extract inner logic.",
                )
            )

        return violations

    def _find_nested_location(self, context: AnalysisContext) -> Location:
        """Locate the first deeply-indented line as the violation anchor.

        Uses a simple heuristic — searches for the first line starting with
        four spaces — since the exact threshold-exceeding line is not tracked
        by ``detect_deep_nesting``.

        Args:
            context: Analysis context with the source text to scan.

        Returns:
            Location: Approximate source location of the deepest nesting.
        """
        return self.find_location_by_substring(context.code, "    ")

    def _max_loop_depth(self, context: AnalysisContext) -> int:
        """Compute the maximum depth of nested ``for``/``while`` loops via AST traversal.

        Recursively walks the tree, incrementing depth at each loop node
        and tracking the maximum seen across all branches.

        Args:
            context: Analysis context with source text and parsed tree.

        Returns:
            int: Deepest loop nesting level (0 means no loops).
        """
        try:
            tree = (
                context.ast_tree.tree
                if isinstance(context.ast_tree, ParserResult)
                else context.ast_tree
            )
            if not isinstance(tree, ast.AST):
                tree = ast.parse(context.code)
        except (AttributeError, SyntaxError):
            return 0

        def walk(node: ast.AST, depth: int) -> int:
            """Recurse through AST children, counting loop nesting depth.

            Args:
                node: Current AST node being visited.
                depth: Accumulated loop nesting depth at this point.

            Returns:
                int: Maximum loop depth encountered in this subtree.
            """
            current = depth
            if isinstance(node, (ast.For, ast.AsyncFor, ast.While)):
                current += 1
            max_depth = current
            for child in ast.iter_child_nodes(node):
                max_depth = max(max_depth, walk(child, current))
            return max_depth

        return walk(tree, 0)


class LongFunctionDetector(ViolationDetector[LongFunctionConfig], LocationHelperMixin):
    """Detect functions whose line count exceeds the configured maximum.

    Long functions tend to do too much — mixing input validation, business
    logic, side effects, and formatting in a single scope.  Shorter functions
    with descriptive names serve as self-documenting building blocks that are
    individually testable.

    Implements the *"Simple is better than complex"* zen principle:
    small, focused functions are the foundation of maintainable code.

    Detection delegates to ``detect_long_functions`` which measures each
    ``def`` block by line span.
    """

    @property
    def name(self) -> str:
        """Return ``"long_functions"`` for detector registry lookup.

        Returns:
            str: Registry key used to wire this detector to its rule config.
        """
        return "long_functions"

    def detect(
        self, context: AnalysisContext, config: LongFunctionConfig
    ) -> list[Violation]:
        """Delegate to ``detect_long_functions`` and emit violations for oversized defs.

        Each function exceeding ``max_function_length`` lines produces one
        violation pinpointed to its ``def`` statement.

        Args:
            context: Analysis context with source text and parsed tree.
            config: Long-function detector thresholds (``max_function_length``).

        Returns:
            list[Violation]: One violation per oversized function.
        """
        from mcp_zen_of_languages.rules.detections import detect_long_functions

        violations: list[Violation] = []
        max_lines = config.max_function_length
        principle = _principle_text(config)
        severity = _severity_level(config)

        long_functions = detect_long_functions(code=context.code, max_lines=max_lines)

        for name, _length in long_functions:
            location = self._find_function_location(context, name)
            violations.append(
                Violation(
                    principle=principle,
                    severity=severity,
                    message=_violation_message(
                        config, contains="Functions longer", index=0
                    ),
                    location=location,
                    suggestion="Split large functions into smaller, focused helpers.",
                )
            )

        return violations

    def _find_function_location(
        self, context: AnalysisContext, func_name: str
    ) -> Location:
        """Locate a specific function definition by name for violation anchoring.

        Tries AST-based lookup first, falling back to a substring search for
        the function name in the raw source.

        Args:
            context: Analysis context with source text and parsed tree.
            func_name: Name of the function to locate.

        Returns:
            Location: Source location of the named function's ``def`` line.
        """
        if context.ast_tree:
            try:
                tree = (
                    context.ast_tree.tree
                    if isinstance(context.ast_tree, ParserResult)
                    else context.ast_tree
                )

                if isinstance(tree, ast.AST):
                    for node in ast.walk(tree):
                        if (
                            isinstance(node, ast.FunctionDef)
                            and node.name == func_name
                            and (
                                loc := self.ast_node_to_location(context.ast_tree, node)
                            )
                        ):
                            return loc
            except (AttributeError, TypeError):
                pass

        return self.find_location_by_substring(context.code, func_name)


class GodClassDetector(ViolationDetector[GodClassConfig]):
    """Detect God classes — classes with too many methods or lines of code.

    A God class absorbs responsibilities that should be distributed across
    several smaller collaborating classes.  They become magnets for change,
    difficult to test in isolation, and resistant to parallel development.

    Implements the *"Simple is better than complex"* zen principle:
    each class should have a single, well-defined responsibility.

    Detection delegates to ``detect_god_classes`` which counts methods and
    measures line span per class, comparing against ``max_methods`` and
    ``max_class_length``.
    """

    @property
    def name(self) -> str:
        """Return ``"god_classes"`` for detector registry lookup.

        Returns:
            str: Registry key used to wire this detector to its rule config.
        """
        return "god_classes"

    def detect(
        self, context: AnalysisContext, config: GodClassConfig
    ) -> list[Violation]:
        """Delegate to ``detect_god_classes`` and flag classes that breach thresholds.

        Args:
            context: Analysis context with source text.
            config: God-class detector thresholds (``max_methods``,
                ``max_class_length``).

        Returns:
            list[Violation]: One violation per God class found.
        """
        from mcp_zen_of_languages.rules.detections import detect_god_classes

        violations: list[Violation] = []
        max_methods = config.max_methods
        max_lines = config.max_class_length
        principle = _principle_text(config)
        severity = _severity_level(config)

        god_classes = detect_god_classes(
            context.code, max_methods=max_methods, max_lines=max_lines
        )

        violations.extend(
            Violation(
                principle=principle,
                severity=severity,
                message=_violation_message(config, contains="Classes longer", index=1),
                suggestion="Break the large class into smaller cohesive classes.",
            )
            for _ in god_classes
        )
        return violations


class MagicMethodDetector(ViolationDetector[MagicMethodConfig], LocationHelperMixin):
    """Detect classes that overload too many dunder (magic) methods.

    While dunder methods are powerful, overusing them creates an opaque API
    where the behaviour of operators like ``+``, ``[]``, and ``==`` becomes
    hard to predict.  A class implementing more than a handful of magic
    methods is often trying to act like a built-in type and should instead
    expose explicit method names.

    Implements the *"Explicit is better than implicit"* zen principle:
    prefer named methods over operator overloading for non-obvious semantics.

    Detection delegates to ``detect_magic_methods_overuse`` which collects
    all ``__dunder__`` method definitions per class, then flags classes
    exceeding ``max_magic_methods``.
    """

    @property
    def name(self) -> str:
        """Return ``"magic_methods"`` for detector registry lookup.

        Returns:
            str: Registry key used to wire this detector to its rule config.
        """
        return "magic_methods"

    def detect(
        self, context: AnalysisContext, config: MagicMethodConfig
    ) -> list[Violation]:
        """Count dunder method definitions and flag when exceeding the threshold.

        The violation is anchored at the first ``def __`` occurrence in the
        source to guide the developer to the most relevant class.

        Args:
            context: Analysis context with source text.
            config: Magic-method detector thresholds (``max_magic_methods``).

        Returns:
            list[Violation]: At most one violation when the count exceeds the
                configured maximum.
        """
        from mcp_zen_of_languages.rules.detections import detect_magic_methods_overuse

        violations: list[Violation] = []

        magic_methods = detect_magic_methods_overuse(context.code)
        max_allowed = config.max_magic_methods
        principle = _principle_text(config)
        severity = _severity_level(config)

        if len(magic_methods) > max_allowed:
            location = self.find_location_by_substring(context.code, "def __")
            violations.append(
                Violation(
                    principle=principle,
                    severity=severity,
                    message=_violation_message(config, contains="magic", index=2),
                    location=location,
                    suggestion="Avoid excessive operator overloading; prefer explicit APIs.",
                )
            )

        return violations


class CircularDependencyDetector(ViolationDetector[CircularDependencyConfig]):
    """Detect circular import dependencies across modules.

    Circular imports are a common source of ``ImportError`` at runtime and
    indicate tangled module responsibilities.  They also prevent clean
    layering and make it impossible to understand a module in isolation.

    Implements the *"Flat is better than nested"* zen principle applied to
    the dependency graph: modules should form a directed acyclic graph.

    Detection uses the pre-built ``context.dependency_analysis`` graph edges
    and delegates cycle-finding to ``detect_dependency_cycles``, which
    performs a topological sort and reports back-edges.
    """

    @property
    def name(self) -> str:
        """Return ``"circular_dependencies"`` for detector registry lookup.

        Returns:
            str: Registry key used to wire this detector to its rule config.
        """
        return "circular_dependencies"

    def detect(
        self, context: AnalysisContext, config: CircularDependencyConfig
    ) -> list[Violation]:
        """Extract dependency graph edges and flag any import cycles.

        Skips detection entirely when no ``dependency_analysis`` is available
        (single-file mode without repository context).

        Args:
            context: Analysis context with a pre-built dependency graph.
            config: Circular-dependency detector thresholds and rule metadata.

        Returns:
            list[Violation]: One violation per import cycle detected.
        """
        from mcp_zen_of_languages.rules.detections import detect_dependency_cycles

        violations: list[Violation] = []

        if context.dependency_analysis is None:
            return violations

        edges = getattr(context.dependency_analysis, "edges", None)
        if not edges:
            return violations

        cycles = detect_dependency_cycles(edges)
        principle = _principle_text(config)
        severity = _severity_level(config)

        violations.extend(
            Violation(
                principle=principle,
                severity=severity,
                message=_violation_message(config, contains="dependencies", index=0),
                suggestion="Refactor to break cycles or introduce interfaces/abstractions.",
            )
            for _ in cycles
        )
        return violations


class DeepInheritanceDetector(ViolationDetector[DeepInheritanceConfig]):
    """Detect class hierarchies that exceed a safe inheritance depth.

    Deep inheritance chains (more than two or three levels) create fragile
    base-class coupling, make method resolution order hard to predict, and
    encourage overriding rather than composing.  Composition via delegation
    or mixins keeps each class understandable in isolation.

    Implements the *"Flat is better than nested"* zen principle applied to
    type hierarchies: shallow, wide hierarchies beat deep, narrow ones.

    Detection requires multi-file context (``context.other_files``).  It
    delegates to ``detect_deep_inheritance`` which traces class parents
    across all provided source files.
    """

    @property
    def name(self) -> str:
        """Return ``"deep_inheritance"`` for detector registry lookup.

        Returns:
            str: Registry key used to wire this detector to its rule config.
        """
        return "deep_inheritance"

    def detect(
        self, context: AnalysisContext, config: DeepInheritanceConfig
    ) -> list[Violation]:
        """Trace class parent chains across files and flag excessive depth.

        Requires ``context.other_files`` for cross-file class resolution;
        returns an empty list in single-file mode.

        Args:
            context: Analysis context with source text and sibling file map.
            config: Deep-inheritance detector thresholds and rule metadata.

        Returns:
            list[Violation]: One violation per inheritance chain exceeding the
                configured depth.
        """
        from mcp_zen_of_languages.rules.detections import detect_deep_inheritance

        violations: list[Violation] = []

        if not context.other_files:
            return violations

        all_files = {
            **(context.other_files or {}),
            (context.path or "<current>"): context.code,
        }
        inheritance_chains = detect_deep_inheritance(all_files)
        principle = _principle_text(config)
        severity = _severity_level(config)

        violations.extend(
            Violation(
                principle=principle,
                severity=severity,
                message=_violation_message(config, contains="inheritance", index=1),
                suggestion="Favor composition over deep inheritance.",
            )
            for _ in inheritance_chains
        )
        return violations


class FeatureEnvyDetector(ViolationDetector[FeatureEnvyConfig]):
    """Detect methods that access another object's data more than their own.

    Feature envy is a classic code smell where a method in class A
    repeatedly reaches into class B's attributes.  This suggests the method
    belongs on B (or on a shared helper) rather than A, and its presence on
    A couples the two classes unnecessarily.

    Implements the *"There should be one obvious way to do it"* zen
    principle: behaviour should live next to the data it operates on.

    Detection delegates to ``detect_feature_envy`` and filters results by
    ``min_occurrences`` to avoid flagging incidental cross-object access.
    """

    @property
    def name(self) -> str:
        """Return ``"feature_envy"`` for detector registry lookup.

        Returns:
            str: Registry key used to wire this detector to its rule config.
        """
        return "feature_envy"

    def detect(
        self, context: AnalysisContext, config: FeatureEnvyConfig
    ) -> list[Violation]:
        """Identify methods excessively accessing another object's attributes.

        Results from ``detect_feature_envy`` are filtered by
        ``min_occurrences`` to suppress noise from incidental attribute
        reads.

        Args:
            context: Analysis context with source text.
            config: Feature-envy detector thresholds (``min_occurrences``).

        Returns:
            list[Violation]: One violation per envious method exceeding the
                occurrence threshold.
        """
        from mcp_zen_of_languages.rules.detections import detect_feature_envy

        violations: list[Violation] = []
        min_occurrences = config.min_occurrences
        principle = _principle_text(config)
        severity = _severity_level(config)

        feature_envies = detect_feature_envy(context.code)
        feature_envies = [
            e for e in feature_envies if getattr(e, "occurrences", 0) >= min_occurrences
        ]

        violations.extend(
            Violation(
                principle=principle,
                severity=severity,
                message=_violation_message(
                    config, contains="Multiple implementations", index=3
                ),
                suggestion="Consider moving the method to the target class or extracting a helper.",
            )
            for _ in feature_envies
        )
        return violations


class DuplicateImplementationDetector(ViolationDetector[DuplicateImplementationConfig]):
    """Detect identical or near-identical function implementations across files.

    Copy-pasted logic creates a maintenance multiplier — every bug fix or
    feature change must be applied in multiple places, and divergence over
    time turns copies into subtle variants with different edge-case handling.

    Implements the *"There should be one obvious way to do it"* zen
    principle: shared logic should live in a single canonical location.

    Detection requires multi-file context (``context.other_files``).  It
    delegates to ``detect_multiple_implementations`` which compares function
    bodies across the provided source map.
    """

    @property
    def name(self) -> str:
        """Return ``"duplicate_implementations"`` for detector registry lookup.

        Returns:
            str: Registry key used to wire this detector to its rule config.
        """
        return "duplicate_implementations"

    def detect(
        self, context: AnalysisContext, config: DuplicateImplementationConfig
    ) -> list[Violation]:
        """Compare function bodies across files and flag duplicates.

        Merges ``context.other_files`` with the current file, then delegates
        to ``detect_multiple_implementations``.  Skips detection in
        single-file mode.

        Args:
            context: Analysis context with source text and sibling file map.
            config: Duplicate-implementation detector thresholds and rule
                metadata.

        Returns:
            list[Violation]: One violation per group of duplicated functions,
                with the ``files`` field listing affected paths.
        """
        from mcp_zen_of_languages.rules.detections import (
            detect_multiple_implementations,
        )

        violations: list[Violation] = []

        if not context.other_files:
            return violations

        all_files = {
            **(context.other_files or {}),
            (context.path or "<current>"): context.code,
        }
        duplicates = detect_multiple_implementations(all_files)
        principle = _principle_text(config)
        severity = _severity_level(config)

        violations.extend(
            Violation(
                principle=principle,
                severity=severity,
                message=_violation_message(
                    config, contains="Multiple implementations", index=3
                ),
                files=duplicate.files,
                suggestion="Consolidate duplicated implementations into a single utility or module.",
            )
            for duplicate in duplicates
        )
        return violations


class SparseCodeDetector(ViolationDetector[SparseCodeConfig], LocationHelperMixin):
    """Detect lines packing multiple statements separated by semicolons.

    Cramming several statements onto one line (``x = 1; y = 2; z = 3``)
    makes code harder to read, harder to step through in a debugger, and
    breaks the one-statement-per-line convention that most Python style
    guides assume.

    Implements the *"Sparse is better than dense"* zen principle:
    each line should do one thing clearly.

    Detection delegates to ``detect_sparse_code`` which counts semicolon-
    separated statements per line and reports those exceeding
    ``max_statements_per_line``.
    """

    @property
    def name(self) -> str:
        """Return ``"sparse_code"`` for detector registry lookup.

        Returns:
            str: Registry key used to wire this detector to its rule config.
        """
        return "sparse_code"

    def detect(
        self, context: AnalysisContext, config: SparseCodeConfig
    ) -> list[Violation]:
        """Flag lines containing more than ``max_statements_per_line`` statements.

        Args:
            context: Analysis context with source text.
            config: Sparse-code detector thresholds (``max_statements_per_line``).

        Returns:
            list[Violation]: One violation per overly dense line.
        """
        from mcp_zen_of_languages.rules.detections import detect_sparse_code

        violations: list[Violation] = []
        max_statements = config.max_statements_per_line
        principle = _principle_text(config)
        severity = _severity_level(config)

        for finding in detect_sparse_code(context.code, max_statements):
            loc = Location(line=finding.line, column=1)
            violations.append(
                Violation(
                    principle=principle,
                    severity=severity,
                    message=_violation_message(
                        config, contains="Multiple statements", index=0
                    ),
                    location=loc,
                    suggestion="Split statements across lines to improve readability.",
                )
            )

        return violations


class ConsistencyDetector(ViolationDetector[ConsistencyConfig], LocationHelperMixin):
    """Detect mixed naming conventions within a single module.

    A module that uses both ``camelCase`` and ``snake_case`` (or other
    styles) signals either multiple authors with different habits or
    unfinished refactoring.  Inconsistency forces readers to context-switch
    between conventions and erodes trust in the codebase.

    Implements the *"There should be one obvious way to do it"* zen
    principle: pick one naming style and apply it everywhere.

    Detection delegates to ``detect_inconsistent_naming_styles`` and flags
    when the number of distinct styles exceeds ``max_naming_styles``.
    """

    @property
    def name(self) -> str:
        """Return ``"consistency"`` for detector registry lookup.

        Returns:
            str: Registry key used to wire this detector to its rule config.
        """
        return "consistency"

    def detect(
        self, context: AnalysisContext, config: ConsistencyConfig
    ) -> list[Violation]:
        """Count distinct naming styles and flag when too many coexist.

        The violation is anchored at the first ``def`` statement since naming
        inconsistency is inherently module-wide rather than localised.

        Args:
            context: Analysis context with source text.
            config: Consistency detector thresholds (``max_naming_styles``).

        Returns:
            list[Violation]: At most one violation when the style count
                exceeds the threshold.
        """
        from mcp_zen_of_languages.rules.detections import (
            detect_inconsistent_naming_styles,
        )

        violations: list[Violation] = []
        max_styles = config.max_naming_styles
        principle = _principle_text(config)
        severity = _severity_level(config)

        findings = detect_inconsistent_naming_styles(context.code)
        if findings and len(findings[0].naming_styles) > max_styles:
            loc = self.find_location_by_substring(context.code, "def ")
            violations.append(
                Violation(
                    principle=principle,
                    severity=severity,
                    message=_violation_message(
                        config, contains="Different naming", index=1
                    ),
                    location=loc,
                    suggestion="Use a single naming style consistently (e.g., snake_case).",
                )
            )

        return violations


class ExplicitnessDetector(ViolationDetector[ExplicitnessConfig], LocationHelperMixin):
    """Detect function parameters missing type annotations.

    Type hints are the primary documentation channel for Python function
    contracts.  Without them, callers must read the implementation to discover
    expected types, and static analysis tools like mypy and pyright cannot
    verify call-site correctness.

    Implements the *"Explicit is better than implicit"* zen principle:
    annotated signatures make interfaces self-describing and machine-
    checkable.

    Detection is gated on ``config.require_type_hints`` and delegates to
    ``detect_missing_type_hints`` which parses function signatures for
    un-annotated parameters.
    """

    @property
    def name(self) -> str:
        """Return ``"explicitness"`` for detector registry lookup.

        Returns:
            str: Registry key used to wire this detector to its rule config.
        """
        return "explicitness"

    def detect(
        self, context: AnalysisContext, config: ExplicitnessConfig
    ) -> list[Violation]:
        """Scan function signatures for un-annotated parameters.

        No-ops when ``config.require_type_hints`` is ``False``, allowing
        projects to opt out of this check.

        Args:
            context: Analysis context with source text.
            config: Explicitness detector thresholds (``require_type_hints``).

        Returns:
            list[Violation]: One violation per function with missing type
                annotations.
        """
        if not config.require_type_hints:
            return []

        from mcp_zen_of_languages.rules.detections import detect_missing_type_hints

        violations: list[Violation] = []
        principle = _principle_text(config)
        severity = _severity_level(config)

        for finding in detect_missing_type_hints(context.code):
            loc = self.find_location_by_substring(
                context.code, f"def {finding.function}"
            )
            violations.append(
                Violation(
                    principle=principle,
                    severity=severity,
                    message=_violation_message(
                        config, contains="Missing input", index=2
                    ),
                    location=loc,
                    suggestion="Add explicit type hints to function parameters.",
                )
            )

        return violations


class NamespaceUsageDetector(ViolationDetector[NamespaceConfig], LocationHelperMixin):
    """Detect modules with too many top-level symbols or ``__all__`` exports.

    A module that defines dozens of public names is likely doing too much
    and should be split into sub-modules.  Overly large ``__all__`` lists
    signal the same problem from the export side.  Keeping modules focused
    makes imports predictable and navigation fast.

    Implements the *"Namespaces are one honking great idea"* zen principle:
    each module should own a narrow, well-defined slice of the namespace.

    Detection delegates to ``detect_namespace_usage`` which counts top-level
    symbols and ``__all__`` entries, comparing against ``max_top_level_symbols``
    and ``max_exports``.
    """

    @property
    def name(self) -> str:
        """Return ``"namespace_usage"`` for detector registry lookup.

        Returns:
            str: Registry key used to wire this detector to its rule config.
        """
        return "namespace_usage"

    def detect(
        self, context: AnalysisContext, config: NamespaceConfig
    ) -> list[Violation]:
        """Count top-level symbols and ``__all__`` entries against thresholds.

        Two independent checks are performed: one for total top-level symbol
        count and one for ``__all__`` export count.  Either or both may fire.

        Args:
            context: Analysis context with source text.
            config: Namespace detector thresholds (``max_top_level_symbols``,
                ``max_exports``).

        Returns:
            list[Violation]: Up to two violations — one for symbols, one for
                exports.
        """
        from mcp_zen_of_languages.rules.detections import detect_namespace_usage

        violations: list[Violation] = []
        principle = _principle_text(config)
        severity = _severity_level(config)

        finding = detect_namespace_usage(context.code)
        if finding.top_level_symbols > config.max_top_level_symbols:
            violations.append(
                Violation(
                    principle=principle,
                    severity=severity,
                    message=_violation_message(config, contains="Polluting", index=0),
                    suggestion="Refactor to reduce module-level symbols or split the module.",
                )
            )
        if (
            finding.export_count is not None
            and finding.export_count > config.max_exports
        ):
            violations.append(
                Violation(
                    principle=principle,
                    severity=severity,
                    message=_violation_message(config, contains="__all__", index=1),
                    suggestion="Reduce __all__ exports or split the module into submodules.",
                )
            )

        return violations


__all__ = [
    "BareExceptDetector",
    "CircularDependencyDetector",
    "ClassSizeDetector",
    "ComplexOneLinersDetector",
    "ConsistencyDetector",
    "ContextManagerDetector",
    "CyclomaticComplexityDetector",
    "DeepInheritanceDetector",
    "DocstringDetector",
    "DuplicateImplementationDetector",
    "ExplicitnessDetector",
    "FeatureEnvyDetector",
    "GodClassDetector",
    "LineLengthDetector",
    "LongFunctionDetector",
    "MagicMethodDetector",
    "MagicNumberDetector",
    "NameStyleDetector",
    "NamespaceUsageDetector",
    "NestingDepthDetector",
    "ShortVariableNamesDetector",
    "SparseCodeDetector",
    "StarImportDetector",
]
