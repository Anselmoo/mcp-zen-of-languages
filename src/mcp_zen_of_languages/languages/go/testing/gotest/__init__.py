"""Go testing framework analyzer."""

from __future__ import annotations

from mcp_zen_of_languages.analyzers.base import DetectionPipeline
from mcp_zen_of_languages.analyzers.framework_bridge import FRAMEWORK_REGISTRY
from mcp_zen_of_languages.analyzers.framework_bridge import FrameworkAnalyzer
from mcp_zen_of_languages.languages.go.testing.gotest.detectors import (
    EmptySubtestNameDetector,
)
from mcp_zen_of_languages.languages.go.testing.gotest.detectors import (
    FatalInAssertDetector,
)
from mcp_zen_of_languages.languages.go.testing.gotest.detectors import (
    GlobalMutableStateDetector,
)
from mcp_zen_of_languages.languages.go.testing.gotest.detectors import (
    MissingTHelperDetector,
)
from mcp_zen_of_languages.languages.go.testing.gotest.detectors import (
    OsExitInTestDetector,
)
from mcp_zen_of_languages.languages.go.testing.gotest.detectors import (
    ParallelTestDetector,
)
from mcp_zen_of_languages.languages.go.testing.gotest.detectors import (
    TimeSleepInTestDetector,
)


class GoTestAnalyzer(FrameworkAnalyzer):
    """Framework analyzer for Go test files."""

    test_file_patterns: tuple[str, ...] = (r".*_test\.go$",)
    parent_language: str = "go"

    def language(self) -> str:
        """Return the framework language identifier."""
        return "gotest"

    def build_pipeline(self) -> DetectionPipeline:
        """Build the Go test detection pipeline."""
        return DetectionPipeline(
            detectors=[
                ParallelTestDetector(),
                FatalInAssertDetector(),
                MissingTHelperDetector(),
                OsExitInTestDetector(),
                TimeSleepInTestDetector(),
                EmptySubtestNameDetector(),
                GlobalMutableStateDetector(),
            ]
        )


FRAMEWORK_REGISTRY.register(GoTestAnalyzer)
