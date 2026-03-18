"""Shared contracts and helpers for framework analyzers."""

from __future__ import annotations

from typing import ClassVar

from pydantic import BaseModel
from pydantic import ConfigDict


class FrameworkDescriptor(BaseModel):
    """Describe one supported framework and its parent language."""

    model_config = ConfigDict(frozen=True)

    key: str
    parent_language: str


FRAMEWORK_DESCRIPTORS: tuple[FrameworkDescriptor, ...] = (
    FrameworkDescriptor(key="react", parent_language="typescript"),
    FrameworkDescriptor(key="vue", parent_language="javascript"),
    FrameworkDescriptor(key="angular", parent_language="typescript"),
    FrameworkDescriptor(key="nextjs", parent_language="react"),
    FrameworkDescriptor(key="pydantic", parent_language="python"),
    FrameworkDescriptor(key="fastapi", parent_language="python"),
    FrameworkDescriptor(key="django", parent_language="python"),
    FrameworkDescriptor(key="sqlalchemy", parent_language="python"),
)

FRAMEWORK_KEYS: frozenset[str] = frozenset(
    descriptor.key for descriptor in FRAMEWORK_DESCRIPTORS
)
_FRAMEWORKS_BY_KEY = {
    descriptor.key: descriptor for descriptor in FRAMEWORK_DESCRIPTORS
}


def framework_descriptor(language: str) -> FrameworkDescriptor | None:
    """Return the framework descriptor for *language*, if it is a framework key."""
    return _FRAMEWORKS_BY_KEY.get(language)


def is_framework_key(language: str) -> bool:
    """Return whether *language* refers to a supported framework analyzer."""
    return language in FRAMEWORK_KEYS


def module_prefix_for_language(language: str) -> str:
    """Return the import package prefix for a language or framework key."""
    return "frameworks" if is_framework_key(language) else "languages"


def module_import_path(language: str, module_name: str) -> str:
    """Build an absolute module path for a language/framework support module."""
    prefix = module_prefix_for_language(language)
    return f"mcp_zen_of_languages.{prefix}.{language}.{module_name}"


class FrameworkAnalyzerMixin:
    """Mixin that gives framework analyzers a stable framework identity contract."""

    framework_key: ClassVar[str]
    parent_language_key: ClassVar[str]

    def language(self) -> str:
        """Return the framework key used for routing and reporting."""
        return self.framework_key

    @classmethod
    def framework_language(cls) -> str:
        """Return the canonical framework key for the analyzer class."""
        return cls.framework_key

    @classmethod
    def parent_language(cls) -> str:
        """Return the canonical parent language key for the framework."""
        return cls.parent_language_key
