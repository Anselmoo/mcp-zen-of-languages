---
applyTo: '**'
---

# Mandatory pre-commit verification

Do not submit or mark work complete until pre-commit verification has run successfully.

Required:
1. Run `uvx pre-commit run --all-files` after making changes.
2. If checks fail, fix issues and re-run until all checks pass.
3. Include a brief note in your final response confirming pre-commit was run and whether it passed.

Use `uvx pre-commit run --hook-stage pre-push --all-files` when changes affect docs or release-facing files.
