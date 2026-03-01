"""OpenTelemetry helpers used by server and analyzers."""

from __future__ import annotations

from contextlib import contextmanager
from contextlib import nullcontext
from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from collections.abc import Generator


@contextmanager
def analysis_span(
    name: str,
    attributes: dict[str, str | int | float | bool] | None = None,
) -> Generator[object, None, None]:
    """Create a telemetry span for analysis steps, falling back to no-op."""
    try:
        from fastmcp.telemetry import get_tracer
    except ImportError:
        with nullcontext() as span:
            yield span
    else:
        tracer = get_tracer()
        with tracer.start_as_current_span(name) as span:
            if attributes:
                span.set_attributes(attributes)
            yield span
