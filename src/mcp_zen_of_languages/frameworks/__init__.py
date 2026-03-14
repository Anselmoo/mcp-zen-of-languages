"""Framework support modules and shared framework metadata."""

from .base import FRAMEWORK_DESCRIPTORS
from .base import FRAMEWORK_KEYS
from .base import FrameworkAnalyzerMixin
from .base import FrameworkDescriptor
from .base import framework_descriptor
from .base import is_framework_key
from .base import module_import_path
from .base import module_prefix_for_language


__all__ = [
    "FRAMEWORK_DESCRIPTORS",
    "FRAMEWORK_KEYS",
    "FrameworkAnalyzerMixin",
    "FrameworkDescriptor",
    "framework_descriptor",
    "is_framework_key",
    "module_import_path",
    "module_prefix_for_language",
]
