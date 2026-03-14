"""Universal dogma detectors that classify violations across every language."""

from __future__ import annotations

from abc import ABC

from mcp_zen_of_languages.core.universal_dogmas import UniversalDogmaID
from mcp_zen_of_languages.models import AnalysisResult
from mcp_zen_of_languages.models import DogmaFinding
from mcp_zen_of_languages.models import Violation


def _dedupe(values: list[str]) -> list[str]:
    """Return values in first-seen order without duplicates."""
    seen: set[str] = set()
    ordered: list[str] = []
    for value in values:
        if not value or value in seen:
            continue
        seen.add(value)
        ordered.append(value)
    return ordered


def _dogma_label(dogma_id: str) -> str:
    """Convert a dogma id into a human-readable label."""
    try:
        return UniversalDogmaID(dogma_id).name.replace("_", " ").title()
    except ValueError:
        return dogma_id


def _violation_signature(violation: Violation) -> str:
    """Build a normalized cross-language signature for dogma classification."""
    parts = [
        violation.principle,
        violation.message,
        violation.suggestion or "",
        violation.rule_id or "",
        violation.detector_id or "",
    ]
    return " ".join(parts).lower().replace("_", " ").replace("-", " ")


class DogmaDetector(ABC):
    """Classify violations into one universal dogma and aggregate the matches."""

    dogma_id: str
    keywords: tuple[str, ...] = ()

    def detect(self, result: AnalysisResult) -> DogmaFinding | None:
        """Return a finding for this dogma when matching violations exist."""
        relevant = [
            violation
            for violation in result.violations
            if self.matches_violation(violation)
        ]
        if not relevant:
            return None

        files = _dedupe(self._files_for(result, relevant))
        rule_ids = _dedupe([violation.rule_id or "" for violation in relevant])
        detector_ids = _dedupe([violation.detector_id or "" for violation in relevant])
        messages = _dedupe([violation.message for violation in relevant])[:5]
        return DogmaFinding(
            dogma_id=self.dogma_id,
            label=_dogma_label(self.dogma_id),
            severity=max(violation.severity for violation in relevant),
            violation_count=len(relevant),
            rule_ids=rule_ids,
            detector_ids=detector_ids,
            messages=messages,
            files=files,
        )

    def matches_violation(self, violation: Violation) -> bool:
        """Classify a violation for this dogma using universal heuristics."""
        if self.dogma_id in violation.universal_dogma_ids:
            return True
        signature = _violation_signature(violation)
        return any(keyword in signature for keyword in self.keywords)

    @staticmethod
    def _files_for(result: AnalysisResult, violations: list[Violation]) -> list[str]:
        """Collect file paths that support a dogma finding."""
        files: list[str] = []
        for violation in violations:
            if violation.files:
                files.extend(violation.files)
            elif result.path:
                files.append(result.path)
        return files


class UtilizeArgumentsDogmaDetector(DogmaDetector):
    """Classify violations about unused or vestigial arguments."""

    dogma_id = UniversalDogmaID.UTILIZE_ARGUMENTS.value
    keywords = (
        "unused argument",
        "unused parameter",
        "unused params",
        "unused kwargs",
        "unused args",
        "vestigial parameter",
        "deprecated argument",
        "signature",
    )


class ExplicitIntentDogmaDetector(DogmaDetector):
    """Classify violations about hidden behaviour and implicit contracts."""

    dogma_id = UniversalDogmaID.EXPLICIT_INTENT.value
    keywords = (
        "explicit",
        "implicit",
        "magic",
        "wildcard import",
        "star import",
        "strict mode",
        "return type",
        "type annotations",
        "status code",
        "response model",
        "any type",
        "non null assertion",
        "quote all variables",
        "const correctness",
        "shell for run steps",
    )


class ReturnEarlyDogmaDetector(DogmaDetector):
    """Classify violations about deep nesting and non-flat traversal."""

    dogma_id = UniversalDogmaID.RETURN_EARLY.value
    keywords = (
        "nested",
        "nesting",
        "guard clause",
        "guard clauses",
        "early return",
        "depth",
        "flatten",
        "deeply nested",
        "complex one liners",
        "god pipeline",
    )


class FailFastDogmaDetector(DogmaDetector):
    """Classify violations about swallowed errors and weak failure semantics."""

    dogma_id = UniversalDogmaID.FAIL_FAST.value
    keywords = (
        "error",
        "errors",
        "exception",
        "exceptions",
        "panic",
        "unwrap",
        "bare except",
        "swallow",
        "null values",
        "allow failure",
        "interruptible",
        "cleanup",
        "re raise",
        "fail",
    )


class RightAbstractionDogmaDetector(DogmaDetector):
    """Classify violations about poor or overbearing abstractions."""

    dogma_id = UniversalDogmaID.RIGHT_ABSTRACTION.value
    keywords = (
        "abstraction",
        "abstract",
        "interface",
        "inheritance",
        "composition",
        "god class",
        "feature envy",
        "background tasks",
        "context manager",
        "enum",
        "dependency",
        "declarative",
        "validator",
        "organize responsibility",
    )


class UnambiguousNameDogmaDetector(DogmaDetector):
    """Classify violations about unclear naming and readability."""

    dogma_id = UniversalDogmaID.UNAMBIGUOUS_NAME.value
    keywords = (
        "name",
        "naming",
        "names",
        "alias",
        "identifier",
        "descriptive",
        "readable",
        "self documenting",
        "docstring",
        "labels and references",
        "descriptive table aliases",
    )


class VisibleStateDogmaDetector(DogmaDetector):
    """Classify violations about hidden mutation and unclear state."""

    dogma_id = UniversalDogmaID.VISIBLE_STATE.value
    keywords = (
        "state",
        "mutable",
        "mutation",
        "side effect",
        "session",
        "lifecycle",
        "readonly",
        "const",
        "cache key",
        "stable key",
        "zero value",
        "global",
    )


class StrictFencesDogmaDetector(DogmaDetector):
    """Classify violations about broken boundaries and leaked internals."""

    dogma_id = UniversalDogmaID.STRICT_FENCES.value
    keywords = (
        "boundary",
        "boundaries",
        "private",
        "protected",
        "namespace",
        "import",
        "imports",
        "export",
        "exports",
        "encapsulation",
        "public api",
        "exposed",
        "root user",
        "dockerignore",
        "permission",
        "permissions",
        "artifact",
    )


class RuthlessDeletionDogmaDetector(DogmaDetector):
    """Classify violations about dead code, clutter, and stale paths."""

    dogma_id = UniversalDogmaID.RUTHLESS_DELETION.value
    keywords = (
        "dead code",
        "unreachable",
        "todo",
        "stub",
        "duplicate",
        "duplicates",
        "duplicated",
        "clutter",
        "unused",
        "orphan",
        "deprecated",
        "legacy",
        "sparse",
    )


class ProportionateComplexityDogmaDetector(DogmaDetector):
    """Classify violations about excessive complexity or over-engineering."""

    dogma_id = UniversalDogmaID.PROPORTIONATE_COMPLEXITY.value
    keywords = (
        "complexity",
        "complex",
        "long function",
        "line length",
        "large",
        "premature",
        "optimization",
        "benchmark",
        "matrix values",
        "god pipeline",
        "one liners",
        "deep embedding",
        "longer than",
    )


def build_dogma_detectors() -> list[DogmaDetector]:
    """Return the default detector suite for universal dogma analysis."""
    return [
        UtilizeArgumentsDogmaDetector(),
        ExplicitIntentDogmaDetector(),
        ReturnEarlyDogmaDetector(),
        FailFastDogmaDetector(),
        RightAbstractionDogmaDetector(),
        UnambiguousNameDogmaDetector(),
        VisibleStateDogmaDetector(),
        StrictFencesDogmaDetector(),
        RuthlessDeletionDogmaDetector(),
        ProportionateComplexityDogmaDetector(),
    ]


__all__ = [
    "DogmaDetector",
    "ExplicitIntentDogmaDetector",
    "FailFastDogmaDetector",
    "ProportionateComplexityDogmaDetector",
    "ReturnEarlyDogmaDetector",
    "RightAbstractionDogmaDetector",
    "RuthlessDeletionDogmaDetector",
    "StrictFencesDogmaDetector",
    "UnambiguousNameDogmaDetector",
    "UtilizeArgumentsDogmaDetector",
    "VisibleStateDogmaDetector",
    "build_dogma_detectors",
]
