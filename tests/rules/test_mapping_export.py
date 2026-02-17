from __future__ import annotations

import json

from mcp_zen_of_languages.rules.mapping_export import (
    build_rule_detector_mapping,
    export_mapping_json,
)


def test_build_rule_detector_mapping_for_python():
    data = build_rule_detector_mapping(["python", "unknown"])

    assert "python" in data["languages"]
    assert "unknown" not in data["languages"]
    python = data["languages"]["python"]
    assert python["rules_count"] > 0
    assert python["detectors_count"] > 0
    assert "mapping" in python


def test_export_mapping_json(tmp_path):
    output = tmp_path / "mapping.json"
    data = export_mapping_json(output, ["python"])

    assert output.exists()
    loaded = json.loads(output.read_text())
    assert loaded["languages"]["python"] == data["languages"]["python"]
