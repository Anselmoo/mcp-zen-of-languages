"""JSON language package."""

from .analyzer import JSONAnalyzer, JsonAnalyzer
from .rules import JSON_ZEN

__all__ = ["JSON_ZEN", "JSONAnalyzer", "JsonAnalyzer"]
