"""OpenTelemetry helpers used by server and analyzers."""

from __future__ import annotations

from contextlib import contextmanager, nullcontext


@contextmanager
def analysis_span(
    name: str,
    attributes: dict[str, str | int | float | bool] | None = None,
) -> object:
    """Create a telemetry span for analysis steps, falling back to no-op."""
    try:
        from fastmcp.telemetry import get_tracer
    except ImportError:
        with nullcontext() as span:
            yield span
            return

    tracer = get_tracer()
    with tracer.start_as_current_span(name) as span:
        if attributes:
            span.set_attributes(dict(attributes))
        yield span
