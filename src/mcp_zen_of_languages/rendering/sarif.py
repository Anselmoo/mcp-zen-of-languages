"""SARIF v2.1.0 rendering helpers for analysis results."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from mcp_zen_of_languages.models import AnalysisResult

# Severity tier thresholds (1-10 scale)
SEVERITY_CRITICAL = 9
SEVERITY_MEDIUM = 4


def _sarif_level(severity: int) -> str:
    if severity >= SEVERITY_CRITICAL:
        return "error"
    return "warning" if severity >= SEVERITY_MEDIUM else "note"


def analysis_results_to_sarif(
    results: list[AnalysisResult],
    *,
    tool_name: str = "zen-of-languages",
) -> dict[str, object]:
    """Convert analysis results into a SARIF 2.1.0 payload."""
    rules: dict[str, dict[str, object]] = {}
    sarif_results: list[dict[str, object]] = []

    for result in results:
        path = result.path or "<input>"
        for violation in result.violations:
            rule_id = violation.principle
            if rule_id not in rules:
                rules[rule_id] = {
                    "id": rule_id,
                    "name": violation.principle,
                    "shortDescription": {"text": violation.principle},
                }
            region: dict[str, int] | None = None
            if violation.location is not None:
                region = {
                    "startLine": violation.location.line,
                    "startColumn": violation.location.column,
                }
            sarif_results.append(
                {
                    "ruleId": rule_id,
                    "level": _sarif_level(violation.severity),
                    "message": {"text": violation.message},
                    "locations": [
                        {
                            "physicalLocation": {
                                "artifactLocation": {"uri": path},
                                **({"region": region} if region is not None else {}),
                            }
                        }
                    ],
                }
            )

    return {
        "$schema": (
            "https://raw.githubusercontent.com/microsoft/"
            "sarif-python-om/refs/heads/main/sarif-schema-2.1.0.json"
        ),
        "version": "2.1.0",
        "runs": [
            {
                "tool": {
                    "driver": {
                        "name": tool_name,
                        "rules": list(rules.values()),
                    }
                },
                "results": sarif_results,
            }
        ],
    }
