"""Detectors for Markdown/MDX documentation quality checks."""
# ruff: noqa: D102

from __future__ import annotations

import re

from mcp_zen_of_languages.analyzers.base import (
    AnalysisContext,
    LocationHelperMixin,
    ViolationDetector,
)
from mcp_zen_of_languages.languages.configs import (
    MarkdownAltTextConfig,
    MarkdownBareUrlConfig,
    MarkdownCodeFenceLanguageConfig,
    MarkdownFrontMatterConfig,
    MarkdownHeadingHierarchyConfig,
    MarkdownMdxImportHygieneConfig,
    MarkdownMdxNamedDefaultExportConfig,
)
from mcp_zen_of_languages.models import Location, Violation

_HEADING_RE = re.compile(r"^\s{0,3}(#{1,6})\s+\S")
_IMAGE_RE = re.compile(r"!\[([^\]]*)\]\(([^)]+)\)")
_MARKDOWN_LINK_RE = re.compile(r"\[[^\]]+\]\([^)]+\)")
_ANGLE_URL_RE = re.compile(r"<https?://[^>]+>")
_INLINE_CODE_RE = re.compile(r"`[^`\n]+`")
_URL_RE = re.compile(r"https?://[^\s<>)\]]+")
_FENCE_RE = re.compile(r"^\s*```(?P<lang>[^\s`]*)\s*$")
_FRONTMATTER_RE = re.compile(r"^([A-Za-z_][\w-]*)\s*:")
_MDX_IMPORT_RE = re.compile(r'^\s*import\s+(.+?)\s+from\s+["\'][^"\']+["\']')
_MDX_IMPORT_SIDE_EFFECT_RE = re.compile(r'^\s*import\s+["\'][^"\']+["\']')


def _frontmatter_end_line(lines: list[str]) -> int | None:
    if not lines or lines[0].strip() != "---":
        return None
    for idx in range(1, len(lines)):
        if lines[idx].strip() == "---":
            return idx
    return None


def _iter_text_lines(code: str) -> list[tuple[int, str]]:
    lines = code.splitlines()
    frontmatter_end = _frontmatter_end_line(lines)
    start = (frontmatter_end + 1) if frontmatter_end is not None else 0
    in_fence = False
    output: list[tuple[int, str]] = []
    for line_no, line in enumerate(lines[start:], start=start + 1):
        if _FENCE_RE.match(line):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        output.append((line_no, line))
    return output


def _is_mdx_context(context: AnalysisContext) -> bool:
    if context.path and context.path.lower().endswith(".mdx"):
        return True
    for _line_no, line in _iter_text_lines(context.code):
        if re.match(r"^\s*(import|export)\s+", line):
            return True
    return False


class MarkdownHeadingHierarchyDetector(
    ViolationDetector[MarkdownHeadingHierarchyConfig],
    LocationHelperMixin,
):
    """Detect heading level skips in Markdown documents."""

    @property
    def name(self) -> str:
        return "md-001"

    def detect(
        self,
        context: AnalysisContext,
        config: MarkdownHeadingHierarchyConfig,
    ) -> list[Violation]:
        previous_level: int | None = None
        for line_no, line in _iter_text_lines(context.code):
            if not (match := _HEADING_RE.match(line)):
                continue
            level = len(match.group(1))
            if previous_level is not None and level > previous_level + 1:
                return [
                    self.build_violation(
                        config,
                        location=Location(line=line_no, column=1),
                        suggestion="Add intermediate heading levels to preserve document outline.",
                    ),
                ]
            previous_level = level
        return []


class MarkdownAltTextDetector(
    ViolationDetector[MarkdownAltTextConfig], LocationHelperMixin
):
    """Detect Markdown image syntax with empty alt text."""

    @property
    def name(self) -> str:
        return "md-002"

    def detect(
        self,
        context: AnalysisContext,
        config: MarkdownAltTextConfig,
    ) -> list[Violation]:
        for line_no, line in _iter_text_lines(context.code):
            for match in _IMAGE_RE.finditer(line):
                if not match.group(1).strip():
                    return [
                        self.build_violation(
                            config,
                            location=Location(line=line_no, column=match.start() + 1),
                            suggestion="Provide meaningful alternative text for screen readers.",
                        ),
                    ]
        return []


class MarkdownBareUrlDetector(
    ViolationDetector[MarkdownBareUrlConfig], LocationHelperMixin
):
    """Detect raw HTTP(S) URLs not wrapped in Markdown link syntax."""

    @property
    def name(self) -> str:
        return "md-003"

    def detect(
        self,
        context: AnalysisContext,
        config: MarkdownBareUrlConfig,
    ) -> list[Violation]:
        for line_no, line in _iter_text_lines(context.code):
            sanitized = _INLINE_CODE_RE.sub(
                "",
                _MARKDOWN_LINK_RE.sub("", _ANGLE_URL_RE.sub("", line)),
            )
            if match := _URL_RE.search(sanitized):
                return [
                    self.build_violation(
                        config,
                        location=Location(line=line_no, column=match.start() + 1),
                        suggestion="Wrap URLs as [label](url) or <url>.",
                    ),
                ]
        return []


class MarkdownCodeFenceLanguageDetector(
    ViolationDetector[MarkdownCodeFenceLanguageConfig],
    LocationHelperMixin,
):
    """Detect fenced code blocks that omit a language identifier."""

    @property
    def name(self) -> str:
        return "md-004"

    def detect(
        self,
        context: AnalysisContext,
        config: MarkdownCodeFenceLanguageConfig,
    ) -> list[Violation]:
        in_fence = False
        for line_no, line in enumerate(context.code.splitlines(), start=1):
            if not (match := _FENCE_RE.match(line)):
                continue
            if not in_fence and not match.group("lang").strip():
                return [
                    self.build_violation(
                        config,
                        location=Location(line=line_no, column=1),
                        suggestion="Add a language tag after opening backticks (e.g. ```python).",
                    ),
                ]
            in_fence = not in_fence
        return []


class MarkdownFrontMatterDetector(
    ViolationDetector[MarkdownFrontMatterConfig],
    LocationHelperMixin,
):
    """Detect incomplete YAML front-matter blocks."""

    @property
    def name(self) -> str:
        return "md-005"

    def detect(
        self,
        context: AnalysisContext,
        config: MarkdownFrontMatterConfig,
    ) -> list[Violation]:
        lines = context.code.splitlines()
        frontmatter_end = _frontmatter_end_line(lines)
        if frontmatter_end is None:
            return []
        keys = {
            match.group(1).lower()
            for line in lines[1:frontmatter_end]
            if (match := _FRONTMATTER_RE.match(line.strip()))
        }
        missing = [
            key for key in config.required_frontmatter_keys if key.lower() not in keys
        ]
        if missing:
            return [
                self.build_violation(
                    config,
                    location=Location(line=1, column=1),
                    suggestion=f"Add required front-matter keys: {', '.join(missing)}.",
                ),
            ]
        return []


class MarkdownMdxNamedDefaultExportDetector(
    ViolationDetector[MarkdownMdxNamedDefaultExportConfig],
    LocationHelperMixin,
):
    """Detect anonymous default exports in MDX modules."""

    @property
    def name(self) -> str:
        return "md-006"

    def detect(
        self,
        context: AnalysisContext,
        config: MarkdownMdxNamedDefaultExportConfig,
    ) -> list[Violation]:
        if config.mdx_only and not _is_mdx_context(context):
            return []
        for line_no, line in enumerate(context.code.splitlines(), start=1):
            stripped = line.strip()
            if re.match(r"export\s+default\s+function\s*(?:\(|$)", stripped):
                return [
                    self.build_violation(
                        config,
                        location=Location(line=line_no, column=1),
                        suggestion="Name the default function export (e.g. export default function Page()).",
                    ),
                ]
            if re.match(r"export\s+default\s+class\s*(?:\{|$)", stripped):
                return [
                    self.build_violation(
                        config,
                        location=Location(line=line_no, column=1),
                        suggestion="Name the default class export to improve stack traces and maintainability.",
                    ),
                ]
            if re.match(r"export\s+default\s*(?:\(|async\s*\(|\{|\[)", stripped):
                return [
                    self.build_violation(
                        config,
                        location=Location(line=line_no, column=1),
                        suggestion="Export a named component/function instead of an anonymous default expression.",
                    ),
                ]
        return []


class MarkdownMdxImportHygieneDetector(
    ViolationDetector[MarkdownMdxImportHygieneConfig],
    LocationHelperMixin,
):
    """Detect imported MDX identifiers that are never referenced."""

    @property
    def name(self) -> str:
        return "md-007"

    def detect(
        self,
        context: AnalysisContext,
        config: MarkdownMdxImportHygieneConfig,
    ) -> list[Violation]:
        if config.mdx_only and not _is_mdx_context(context):
            return []
        imports: dict[str, int] = {}
        non_import_lines: list[str] = []
        for line_no, line in enumerate(context.code.splitlines(), start=1):
            stripped = line.strip()
            if _MDX_IMPORT_SIDE_EFFECT_RE.match(stripped):
                continue
            if match := _MDX_IMPORT_RE.match(stripped):
                for identifier in _extract_imported_identifiers(match.group(1)):
                    imports.setdefault(identifier, line_no)
                continue
            non_import_lines.append(line)

        if not imports:
            return []
        usage_text = "\n".join(non_import_lines)
        unused = next(
            (
                (name, line_no)
                for name, line_no in imports.items()
                if not re.search(rf"<{re.escape(name)}\b", usage_text)
                and not re.search(rf"\b{re.escape(name)}\b", usage_text)
            ),
            None,
        )
        if unused is None:
            return []
        name, line_no = unused
        return [
            self.build_violation(
                config,
                location=Location(line=line_no, column=1),
                suggestion=f"Remove unused import '{name}' or reference it in MDX content.",
            ),
        ]


def _extract_imported_identifiers(import_clause: str) -> set[str]:
    names: set[str] = set()
    clause = import_clause.strip()
    if clause.startswith("{"):
        return _parse_named_imports(clause)
    if clause.startswith("*"):
        if match := re.match(r"\*\s+as\s+([A-Za-z_][A-Za-z0-9_]*)", clause):
            names.add(match.group(1))
        return names
    if "," in clause:
        default_name, remainder = [part.strip() for part in clause.split(",", 1)]
        if re.match(r"[A-Za-z_][A-Za-z0-9_]*$", default_name):
            names.add(default_name)
        if remainder.startswith("{"):
            names |= _parse_named_imports(remainder)
        elif remainder.startswith("*") and (
            match := re.match(r"\*\s+as\s+([A-Za-z_][A-Za-z0-9_]*)", remainder)
        ):
            names.add(match.group(1))
        return names
    if re.match(r"[A-Za-z_][A-Za-z0-9_]*$", clause):
        names.add(clause)
    return names


def _parse_named_imports(clause: str) -> set[str]:
    match = re.search(r"\{(.+)\}", clause)
    if not match:
        return set()
    names: set[str] = set()
    for part in match.group(1).split(","):
        token = part.strip()
        if not token:
            continue
        if " as " in token:
            _, alias = token.split(" as ", 1)
            token = alias.strip()
        if re.match(r"[A-Za-z_][A-Za-z0-9_]*$", token):
            names.add(token)
    return names


__all__ = [
    "MarkdownAltTextDetector",
    "MarkdownBareUrlDetector",
    "MarkdownCodeFenceLanguageDetector",
    "MarkdownFrontMatterDetector",
    "MarkdownHeadingHierarchyDetector",
    "MarkdownMdxImportHygieneDetector",
    "MarkdownMdxNamedDefaultExportDetector",
]
