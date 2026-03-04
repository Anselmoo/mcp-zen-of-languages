## [Unreleased]

### Added
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
