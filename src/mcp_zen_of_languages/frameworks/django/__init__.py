"""Django framework support."""

from .analyzer import DjangoAnalyzer
from .rules import DJANGO_ZEN


__all__ = ["DJANGO_ZEN", "DjangoAnalyzer"]
