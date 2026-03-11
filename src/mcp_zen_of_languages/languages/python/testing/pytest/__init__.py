"""Pytest framework analyzer."""

from __future__ import annotations

from mcp_zen_of_languages.analyzers.base import DetectionPipeline
from mcp_zen_of_languages.analyzers.framework_bridge import FRAMEWORK_REGISTRY
from mcp_zen_of_languages.analyzers.framework_bridge import FrameworkAnalyzer
from mcp_zen_of_languages.languages.python.testing.pytest.detectors import (
    BareExceptInTestDetector,
)
from mcp_zen_of_languages.languages.python.testing.pytest.detectors import (
    LoopInTestDetector,
)
from mcp_zen_of_languages.languages.python.testing.pytest.detectors import (
    ModuleLevelMockDetector,
)
from mcp_zen_of_languages.languages.python.testing.pytest.detectors import (
    NoAssertInTestDetector,
)
from mcp_zen_of_languages.languages.python.testing.pytest.detectors import (
    PytestRaisesDetector,
)
from mcp_zen_of_languages.languages.python.testing.pytest.detectors import (
    SleepInTestDetector,
)
from mcp_zen_of_languages.languages.python.testing.pytest.detectors import (
    UnittestAssertDetector,
)
from mcp_zen_of_languages.languages.python.testing.pytest.detectors import (
    VagueTestNameDetector,
)


class PytestAnalyzer(FrameworkAnalyzer):
    """Framework analyzer for pytest test files."""

    test_file_patterns: tuple[str, ...] = (
        r"test_.*\.py$",
        r".*_test\.py$",
        r"conftest\.py$",
    )
    parent_language: str = "python"

    def language(self) -> str:
        """Return the framework language identifier."""
        return "pytest"

    def build_pipeline(self) -> DetectionPipeline:
        """Build the pytest detection pipeline."""
        return DetectionPipeline(
            detectors=[
                UnittestAssertDetector(),
                SleepInTestDetector(),
                LoopInTestDetector(),
                NoAssertInTestDetector(),
                VagueTestNameDetector(),
                BareExceptInTestDetector(),
                PytestRaisesDetector(),
                ModuleLevelMockDetector(),
            ]
        )


FRAMEWORK_REGISTRY.register(PytestAnalyzer)
