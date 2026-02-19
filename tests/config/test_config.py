from __future__ import annotations

import pytest

from mcp_zen_of_languages.config import load_config

CONFIG_FILE_SEVERITY = 7
ENV_OVERRIDE_SEVERITY = 8


def test_load_config_defaults(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    config = load_config(None)
    assert config.languages
    assert config.severity_threshold >= 0


def test_load_config_from_path(tmp_path):
    config_path = tmp_path / "zen-config.yaml"
    config_path.write_text(
        f"languages:\n  - python\nseverity_threshold: {CONFIG_FILE_SEVERITY}\n",
        encoding="utf-8",
    )
    config = load_config(str(config_path))
    assert config.languages == ["python"]
    assert config.severity_threshold == CONFIG_FILE_SEVERITY


def test_load_config_missing_path_returns_default(tmp_path):
    config = load_config(str(tmp_path / "missing.yaml"))
    assert config.languages


def test_load_config_applies_env_severity_override(tmp_path, monkeypatch):
    config_path = tmp_path / "zen-config.yaml"
    config_path.write_text("severity_threshold: 5\n", encoding="utf-8")
    monkeypatch.setenv("ZEN_SEVERITY_THRESHOLD", str(ENV_OVERRIDE_SEVERITY))
    config = load_config(str(config_path))
    assert config.severity_threshold == ENV_OVERRIDE_SEVERITY


def test_load_config_rejects_invalid_env_severity(tmp_path, monkeypatch):
    config_path = tmp_path / "zen-config.yaml"
    config_path.write_text("severity_threshold: 5\n", encoding="utf-8")
    monkeypatch.setenv("ZEN_SEVERITY_THRESHOLD", "high")
    with pytest.raises(ValueError, match="ZEN_SEVERITY_THRESHOLD"):
        load_config(str(config_path))
