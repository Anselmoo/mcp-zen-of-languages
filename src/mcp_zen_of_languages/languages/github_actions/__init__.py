"""GitHub Actions language package."""

from .analyzer import GitHubActionsAnalyzer
from .rules import GITHUB_ACTIONS_ZEN

__all__ = ["GITHUB_ACTIONS_ZEN", "GitHubActionsAnalyzer"]
