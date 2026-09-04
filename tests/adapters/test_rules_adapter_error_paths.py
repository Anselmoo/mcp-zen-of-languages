from __future__ import annotations

import logging

from mcp_zen_of_languages.adapters.rules_adapter import RulesAdapter
from mcp_zen_of_languages.rules.base_models import PrincipleCategory
from mcp_zen_of_languages.rules.base_models import ZenPrinciple


class _HostileCycle:
    """A cycle entry whose ``cycle`` attribute raises on access.

    ``hasattr`` only suppresses ``AttributeError``, so a ``ValueError`` from the
    property propagates into the normalisation ``try`` block. ``str()`` still
    works, which is what the recovery path needs.
    """

    @property
    def cycle(self) -> list[str]:
        msg = "cycle is not readable"
        raise ValueError(msg)

    def __str__(self) -> str:
        return "hostile-cycle"


class _Analysis:
    def __init__(self, cycles: list[object]) -> None:
        self.cycles = cycles


def _principle() -> ZenPrinciple:
    return ZenPrinciple(
        id="python-900",
        principle="Avoid circular dependencies",
        category=PrincipleCategory.ARCHITECTURE,
        severity=7,
        description="Circular imports couple modules that should be independent",
    )


def test_unnormalisable_cycle_entry_is_recovered_not_raised(caplog):
    """A cycle entry that blows up during normalisation must not abort the check.

    Exercises the defensive ``except Exception`` recovery in
    ``_check_dependencies``: the entry is logged and degraded to its ``str()``
    form rather than propagating and losing every other cycle in the batch.
    """
    adapter = RulesAdapter("python")

    with caplog.at_level(
        logging.DEBUG, logger="mcp_zen_of_languages.adapters.rules_adapter"
    ):
        violations = adapter._check_dependencies(
            _Analysis([_HostileCycle()]),
            _principle(),
            {"max_dependencies": 100},
        )

    assert isinstance(violations, list)
    assert any(
        "Failed to normalize dependency cycle entry" in r.message
        for r in caplog.records
    ), "expected the recovery path to log the unnormalisable entry"
