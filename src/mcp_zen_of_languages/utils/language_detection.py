"""Resolve source-file language before analysis so the correct analyzer is dispatched.

Two strategies are available: extension-based lookup (high confidence, fast)
and content-heuristic scanning (lower confidence, used when no path is
supplied). The MCP server and CLI invoke these detectors early in the request
lifecycle to route code to the appropriate language-specific pipeline.
"""

from __future__ import annotations

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
    ".sql": "sql",
    ".ddl": "sql",
    ".dml": "sql",
    ".md": "markdown",
    ".markdown": "markdown",
    ".mdx": "markdown",
    ".tex": "latex",
    ".ltx": "latex",
    ".sty": "latex",
    ".bib": "latex",
    ".dockerfile": "dockerfile",
}


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
            A dict with keys ``language``, ``confidence``, ``method``, and ``notes``.
        """
        return self.model_dump()


def detect_language_by_extension(path: str) -> DetectionResult:
    """Look up the file extension in ``EXTENSION_LANGUAGE_MAP`` and return a high-confidence result.

    This is the primary detection strategy and the fastest path. It
    extracts the suffix with ``os.path.splitext``, normalises to lowercase,
    and matches against the static extension map. Unknown extensions yield
    ``language="unknown"`` so callers can fall back to content heuristics.

    Args:
        path: Filesystem path (absolute or relative) whose extension is inspected.

    Returns:
        A ``DetectionResult`` with ``method="extension"`` and confidence 0.95
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
    lang = EXTENSION_LANGUAGE_MAP.get(ext, "unknown")
    return DetectionResult(language=lang, confidence=0.95, method="extension")


def detect_language_from_content(code: str) -> DetectionResult:
    """Infer the programming language by scanning *code* for characteristic keywords.

    Used as a fallback when no file path is available. The heuristic checks
    for ``def `` (Python), ``interface``/``=>`` (TypeScript), and ``function``/
    ``const``/``let`` (JavaScript) in order of decreasing specificity.
    Confidence scores are lower than extension-based detection to reflect
    the inherent ambiguity of keyword matching.

    Args:
        code: Raw source text to scan for language-indicative patterns.

    Returns:
        A ``DetectionResult`` with ``method="heuristics"`` and a confidence
        between 0.1 (unknown) and 0.9 (strong keyword match).
    """
    # Relaxed heuristics: 'def ' alone is sufficient to indicate Python in many fixtures
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
