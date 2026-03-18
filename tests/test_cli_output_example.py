"""Verify the generated CLI output example stays aligned with the live runtime."""

from __future__ import annotations

import importlib.util
import subprocess
import sys

from pathlib import Path


def _load_cli_output_example_module():
    script_path = (
        Path(__file__).resolve().parent.parent
        / "scripts"
        / "generate_cli_output_example.py"
    )
    spec = importlib.util.spec_from_file_location(
        "generate_cli_output_example",
        script_path,
    )
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


cli_output_example = _load_cli_output_example_module()


def test_cli_output_example_generation_includes_perspective_surface() -> None:
    """The generated include should showcase the testing perspective workflow."""
    content = cli_output_example.generate()

    assert "### Perspective-aware CLI example" in content
    assert (
        "zen check tests/fixtures/cli_docs/tests/test_perspective_example.py" in content
    )
    assert "--perspective testing --show-files" in content
    assert "Zen Report" in content
    assert "Beautiful is better than ugly" in content
    assert "tests/fixtures/cli_docs/tests/test_perspective_example.py" in content


def test_cli_output_example_check_mode() -> None:
    """Fail when the committed generated artifact drifts from runtime output."""
    result = subprocess.run(  # noqa: S603
        [sys.executable, "scripts/generate_cli_output_example.py", "--check"],
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        msg = (
            "CLI output example is stale. Run:\n"
            "  uv run python scripts/generate_cli_output_example.py\n\n"
            f"{result.stdout}\n{result.stderr}"
        )
        raise AssertionError(msg)
