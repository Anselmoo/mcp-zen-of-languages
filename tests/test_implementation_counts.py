"""Verify generated implementation counts stay in sync with docs surfaces."""

from __future__ import annotations

import importlib.util
import subprocess
import sys
from pathlib import Path

import pytest


def _load_implementation_counts_module():
    script_path = (
        Path(__file__).resolve().parent.parent
        / "scripts"
        / "generate_implementation_counts.py"
    )
    spec = importlib.util.spec_from_file_location(
        "generate_implementation_counts",
        script_path,
    )
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


implementation_counts = _load_implementation_counts_module()


def test_implementation_counts_checks() -> None:
    """Fail if generated implementation-count artifacts or surfaces are stale."""
    result = subprocess.run(  # noqa: S603
        [sys.executable, "scripts/generate_implementation_counts.py", "--check"],
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        msg = (
            "Implementation count checks failed. Run:\n"
            "  uv run python scripts/generate_implementation_counts.py\n\n"
            f"{result.stdout}\n{result.stderr}"
        )
        raise AssertionError(msg)


def test_validate_documented_languages_covers_current_inventory() -> None:
    """Current script inventories should match canonical rules registry keys."""
    module_keys = {
        *(module_key for module_key, _ in implementation_counts.PROGRAMMING_LANGUAGES),
        *(module_key for module_key, _ in implementation_counts.WORKFLOW_LANGUAGES),
        *(module_key for module_key, _ in implementation_counts.CONFIG_LANGUAGES),
    }
    implementation_counts.validate_documented_languages(module_keys)


def test_validate_documented_languages_reports_missing_css_markdown() -> None:
    """Missing CSS/Markdown entries should fail loudly for generator inventory drift."""
    module_keys = {
        *(module_key for module_key, _ in implementation_counts.PROGRAMMING_LANGUAGES),
        *(module_key for module_key, _ in implementation_counts.WORKFLOW_LANGUAGES),
        *(module_key for module_key, _ in implementation_counts.CONFIG_LANGUAGES),
    }
    module_keys.remove("css")
    module_keys.remove("markdown")
    with pytest.raises(ValueError, match=r"missing=.*css.*markdown"):
        implementation_counts.validate_documented_languages(module_keys)
