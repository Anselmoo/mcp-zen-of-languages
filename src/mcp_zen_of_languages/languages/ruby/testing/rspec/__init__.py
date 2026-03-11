"""RSpec framework analyzer."""

from __future__ import annotations

from mcp_zen_of_languages.analyzers.base import DetectionPipeline
from mcp_zen_of_languages.analyzers.framework_bridge import FRAMEWORK_REGISTRY
from mcp_zen_of_languages.analyzers.framework_bridge import FrameworkAnalyzer
from mcp_zen_of_languages.languages.ruby.testing.rspec.detectors import AnonItDetector
from mcp_zen_of_languages.languages.ruby.testing.rspec.detectors import (
    AnyInstanceDetector,
)
from mcp_zen_of_languages.languages.ruby.testing.rspec.detectors import (
    BeforeAllMutationDetector,
)
from mcp_zen_of_languages.languages.ruby.testing.rspec.detectors import (
    FocusMarkerDetector,
)
from mcp_zen_of_languages.languages.ruby.testing.rspec.detectors import (
    InstanceVarInBeforeDetector,
)
from mcp_zen_of_languages.languages.ruby.testing.rspec.detectors import LetBangDetector
from mcp_zen_of_languages.languages.ruby.testing.rspec.detectors import (
    PendingExampleDetector,
)


class RSpecAnalyzer(FrameworkAnalyzer):
    """Framework analyzer for RSpec test files."""

    test_file_patterns: tuple[str, ...] = (r".*_spec\.rb$",)
    parent_language: str = "ruby"

    def language(self) -> str:
        """Return the framework language identifier."""
        return "rspec"

    def build_pipeline(self) -> DetectionPipeline:
        """Build the RSpec detection pipeline."""
        return DetectionPipeline(
            detectors=[
                AnonItDetector(),
                InstanceVarInBeforeDetector(),
                LetBangDetector(),
                BeforeAllMutationDetector(),
                AnyInstanceDetector(),
                PendingExampleDetector(),
                FocusMarkerDetector(),
            ]
        )


FRAMEWORK_REGISTRY.register(RSpecAnalyzer)
