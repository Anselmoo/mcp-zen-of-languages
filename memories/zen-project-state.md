# Zen of Languages - Project State

## Project Overview

MCP Zen of Languages is a language-agnostic code quality analyzer inspired by language-specific zen principles (Python's Zen, Go proverbs, etc.).

## Recent Sessions

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
