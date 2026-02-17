"""Heuristic detection helpers for Python and TypeScript zen principles.

Each function in this module implements a lightweight, regex- or AST-based
check that the ``DetectionPipeline`` (or the legacy ``RulesAdapter``) calls
to discover specific code smells.  Return types are Pydantic models so
that downstream consumers get typed, serialisable results.

Note:
    These detectors use **naive heuristics** (regex line scanning, simple
    AST walks).  They are intentionally fast rather than perfectly accurate,
    trading precision for low latency inside the MCP server loop.
"""

from __future__ import annotations

import ast
import re

from pydantic import BaseModel


class DuplicateFinding(BaseModel):
    """A function name that appears in more than one file.

    Attributes:
        name: Function name found in multiple files.
        files: Paths of the files containing the duplicate definition.
    """

    name: str
    files: list[str]


class GodClassFinding(BaseModel):
    """A class that exceeds method-count or line-count thresholds.

    Attributes:
        name: Class name.
        method_count: Number of ``def`` statements inside the class.
        lines: Total line span of the class body.
    """

    name: str
    method_count: int
    lines: int


class InheritanceFinding(BaseModel):
    """An inheritance chain that exceeds the allowed depth.

    Attributes:
        chain: Ordered list of class names from child to deepest ancestor.
        depth: Number of inheritance hops (``len(chain) - 1``).
    """

    chain: list[str]
    depth: int


class DependencyCycleFinding(BaseModel):
    """A circular dependency path discovered in the import graph.

    Attributes:
        cycle: Module names forming the cycle, ending with a repeat of the
            first element.
    """

    cycle: list[str]


class FeatureEnvyFinding(BaseModel):
    """A method that accesses another object's attributes more than its own.

    Attributes:
        method: Name of the envious method (``"<unknown>"`` when file-level).
        target_class: Most-referenced external object name.
        occurrences: Number of attribute accesses on *target_class*.
    """

    method: str
    target_class: str
    occurrences: int


class SparseCodeFinding(BaseModel):
    """A source line containing too many semicolon-separated statements.

    Attributes:
        line: 1-based line number.
        statements: Number of statements found on the line.
    """

    line: int
    statements: int


class ConsistencyFinding(BaseModel):
    """Mixed naming conventions detected among function definitions.

    Attributes:
        naming_styles: Sorted list of observed styles (e.g.
            ``["camelCase", "snake_case"]``).
    """

    naming_styles: list[str]


class ExplicitnessFinding(BaseModel):
    """A function with one or more parameters lacking type annotations.

    Attributes:
        function: Name of the under-annotated function.
        missing_params: Parameter names without type hints.
    """

    function: str
    missing_params: list[str]


class NamespaceFinding(BaseModel):
    """Namespace pollution metrics for a single source file.

    Attributes:
        top_level_symbols: Count of top-level definitions, imports, and
            assignments.
        export_count: Number of entries in ``__all__``, or ``None`` when
            ``__all__`` is not defined.
    """

    top_level_symbols: int
    export_count: int | None


class TsAnyFinding(BaseModel):
    """Occurrences of the ``any`` keyword in TypeScript source.

    Attributes:
        count: Total number of ``any`` keyword matches.
    """

    count: int


class TsTypeAliasFinding(BaseModel):
    """Object-style type aliases (``type X = { … }``) found in TypeScript source.

    Attributes:
        count: Number of object-literal type aliases.
    """

    count: int


class TsReturnTypeFinding(BaseModel):
    """Exported functions missing explicit return-type annotations.

    Attributes:
        count: Number of exported functions without a return type.
    """

    count: int


class TsReadonlyFinding(BaseModel):
    """Occurrences of the ``readonly`` modifier in TypeScript source.

    Attributes:
        count: Number of ``readonly`` keyword matches.
    """

    count: int


class TsAssertionFinding(BaseModel):
    """Type-assertion expressions (``as T``) found in TypeScript source.

    Attributes:
        count: Number of ``as`` type-assertion matches.
    """

    count: int


class TsUtilityTypeFinding(BaseModel):
    """Built-in utility-type references (``Partial``, ``Pick``, etc.) in TypeScript source.

    Attributes:
        count: Combined occurrences of ``Partial``, ``Pick``, ``Omit``,
            ``Record``, and ``Readonly``.
    """

    count: int


class TsNonNullFinding(BaseModel):
    """Non-null assertion operators (``!``) found in TypeScript source.

    Attributes:
        count: Number of non-null assertion matches.
    """

    count: int


class TsEnumObjectFinding(BaseModel):
    """``const`` object literals that may serve as ad-hoc enums.

    Attributes:
        count: Number of ``const X = {`` patterns found.
    """

    count: int


class TsUnknownAnyFinding(BaseModel):
    """Comparative counts of ``any`` vs ``unknown`` keywords in TypeScript source.

    Attributes:
        any_count: Occurrences of the ``any`` keyword.
        unknown_count: Occurrences of the ``unknown`` keyword.
    """

    any_count: int
    unknown_count: int


def detect_deep_nesting(code: str, max_depth: int = 3) -> tuple[bool, int]:
    """Measure the deepest indentation level using 4-space tab stops.

    Args:
        code: Python source text to scan.
        max_depth: Nesting-depth ceiling used for the boolean flag.

    Returns:
        ``(exceeds_threshold, deepest_level)`` — the boolean is ``True``
        when *deepest_level* is strictly greater than *max_depth*.
    """
    max_found = 0
    for line in code.splitlines():
        stripped = line.lstrip("\t ")
        depth = (len(line) - len(stripped)) // 4
        if depth > max_found:
            max_found = depth
    return (max_found > max_depth, max_found)


def detect_long_functions(code: str, max_lines: int = 50) -> list[tuple[str, int]]:
    """Find top-level ``def`` blocks that exceed *max_lines*.

    Uses naive line counting: a new ``def`` at column 0 starts a new block
    and terminates the previous one.

    Args:
        code: Python source text.
        max_lines: Line-count ceiling.  Blocks at or below this are ignored.

    Returns:
        ``[(function_header, line_count), …]`` for each over-long function.
    """
    funcs: list[tuple[str, int]] = []
    current_name = None
    current_count = 0
    for line in code.splitlines():
        if re.match(r"^def\s+\w+", line):
            if current_name and current_count > max_lines:
                funcs.append((current_name, current_count))
            current_name = line.strip()
            current_count = 1
        elif current_name:
            current_count += 1
    if current_name and current_count > max_lines:
        funcs.append((current_name, current_count))
    return funcs


def detect_magic_methods_overuse(code: str) -> list[str]:
    """Collect all dunder-method definitions (``def __xxx__``) in *code*.

    Args:
        code: Python source text to scan.

    Returns:
        Raw matched lines (including leading whitespace) for each dunder ``def``.
    """
    methods = re.findall(r"^\s*def\s+__\w+__", code, flags=re.M)
    return methods


def detect_multiple_implementations(files: dict[str, str]) -> list[DuplicateFinding]:
    """Identify function names defined in more than one file.

    Scans each file for top-level ``def`` statements and groups them by
    function name.  Any name appearing in two or more files produces a
    ``DuplicateFinding``.

    Args:
        files: ``{filename: source_code}`` mapping.

    Returns:
        One ``DuplicateFinding`` per duplicated function name.
    """
    name_map: dict[str, list[str]] = {}
    for fname, code in files.items():
        for m in re.finditer(r"^def\s+(\w+)", code, flags=re.M):
            name = m.group(1)
            name_map.setdefault(name, []).append(fname)
    duplicates: list[DuplicateFinding] = []
    for name, fns in name_map.items():
        if len(fns) > 1:
            duplicates.append(DuplicateFinding(name=name, files=fns))
    return duplicates


# New detectors
def detect_god_classes(
    code: str, max_methods: int = 10, max_lines: int = 500
) -> list[GodClassFinding]:
    """Flag classes that exceed method-count or line-span thresholds.

    Parses class boundaries by looking for ``class Foo`` at column 0 and
    counting indented ``def`` lines inside each block.

    Args:
        code: Python source text.
        max_methods: Method-count ceiling.
        max_lines: Line-span ceiling.

    Returns:
        One ``GodClassFinding`` per class breaching either threshold.
    """
    results: list[GodClassFinding] = []
    lines = code.splitlines()
    current_class = None
    class_start = 0
    method_count = 0
    for i, ln in enumerate(lines, start=1):
        m = re.match(r"^class\s+(\w+)", ln)
        if m:
            # close previous
            if current_class:
                length = i - class_start
                if method_count > max_methods or length > max_lines:
                    results.append(
                        GodClassFinding(
                            name=current_class, method_count=method_count, lines=length
                        )
                    )
            current_class = m.group(1)
            class_start = i
            method_count = 0
        elif current_class and re.match(r"^\s+def\s+\w+", ln):
            method_count += 1
    # finalize
    if current_class:
        length = len(lines) - class_start + 1
        if method_count > max_methods or length > max_lines:
            results.append(
                GodClassFinding(
                    name=current_class, method_count=method_count, lines=length
                )
            )
    return results


def detect_deep_inheritance(
    code_map: dict[str, str], max_depth: int = 3
) -> list[InheritanceFinding]:
    """Discover inheritance chains deeper than *max_depth* across multiple files.

    Builds a parent map by regex-parsing ``class Foo(Bar, Baz)`` declarations,
    then walks chains recursively.  Cycles are detected and short-circuited.

    Args:
        code_map: ``{filepath: source_code}`` mapping for all files to consider.
        max_depth: Maximum allowed inheritance hops.

    Returns:
        One ``InheritanceFinding`` per chain exceeding *max_depth*.
    """
    parent_map: dict[str, list[str]] = {}
    for fname, code in code_map.items():
        for m in re.finditer(r"^class\s+(\w+)\(([^\)]+)\)", code, flags=re.M):
            cls = m.group(1)
            parents = [p.strip().split()[0] for p in m.group(2).split(",") if p.strip()]
            parent_map[cls] = parents
    # compute chains
    results: list[InheritanceFinding] = []

    def walk_chain(start, seen):
        """Recursively trace the inheritance path from *start* to its ancestors."""
        if start in seen:
            return [start]
        seen = seen | {start}
        parents = parent_map.get(start, [])
        if not parents:
            return [start]
        chains = []
        for p in parents:
            for tail in walk_chain(p, seen):
                chains.append([start] + (tail if isinstance(tail, list) else [tail]))
        return chains

    for cls in parent_map.keys():
        chains = walk_chain(cls, set())
        for ch in chains:
            if isinstance(ch, list) and len(ch) - 1 > max_depth:
                results.append(InheritanceFinding(chain=ch, depth=len(ch) - 1))
    return results


def detect_dependency_cycles(
    edges: list[tuple[str, str]],
) -> list[DependencyCycleFinding]:
    """Find circular dependencies in a directed edge list via depth-first search.

    Args:
        edges: ``[(source, target), …]`` import-dependency pairs.

    Returns:
        One ``DependencyCycleFinding`` per distinct cycle discovered.
    """
    adj: dict[str, list[str]] = {}
    for a, b in edges:
        adj.setdefault(a, []).append(b)
    results: list[DependencyCycleFinding] = []

    def dfs(node, path, seen):
        """Recurse through the adjacency list, recording cycles when a node is revisited."""
        if node in path:
            idx = path.index(node)
            cycle = path[idx:] + [node]
            results.append(DependencyCycleFinding(cycle=cycle))
            return
        if node in seen:
            return
        seen.add(node)
        path.append(node)
        for nb in adj.get(node, []):
            dfs(nb, path, seen)
        path.pop()

    for n in adj.keys():
        dfs(n, [], set())
    return results


def detect_feature_envy(code: str) -> list[FeatureEnvyFinding]:
    """Heuristic: flag files where an external object's attributes are accessed more often than ``self``.

    Counts ``self.attr`` vs ``other.attr`` patterns globally across the file.
    When any single external name outweighs ``self`` references, a finding
    is emitted.

    Args:
        code: Python source text.

    Returns:
        At most one ``FeatureEnvyFinding`` per file.
    """
    results: list[FeatureEnvyFinding] = []
    # Very naive: count occurrences of 'other.attr' patterns vs 'self.attr'
    for m in re.finditer(r"def\s+(\w+)\(|class\s+(\w+)", code):
        pass
    # Simple global heuristic across whole file
    self_refs = len(re.findall(r"self\.[a-zA-Z_]+", code))
    others = re.findall(r"(\w+)\.[a-zA-Z_]+", code)
    other_counts: dict[str, int] = {}
    for o in others:
        if o == "self":
            continue
        other_counts[o] = other_counts.get(o, 0) + 1
    if other_counts:
        top = max(other_counts.items(), key=lambda kv: kv[1])
        if top[1] > self_refs:
            results.append(
                FeatureEnvyFinding(
                    method="<unknown>", target_class=top[0], occurrences=top[1]
                )
            )
    return results


def detect_sparse_code(
    code: str, max_statements_per_line: int = 1
) -> list[SparseCodeFinding]:
    """Flag lines containing multiple semicolon-separated statements.

    Comment-only lines are skipped.

    Args:
        code: Python source text.
        max_statements_per_line: Maximum allowed statements per line.

    Returns:
        One ``SparseCodeFinding`` per offending line.
    """
    results: list[SparseCodeFinding] = []
    for i, line in enumerate(code.splitlines(), start=1):
        if line.strip().startswith("#"):
            continue
        statements = [seg for seg in line.split(";") if seg.strip()]
        if len(statements) > max_statements_per_line:
            results.append(SparseCodeFinding(line=i, statements=len(statements)))
    return results


def detect_inconsistent_naming_styles(code: str) -> list[ConsistencyFinding]:
    """Check whether function names mix ``snake_case``, ``camelCase``, or ``PascalCase``.

    Args:
        code: Python source text.

    Returns:
        A single-element list when more than one style is detected,
        otherwise an empty list.
    """
    styles: set[str] = set()
    for m in re.finditer(r"^def\s+([A-Za-z_][A-Za-z0-9_]*)", code, flags=re.M):
        name = m.group(1)
        if re.match(r"^_?[a-z][a-z0-9_]*$", name):
            styles.add("snake_case")
        elif re.match(r"^[a-z][A-Za-z0-9]*$", name):
            styles.add("camelCase")
        elif re.match(r"^[A-Z][A-Za-z0-9]*$", name):
            styles.add("PascalCase")
        else:
            styles.add("other")
    if len(styles) > 1:
        return [ConsistencyFinding(naming_styles=sorted(styles))]
    return []


def detect_missing_type_hints(code: str) -> list[ExplicitnessFinding]:
    """Walk the AST to find functions with unannotated parameters (excluding ``self``).

    Args:
        code: Python source text.

    Returns:
        One ``ExplicitnessFinding`` per function with at least one missing annotation.
    """
    results: list[ExplicitnessFinding] = []
    try:
        tree = ast.parse(code)
    except Exception:
        return results
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            missing: list[str] = []
            for arg in node.args.args:
                if arg.arg == "self":
                    continue
                if arg.annotation is None:
                    missing.append(arg.arg)
            if missing:
                results.append(
                    ExplicitnessFinding(function=node.name, missing_params=missing)
                )
    return results


def detect_namespace_usage(code: str) -> NamespaceFinding:
    """Count top-level symbols and ``__all__`` entries to gauge namespace pollution.

    Args:
        code: Python source text.

    Returns:
        A ``NamespaceFinding`` with symbol count and optional export count.
    """
    top_level_symbols = 0
    export_count: int | None = None
    try:
        tree = ast.parse(code)
    except Exception:
        return NamespaceFinding(top_level_symbols=0, export_count=None)
    for node in tree.body:
        if isinstance(
            node,
            (
                ast.FunctionDef,
                ast.ClassDef,
                ast.Assign,
                ast.AnnAssign,
                ast.Import,
                ast.ImportFrom,
            ),
        ):
            top_level_symbols += 1
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == "__all__":
                    if isinstance(node.value, (ast.List, ast.Tuple)):
                        export_count = len(node.value.elts)
                    else:
                        export_count = None
    return NamespaceFinding(
        top_level_symbols=top_level_symbols, export_count=export_count
    )


def detect_ts_any_usage(code: str) -> TsAnyFinding:
    """Count occurrences of the ``any`` type keyword in TypeScript source.

    Args:
        code: TypeScript source text.

    Returns:
        A ``TsAnyFinding`` with the match count.
    """
    count = len(re.findall(r"\bany\b", code))
    return TsAnyFinding(count=count)


def detect_ts_object_type_aliases(code: str) -> TsTypeAliasFinding:
    """Count ``type X = { … }`` object-literal type aliases in TypeScript.

    Args:
        code: TypeScript source text.

    Returns:
        A ``TsTypeAliasFinding`` with the match count.
    """
    count = len(re.findall(r"\btype\s+\w+\s*=\s*\{", code))
    return TsTypeAliasFinding(count=count)


def detect_ts_missing_return_types(code: str) -> TsReturnTypeFinding:
    """Count exported functions lacking an explicit return-type annotation.

    Args:
        code: TypeScript source text.

    Returns:
        A ``TsReturnTypeFinding`` with the match count.
    """
    count = len(re.findall(r"export\s+function\s+\w+\s*\([^)]*\)\s*\{", code))
    return TsReturnTypeFinding(count=count)


def detect_ts_readonly_usage(code: str) -> TsReadonlyFinding:
    """Count ``readonly`` modifier occurrences in TypeScript source.

    Args:
        code: TypeScript source text.

    Returns:
        A ``TsReadonlyFinding`` with the match count.
    """
    count = len(re.findall(r"\breadonly\b", code))
    return TsReadonlyFinding(count=count)


def detect_ts_type_assertions(code: str) -> TsAssertionFinding:
    """Count ``as T`` type-assertion expressions in TypeScript source.

    Args:
        code: TypeScript source text.

    Returns:
        A ``TsAssertionFinding`` with the match count.
    """
    count = len(re.findall(r"\bas\s+\w+", code))
    return TsAssertionFinding(count=count)


def detect_ts_utility_types(code: str) -> TsUtilityTypeFinding:
    """Count built-in utility-type references (``Partial``, ``Pick``, ``Omit``, ``Record``, ``Readonly``).

    Args:
        code: TypeScript source text.

    Returns:
        A ``TsUtilityTypeFinding`` with the combined match count.
    """
    count = len(re.findall(r"\b(Partial|Pick|Omit|Record|Readonly)\b", code))
    return TsUtilityTypeFinding(count=count)


def detect_ts_non_null_assertions(code: str) -> TsNonNullFinding:
    """Count non-null assertion operators (``expr!``) in TypeScript source.

    Args:
        code: TypeScript source text.

    Returns:
        A ``TsNonNullFinding`` with the match count.
    """
    count = len(re.findall(r"\b\w+!", code))
    return TsNonNullFinding(count=count)


def detect_ts_plain_enum_objects(code: str) -> TsEnumObjectFinding:
    """Count ``const X = {`` patterns that may function as ad-hoc enums.

    Args:
        code: TypeScript source text.

    Returns:
        A ``TsEnumObjectFinding`` with the match count.
    """
    count = len(re.findall(r"\bconst\s+\w+\s*=\s*\{", code))
    return TsEnumObjectFinding(count=count)


def detect_ts_unknown_over_any(code: str) -> TsUnknownAnyFinding:
    """Compare ``any`` vs ``unknown`` keyword usage in TypeScript source.

    A high ``any_count`` relative to ``unknown_count`` suggests the codebase
    should migrate toward ``unknown`` for safer type narrowing.

    Args:
        code: TypeScript source text.

    Returns:
        A ``TsUnknownAnyFinding`` with both counts.
    """
    any_count = len(re.findall(r"\bany\b", code))
    unknown_count = len(re.findall(r"\bunknown\b", code))
    return TsUnknownAnyFinding(any_count=any_count, unknown_count=unknown_count)
