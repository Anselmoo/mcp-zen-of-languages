"""Framework support modules and shared framework metadata."""

from .base import FRAMEWORK_DESCRIPTORS
from .base import FRAMEWORK_KEYS
from .base import FrameworkAnalyzerMixin
from .base import FrameworkDescriptor
from .base import framework_descriptor
from .base import is_framework_key
from .base import module_import_path
from .base import module_prefix_for_language
from .dogmas import FRAMEWORK_RULE_DOGMAS
from .dogmas import framework_rule_dogmas


__all__ = [
    "FRAMEWORK_DESCRIPTORS",
    "FRAMEWORK_KEYS",
    "FRAMEWORK_RULE_DOGMAS",
    "FrameworkAnalyzerMixin",
    "FrameworkDescriptor",
    "framework_descriptor",
    "framework_rule_dogmas",
    "is_framework_key",
    "module_import_path",
    "module_prefix_for_language",
]
