---
title: Adding a Language
description: Step-by-step guide to adding a new language with rules, analyzers, detectors, and mappings.
icon: material/source-branch
tags:
  - API
  - Configuration
---

# Adding a Language

Every language in MCP Zen of Languages follows the same structure. You'll define zen principles, implement an analyzer, create detectors, and wire everything together. The architecture does the rest.

## Mental model

Think of each language module as answering three questions:

1. **What does "good code" mean?** → `rules.py` (zen principles)
2. **How do we parse the code?** → `analyzer.py` (Template Method hooks)
3. **What patterns do we flag?** → `detectors.py` (Strategy implementations)

## Directory structure

Create `src/mcp_zen_of_languages/languages/<language>/` with:

```
<language>/
├── __init__.py          # Module exports
├── rules.py             # Zen principles (ZenPrinciple models)
├── analyzer.py          # Subclass of BaseAnalyzer
├── detectors.py         # ViolationDetector implementations
└── mapping.py           # Rule ID → Detector class bindings
```

## Step-by-step

### 1. Define zen principles

In `rules.py`, define principles as `ZenPrinciple` Pydantic models. Each principle needs a unique rule ID, name, category, and severity:

```python
# languages/kotlin/rules.py
KOTLIN_ZEN_RULES = [
    ZenPrinciple(
        rule_id="kt-001",
        name="Null safety is non-negotiable",
        category="SAFETY",
        severity=7,
        description="Use Kotlin's type system to eliminate null pointer exceptions.",
    ),
    # ... more principles
]
```

### 2. Implement the analyzer

Subclass `BaseAnalyzer` and implement the two abstract methods:

```python
# languages/kotlin/analyzer.py
from mcp_zen_of_languages.analyzers.base import BaseAnalyzer

class KotlinAnalyzer(BaseAnalyzer):
    def parse_code(self, code: str):
        return None  # Use None for regex-based detection

    def compute_metrics(self, code: str, ast_tree):
        return None, None, len(code.splitlines())
```

Most languages use regex-based detection (no AST parsing required). Only Python currently has full AST support.

### 2.1 Declare analyzer capabilities

Every analyzer can optionally override `capabilities()` to declare support for AST parsing, dependency analysis, and richer metrics.

```python
from mcp_zen_of_languages.analyzers.base import AnalyzerCapabilities

class KotlinAnalyzer(BaseAnalyzer):
    def capabilities(self) -> AnalyzerCapabilities:
        return AnalyzerCapabilities(supports_ast=False)
```

Guidance:

- Keep hook signatures (`parse_code`, `compute_metrics`, `_build_dependency_analysis`) intact even when implementations are placeholders.
- Returning `None` from `parse_code` is valid for text-only analyzers; `BaseAnalyzer` records this via `AnalysisContext.ast_status`.
- Override `capabilities()` when you add a real parser or dependency graph so detectors can branch on explicit support.

### 3. Create detectors

Each detector implements `ViolationDetector` with a `detect()` method:

```python
# languages/kotlin/detectors.py
from mcp_zen_of_languages.analyzers.detectors.base import ViolationDetector

class NullAssertionDetector(ViolationDetector):
    def detect(self, context, config):
        violations = []
        for i, line in enumerate(context.code.splitlines(), 1):
            if "!!" in line:
                violations.append(self._build_violation(
                    rule_id="kt-001",
                    message=f"Non-null assertion (!!) at line {i}",
                    severity=7,
                    line=i,
                ))
        return violations
```

### 4. Register mappings

In `mapping.py`, connect rule IDs to detector classes:

```python
# languages/kotlin/mapping.py
from .detectors import NullAssertionDetector

RULE_DETECTOR_MAP = {
    "kt-001": NullAssertionDetector,
}
```

### 5. Add detector configs (if needed)

If your detectors need configurable thresholds, add config models in `languages/configs.py`.

### 6. Register in the factory

Add your analyzer to `analyzers/analyzer_factory.py` so the factory can create it.

### 7. Add tests

At minimum, write tests for each detector in `tests/`. Test both positive cases (violation expected) and negative cases (clean code).

## Verification

```bash
uv run python scripts/check_language_structure.py  # Structure check
uv run pytest                                        # All tests
```

## See Also

- [Architecture](architecture.md) — How the patterns connect
- [Adding a Detector](adding-detector.md) — Focused guide for single detectors
- [Languages](../user-guide/languages/index.md) — Existing language implementations for reference
