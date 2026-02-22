# Zen of Languages - Project State

## Project Overview

MCP Zen of Languages is a language-agnostic code quality analyzer inspired by language-specific zen principles (Python's Zen, Go proverbs, etc.).

## Recent Sessions

---

### PR #73 Follow-up: Universal Adapter Architecture - Commit 3465325

**Date**: Current session

**Context**:
Addressed maintainer comment requiring that adapter/rule set must be universal for all languages rather than language-specific initialization.

**Changes Made**:
1. Universal adapter module:
   - Created `src/mcp_zen_of_languages/adapters/universal.py`
   - Implemented `AnalyzerFactoryAdapter` for universal language support
   - Added `build_universal_adapters()` using `analyzer_factory.supported_languages()`
   - Auto-generates adapters for all supported languages (Python, TypeScript, SQL, Markdown, etc.)

2. UniversalZenDetector enhancement:
   - Updated `core/detector.py` to auto-load all language adapters when `adapters=None`
   - Default behavior now provides universal language support out-of-box
   - No manual adapter configuration needed for standard use cases

3. Module exports:
   - Updated `adapters/__init__.py` to export universal adapter components
   - Provides clean public API for universal adapter usage

4. Test updates:
   - Updated `tests/analyzers/test_universal_detector.py`
   - Verified default detector handles Python analysis
   - Verified default detector handles TypeScript analysis
   - Confirms multi-language support works automatically

**Validation Status**:
- ✅ Targeted pytest: passed
- ✅ Ruff: passed
- ✅ Pre-commit all-files: passed
- ✅ Code review: no comments
- ✅ CodeQL: 0 alerts

**Key Technical Insight**:
The universal adapter pattern leverages the analyzer factory's language registry to dynamically build adapters for all supported languages. This eliminates the need for explicit adapter initialization and ensures consistent behavior across all languages. The architecture is extensible—adding a new language analyzer automatically adds its adapter to the universal set.

**Architectural Impact**:
This change shifts from explicit adapter management to implicit universal coverage, making the detector API simpler and more maintainable. It aligns with the principle that the tool should "just work" for all supported languages without configuration.

**Status**: Completed and validated

### PR #60 SQL Detectors - Reviewer Feedback - Commit 4236efb

**Date**: Current session

**Changes Made**:
1. SQL-001 (SELECT * projection) enhancement:
   - Now only flags top-level projection stars (column selection)
   - Ignores COUNT(*) aggregate function (valid pattern)
   - More precise targeting of anti-pattern

2. Location lookup improvements:
   - Preserves matched casing for SELECT*/select keywords
   - Preserves matched casing for NOLOCK/nolock hints
   - Preserves matched casing for BEGIN TRANSACTION/begin transaction
   - Uses regex match groups to capture exact matched text

3. Unbounded query detector (sql-002):
   - SELECT location lookup now case-insensitive
   - Handles lowercase SQL code properly

4. Transaction boundary detector (sql-003):
   - Now uses `finditer` instead of `search`
   - Captures first matched BEGIN lexeme for accurate location
   - Improved location precision

5. Test updates:
   - Added COUNT(*) non-violation test case
   - Added lowercase keyword location test cases
   - Updated tests in `tests/detectors/test_sql_detectors.py`

**Validation Status**:
- ✅ SQL detector tests: `uv run --no-sync pytest --no-cov tests/detectors/test_sql_detectors.py` passed
- ✅ Pre-commit all-files: passed
- ✅ Code review: 1 non-blocking duplication suggestion
- ✅ CodeQL: 0 alerts

**Key Technical Insight**:
Using regex match groups (e.g., `(SELECT\s*\*)` with `match.group(1)`) preserves the exact matched casing from the source code, providing better location accuracy and respecting the original code style. The distinction between projection stars (anti-pattern) and COUNT(*) (valid pattern) was properly implemented.

**Status**: Completed and validated

---

### PR #59 Follow-up Fix - Commit f7bfcdc

**Date**: Current session

**Changes Made**:
1. Markdown detectors enhancement:
   - `_is_mdx_context` now fence/front-matter aware via `_iter_text_lines`
   - Prevents false positives in fenced code blocks and front matter

2. Bare URL detector fix:
   - Now ignores inline code spans
   - Prevents flagging URLs in code examples

3. Test coverage:
   - Added regression tests for fenced export/import false positives
   - Validates proper context awareness

4. Documentation updates:
   - md-004 docs pattern now properly escaped as `\`\`\``
   - Regenerated markdown language docs

**Validation Status**:
- ✅ Pre-commit all-files: passed
- ✅ Pre-push: passed (after `uv sync --all-groups --all-extras`)
- ✅ Code review: clean
- ✅ CodeQL: clean

**Key Technical Insight**:
The `_iter_text_lines` helper now provides context-aware text iteration for markdown detectors, allowing them to skip false positives in code fences and YAML front matter. This is a critical pattern for markdown linters.

**Status**: Completed and validated

---

## Current Analysis Baseline

*To be populated with violation counts by category*

## Configuration Decisions

*To be populated with configuration rationale*

## Detector Development

*To be populated with in-progress detectors*

## Known Issues

*To be populated with tracked problems and workarounds*

## Project Roadmap

*To be populated with upcoming features and priorities*
