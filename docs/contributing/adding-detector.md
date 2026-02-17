---
title: Adding a Detector
description: Implement a new violation detector, register it in the pipeline, and add tests.
icon: material/source-branch
tags:
  - API
  - Configuration
---

# Adding a Detector

Detectors are the core extension point. Each one is a **Strategy** — a single class with a single responsibility: find one kind of violation in code.

## How detectors work

A detector receives an `AnalysisContext` (containing the code, AST, metrics, and config) and returns a list of `Violation` objects. The pipeline calls every registered detector and collects the results.

## Step-by-step

### 1. Create the detector class

```python
from mcp_zen_of_languages.analyzers.detectors.base import ViolationDetector

class NoTodoDetector(ViolationDetector):
    def detect(self, context, config):
        violations = []
        for i, line in enumerate(context.code.splitlines(), 1):
            if "TODO" in line:
                violations.append(self._build_violation(
                    rule_id="no-todo",
                    message=f"TODO comment at line {i} — resolve or track in issue tracker.",
                    severity=4,
                    line=i,
                ))
        return violations
```

### 2. Add a config model (if needed)

If your detector needs configurable thresholds, add a config model in `languages/configs.py`:

```python
class NoTodoConfig(DetectorConfig):
    type: str = "no-todo"
    max_todos: int = 0
```

### 3. Register in mapping

In the language's `mapping.py`, bind the rule ID to the detector class:

```python
from .detectors import NoTodoDetector

RULE_DETECTOR_MAP = {
    "no-todo": NoTodoDetector,
}
```

### 4. Add tests

Write at least two tests — one where the violation fires, one where clean code passes:

```python
def test_no_todo_detects_violation():
    detector = NoTodoDetector()
    context = AnalysisContext(code="x = 1  # TODO: fix this", language="python")
    violations = detector.detect(context, config)
    assert len(violations) == 1
    assert violations[0].severity == 4

def test_no_todo_clean_code():
    detector = NoTodoDetector()
    context = AnalysisContext(code="x = 1  # done", language="python")
    violations = detector.detect(context, config)
    assert len(violations) == 0
```

## Terminal output guidelines

If your detector changes what users see in terminal output:

- Keep output within `get_output_width(console)` limits
- Use shared box constants from `rendering/themes.py`
- Align severity output via `severity_badge(...)` — keep `Sev` column at 12 characters
- Prefer Rich renderables (`Panel`, `Table`, `Syntax`) over markdown-like strings

## See Also

- [Architecture](architecture.md) — How detectors fit into the pipeline
- [Adding a Language](adding-language.md) — Full language module setup
- [Languages](../user-guide/languages/index.md) — See existing detectors for reference
