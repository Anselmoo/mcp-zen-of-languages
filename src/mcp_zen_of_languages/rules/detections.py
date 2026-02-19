"""Compatibility shim: re-export detection helpers from rules.tools.detections.

Legacy import path: `mcp_zen_of_languages.rules.detections`
New canonical path: `mcp_zen_of_languages.rules.tools.detections`
"""

from .tools import detections as _detections
from .tools.detections import *  # noqa: F403

__all__ = list(_detections.__all__)
