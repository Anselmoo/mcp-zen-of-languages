"""Shared builder helpers for framework mapping modules.

These utilities reduce boilerplate in every ``frameworks/<name>/mapping.py``
module by providing a single, consistent definition of the common factory
functions (*rule config*, *dogmas*, *testing*, *projection*) that every
framework mapping uses.
"""

from __future__ import annotations

from typing import Literal

from pydantic import create_model

from mcp_zen_of_languages.languages.configs import DetectorConfig


def make_rule_config(rule_id: str) -> type[DetectorConfig]:
    """Return a typed ``DetectorConfig`` subclass for the given framework rule.

    The generated class is named after the rule id in PascalCase (e.g.
    ``React001Config`` for ``react-001``) and carries the ``type`` discriminator
    literal so the registry can round-trip it through a discriminated union.

    Args:
        rule_id: Framework rule identifier, e.g. ``"react-001"``.

    Returns:
        A dynamically-created Pydantic model subclass of ``DetectorConfig``.
    """
    class_name = "".join(part.capitalize() for part in rule_id.split("-")) + "Config"
    return create_model(
        class_name,
        __base__=DetectorConfig,
        type=(Literal[rule_id], rule_id),
    )


def dogma_ids(*ids: str) -> list[str]:
    """Return the supplied universal dogma IDs as a plain list.

    Args:
        *ids: One or more universal dogma ID strings
            (e.g. ``"ZEN-STRICT-FENCES"``).

    Returns:
        A new list containing *ids* in the supplied order.
    """
    return list(ids)


def testing_ids(*ids: str) -> list[str]:
    """Return the supplied testing family IDs as a plain list.

    Args:
        *ids: One or more testing family ID strings (e.g. ``"pytest"``).

    Returns:
        A new list containing *ids* in the supplied order.
    """
    return list(ids)


def projection_ids(*ids: str) -> list[str]:
    """Return the supplied projection family IDs as a plain list.

    Args:
        *ids: One or more projection family ID strings (e.g. ``"sql"``).

    Returns:
        A new list containing *ids* in the supplied order.
    """
    return list(ids)


__all__ = ["dogma_ids", "make_rule_config", "projection_ids", "testing_ids"]
