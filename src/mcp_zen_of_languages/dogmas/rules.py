"""Compatibility wrappers around the explicit dogma catalog."""

from __future__ import annotations

from typing import TYPE_CHECKING

from mcp_zen_of_languages.core.universal_dogmas import dogmas_for_rule
from mcp_zen_of_languages.core.universal_dogmas import dogmas_for_rule_ids


if TYPE_CHECKING:
    from collections.abc import Iterable


def resolved_rule_dogmas(language: str, rule_id: str) -> tuple[str, ...]:
    """Return the explicit dogma set assigned to one rule id."""
    return dogmas_for_rule(language, rule_id)


def resolved_rule_dogmas_for_rule_ids(
    language: str,
    rule_ids: Iterable[str],
) -> tuple[str, ...]:
    """Return ordered unique explicit dogmas for one or more rule ids."""
    return dogmas_for_rule_ids(language, tuple(rule_ids))


__all__ = ["resolved_rule_dogmas", "resolved_rule_dogmas_for_rule_ids"]
