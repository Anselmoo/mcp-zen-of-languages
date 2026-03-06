"""Shared target collection and analysis orchestration for CLI, server, and reports."""

from __future__ import annotations

import logging

from pathlib import Path
from pathlib import PurePosixPath
from typing import TYPE_CHECKING
from typing import Literal

from mcp_zen_of_languages.analyzers.analyzer_factory import create_analyzer
from mcp_zen_of_languages.config import load_config
from mcp_zen_of_languages.models import AnalysisResult
from mcp_zen_of_languages.models import CyclomaticSummary
from mcp_zen_of_languages.models import Metrics
from mcp_zen_of_languages.models import Violation
from mcp_zen_of_languages.utils.language_detection import detect_language_by_extension


if TYPE_CHECKING:
    from collections.abc import Callable

    from mcp_zen_of_languages.analyzers.pipeline import PipelineConfig

logger = logging.getLogger(__name__)

# Minimum number of whitespace-split tokens in an import statement to extract the module name
MIN_IMPORT_PARTS = 2
IGNORE_FILES = (".gitignore", ".zen-of-languages.ignore")


class _IgnoreRule:
    def __init__(self, pattern: str, *, negate: bool, directory_only: bool) -> None:
        self.pattern = pattern
        self.negate = negate
        self.directory_only = directory_only


def _parse_ignore_rules(path: Path) -> list[_IgnoreRule]:
    rules: list[_IgnoreRule] = []
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        negate = line.startswith("!")
        if negate:
            line = line[1:].strip()
            if not line:
                continue
        directory_only = line.endswith("/")
        rules.append(_IgnoreRule(line.rstrip("/"), negate=negate, directory_only=directory_only))
    return rules


def _collect_ignore_rule_sets(scan_root: Path) -> list[tuple[Path, list[_IgnoreRule]]]:
    roots = [*reversed(scan_root.parents), scan_root]
    rule_sets: list[tuple[Path, list[_IgnoreRule]]] = []
    for root in roots:
        for ignore_name in IGNORE_FILES:
            ignore_path = root / ignore_name
            if not ignore_path.is_file():
                continue
            try:
                rules = _parse_ignore_rules(ignore_path)
            except OSError as exc:
                logger.debug("Unable to read ignore file %s: %s", ignore_path, exc)
                continue
            if rules:
                rule_sets.append((root, rules))
    return rule_sets


def _rule_matches(rule: _IgnoreRule, rel_path: str) -> bool:
    pattern = rule.pattern
    if not pattern:
        return False

    if rule.directory_only:
        if "/" in pattern:
            return rel_path == pattern or rel_path.startswith(f"{pattern}/")
        return f"/{pattern}/" in f"/{rel_path}/"

    if "/" in pattern:
        direct_match = rel_path == pattern
        subtree_match = rel_path.startswith(f"{pattern}/")
        glob_match = PurePosixPath(rel_path).match(pattern)
        return direct_match or subtree_match or glob_match

    parts = rel_path.split("/")
    return any(PurePosixPath(part).match(pattern) for part in parts)


def _is_ignored(
    path: Path,
    *,
    rule_sets: list[tuple[Path, list[_IgnoreRule]]],
) -> bool:
    ignored = False
    for root, rules in rule_sets:
        try:
            rel_path = path.relative_to(root).as_posix()
        except ValueError:
            continue
        for rule in rules:
            if _rule_matches(rule, rel_path):
                ignored = not rule.negate
    return ignored


def collect_targets(
    target: Path,
    language_override: str | None,
) -> list[tuple[Path, str]]:
    """Discover analysable source files under a target path."""
    scan_root = target if target.is_dir() else target.parent
    rule_sets = _collect_ignore_rule_sets(scan_root)
    if target.is_file():
        if _is_ignored(target, rule_sets=rule_sets):
            return []
        if language_override:
            return [(target, language_override)]
        detected = detect_language_by_extension(str(target)).language
        return [(target, detected if detected != "unknown" else "python")]

    targets: list[tuple[Path, str]] = []
    for path in target.rglob("*"):
        if _is_ignored(path, rule_sets=rule_sets):
            continue
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
    language: str,
    path: str,
    error: Exception,
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
            ),
        ],
        overall_score=0.0,
    )


def analyze_targets(  # noqa: C901, PLR0912, PLR0913, PLR0915
    targets: list[tuple[Path, str]],
    *,
    config_path: str | None = None,
    pipeline_resolver: Callable[[str], PipelineConfig] | None = None,
    unsupported_language: Literal["skip", "placeholder"] = "skip",
    include_read_errors: bool = False,
    progress_callback: Callable[[], None] | None = None,
    enable_external_tools: bool = False,
    allow_temporary_tools: bool = False,
) -> list[AnalysisResult]:
    """Analyze targets grouped by language using the analyzer factory.

    Args:
        targets (list[tuple[Path, str]]): File-path / language pairs to analyse.
        config_path (str | None, optional): Custom ``zen-config.yaml`` path, or ``None`` for auto-discovery. Default to None.
        pipeline_resolver (Callable[[str], PipelineConfig] | None, optional): Callable returning pipeline config per language. Default to None.
        unsupported_language (Literal['skip', 'placeholder'], optional): Strategy for unsupported languages. Default to "skip".
        include_read_errors (bool, optional): Include file read errors in results. Default to False.
        progress_callback (Callable[[], None] | None, optional): Called after each file is analysed. Default to None.
        enable_external_tools (bool, optional): Opt-in execution of external linters. Default to False.
        allow_temporary_tools (bool, optional): Allow temporary tool runners (e.g. npx/uvx). Default to False.
    """
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

        if language == "latex":
            file_contents: dict[str, str] = {}
            for path in files:
                try:
                    file_contents[str(path)] = path.read_text(encoding="utf-8")
                except Exception as exc:
                    if include_read_errors:
                        logger.warning(
                            "Failed to read %s during analysis scan: %s",
                            path,
                            exc,
                        )
                        results.append(
                            _file_read_error_result(language, str(path), exc)
                        )
                        if progress_callback is not None:
                            progress_callback()
                        continue
                    if progress_callback is not None:
                        progress_callback()
                    raise

            for path_str, code in file_contents.items():
                analyze_kwargs: dict[str, object] = {
                    "path": path_str,
                    "other_files": file_contents,
                    "repository_imports": repository_imports,
                }
                if enable_external_tools:
                    analyze_kwargs["enable_external_tools"] = True
                if allow_temporary_tools:
                    analyze_kwargs["allow_temporary_tools"] = True
                results.append(
                    analyzer.analyze(
                        code,
                        **analyze_kwargs,
                    ),
                )
                if progress_callback is not None:
                    progress_callback()
            continue

        for path in files:
            try:
                code = path.read_text(encoding="utf-8")
            except Exception as exc:
                if include_read_errors:
                    logger.warning(
                        "Failed to read %s during analysis scan: %s",
                        path,
                        exc,
                    )
                    results.append(_file_read_error_result(language, str(path), exc))
                    if progress_callback is not None:
                        progress_callback()
                    continue
                if progress_callback is not None:
                    progress_callback()
                raise
            analyze_kwargs = {
                "path": str(path),
                "repository_imports": repository_imports,
            }
            if enable_external_tools:
                analyze_kwargs["enable_external_tools"] = True
            if allow_temporary_tools:
                analyze_kwargs["allow_temporary_tools"] = True
            results.append(
                analyzer.analyze(
                    code,
                    **analyze_kwargs,
                ),
            )
            if progress_callback is not None:
                progress_callback()
    return results
