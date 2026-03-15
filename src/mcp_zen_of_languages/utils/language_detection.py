"""Resolve source-file language before analysis so the correct analyzer is dispatched.

Two strategies are available: extension-based lookup (high confidence, fast)
and content-heuristic scanning (lower confidence, used when no path is
supplied). The MCP server and CLI invoke these detectors early in the request
lifecycle to route code to the appropriate language-specific pipeline.
"""

from __future__ import annotations

import re

from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

from pydantic import BaseModel


EXTENSION_LANGUAGE_MAP: dict[str, str] = {
    ".py": "python",
    ".rb": "ruby",
    ".rs": "rust",
    ".go": "go",
    ".ts": "typescript",
    ".tsx": "typescript",
    ".js": "javascript",
    ".jsx": "javascript",
    ".sh": "bash",
    ".bash": "bash",
    ".pwsh": "powershell",
    ".ps1": "powershell",
    ".css": "css",
    ".scss": "css",
    ".less": "css",
    ".yaml": "yaml",
    ".yml": "yaml",
    ".toml": "toml",
    ".json": "json",
    ".xml": "xml",
    ".svg": "svg",
    ".sql": "sql",
    ".ddl": "sql",
    ".dml": "sql",
    ".tf": "terraform",
    ".tfvars": "terraform",
    ".md": "markdown",
    ".markdown": "markdown",
    ".mdx": "markdown",
    ".tex": "latex",
    ".ltx": "latex",
    ".sty": "latex",
    ".bib": "latex",
    ".dockerfile": "dockerfile",
    ".vue": "vue",
}

GITLAB_CI_FILENAMES = {".gitlab-ci.yml", ".gitlab-ci.yaml"}
YAML_EXTENSIONS = {".yml", ".yaml"}
ANSIBLE_PATH_SEGMENTS = {"tasks", "handlers", "vars", "defaults"}
ANSIBLE_SIGNAL_THRESHOLD = 2
ANSIBLE_DETECTION_READ_LIMIT = 16 * 1024
FRAMEWORK_DETECTION_READ_LIMIT = 16 * 1024
NEXTJS_CONFIG_FILENAMES = {
    "next.config.js",
    "next.config.mjs",
    "next.config.ts",
    "next.config.cjs",
}
NEXTJS_SPECIAL_FILENAMES = {
    "page.js",
    "page.jsx",
    "page.ts",
    "page.tsx",
    "layout.js",
    "layout.jsx",
    "layout.ts",
    "layout.tsx",
    "loading.js",
    "loading.jsx",
    "loading.ts",
    "loading.tsx",
    "error.js",
    "error.jsx",
    "error.ts",
    "error.tsx",
    "not-found.js",
    "not-found.jsx",
    "not-found.ts",
    "not-found.tsx",
    "template.js",
    "template.jsx",
    "template.ts",
    "template.tsx",
    "default.js",
    "default.jsx",
    "default.ts",
    "default.tsx",
    "route.js",
    "route.ts",
    "route.jsx",
    "route.tsx",
    "middleware.js",
    "middleware.ts",
}
ANGULAR_TS_SUFFIXES = (
    ".component.ts",
    ".service.ts",
    ".module.ts",
    ".directive.ts",
    ".pipe.ts",
    ".guard.ts",
    ".resolver.ts",
    ".interceptor.ts",
)
ANGULAR_HTML_SUFFIXES = (".component.html", ".page.html")
DJANGO_MARKER_FILENAMES = {"manage.py", "asgi.py", "wsgi.py"}


class DetectionResult(BaseModel):
    """Outcome of a language detection attempt, carrying the inferred language and reliability signals.

    Attributes:
        language: Canonical language identifier (e.g. ``"python"``, ``"typescript"``).
        confidence: Score between 0 and 1 indicating detection reliability.
        method: Strategy that produced this result (``"extension"`` or ``"heuristics"``).
        notes: Optional free-text annotation explaining the detection rationale.
    """

    language: str
    confidence: float = 0.9
    method: str | None = None
    notes: str | None = None

    def as_dict(self) -> dict:
        """Serialize the detection result to a plain dictionary via Pydantic's ``model_dump``.

        Returns:
            dict: A dict with keys ``language``, ``confidence``, ``method``, and ``notes``.
        """
        return self.model_dump()


@dataclass(frozen=True, slots=True)
class TestingFamilyDescriptor:
    """Describe one test-family overlay and how to match its file paths."""

    language: str
    family: str

    def matches(self, path_obj: Path) -> bool:
        """Return whether *path_obj* belongs to this testing family."""
        file_name = path_obj.name.lower()
        parts = {part.lower() for part in path_obj.parts}
        if self.family == "pytest":
            return (
                file_name == "conftest.py"
                or file_name.startswith("test_")
                or file_name.endswith("_test.py")
                or ("tests" in parts and path_obj.suffix.lower() == ".py")
            )
        if self.family == "gotest":
            return file_name.endswith("_test.go")
        if self.family == "jest":
            return (
                file_name.endswith(
                    (".test.ts", ".test.tsx", ".spec.ts", ".spec.tsx"),
                )
                or "__tests__" in parts
            )
        if self.family == "rspec":
            return file_name.endswith("_spec.rb") or "spec" in parts
        return False


TESTING_FAMILY_DESCRIPTORS: tuple[TestingFamilyDescriptor, ...] = (
    TestingFamilyDescriptor(language="python", family="pytest"),
    TestingFamilyDescriptor(language="go", family="gotest"),
    TestingFamilyDescriptor(language="typescript", family="jest"),
    TestingFamilyDescriptor(language="ruby", family="rspec"),
)


def _is_ansible_path(path_obj: Path) -> bool:
    parts = {part.lower() for part in path_obj.parts}
    parent_name = path_obj.parent.name.lower()
    return (
        parent_name in {"group_vars", "host_vars"}
        or ("roles" in parts and parent_name in ANSIBLE_PATH_SEGMENTS)
        or path_obj.name.lower()
        in {"playbook.yml", "playbook.yaml", "site.yml", "site.yaml"}
    )


def _is_ansible_yaml_content(text: str) -> bool:
    lowered = text.lower()
    signals = 0
    if re.search(r"(?m)^\s*-\s*hosts\s*:", lowered):
        signals += 1
    if re.search(r"(?m)^\s*(tasks|handlers|pre_tasks|post_tasks)\s*:", lowered):
        signals += 1
    if re.search(r"(?m)^\s*(become|gather_facts|roles)\s*:", lowered):
        signals += 1
    if re.search(
        r"(?m)^\s*(?:ansible\.builtin\.[a-z_]+|-\s*(?:command|shell))\s*:",
        lowered,
    ):
        signals += 1
    return signals >= ANSIBLE_SIGNAL_THRESHOLD


def _detect_ansible_yaml(path_obj: Path, ext: str) -> DetectionResult | None:
    if ext not in YAML_EXTENSIONS or not path_obj.exists():
        return None
    if _is_ansible_path(path_obj):
        return DetectionResult(
            language="ansible",
            confidence=0.99,
            method="extension",
            notes="Matched Ansible-specific YAML path",
        )
    try:
        with path_obj.open(encoding="utf-8", errors="ignore") as handle:
            contents = handle.read(ANSIBLE_DETECTION_READ_LIMIT)
    except OSError:
        return None
    if contents and _is_ansible_yaml_content(contents):
        return DetectionResult(
            language="ansible",
            confidence=0.9,
            method="extension",
            notes="Matched Ansible YAML structure",
        )
    return None


def _read_text_prefix(path_obj: Path, limit: int) -> str:
    try:
        with path_obj.open(encoding="utf-8", errors="ignore") as handle:
            return handle.read(limit)
    except OSError:
        return ""


@lru_cache(maxsize=1024)
def _search_parents_for_marker(
    start_dir: str,
    marker_names: tuple[str, ...],
) -> str | None:
    current = Path(start_dir).resolve()
    for candidate in (current, *current.parents):
        for marker in marker_names:
            if (candidate / marker).exists():
                return str(candidate)
        if (candidate / "pyproject.toml").exists():
            break
    return None


def _has_project_marker(path_obj: Path, marker_names: set[str]) -> bool:
    return (
        _search_parents_for_marker(
            str(path_obj.parent),
            tuple(sorted(marker_names)),
        )
        is not None
    )


def _detect_nextjs(path_obj: Path, ext: str) -> DetectionResult | None:
    if ext not in {".js", ".jsx", ".ts", ".tsx"}:
        return None
    if not _has_project_marker(path_obj, NEXTJS_CONFIG_FILENAMES):
        return None

    file_name = path_obj.name.lower()
    parts = {part.lower() for part in path_obj.parts}
    contents = _read_text_prefix(path_obj, FRAMEWORK_DETECTION_READ_LIMIT)

    if file_name in NEXTJS_SPECIAL_FILENAMES:
        return DetectionResult(
            language="nextjs",
            confidence=0.99,
            method="extension",
            notes="Matched a Next.js special file in a Next.js project",
        )
    if "pages" in parts:
        return DetectionResult(
            language="nextjs",
            confidence=0.97,
            method="extension",
            notes="Matched a file inside a Next.js pages/ directory",
        )
    if (
        'from "next/' in contents
        or "from 'next/" in contents
        or '"next/navigation"' in contents
        or "'next/navigation'" in contents
        or '"next/server"' in contents
        or "'next/server'" in contents
    ):
        return DetectionResult(
            language="nextjs",
            confidence=0.96,
            method="extension",
            notes="Matched a direct Next.js framework import",
        )
    return None


def _detect_angular(path_obj: Path, ext: str) -> DetectionResult | None:
    file_name = path_obj.name.lower()
    if ext == ".html" and any(
        file_name.endswith(suffix) for suffix in ANGULAR_HTML_SUFFIXES
    ):
        return DetectionResult(
            language="angular",
            confidence=0.99,
            method="extension",
            notes="Matched Angular template naming convention",
        )
    if ext != ".ts":
        return None
    if any(file_name.endswith(suffix) for suffix in ANGULAR_TS_SUFFIXES):
        return DetectionResult(
            language="angular",
            confidence=0.99,
            method="extension",
            notes="Matched Angular TypeScript file naming convention",
        )
    contents = _read_text_prefix(path_obj, FRAMEWORK_DETECTION_READ_LIMIT)
    if (
        "@angular/" in contents
        or "@Component(" in contents
        or "@NgModule(" in contents
        or "@Injectable(" in contents
        or "@Pipe(" in contents
        or "@Directive(" in contents
    ):
        return DetectionResult(
            language="angular",
            confidence=0.96,
            method="extension",
            notes="Matched Angular framework decorators or imports",
        )
    return None


def _detect_python_framework(  # noqa: PLR0911
    path_obj: Path,
    ext: str,
) -> DetectionResult | None:
    if ext != ".py":
        return None

    contents = _read_text_prefix(path_obj, FRAMEWORK_DETECTION_READ_LIMIT)
    if "from django" in contents or "import django" in contents:
        return DetectionResult(
            language="django",
            confidence=0.98,
            method="extension",
            notes="Matched Django imports",
        )
    if path_obj.name.lower() in DJANGO_MARKER_FILENAMES and _has_project_marker(
        path_obj,
        DJANGO_MARKER_FILENAMES,
    ):
        return DetectionResult(
            language="django",
            confidence=0.95,
            method="extension",
            notes="Matched Django project markers",
        )
    if "from fastapi" in contents or "import fastapi" in contents:
        return DetectionResult(
            language="fastapi",
            confidence=0.98,
            method="extension",
            notes="Matched FastAPI imports",
        )
    if "from sqlalchemy" in contents or "import sqlalchemy" in contents:
        return DetectionResult(
            language="sqlalchemy",
            confidence=0.97,
            method="extension",
            notes="Matched SQLAlchemy imports",
        )
    if "from pydantic" in contents or "import pydantic" in contents:
        return DetectionResult(
            language="pydantic",
            confidence=0.97,
            method="extension",
            notes="Matched Pydantic imports",
        )
    return None


def detect_testing_family_overlay(language: str, path: str | None) -> str | None:
    """Resolve the testing-family overlay for one file analysed as *language*."""
    if path is None:
        return None
    normalized_language = language.lower()
    path_obj = Path(path)
    for descriptor in TESTING_FAMILY_DESCRIPTORS:
        if descriptor.language != normalized_language:
            continue
        if descriptor.matches(path_obj):
            return descriptor.family
    return None


def detect_language_by_extension(path: str) -> DetectionResult:  # noqa: C901, PLR0911
    """Look up the file extension in ``EXTENSION_LANGUAGE_MAP`` and return a high-confidence result.

    This is the primary detection strategy and the fastest path. It
    extracts the suffix with ``os.path.splitext``, normalises to lowercase,
    and matches against the static extension map. Unknown extensions yield
    ``language="unknown"`` so callers can fall back to content heuristics.

    Args:
        path (str): Filesystem path (absolute or relative) whose extension is inspected.

    Returns:
        DetectionResult: A ``DetectionResult`` with ``method="extension"`` and confidence 0.95
        for known extensions, or ``language="unknown"`` for unrecognised ones.
    """
    path_obj = Path(path)
    parts = path_obj.parts
    ext = path_obj.suffix.lower()
    file_name = path_obj.name.lower()
    if ext in {".yml", ".yaml"} and ".github" in parts and "workflows" in parts:
        github_index = parts.index(".github")
        if github_index + 1 < len(parts) and parts[github_index + 1] == "workflows":
            return DetectionResult(
                language="github-actions",
                confidence=0.99,
                method="extension",
                notes="Matched .github/workflows YAML path",
            )
    if file_name in GITLAB_CI_FILENAMES:
        return DetectionResult(
            language="gitlab_ci", confidence=0.99, method="extension"
        )
    if "gitlab-ci" in {part.lower() for part in parts} and ext in YAML_EXTENSIONS:
        return DetectionResult(
            language="gitlab_ci", confidence=0.98, method="extension"
        )
    if file_name == "dockerfile" or file_name.startswith("dockerfile."):
        return DetectionResult(
            language="dockerfile", confidence=0.98, method="extension"
        )
    if file_name in {
        "docker-compose.yml",
        "docker-compose.yaml",
        "compose.yml",
        "compose.yaml",
    }:
        return DetectionResult(
            language="docker_compose",
            confidence=0.98,
            method="extension",
        )
    if ansible_result := _detect_ansible_yaml(path_obj, ext):
        return ansible_result
    if ext == ".vue":
        return DetectionResult(
            language="vue",
            confidence=0.99,
            method="extension",
            notes="Matched Vue single-file component extension",
        )
    if nextjs_result := _detect_nextjs(path_obj, ext):
        return nextjs_result
    if ext in {".jsx", ".tsx"}:
        return DetectionResult(
            language="react",
            confidence=0.99,
            method="extension",
            notes="Matched JSX or TSX component extension",
        )
    if angular_result := _detect_angular(path_obj, ext):
        return angular_result
    if python_framework_result := _detect_python_framework(path_obj, ext):
        return python_framework_result
    lang = EXTENSION_LANGUAGE_MAP.get(ext, "unknown")
    return DetectionResult(language=lang, confidence=0.95, method="extension")


def detect_language_from_content(code: str) -> DetectionResult:  # noqa: C901, PLR0911
    """Infer the programming language by scanning *code* for characteristic keywords.

    Used as a fallback when no file path is available. The heuristic checks
    for ``def `` (Python), ``interface``/``=>`` (TypeScript), and ``function``/
    ``const``/``let`` (JavaScript) in order of decreasing specificity.
    Confidence scores are lower than extension-based detection to reflect
    the inherent ambiguity of keyword matching.

    Args:
        code (str): Raw source text to scan for language-indicative
            patterns.

    Returns:
        DetectionResult: A ``DetectionResult`` with
        ``method="heuristics"`` and a confidence between 0.1 (unknown)
        and 0.9 (strong keyword match).
    """
    lowered = code.lower()
    if _is_ansible_yaml_content(code):
        return DetectionResult(language="ansible", confidence=0.85, method="heuristics")
    if "from django" in lowered or "import django" in lowered:
        return DetectionResult(language="django", confidence=0.9, method="heuristics")
    if "from fastapi" in lowered or "import fastapi" in lowered:
        return DetectionResult(language="fastapi", confidence=0.9, method="heuristics")
    if "from sqlalchemy" in lowered or "import sqlalchemy" in lowered:
        return DetectionResult(
            language="sqlalchemy", confidence=0.88, method="heuristics"
        )
    if "from pydantic" in lowered or "import pydantic" in lowered:
        return DetectionResult(
            language="pydantic", confidence=0.88, method="heuristics"
        )
    if "<template" in lowered and ("defineprops" in lowered or "v-for" in lowered):
        return DetectionResult(language="vue", confidence=0.86, method="heuristics")
    if "from 'next/" in lowered or 'from "next/' in lowered:
        return DetectionResult(language="nextjs", confidence=0.86, method="heuristics")
    if "@component(" in lowered or "@ngmodule(" in lowered or "@angular/" in lowered:
        return DetectionResult(language="angular", confidence=0.85, method="heuristics")
    if "usestate(" in lowered or "useeffect(" in lowered:
        return DetectionResult(language="react", confidence=0.82, method="heuristics")
    if "def " in code:
        return DetectionResult(language="python", confidence=0.9, method="heuristics")
    if "interface " in code or "=>" in code or "function " in code:
        return DetectionResult(
            language="typescript",
            confidence=0.85,
            method="heuristics",
        )
    if "const " in code or "let " in code:
        return DetectionResult(
            language="javascript",
            confidence=0.8,
            method="heuristics",
        )
    return DetectionResult(language="unknown", confidence=0.1, method="heuristics")
