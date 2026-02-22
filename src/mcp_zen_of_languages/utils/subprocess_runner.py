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
import os
import shutil
import subprocess
from pathlib import Path
from typing import ClassVar

from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

__all__ = [
    "KNOWN_TOOLS",
    "SubprocessResult",
    "SubprocessToolRunner",
    "ToolResolution",
]

DEFAULT_TIMEOUT_SECONDS = 30


class SubprocessResult(BaseModel):
    """Structured output from an external tool invocation."""

    tool: str = Field(description="Name of the tool that was invoked.")
    returncode: int = Field(description="Process exit code (0 = success).")
    stdout: str = Field(default="", description="Captured standard output.")
    stderr: str = Field(default="", description="Captured standard error.")
    strategy: str | None = Field(
        default=None,
        description="Resolution strategy used to execute the tool command.",
    )
    command: list[str] = Field(
        default_factory=list,
        description="Resolved command prefix + arguments passed to subprocess.",
    )
    resolution_attempts: list[str] = Field(
        default_factory=list,
        description="Human-readable resolution attempts performed before execution.",
    )


class ToolResolution(BaseModel):
    """Resolved command metadata for one tool invocation attempt."""

    tool: str
    command: list[str] | None = None
    strategy: str | None = None
    attempts: list[str] = Field(default_factory=list)


# Language → tool → default CLI arguments.
# Only tools in this mapping are allowed to be executed.
KNOWN_TOOLS: dict[str, dict[str, list[str]]] = {
    "bash": {"shellcheck": ["-", "-f", "json"]},
    "go": {"go": ["vet", "./..."]},
    "rust": {"cargo": ["clippy", "--message-format=json"]},
    "python": {"ruff": ["check", "--stdin-filename", "stdin.py", "-"]},
    "javascript": {
        "eslint": ["--stdin", "--format", "json"],
        "biome": ["lint", "--stdin-file-path", "stdin.js", "--reporter", "json"],
        "prettier": ["--check", "--stdin-filepath", "stdin.js"],
    },
    "typescript": {
        "eslint": ["--stdin", "--format", "json"],
        "biome": ["lint", "--stdin-file-path", "stdin.ts", "--reporter", "json"],
        "prettier": ["--check", "--stdin-filepath", "stdin.ts"],
    },
    "ruby": {"rubocop": ["--stdin", "stdin.rb", "--format", "json"]},
    "cpp": {"cppcheck": ["--language=c++", "-"]},
    "csharp": {"dotnet": ["format", "--verify-no-changes"]},
    "css": {
        "stylelint": ["--stdin-filename", "stdin.css"],
        "biome": ["lint", "--stdin-file-path", "stdin.css", "--reporter", "json"],
        "prettier": ["--check", "--stdin-filepath", "stdin.css"],
    },
    "powershell": {
        "pwsh": ["-Command", "Invoke-ScriptAnalyzer -ScriptDefinition $input"]
    },
    "dockerfile": {"hadolint": ["-f", "json", "-"]},
    "docker_compose": {"docker": ["compose", "-f", "-", "config", "-q"]},
    "latex": {"chktex": ["-q", "-v0", "-"]},
    "markdown": {
        "markdownlint": ["--stdin", "--json"],
        "prettier": ["--check", "--stdin-filepath", "stdin.md"],
    },
}

_ALL_ALLOWED_TOOLS: frozenset[str] = frozenset(
    tool for lang_tools in KNOWN_TOOLS.values() for tool in lang_tools
)

_NO_INSTALL_RUNNERS: dict[str, list[str]] = {
    "python": ["uv", "run", "--no-sync"],
    "javascript": ["npm", "exec", "--no-install"],
    "typescript": ["npm", "exec", "--no-install"],
    "css": ["npm", "exec", "--no-install"],
    "markdown": ["npm", "exec", "--no-install"],
}

_TEMPORARY_RUNNERS: dict[str, list[str]] = {
    "python": ["uvx"],
    "javascript": ["npx", "--yes"],
    "typescript": ["npx", "--yes"],
    "css": ["npx", "--yes"],
    "markdown": ["npx", "--yes"],
}


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
    def _venv_candidates(tool: str) -> list[str]:
        """Build candidate tool paths from active/project virtual environments."""
        candidates: list[str] = []
        suffixes = [tool]
        if os.name == "nt":
            suffixes.append(f"{tool}.exe")

        virtual_env = os.environ.get("VIRTUAL_ENV")
        roots: list[Path] = []
        if virtual_env:
            roots.append(Path(virtual_env))
        roots.append(Path.cwd() / ".venv")

        for root in roots:
            scripts_dir = root / ("Scripts" if os.name == "nt" else "bin")
            candidates.extend(str(scripts_dir / suffix) for suffix in suffixes)
        return candidates

    @staticmethod
    def _runner_prefix(
        language: str, *, allow_temporary_tools: bool
    ) -> list[str] | None:
        """Return language-specific runner prefix, honoring temporary-runner consent."""
        if allow_temporary_tools:
            return _TEMPORARY_RUNNERS.get(language)
        return _NO_INSTALL_RUNNERS.get(language)

    def resolve_tool(  # noqa: PLR0911
        self,
        tool: str,
        *,
        language: str | None = None,
        allow_temporary_tools: bool = False,
    ) -> ToolResolution:
        """Resolve the executable command prefix for a tool without running it."""
        attempts: list[str] = []
        if tool not in _ALL_ALLOWED_TOOLS:
            attempts.append("allowlist:blocked")
            return ToolResolution(tool=tool, attempts=attempts)

        direct = shutil.which(tool)
        attempts.append(f"path:{tool}")
        if direct is not None:
            self._cache[tool] = True
            return ToolResolution(
                tool=tool,
                command=[direct],
                strategy="path",
                attempts=attempts,
            )
        self._cache[tool] = False

        for candidate in self._venv_candidates(tool):
            attempts.append(f"venv:{candidate}")
            if Path(candidate).is_file():
                return ToolResolution(
                    tool=tool,
                    command=[candidate],
                    strategy="venv",
                    attempts=attempts,
                )

        if language is None:
            return ToolResolution(tool=tool, attempts=attempts)

        runner_prefix = self._runner_prefix(
            language,
            allow_temporary_tools=False,
        )
        if runner_prefix and shutil.which(runner_prefix[0]):
            attempts.append(f"runner-no-install:{' '.join([*runner_prefix, tool])}")
            return ToolResolution(
                tool=tool,
                command=[*runner_prefix, tool],
                strategy="runner_no_install",
                attempts=attempts,
            )

        attempts.append("runner-no-install:unavailable")
        if allow_temporary_tools:
            temporary_prefix = self._runner_prefix(
                language,
                allow_temporary_tools=True,
            )
            if temporary_prefix and shutil.which(temporary_prefix[0]):
                attempts.append(
                    f"runner-temporary:{' '.join([*temporary_prefix, tool])}"
                )
                return ToolResolution(
                    tool=tool,
                    command=[*temporary_prefix, tool],
                    strategy="temporary_runner",
                    attempts=attempts,
                )
            attempts.append("runner-temporary:unavailable")

        return ToolResolution(tool=tool, attempts=attempts)

    @staticmethod
    def is_available(
        tool: str,
        *,
        language: str | None = None,
        allow_temporary_tools: bool = False,
    ) -> bool:
        """Return *True* when the tool can be resolved through allowed strategies."""
        resolution = SubprocessToolRunner().resolve_tool(
            tool,
            language=language,
            allow_temporary_tools=allow_temporary_tools,
        )
        return resolution.command is not None

    def run(
        self,
        tool: str,
        args: list[str] | None = None,
        *,
        code: str = "",
        language: str | None = None,
        allow_temporary_tools: bool = False,
    ) -> SubprocessResult | None:
        """Invoke *tool* with *code* on stdin.

        Returns ``None`` when the tool cannot be resolved or execution fails.
        """
        resolution = self.resolve_tool(
            tool,
            language=language,
            allow_temporary_tools=allow_temporary_tools,
        )
        if resolution.command is None:
            logger.debug(
                "Tool %r unresolved (attempts=%s)",
                tool,
                ", ".join(resolution.attempts),
            )
            return None

        cmd = [*resolution.command, *(args or [])]
        try:
            proc = subprocess.run(  # noqa: S603
                cmd,
                input=code,
                capture_output=True,
                text=True,
                timeout=self.timeout,
                check=False,
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
            strategy=resolution.strategy,
            command=cmd,
            resolution_attempts=resolution.attempts,
        )

    def run_for_language(
        self,
        language: str,
        code: str,
        *,
        allow_temporary_tools: bool = False,
    ) -> dict[str, SubprocessResult]:
        """Run **all** known tools for *language*, returning results keyed by tool name."""
        results: dict[str, SubprocessResult] = {}
        for tool, default_args in KNOWN_TOOLS.get(language, {}).items():
            result = self.run(
                tool,
                default_args,
                code=code,
                language=language,
                allow_temporary_tools=allow_temporary_tools,
            )
            if result is not None:
                results[tool] = result
        return results
