from __future__ import annotations

import pytest

from mcp_zen_of_languages.analyzers.pipeline import PipelineConfig
from mcp_zen_of_languages.config import ConfigModel, load_config
from mcp_zen_of_languages.languages.configs import DetectorConfig


def test_pipeline_for_unknown_language_raises():
    config = ConfigModel()
    with pytest.raises(ValueError, match="No zen rules for language: unknown"):
        config.pipeline_for("unknown")


def test_validate_pipelines_rejects_non_list():
    with pytest.raises(TypeError):
        ConfigModel.model_validate({"pipelines": "bad"})


def test_validate_pipelines_none_returns_empty():
    config = ConfigModel.model_validate({"pipelines": None})
    assert config.pipelines == []


def test_pipeline_merge_round_trip():
    base = PipelineConfig.from_rules("python")
    override = PipelineConfig(language="python", detectors=base.detectors[:1])
    merged = ConfigModel(pipelines=[override]).pipeline_for("python")
    assert merged.language == "python"


def test_select_violation_message_falls_back_to_first():
    config = DetectorConfig(type="test", violation_messages=["first", "second"])
    assert config.select_violation_message(index=10) == "first"


def test_load_config_discovers_parent(tmp_path, monkeypatch):
    root = tmp_path / "root"
    root.mkdir()
    (root / "zen-config.yaml").write_text("languages:\n  - python\n", encoding="utf-8")
    child = root / "child"
    child.mkdir()
    monkeypatch.chdir(child)
    config = load_config()
    assert "python" in config.languages
