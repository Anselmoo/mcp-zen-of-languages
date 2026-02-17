"""Normalize raw parser output into a uniform ``ParserResult`` for the analysis pipeline.

Python source can be parsed by multiple backends (stdlib ``ast``, tree-sitter,
etc.).  This module bridges the gap by coercing whatever a backend returns into
the canonical ``ParserResult`` model that downstream detectors and metrics
collectors rely on.
"""

from __future__ import annotations

from mcp_zen_of_languages.models import ParserResult


class ParserNormalizer:
    """Coerce raw parser output into a canonical ``ParserResult``.

    Different parsing backends (stdlib ``ast.parse``, tree-sitter grammars)
    return heterogeneous objects.  ``ParserNormalizer`` wraps them in a
    ``ParserResult`` so that every detector and metrics collector can rely on
    a single, well-typed interface.

    Note:
        This class is stateless; all behaviour lives in the ``normalize``
        static method.
    """

    @staticmethod
    def normalize(raw: object | None) -> ParserResult | None:
        """Wrap a raw parser object in a ``ParserResult`` envelope.

        If *raw* is already a ``ParserResult`` it is returned as-is.
        If *raw* is ``None`` (parsing failed or was skipped) the method
        propagates ``None`` so callers can branch on it cleanly.
        Any other object is wrapped with ``type="unknown"``.

        Args:
            raw: Opaque object returned by a parsing backend (e.g. an
                ``ast.Module`` from stdlib or a tree-sitter ``Tree``).

        Returns:
            ParserResult | None: Normalized result ready for detectors, or
                ``None`` when no parse tree is available.
        """
        if raw is None:
            return None
        if isinstance(raw, ParserResult):
            return raw
        return ParserResult(type="unknown", tree=raw)
