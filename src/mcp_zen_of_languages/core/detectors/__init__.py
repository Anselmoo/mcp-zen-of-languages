"""Universal detector module stubs grouped by Zen Dogma areas."""

from mcp_zen_of_languages.core.detectors.clutter import ClutterDetector
from mcp_zen_of_languages.core.detectors.control_flow import ControlFlowDetector
from mcp_zen_of_languages.core.detectors.signature import SignatureDetector
from mcp_zen_of_languages.core.detectors.state_mutation import StateMutationDetector

__all__ = [
    "ClutterDetector",
    "ControlFlowDetector",
    "SignatureDetector",
    "StateMutationDetector",
]
