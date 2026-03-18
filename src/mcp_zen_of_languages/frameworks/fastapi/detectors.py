"""Rule-aware detectors for FastAPI framework guidance."""

from __future__ import annotations

import io
import re
import tokenize

from typing import TYPE_CHECKING

from mcp_zen_of_languages.frameworks.detector_base import FrameworkRuleDetectorBase
from mcp_zen_of_languages.models import Location


if TYPE_CHECKING:
    from collections.abc import Callable

    from mcp_zen_of_languages.analyzers.base import AnalysisContext
    from mcp_zen_of_languages.languages.configs import DetectorConfig
    from mcp_zen_of_languages.models import Violation


def _mask_comments(code: str) -> str:
    """Replace comment spans with spaces while preserving offsets."""
    lines = code.splitlines(keepends=True)
    try:
        tokens = tokenize.generate_tokens(io.StringIO(code).readline)
        for token in tokens:
            if token.type != tokenize.COMMENT:
                continue
            start_line, start_column = token.start
            end_line, end_column = token.end
            if start_line != end_line:
                continue
            line = lines[start_line - 1]
            lines[start_line - 1] = (
                line[:start_column]
                + (" " * (end_column - start_column))
                + line[end_column:]
            )
    except tokenize.TokenError:
        return code
    return "".join(lines)


def _location(line_number: int, line: str) -> Location:
    """Build a location anchored on the first non-whitespace character."""
    column = len(line) - len(line.lstrip()) + 1
    return Location(line=line_number, column=column)


class FastapiRuleDetector(FrameworkRuleDetectorBase):
    """Framework-specific detector with FastAPI-aware heuristics."""

    def _rule_handlers(
        self,
    ) -> dict[str, Callable[[AnalysisContext, DetectorConfig], list[Violation]]]:
        return {
            "fastapi-001": self._detect_missing_response_model,
            "fastapi-002": self._detect_missing_post_status_code,
            "fastapi-003": self._detect_bare_exception,
            "fastapi-004": self._detect_raw_threads,
            "fastapi-005": self._detect_blocking_calls_in_async_routes,
            "fastapi-006": self._detect_generic_route_decorator,
        }

    def _decorated_routes(self, code: str) -> list[tuple[str, str, int, str, bool]]:
        """Collect FastAPI decorator blocks with their attached handler line."""
        routes: list[tuple[str, str, int, str, bool]] = []
        lines = code.splitlines()
        line_count = len(lines)
        index = 0
        while index < line_count:
            line = lines[index]
            stripped = line.lstrip()
            if not stripped.startswith(("@app.", "@router.")):
                index += 1
                continue
            if not re.match(
                r"@(?:app|router)\.(?:get|post|put|delete|patch|route)\(",
                stripped,
            ):
                index += 1
                continue

            decorator_lines = [line]
            balance = line.count("(") - line.count(")")
            start_line = index + 1
            next_index = index + 1
            while balance > 0 and next_index < line_count:
                decorator_lines.append(lines[next_index])
                balance += lines[next_index].count("(") - lines[next_index].count(")")
                next_index += 1

            while next_index < line_count and not lines[next_index].strip():
                next_index += 1

            handler_line = lines[next_index] if next_index < line_count else ""
            is_async = handler_line.lstrip().startswith("async def ")
            routes.append(
                (
                    stripped,
                    "\n".join(decorator_lines),
                    start_line,
                    handler_line,
                    is_async,
                )
            )
            index = next_index if next_index > index else index + 1
        return routes

    def _detect_missing_response_model(
        self,
        context: AnalysisContext,
        config: DetectorConfig,
    ) -> list[Violation]:
        violations: list[Violation] = []
        for _, decorator, line_number, line, _ in self._decorated_routes(
            _mask_comments(context.code)
        ):
            if ".route(" in decorator or "response_model=" in decorator:
                continue
            violations.append(
                self.build_violation(
                    config,
                    contains="response_model",
                    location=_location(line_number, line),
                    suggestion=config.recommended_alternative,
                )
            )
        return violations

    def _detect_missing_post_status_code(
        self,
        context: AnalysisContext,
        config: DetectorConfig,
    ) -> list[Violation]:
        violations: list[Violation] = []
        for stripped, decorator, line_number, line, _ in self._decorated_routes(
            _mask_comments(context.code)
        ):
            if ".post(" not in stripped or "status_code=" in decorator:
                continue
            violations.append(
                self.build_violation(
                    config,
                    contains="status_code",
                    location=_location(line_number, line),
                    suggestion=config.recommended_alternative,
                )
            )
        return violations

    def _detect_bare_exception(
        self,
        context: AnalysisContext,
        config: DetectorConfig,
    ) -> list[Violation]:
        return self.regex_violations(
            context,
            config,
            r"raise\s+Exception\(",
            contains="raise Exception",
        )

    def _detect_raw_threads(
        self,
        context: AnalysisContext,
        config: DetectorConfig,
    ) -> list[Violation]:
        return self.regex_violations(
            context,
            config,
            r"\bthreading\.Thread\(",
            contains="threading.Thread",
        )

    def _detect_blocking_calls_in_async_routes(
        self,
        context: AnalysisContext,
        config: DetectorConfig,
    ) -> list[Violation]:
        masked_code = _mask_comments(context.code)
        lines = masked_code.splitlines()
        violations: list[Violation] = []
        blocking_pattern = re.compile(
            r"\b(?:requests\.\w+|time\.sleep\(|subprocess\.run\()"
        )
        for _, _, _, handler_line, is_async in self._decorated_routes(masked_code):
            if not is_async:
                continue
            handler_name = handler_line.split("def ", maxsplit=1)[-1].split(
                "(", maxsplit=1
            )[0]
            handler_match = re.search(
                rf"^\s*async\s+def\s+{re.escape(handler_name)}\b",
                masked_code,
                re.MULTILINE,
            )
            if handler_match is None:
                continue
            handler_line_number = masked_code.count("\n", 0, handler_match.start()) + 1
            base_indent = len(handler_line) - len(handler_line.lstrip())
            for current_index in range(handler_line_number, len(lines)):
                candidate = lines[current_index]
                stripped = candidate.strip()
                if not stripped:
                    continue
                indent = len(candidate) - len(candidate.lstrip())
                if indent <= base_indent and current_index + 1 > handler_line_number:
                    break
                if not blocking_pattern.search(candidate):
                    continue
                violations.append(
                    self.build_violation(
                        config,
                        contains="blocking I/O",
                        location=_location(current_index + 1, candidate),
                        suggestion=config.recommended_alternative,
                    )
                )
                break
        return violations

    def _detect_generic_route_decorator(
        self,
        context: AnalysisContext,
        config: DetectorConfig,
    ) -> list[Violation]:
        violations: list[Violation] = []
        for stripped, _, line_number, line, _ in self._decorated_routes(
            _mask_comments(context.code)
        ):
            if ".route(" not in stripped:
                continue
            violations.append(
                self.build_violation(
                    config,
                    contains="@app.route",
                    location=_location(line_number, line),
                    suggestion=config.recommended_alternative,
                )
            )
        return violations


class _BoundFastapiDetector(FastapiRuleDetector):
    """Base class for rule-bound fastapi detectors."""

    _handler_name: str

    def detect(
        self,
        context: AnalysisContext,
        config: DetectorConfig,
    ) -> list[Violation]:
        """Run the bound fastapi detector handler."""
        handler = getattr(self, self._handler_name)
        return handler(context, config)


class FastapiAsyncIoDetector(_BoundFastapiDetector):
    """Concrete detector binding for FastapiAsyncIoDetector."""

    _handler_name = "_detect_blocking_calls_in_async_routes"


class FastapiBackgroundTasksDetector(_BoundFastapiDetector):
    """Concrete detector binding for FastapiBackgroundTasksDetector."""

    _handler_name = "_detect_raw_threads"


class FastapiHttpExceptionDetector(_BoundFastapiDetector):
    """Concrete detector binding for FastapiHttpExceptionDetector."""

    _handler_name = "_detect_bare_exception"


class FastapiResponseModelDetector(_BoundFastapiDetector):
    """Concrete detector binding for FastapiResponseModelDetector."""

    _handler_name = "_detect_missing_response_model"


class FastapiStatusCodeDetector(_BoundFastapiDetector):
    """Concrete detector binding for FastapiStatusCodeDetector."""

    _handler_name = "_detect_missing_post_status_code"


class FastapiVerbDecoratorDetector(_BoundFastapiDetector):
    """Concrete detector binding for FastapiVerbDecoratorDetector."""

    _handler_name = "_detect_generic_route_decorator"


__all__ = [
    "FastapiAsyncIoDetector",
    "FastapiBackgroundTasksDetector",
    "FastapiHttpExceptionDetector",
    "FastapiResponseModelDetector",
    "FastapiStatusCodeDetector",
    "FastapiVerbDecoratorDetector",
]
