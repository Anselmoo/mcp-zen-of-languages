## [Unreleased]

### Added
- **ci**: add `rrt-checks` job using `repo-release-tools@v1.8.1` for branch name, commit subject, changelog, and release-health policy validation
- **ci**: add `build-mcpb` job that produces a DXT v0.4 `.mcpb` bundle and attaches it to every GitHub Release alongside wheel, sdist, and SBOM
- **release**: add `scripts/build_mcpb.py` and `poe build_mcpb` task to build the `.mcpb` bundle locally (`dist/` is gitignored)
- **docs**: document `.mcpb` one-click install for Claude Desktop in installation and MCP-integration pages
- **dev**: add `CLAUDE.md` with project conventions for Claude Code sessions

### Fixed
- **release**: `.mcpb` manifest schema corrected to DXT spec v0.4 (`manifest_version`, `repository` as object, `server.entry_point` added)
- **release**: replace `pyproject.toml` entry-point with a stdlib-only `server/main.py` shim — bundling `pyproject.toml` triggered `uv_build.build_editable`, which failed without the full source tree
- **release**: use `uv tool run` instead of `uvx` in `mcp_config` so the command is valid regardless of how Claude Desktop resolves the binary path

### Changed
- **ci**: bump pre-commit `repo-release-tools` hook from `v0.1.1` to `v1.8.1`

## [0.7.1] - 2026-04-01

### Added
- **ci**: upload test coverage XML and artifact for codecov/upload (#156)
- enhance MCP integration with Codex and Copilot support, update documentation and CLI commands (#149)

## [0.7.0] – 2026-03-20

### Fixed
- update documentation links and structure (#141)

## [0.6.0] – 2026-03-18

### Added
- Add SQLAlchemy framework support and enhance documentation (#138)

### Fixed
- **docs**: repair Mermaid contrast, text overflow, and expand diagram coverage (#137)

## [0.5.2] – 2026-03-09

### Changed
- enhance CLI with brand-aligned styles and improved documentation (#115)

## [0.5.1] – 2026-03-07

### Added
- Batch mode — LLM-safe chunked analysis with cursor pagination (#110)
- Fix `overall_score` scale (0–100 → 0–10) to match documented contract in `models.py` (#110)
- Implement proper weighted health score in `analyze_batch_summary`: severity² penalty (70%), violation density (20%), maintainability index (10%) (#19, #110)
- Add `analyze_batch_auto` MCP tool: auto-routes to full result or paginated batch based on token budget (#20, #110)

## [0.5.0] – 2026-03-03

### Added
- enhance branch creation with normalization and description joining functions; add tests for dry-run behavior (#107)
- Add support for Ansible, Terraform, and SVG analysis (#105)
- complete zen rules for all 5 languages (#75–#79) (#95)

### Fixed
- Update README to use PNG for dogma illustration and fix URL (#108)
- Refactor docstrings and import statements for consistency (#93)

### Documentation
- extend abbreviations list with 17 new entries (#104)
- Refactor documentation and add Dogma mapping generation script (#92)

## [0.4.0] – 2026-02-26

### Added
- Add philosophy document and update links in README; adjust argument names in analyzers (#90)
- enhance language analyzers with AST parsing capabilities (#71)

### Fixed
- Improve branch creation checks and add tests for uncommitted changes (#87)

### Documentation
- MCP-first reorientation of README.md and installation docs (#70)

## [0.3.0] – 2026-02-22

### Added
- **ci**: enable verbose output for TestPyPI package publishing
- **gitlab_ci**: Add GitLab CI support with multiple detectors and principles (#67)
- enhance language validation and documentation generation (#65)

### Fixed
- **css**: resolve back-to-top flip, contrast failures, and add cherry-red palette (#46)
- linting issues ruff (#45)

### Documentation
- add content quality checks and guide to documentation (#34)
