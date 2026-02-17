from __future__ import annotations

from mcp_zen_of_languages.config import load_config


def test_load_config_invalid_yaml(tmp_path):
    cfg_path = tmp_path / "zen-config.yaml"
    cfg_path.write_text("pipelines: bad", encoding="utf-8")
    try:
        load_config(str(cfg_path))
    except Exception:
        assert True


def test_load_config_with_override_pipelines(tmp_path):
    cfg_path = tmp_path / "zen-config.yaml"
    cfg_path.write_text(
        "languages:\n  - python\npipelines: []\n",
        encoding="utf-8",
    )
    cfg = load_config(str(cfg_path))
    assert cfg.pipelines
