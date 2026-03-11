"""Jest framework analyzer."""

from __future__ import annotations

from mcp_zen_of_languages.analyzers.base import DetectionPipeline
from mcp_zen_of_languages.analyzers.framework_bridge import FRAMEWORK_REGISTRY
from mcp_zen_of_languages.analyzers.framework_bridge import FrameworkAnalyzer
from mcp_zen_of_languages.languages.typescript.testing.jest.detectors import (
    AssertionsZeroDetector,
)
from mcp_zen_of_languages.languages.typescript.testing.jest.detectors import (
    DeepDescribeDetector,
)
from mcp_zen_of_languages.languages.typescript.testing.jest.detectors import (
    EmptyDescribeDetector,
)
from mcp_zen_of_languages.languages.typescript.testing.jest.detectors import (
    NoExpectDetector,
)
from mcp_zen_of_languages.languages.typescript.testing.jest.detectors import (
    NoRestoreMocksDetector,
)
from mcp_zen_of_languages.languages.typescript.testing.jest.detectors import (
    RealTimerInTestDetector,
)
from mcp_zen_of_languages.languages.typescript.testing.jest.detectors import (
    UnawaitedPromiseDetector,
)
from mcp_zen_of_languages.languages.typescript.testing.jest.detectors import (
    VagueTitleDetector,
)


class JestAnalyzer(FrameworkAnalyzer):
    """Framework analyzer for Jest/Vitest test files."""

    test_file_patterns: tuple[str, ...] = (
        r".*\.(test|spec)\.(ts|tsx|js|jsx)$",
        r"__tests__/.*",
    )
    parent_language: str = "typescript"

    def language(self) -> str:
        """Return the framework language identifier."""
        return "jest"

    def build_pipeline(self) -> DetectionPipeline:
        """Build the Jest detection pipeline."""
        return DetectionPipeline(
            detectors=[
                NoExpectDetector(),
                UnawaitedPromiseDetector(),
                RealTimerInTestDetector(),
                EmptyDescribeDetector(),
                AssertionsZeroDetector(),
                VagueTitleDetector(),
                DeepDescribeDetector(),
                NoRestoreMocksDetector(),
            ]
        )


FRAMEWORK_REGISTRY.register(JestAnalyzer)
