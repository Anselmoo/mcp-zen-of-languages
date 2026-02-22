"""Universal detector module stubs grouped by Zen Dogma areas."""

from mcp_zen_of_languages.detectors.clutter import ClutterDetector
from mcp_zen_of_languages.detectors.control_flow import ControlFlowDetector
from mcp_zen_of_languages.detectors.signature import SignatureDetector
from mcp_zen_of_languages.detectors.state_mutation import StateMutationDetector

__all__ = [
    "ClutterDetector",
    "ControlFlowDetector",
    "SignatureDetector",
    "StateMutationDetector",
]
