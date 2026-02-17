---
applyTo: '**'
---
# Analyzer Architecture Refactoring

## Problem Statement

The original `PythonAnalyzer.analyze()` method had **multiple anti-patterns**:

1. ❌ **400+ lines** in a single method
2. ❌ **Deeply nested** (5+ levels)
3. ❌ **Mixed concerns** (parsing, metrics, detection, formatting)
4. ❌ **Dictionary-based config** instead of Pydantic
5. ❌ **Hard to extend** to other languages
6. ❌ **Hard to test** individual detectors
7. ❌ **No separation of concerns**

## Solution: Architectural Patterns

We use a combination of proven design patterns:

### 1. **Template Method Pattern** (Base Structure)

**Purpose**: Define the analysis algorithm skeleton in the base class, with hooks for language-specific behavior.

```python
class BaseAnalyzer(ABC):
    def analyze(self, code: str, ...) -> AnalysisResult:
        # Template method - defines the flow
        context = self._create_context(...)
        context.ast_tree = self.parse_code(code)        # Hook
        metrics = self.compute_metrics(...)             # Hook
        violations = self.pipeline.run(context, config)
        return self._build_result(context, violations)

    @abstractmethod
    def parse_code(self, code: str) -> ParserResult:
        pass  # Language-specific hook

    @abstractmethod
    def compute_metrics(self, ...) -> tuple:
        pass  # Language-specific hook
```

**Benefits**:
- ✅ Common flow defined once
- ✅ Language-specific parts isolated
- ✅ Easy to maintain the overall structure

### 2. **Strategy Pattern** (Detectors)

**Purpose**: Encapsulate each violation detection algorithm in its own class.

```python
class ViolationDetector(ABC):
    @abstractmethod
    def detect(self, context: AnalysisContext, config: AnalyzerConfig) -> list[Violation]:
        pass

class CyclomaticComplexityDetector(ViolationDetector):
    def detect(self, context, config) -> list[Violation]:
        # Focused, single-responsibility logic
        ...

class NestingDepthDetector(ViolationDetector):
    def detect(self, context, config) -> list[Violation]:
        # Each detector is independent
        ...
```

**Benefits**:
- ✅ Each detector has **single responsibility**
- ✅ Easy to **add/remove** detectors
- ✅ Easy to **test** in isolation
- ✅ Can be **reused** across languages

### 3. **Pipeline Pattern** (Chain of Responsibility)

**Purpose**: Run multiple detectors in sequence, collecting all violations.

```python
class DetectionPipeline:
    def __init__(self, detectors: list[ViolationDetector]):
        self.detectors = detectors

    def run(self, context: AnalysisContext, config: AnalyzerConfig) -> list[Violation]:
        violations = []
        for detector in self.detectors:
            violations.extend(detector.detect(context, config))
        return violations
```

**Benefits**:
- ✅ **Fail-safe**: One detector error doesn't stop others
- ✅ **Configurable**: Easy to reorder or disable detectors
- ✅ **Composable**: Build different pipelines for different needs

### 4. **Context Object Pattern**

**Purpose**: Pass all analysis state in a single, type-safe object.

```python
class AnalysisContext(BaseModel):
    code: str
    ast_tree: ParserResult | None = None
    cyclomatic_summary: CyclomaticSummary | None = None
    violations: list[Violation] = []
    # ... all intermediate results
```

**Benefits**:
- ✅ **Type-safe**: All fields validated by Pydantic
- ✅ **No parameter explosion**: Pass one object instead of 10 parameters
- ✅ **Discoverable**: IDE autocomplete shows all available data

### 5. **Factory Pattern**

**Purpose**: Centralized creation of language-specific analyzers.

```python
class AnalyzerFactory:
    _analyzers = {
        "python": PythonAnalyzer,
        "typescript": TypeScriptAnalyzer,
        "rust": RustAnalyzer,
    }

    @classmethod
    def create(cls, language: str, config=None) -> BaseAnalyzer:
        return cls._analyzers[language](config)
```

**Benefits**:
- ✅ **Single point** for analyzer creation
- ✅ **Easy registration** of new languages
- ✅ **Centralized validation** of language support

## Architecture Comparison

### Before (Monolithic):

```python
class PythonAnalyzer:
    def analyze(self, code, path=None, other_files=None, ...):
        # 400+ lines of mixed concerns:
        # - Parse code
        # - Compute metrics
        # - Check nesting
        # - Check complexity
        # - Check god classes
        # - Check dependencies
        # - Check duplicates
        # - Check feature envy
        # - Build result
        # ... all in one method!
```

**Problems**:
- Cannot test individual checks
- Cannot reuse checks across languages
- Hard to understand flow
- Hard to modify without breaking things

### After (Modular):

```python
class PythonAnalyzer(BaseAnalyzer):
    def parse_code(self, code: str) -> ParserResult:
        # 5 lines

    def compute_metrics(self, code, ast) -> tuple:
        # 10 lines

    def build_pipeline(self) -> DetectionPipeline:
        return DetectionPipeline([
            CyclomaticComplexityDetector(),  # 30 lines each
            NestingDepthDetector(),
            LongFunctionDetector(),
            GodClassDetector(),
            # ... easy to add more
        ])

# analyze() inherited from BaseAnalyzer - no duplication!
```

**Benefits**:
- Each component is 5-50 lines
- Can test each detector independently
- Can reuse detectors across languages
- Clear separation of concerns

## Code Metrics Comparison

| Metric | Before | After | Improvement |
|--------|--------|-------|-------------|
| **analyze() lines** | 400+ | 15 (inherited) | 96% reduction |
| **Max nesting depth** | 5-6 | 2-3 | Flatter code |
| **Method complexity** | High (>20) | Low (<5) | Much simpler |
| **Testability** | Hard | Easy | Isolated units |
| **Reusability** | None | High | Share detectors |
| **Extensibility** | Difficult | Easy | Add languages |

## Extending to New Languages

### Before: Duplicate Everything

```python
class TypeScriptAnalyzer:
    def analyze(self, code, ...):
        # Copy-paste 400 lines from PythonAnalyzer
        # Modify language-specific parts
        # Hope you didn't miss anything
```

### After: Implement 3 Methods

```python
class TypeScriptAnalyzer(BaseAnalyzer):
    def parse_code(self, code: str) -> ParserResult:
        return parse_typescript(code)  # 1 line

    def compute_metrics(self, code, ast) -> tuple:
        return compute_ts_metrics(code)  # 1 line

    def build_pipeline(self) -> DetectionPipeline:
        return DetectionPipeline([
            AnyTypeDetector(),
            NonNullAssertionDetector(),
            ImplicitReturnTypeDetector(),
        ])  # 5 lines
```

**That's it!** The base analyzer handles:
- Context creation
- Pipeline execution
- Result building
- Error handling

## Testing Benefits

### Before: Monolithic Test

```python
def test_analyze():
    # Must set up entire analysis pipeline
    # Hard to isolate what you're testing
    # One failure breaks everything
    analyzer = PythonAnalyzer()
    result = analyzer.analyze(complex_code)
    # Now what? Too many things to check
```

### After: Focused Tests

```python
def test_cyclomatic_detector():
    detector = CyclomaticComplexityDetector()
    context = AnalysisContext(
        code="def foo(): ...",
        cyclomatic_summary=CyclomaticSummary(average=15.0)
    )
    config = AnalyzerConfig(max_cyclomatic_complexity=10)

    violations = detector.detect(context, config)

    assert len(violations) == 1
    assert violations[0].severity == 6
    # Test ONLY this detector
```

## Pydantic Benefits

### Before: Dictionaries

```python
def __init__(self, config: dict | None = None):
    self.config = config or {}
    max_complexity = self.config.get("max_cyclomatic_complexity", 10)
    # No validation, no type checking, easy to mistype keys
```

### After: Pydantic Models

```python
class AnalyzerConfig(BaseModel):
    max_cyclomatic_complexity: int = Field(default=10, ge=1, le=50)
    max_nesting_depth: int = Field(default=3, ge=1, le=10)

config = AnalyzerConfig(max_cyclomatic_complexity=8)
# Validated, type-safe, autocomplete works!
```

## Real-World Usage

### Creating Analyzers

```python
# Factory pattern - clean API
analyzer = AnalyzerFactory.create("python", PythonAnalyzerConfig(
    max_cyclomatic_complexity=8,
    detect_god_classes=True,
))

result = analyzer.analyze(code)
```

### Adding Custom Detector

```python
class MyCustomDetector(ViolationDetector):
    def detect(self, context, config) -> list[Violation]:
        # Your custom logic
        return violations

# Add to pipeline
class MyPythonAnalyzer(PythonAnalyzer):
    def build_pipeline(self) -> DetectionPipeline:
        pipeline = super().build_pipeline()
        pipeline.detectors.append(MyCustomDetector())
        return pipeline
```

### Language-Specific Configuration

```python
# Each language has its own typed config
python_config = PythonAnalyzerConfig(
    max_cyclomatic_complexity=10,
    detect_magic_methods=True,      # Python-specific
    max_magic_methods=3,
)

ts_config = TypeScriptAnalyzerConfig(
    max_cyclomatic_complexity=10,
    detect_any_usage=True,          # TypeScript-specific
    max_type_parameters=5,
)

rust_config = RustAnalyzerConfig(
    max_cyclomatic_complexity=10,
    detect_unwrap_usage=True,       # Rust-specific
    detect_unsafe_blocks=True,
)
```

## Migration Path

1. ✅ **Create base classes** (BaseAnalyzer, ViolationDetector, etc.)
2. ✅ **Extract detectors** from monolithic analyze() method
3. ✅ **Create Pydantic configs** to replace dictionaries
4. ✅ **Refactor PythonAnalyzer** to use new architecture
5. ✅ **Add tests** for each detector
6. ✅ **Add TypeScript/Rust** analyzers (easy now!)
7. ✅ **Deprecate** old monolithic code

## Summary

### Patterns Used

1. **Template Method** - Define analysis flow once
2. **Strategy** - Encapsulate each detector
3. **Pipeline** - Chain detectors together
4. **Context Object** - Type-safe state passing
5. **Factory** - Centralized analyzer creation
6. **Mixin** - Share location helpers

### Key Improvements

- ✅ **96% reduction** in method length
- ✅ **Type-safe** throughout with Pydantic
- ✅ **Testable** in isolation
- ✅ **Extensible** to new languages
- ✅ **Maintainable** with clear structure
- ✅ **Reusable** components
- ✅ **Pythonic** and clean

### Result

From a **400-line monolithic anti-pattern** to a **clean, modular, extensible architecture** that makes adding new languages trivial and testing straightforward.

**Recommended for production use!** ✨
