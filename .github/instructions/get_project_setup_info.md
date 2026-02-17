---
applyTo: ["*.md", "**/README.md"]
---

# Project setup quick reference

Use this repository-specific setup sequence:

1. `uv sync --all-groups --all-extras`
2. `uvx pre-commit run --all-files`
3. `uvx pre-commit run --hook-stage pre-push --all-files`
4. `uv run pytest`
5. `uv build`

Notes:
- Source of truth for architecture/workflow guidance: `.github/copilot-instructions.md`.
- This project uses FastMCP, Pydantic v2, and Python 3.12+ syntax (`str | None`).
