"""Tests for the subprocess runner utility."""

from __future__ import annotations

from unittest.mock import patch

from mcp_zen_of_languages.utils.subprocess_runner import (
    KNOWN_TOOLS,
    SubprocessResult,
    SubprocessToolRunner,
)


class TestSubprocessResult:
    def test_construction(self) -> None:
        result = SubprocessResult(tool="ruff", returncode=0, stdout="ok", stderr="")
        assert result.tool == "ruff"
        assert result.returncode == 0
        assert result.stdout == "ok"

    def test_defaults(self) -> None:
        result = SubprocessResult(tool="ruff", returncode=1)
        assert result.stdout == ""
        assert result.stderr == ""


class TestKnownTools:
    def test_known_tools_populated(self) -> None:
        assert len(KNOWN_TOOLS) > 0
        assert "python" in KNOWN_TOOLS
        assert "ruff" in KNOWN_TOOLS["python"]

    def test_bash_has_shellcheck(self) -> None:
        assert "shellcheck" in KNOWN_TOOLS["bash"]

    def test_dockerfile_has_hadolint(self) -> None:
        assert "hadolint" in KNOWN_TOOLS["dockerfile"]


class TestSubprocessToolRunner:
    def test_not_allowlisted_tool(self) -> None:
        assert SubprocessToolRunner.is_available("rm") is False

    def test_is_available_checks_path(self) -> None:
        SubprocessToolRunner._cache.pop("ruff", None)
        with patch("shutil.which", return_value="/usr/bin/ruff"):
            assert SubprocessToolRunner.is_available("ruff") is True
        SubprocessToolRunner._cache.pop("ruff", None)

    def test_is_available_caches(self) -> None:
        with patch("shutil.which", return_value="/usr/bin/ruff"):
            assert SubprocessToolRunner.is_available("ruff") is True
        assert SubprocessToolRunner._cache.get("ruff") is True
        SubprocessToolRunner._cache.pop("ruff", None)

    def test_run_unavailable_returns_none(self) -> None:
        runner = SubprocessToolRunner()
        SubprocessToolRunner._cache["nonexistent"] = False
        result = runner.run("nonexistent")
        assert result is None

    def test_run_not_allowlisted_returns_none(self) -> None:
        runner = SubprocessToolRunner()
        result = runner.run("rm", ["-rf", "/"])
        assert result is None

    def test_run_success_with_mock(self) -> None:
        runner = SubprocessToolRunner()
        with (
            patch("shutil.which", return_value="/usr/bin/ruff"),
            patch("subprocess.run") as mock_run,
        ):
            mock_run.return_value.returncode = 0
            mock_run.return_value.stdout = "all good"
            mock_run.return_value.stderr = ""
            result = runner.run("ruff", ["check", "-"], code="x = 1")
        assert result is not None
        assert result.returncode == 0
        assert result.stdout == "all good"
        assert result.strategy == "path"
        SubprocessToolRunner._cache.pop("ruff", None)

    def test_run_timeout_returns_none(self) -> None:
        import subprocess as sp

        runner = SubprocessToolRunner()
        with (
            patch("shutil.which", return_value="/usr/bin/ruff"),
            patch("subprocess.run", side_effect=sp.TimeoutExpired("ruff", 30)),
        ):
            result = runner.run("ruff", ["check"], code="x = 1")
        assert result is None
        SubprocessToolRunner._cache.pop("ruff", None)

    def test_run_file_not_found_returns_none(self) -> None:
        runner = SubprocessToolRunner()
        with (
            patch("shutil.which", return_value="/usr/bin/ruff"),
            patch("subprocess.run", side_effect=FileNotFoundError),
        ):
            result = runner.run("ruff", ["check"], code="x = 1")
        assert result is None
        assert "ruff" not in SubprocessToolRunner._cache

    def test_run_for_language_with_available_tool(self) -> None:
        runner = SubprocessToolRunner()
        with (
            patch(
                "shutil.which",
                side_effect=lambda tool: "/usr/bin/ruff" if tool == "ruff" else None,
            ),
            patch("subprocess.run") as mock_run,
        ):
            mock_run.return_value.returncode = 0
            mock_run.return_value.stdout = ""
            mock_run.return_value.stderr = ""
            results = runner.run_for_language("python", "x = 1")
        assert "ruff" in results
        SubprocessToolRunner._cache.pop("ruff", None)

    def test_run_for_language_empty(self) -> None:
        runner = SubprocessToolRunner()
        result = runner.run_for_language("unknown_lang", "code")
        assert result == {}

    def test_timeout_default(self) -> None:
        runner = SubprocessToolRunner()
        expected_timeout = 30
        assert runner.timeout == expected_timeout

    def test_timeout_custom(self) -> None:
        custom_timeout = 60
        runner = SubprocessToolRunner(timeout=custom_timeout)
        assert runner.timeout == custom_timeout

    def test_resolve_tool_uses_no_install_runner(self) -> None:
        runner = SubprocessToolRunner()

        def _which(tool: str) -> str | None:
            return "/usr/bin/npm" if tool == "npm" else None

        with patch("shutil.which", side_effect=_which):
            resolution = runner.resolve_tool("eslint", language="javascript")

        assert resolution.command is not None
        assert resolution.strategy == "runner_no_install"
        assert resolution.command[:3] == ["npm", "exec", "--no-install"]

    def test_resolve_tool_uses_temporary_runner_when_opted_in(self) -> None:
        runner = SubprocessToolRunner()

        def _which(tool: str) -> str | None:
            return "/usr/bin/npx" if tool == "npx" else None

        with patch("shutil.which", side_effect=_which):
            resolution = runner.resolve_tool(
                "eslint",
                language="javascript",
                allow_temporary_tools=True,
            )

        assert resolution.command is not None
        assert resolution.strategy == "temporary_runner"
        assert resolution.command[:2] == ["npx", "--yes"]
