from __future__ import annotations

import ast
import re
from pathlib import Path

SRC_PY_FILES = sorted(Path("src/mcp_zen_of_languages").rglob("*.py"))

BANNED_DOCSTRING_PATTERNS = [
    r">>> 1 \+ 1",
    r"Value for ``[^`]+``\.",
    r"provided by the caller\.",
    r"The [A-Za-z_]+ input value\.",
    r"Result of this function call\.",
    r"Return value for ``[^`]+``\.",
    r"Computed return value\.",
    r"Result produced by this function\.",
    r"Input value used by this operation\.",
    r"Result returned to callers for downstream processing\.",
    r'"""[A-Za-z_]+\s+function\.',
    # Guard against a previously copied boilerplate See Also block.
    r"See Also:\s+`AnalysisResult`:",
]

GENERIC_ARG_PATTERNS = (
    re.compile(r"^The [A-Za-z_]+ input value\.$"),
    re.compile(r"^Context-specific input consumed by this operation\.$"),
    re.compile(r"^Input value used by this operation\.$"),
)

GENERIC_RETURN_PATTERNS = (
    re.compile(r"^Computed return value\.$"),
    re.compile(r"^Result produced by this function\.$"),
    re.compile(r"^Result returned to callers for downstream processing\.$"),
    re.compile(r"^Output value consumed by downstream analysis or rendering steps\.$"),
)


def _iter_function_docstrings() -> list[tuple[Path, str, int, str]]:
    entries: list[tuple[Path, str, int, str]] = []
    for path in Path("src").rglob("*.py"):
        source = path.read_text(encoding="utf-8")
        try:
            tree = ast.parse(source)
        except SyntaxError:
            continue
        for node in ast.walk(tree):
            if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                continue
            if not node.body or not isinstance(node.body[0], ast.Expr):
                continue
            value = getattr(node.body[0], "value", None)
            if not isinstance(value, ast.Constant) or not isinstance(value.value, str):
                continue
            entries.append((path, node.name, node.lineno, value.value))
    return entries


def _iter_module_asts() -> list[tuple[Path, ast.Module]]:
    entries: list[tuple[Path, ast.Module]] = []
    for path in SRC_PY_FILES:
        source = path.read_text(encoding="utf-8")
        try:
            tree = ast.parse(source)
        except SyntaxError:
            continue
        entries.append((path, tree))
    return entries


def test_function_docstrings_do_not_start_with_blank_line() -> None:
    offenders: list[str] = [
        f"{path}:{lineno}:{name}"
        for path, name, lineno, doc in _iter_function_docstrings()
        if doc.startswith("\n")
    ]
    assert not offenders, (
        "Docstrings must start with summary on opening line:\n" + "\n".join(offenders)
    )


def test_function_docstrings_have_single_args_and_returns_sections() -> None:
    offenders: list[str] = []
    for path, name, lineno, doc in _iter_function_docstrings():
        args_count = len(re.findall(r"^\s*Args:\s*$", doc, re.MULTILINE))
        returns_count = len(re.findall(r"^\s*Returns:\s*$", doc, re.MULTILINE))
        if args_count > 1 or returns_count > 1:
            offenders.append(
                f"{path}:{lineno}:{name} (Args={args_count}, Returns={returns_count})"
            )
    assert not offenders, (
        "Docstrings must not duplicate Args/Returns sections:\n" + "\n".join(offenders)
    )


def test_src_docstrings_do_not_use_placeholder_templates() -> None:
    offenders: list[str] = []
    for path in SRC_PY_FILES:
        source = path.read_text(encoding="utf-8")
        offenders.extend(
            f"{path}: {pattern}"
            for pattern in BANNED_DOCSTRING_PATTERNS
            if re.search(pattern, source)
        )
    assert not offenders, (
        "src docstrings must not contain placeholder docstring templates:\n"
        + "\n".join(offenders)
    )


def test_args_sections_are_semantically_described() -> None:
    offenders: list[str] = []
    arg_line = re.compile(r"^\s*([*]*[A-Za-z_][A-Za-z0-9_]*)\s*\([^)]*\):\s*(.+)$")
    for path, name, lineno, doc in _iter_function_docstrings():
        in_args = False
        for line in doc.splitlines():
            stripped = line.strip()
            if stripped == "Args:":
                in_args = True
                continue
            if in_args and stripped.endswith(":") and stripped not in {"Args:"}:
                in_args = False
            if not in_args or not stripped:
                continue
            match = arg_line.match(line)
            if not match:
                continue
            param_name, description = match[1].lstrip("*"), match[2].strip()
            if any(pattern.match(description) for pattern in GENERIC_ARG_PATTERNS):
                offenders.append(
                    f"{path}:{lineno}:{name}:{param_name} -> generic args description"
                )
            if description.lower().startswith(f"the {param_name.lower()} "):
                offenders.append(
                    f"{path}:{lineno}:{name}:{param_name} -> name-repeating args description"
                )
    assert not offenders, (
        "Args descriptions must explain semantics, not templates:\n"
        + "\n".join(offenders)
    )


def test_returns_sections_are_semantically_described() -> None:
    offenders: list[str] = []
    return_line = re.compile(r"^\s*([^:]+):\s*(.+)$")
    for path, name, lineno, doc in _iter_function_docstrings():
        in_returns = False
        for line in doc.splitlines():
            stripped = line.strip()
            if stripped == "Returns:":
                in_returns = True
                continue
            if in_returns and stripped.endswith(":") and stripped not in {"Returns:"}:
                in_returns = False
            if not in_returns or not stripped:
                continue
            match = return_line.match(line)
            if not match:
                continue
            description = match[2].strip()
            if any(pattern.match(description) for pattern in GENERIC_RETURN_PATTERNS):
                offenders.append(
                    f"{path}:{lineno}:{name} -> generic returns description"
                )
    assert not offenders, (
        "Returns descriptions must communicate caller-visible contract:\n"
        + "\n".join(offenders)
    )


def test_args_sections_match_callable_signatures() -> None:
    offenders: list[str] = []
    for path, tree in _iter_module_asts():
        for node in ast.walk(tree):
            if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                continue
            doc = ast.get_docstring(node)
            if not doc or "Args:" not in doc:
                continue
            params = [
                arg.arg for arg in node.args.args if arg.arg not in {"self", "cls"}
            ]
            if node.args.vararg:
                params.append(node.args.vararg.arg)
            params.extend(arg.arg for arg in node.args.kwonlyargs)
            if node.args.kwarg:
                params.append(node.args.kwarg.arg)
            if not params:
                offenders.append(f"{path}:{node.lineno}:{node.name}")
    assert not offenders, (
        "Functions without callable parameters must not include Args sections:\n"
        + "\n".join(offenders)
    )


def test_public_api_symbols_have_non_trivial_docstrings() -> None:
    offenders: list[str] = []
    excluded_module_names = {"__init__.py", "mapping.py"}
    excluded_module_parts = {"rules", "template"}
    for path, tree in _iter_module_asts():
        if path.name in excluded_module_names or any(
            part in excluded_module_parts for part in path.parts
        ):
            continue
        module_doc = ast.get_docstring(tree)
        if not module_doc or len(module_doc.strip()) < 20:
            offenders.append(f"{path}:module")
        for node in tree.body:
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                if node.name.startswith("_"):
                    continue
                doc = ast.get_docstring(node)
                if not doc or len(doc.strip()) < 20:
                    offenders.append(f"{path}:{node.lineno}:{node.name}")
    assert not offenders, (
        "Public modules/classes/functions must have non-trivial docstrings:\n"
        + "\n".join(offenders)
    )
