"""Subprocess runner for external language tools.

Provides a secure, timeout-guarded interface for invoking external analysis
tools (linters, formatters, type checkers) when they are installed on the
host system.  Analyzers can optionally use this to augment regex-based
detection with tool-specific diagnostics.

Security model:
    * Only tools listed in :data:`KNOWN_TOOLS` are allowed.
    * ``shell=True`` is **never** used.
    * A configurable *timeout* prevents runaway processes.
    * Code is passed via **stdin** — no temporary files on disk.

Example::

    runner = SubprocessToolRunner()
    if runner.is_available("shellcheck"):
        result = runner.run("shellcheck", ["-"], code=script_text)
        if result and result.returncode != 0:
            # parse result.stdout for diagnostics
            ...
"""

from __future__ import annotations

import logging
import shutil
import subprocess
from typing import ClassVar

from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

__all__ = [
    "KNOWN_TOOLS",
    "SubprocessResult",
    "SubprocessToolRunner",
]

DEFAULT_TIMEOUT_SECONDS = 30


class SubprocessResult(BaseModel):
    """Structured output from an external tool invocation."""

    tool: str = Field(description="Name of the tool that was invoked.")
    returncode: int = Field(description="Process exit code (0 = success).")
    stdout: str = Field(default="", description="Captured standard output.")
    stderr: str = Field(default="", description="Captured standard error.")


# Language → tool → default CLI arguments.
# Only tools in this mapping are allowed to be executed.
KNOWN_TOOLS: dict[str, dict[str, list[str]]] = {
    "bash": {"shellcheck": ["-", "-f", "json"]},
    "go": {"go": ["vet", "./..."]},
    "rust": {"cargo": ["clippy", "--message-format=json"]},
    "python": {"ruff": ["check", "--stdin-filename", "stdin.py", "-"]},
    "javascript": {"eslint": ["--stdin", "--format", "json"]},
    "typescript": {"eslint": ["--stdin", "--format", "json"]},
    "ruby": {"rubocop": ["--stdin", "stdin.rb", "--format", "json"]},
    "cpp": {"cppcheck": ["--language=c++", "-"]},
    "csharp": {"dotnet": ["format", "--verify-no-changes"]},
    "css": {"stylelint": ["--stdin-filename", "stdin.css"]},
    "powershell": {
        "pwsh": ["-Command", "Invoke-ScriptAnalyzer -ScriptDefinition $input"]
    },
}

_ALL_ALLOWED_TOOLS: frozenset[str] = frozenset(
    tool for lang_tools in KNOWN_TOOLS.values() for tool in lang_tools
)


class SubprocessToolRunner:
    """Run allow-listed external tools with stdin-based code input.

    Args:
        timeout: Maximum wall-clock seconds for each tool invocation.
    """

    _cache: ClassVar[dict[str, bool]] = {}

    def __init__(self, timeout: int = DEFAULT_TIMEOUT_SECONDS) -> None:
        """Initialize the runner with a default timeout for subprocess calls."""
        self.timeout = timeout

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    @staticmethod
    def is_available(tool: str) -> bool:
        """Return *True* if *tool* is on ``$PATH`` **and** in the allow-list."""
        if tool not in _ALL_ALLOWED_TOOLS:
            return False
        if tool not in SubprocessToolRunner._cache:
            SubprocessToolRunner._cache[tool] = shutil.which(tool) is not None
        return SubprocessToolRunner._cache[tool]

    def run(
        self,
        tool: str,
        args: list[str] | None = None,
        *,
        code: str = "",
    ) -> SubprocessResult | None:
        """Invoke *tool* with *code* on stdin.

        Returns ``None`` when the tool is not installed or not allow-listed.
        """
        if not self.is_available(tool):
            logger.debug("Tool %r not available or not allow-listed", tool)
            return None

        cmd = [tool, *(args or [])]
        try:
            proc = subprocess.run(  # noqa: S603
                cmd,
                input=code,
                capture_output=True,
                text=True,
                timeout=self.timeout,
                check=True,
            )
        except subprocess.TimeoutExpired:
            logger.warning("Tool %r timed out after %ds", tool, self.timeout)
            return None
        except FileNotFoundError:
            logger.debug("Tool %r disappeared from PATH", tool)
            SubprocessToolRunner._cache.pop(tool, None)
            return None

        return SubprocessResult(
            tool=tool,
            returncode=proc.returncode,
            stdout=proc.stdout,
            stderr=proc.stderr,
        )

    def run_for_language(
        self,
        language: str,
        code: str,
    ) -> dict[str, SubprocessResult]:
        """Run **all** known tools for *language*, returning results keyed by tool name."""
        results: dict[str, SubprocessResult] = {}
        for tool, default_args in KNOWN_TOOLS.get(language, {}).items():
            result = self.run(tool, default_args, code=code)
            if result is not None:
                results[tool] = result
        return results
