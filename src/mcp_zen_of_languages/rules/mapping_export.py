"""Export the live rule-to-detector registry as a JSON mapping.

Intended consumers are CI dashboards, coverage reports, and developer
tooling that need a static snapshot of which detectors enforce which zen
principles.  The export format includes per-language rule counts, detector
IDs, and a reverse mapping (detector → rules) for cross-referencing.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from mcp_zen_of_languages.analyzers import registry_bootstrap  # noqa: F401
from mcp_zen_of_languages.analyzers.registry import REGISTRY
from mcp_zen_of_languages.rules import get_all_languages, get_language_zen


def build_rule_detector_mapping(
    languages: list[str] | None = None,
) -> dict[str, Any]:
    """Assemble a JSON-serialisable mapping from principles to their detectors.

    For each language the output contains:

    * ``rules_count`` / ``detectors_count`` — aggregate totals.
    * ``mapping`` — ``{rule_id: {principle, detectors, …}}``.
    * ``reverse_mapping`` — ``{detector_id: [rule_id, …]}``.

    Args:
        languages: Restrict output to these language keys.  ``None`` includes
            every language in the registry.

    Returns:
        Nested dict ready for ``json.dumps`` serialisation.
    """

    data: dict[str, Any] = {
        "$schema": "rule_detector_mapping_schema",
        "$comment": "Generated from the live detector registry.",
        "languages": {},
    }

    for language in languages or get_all_languages():
        lang_zen = get_language_zen(language)
        if not lang_zen:
            continue
        rules: dict[str, Any] = {}
        reverse_mapping: dict[str, set[str]] = {}

        for principle in lang_zen.principles:
            metas = REGISTRY.detectors_for_rule(principle.id, language)
            detector_ids = sorted({meta.detector_id for meta in metas})
            rules[principle.id] = {
                "principle": principle.principle,
                "detectors": detector_ids,
                "uncovered_violations": [],
                "coverage": "partial",
            }

        detector_ids = {
            meta.detector_id for meta in REGISTRY.items() if meta.language == language
        }
        for meta in REGISTRY.items():
            if meta.language != language:
                continue
            for rule_id in meta.rule_ids:
                reverse_mapping.setdefault(meta.detector_id, set()).add(rule_id)

        language_payload: dict[str, Any] = {
            "rules_count": len(lang_zen.principles),
            "detectors_count": len(detector_ids),
            "mapping": rules,
        }
        if reverse_mapping:
            language_payload["reverse_mapping"] = {
                detector_id: sorted(rule_ids)
                for detector_id, rule_ids in sorted(reverse_mapping.items())
            }
        data["languages"][language] = language_payload

    return data


def export_mapping_json(
    output_path: str | Path, languages: list[str] | None = None
) -> dict[str, Any]:
    """Write the rule-to-detector mapping to *output_path* as pretty-printed JSON.

    Args:
        output_path: Destination file (created or overwritten).
        languages: Restrict to these language keys.  ``None`` includes all.

    Returns:
        The same dict that was written to disk, for programmatic reuse.
    """

    data = build_rule_detector_mapping(languages)
    path = Path(output_path)
    path.write_text(json.dumps(data, indent=2), encoding="utf-8")
    return data
