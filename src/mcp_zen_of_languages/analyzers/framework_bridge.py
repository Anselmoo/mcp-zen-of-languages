"""Framework analyzer bridge — routes test files to framework-specific analyzers.

Adds a file-pattern-based sub-analyzer layer on top of BaseAnalyzer.
Framework analyzers activate only when the analyzed file path matches
their test_file_patterns (e.g. ``test_*.py``, ``*.spec.ts``).

Pattern::

    FrameworkAnalyzer(BaseAnalyzer)  — adds is_test_file() + test_file_patterns
    FrameworkRegistry                — maps (language, path) → list[FrameworkAnalyzer]
    FRAMEWORK_REGISTRY               — module-level singleton

Usage::

    from mcp_zen_of_languages.analyzers.framework_bridge import FRAMEWORK_REGISTRY

    frameworks = FRAMEWORK_REGISTRY.get_frameworks("python", "tests/test_auth.py")
    for fw in frameworks:
        result = fw.analyze(code, path=path)
"""

from __future__ import annotations

import re

from abc import abstractmethod
from typing import TYPE_CHECKING

from mcp_zen_of_languages.analyzers.base import AnalyzerConfig
from mcp_zen_of_languages.analyzers.base import BaseAnalyzer
from mcp_zen_of_languages.analyzers.base import DetectionPipeline


if TYPE_CHECKING:
    from collections.abc import Iterator

    from mcp_zen_of_languages.models import CyclomaticSummary
    from mcp_zen_of_languages.models import ParserResult


class FrameworkAnalyzer(BaseAnalyzer):
    """Abstract base for framework-specific test analyzers.

    Extends [`BaseAnalyzer`][mcp_zen_of_languages.analyzers.base.BaseAnalyzer] with
    file-pattern matching so that each framework analyzer is only invoked when
    the file under analysis looks like a test file for that framework (e.g.
    ``test_*.py`` for pytest, ``*.spec.ts`` for Jest).

    Subclasses must still implement the standard ``BaseAnalyzer`` hooks
    (``parse_code``, ``compute_metrics``, ``build_pipeline``), plus set the
    ``test_file_patterns`` and ``parent_language`` class attributes.

    Attributes:
        test_file_patterns: Tuple of regex patterns. A file is considered a
            test file if its path matches *any* of these patterns.
        parent_language: The main language identifier (e.g. ``"python"``,
            ``"typescript"``) that this framework belongs to.
    """

    test_file_patterns: tuple[str, ...] = ()
    parent_language: str = ""

    def __init__(self, config: AnalyzerConfig | None = None) -> None:
        """Initialize the framework analyzer with optional config."""
        self._pipeline_config = None
        super().__init__(config=config)

    def is_test_file(self, path: str | None) -> bool:
        """Return True if the file path matches any of the test file patterns.

        Args:
            path: Filesystem path to check. Returns ``False`` when ``None``.

        Returns:
            bool: ``True`` when at least one pattern in ``test_file_patterns``
            matches the tail portion (basename + parent dir) of *path*.
        """
        if path is None:
            return False
        return any(re.search(pattern, path) for pattern in self.test_file_patterns)

    def default_config(self) -> AnalyzerConfig:
        """Return a baseline analyzer config for the framework."""
        return AnalyzerConfig()

    def parse_code(self, _code: str) -> ParserResult | None:
        """Framework analyzers use regex-only detection; no AST parsing."""
        return None

    def compute_metrics(
        self,
        code: str,
        _ast_tree: ParserResult | None,
    ) -> tuple[CyclomaticSummary | None, float | None, int]:
        """Return minimal metrics (no cyclomatic/maintainability computation)."""
        return None, None, len(code.splitlines())

    @abstractmethod
    def build_pipeline(self) -> DetectionPipeline:
        """Build the framework-specific detection pipeline."""


class FrameworkRegistry:
    """Registry that maps (language, path) to framework analyzer instances.

    Maintains a list of [`FrameworkAnalyzer`][mcp_zen_of_languages.analyzers.framework_bridge.FrameworkAnalyzer] *classes* (not instances)
    and instantiates them on demand when
    `get_frameworks` is called.

    Example::

        FRAMEWORK_REGISTRY.register(PytestAnalyzer)
        analyzers = FRAMEWORK_REGISTRY.get_frameworks("python", "tests/test_foo.py")
    """

    def __init__(self) -> None:
        """Initialize an empty framework registry."""
        self._frameworks: list[type[FrameworkAnalyzer]] = []

    def register(self, framework_cls: type[FrameworkAnalyzer]) -> None:
        """Register a framework analyzer class.

        Args:
            framework_cls: Concrete [`FrameworkAnalyzer`][mcp_zen_of_languages.analyzers.framework_bridge.FrameworkAnalyzer] subclass to
                register. Duplicate registrations are ignored.
        """
        if framework_cls not in self._frameworks:
            self._frameworks.append(framework_cls)

    def get_frameworks(
        self,
        language: str,
        path: str | None,
    ) -> list[FrameworkAnalyzer]:
        """Return instantiated framework analyzers matching language and file path.

        Only framework classes whose ``parent_language`` equals *language* **and**
        whose `is_test_file` returns ``True`` for
        *path* are returned.

        Args:
            language: Language identifier (e.g. ``"python"``).
            path: File path of the code under analysis, or ``None``.

        Returns:
            list[FrameworkAnalyzer]: Zero or more instantiated analyzers.
        """
        result: list[FrameworkAnalyzer] = []
        for cls in self._frameworks:
            # Instantiate temporarily to call is_test_file without storing
            instance = cls.__new__(cls)
            if instance.parent_language != language:
                continue
            if not instance.is_test_file(path):
                continue
            result.append(cls())
        return result

    def __iter__(self) -> Iterator[type[FrameworkAnalyzer]]:
        """Iterate over registered framework classes."""
        return iter(self._frameworks)

    def registered_count(self) -> int:
        """Return the number of registered framework classes."""
        return len(self._frameworks)


FRAMEWORK_REGISTRY: FrameworkRegistry = FrameworkRegistry()
