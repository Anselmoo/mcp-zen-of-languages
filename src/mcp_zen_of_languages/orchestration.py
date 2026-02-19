"""Shared target collection and analysis orchestration for CLI, server, and reports."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Literal

from mcp_zen_of_languages.analyzers.analyzer_factory import create_analyzer
from mcp_zen_of_languages.config import load_config
from mcp_zen_of_languages.models import (
    AnalysisResult,
    CyclomaticSummary,
    Metrics,
    Violation,
)
from mcp_zen_of_languages.utils.language_detection import detect_language_by_extension

if TYPE_CHECKING:
    from collections.abc import Callable
    from pathlib import Path

    from mcp_zen_of_languages.analyzers.pipeline import PipelineConfig

logger = logging.getLogger(__name__)

# Minimum number of whitespace-split tokens in an import statement to extract the module name
MIN_IMPORT_PARTS = 2


def collect_targets(
    target: Path, language_override: str | None
) -> list[tuple[Path, str]]:
    """Discover analysable source files under a target path."""
    if target.is_file():
        if language_override:
            return [(target, language_override)]
        detected = detect_language_by_extension(str(target)).language
        return [(target, detected if detected != "unknown" else "python")]

    targets: list[tuple[Path, str]] = []
    for path in target.rglob("*"):
        if not path.is_file():
            continue
        detected = detect_language_by_extension(str(path)).language
        if language_override:
            if detected != language_override:
                continue
            targets.append((path, language_override))
            continue
        if detected == "unknown":
            continue
        targets.append((path, detected))
    return targets


def _extract_python_imports(text: str) -> list[str]:
    imports: list[str] = []
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith(("import ", "from ")):
            parts = stripped.split()
            if len(parts) >= MIN_IMPORT_PARTS:
                imports.append(parts[1].split(".")[0])
    return imports


def build_repository_imports(files: list[Path], language: str) -> dict[str, list[str]]:
    """Build language-aware repository import maps for cross-file analysis."""
    repository_imports: dict[str, list[str]] = {}
    for path in files:
        text = path.read_text(encoding="utf-8")
        imports = _extract_python_imports(text) if language == "python" else []
        repository_imports[str(path)] = imports
    return repository_imports


def _placeholder_result(language: str, path: str) -> AnalysisResult:
    cyclomatic = CyclomaticSummary(blocks=[], average=0.0)
    metrics = Metrics(cyclomatic=cyclomatic, maintainability_index=0.0, lines_of_code=0)
    return AnalysisResult(
        language=language,
        path=path,
        metrics=metrics,
        violations=[],
        overall_score=100.0,
    )


def _file_read_error_result(
    language: str, path: str, error: Exception
) -> AnalysisResult:
    return AnalysisResult(
        language=language,
        path=path,
        metrics=Metrics(
            cyclomatic=CyclomaticSummary(blocks=[], average=0.0),
            maintainability_index=0.0,
            lines_of_code=0,
        ),
        violations=[
            Violation(
                principle="analysis.file_read_error",
                severity=8,
                message=f"Failed to read {path}: {error}",
                suggestion="Ensure the file is readable and try again.",
                files=[path],
            )
        ],
        overall_score=0.0,
    )


def analyze_targets(
    targets: list[tuple[Path, str]],
    *,
    config_path: str | None = None,
    pipeline_resolver: Callable[[str], PipelineConfig] | None = None,
    unsupported_language: Literal["skip", "placeholder"] = "skip",
    include_read_errors: bool = False,
    progress_callback: Callable[[], None] | None = None,
) -> list[AnalysisResult]:
    """Analyze targets grouped by language using the analyzer factory."""
    config = load_config(config_path)
    results: list[AnalysisResult] = []
    files_by_language: dict[str, list[Path]] = {}
    for path, language in targets:
        files_by_language.setdefault(language, []).append(path)

    for language, files in files_by_language.items():
        try:
            pipeline_config = (
                pipeline_resolver(language)
                if pipeline_resolver is not None
                else config.pipeline_for(language)
            )
            analyzer = create_analyzer(language, pipeline_config=pipeline_config)
        except ValueError:
            if unsupported_language == "placeholder":
                for path in files:
                    results.append(_placeholder_result(language, str(path)))
                    if progress_callback is not None:
                        progress_callback()
            continue

        try:
            repository_imports = build_repository_imports(files, language)
        except Exception as exc:  # noqa: BLE001
            logger.warning("Failed import scan for %s files: %s", language, exc)
            repository_imports = {str(path): [] for path in files}

        for path in files:
            try:
                code = path.read_text(encoding="utf-8")
            except Exception as exc:
                if include_read_errors:
                    logger.warning(
                        "Failed to read %s during analysis scan: %s", path, exc
                    )
                    results.append(_file_read_error_result(language, str(path), exc))
                    if progress_callback is not None:
                        progress_callback()
                    continue
                raise
            results.append(
                analyzer.analyze(
                    code,
                    path=str(path),
                    repository_imports=repository_imports,
                )
            )
            if progress_callback is not None:
                progress_callback()
    return results
