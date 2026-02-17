from __future__ import annotations


def assert_balanced_boxes(output: str) -> None:
    """Assert balanced Rich box-drawing corner characters."""

    assert output.count("╭") == output.count("╰"), "Unbalanced rounded left corners"
    assert output.count("╮") == output.count("╯"), "Unbalanced rounded right corners"
    assert output.count("┏") == output.count("┗"), "Unbalanced heavy left corners"
    assert output.count("┓") == output.count("┛"), "Unbalanced heavy right corners"
    assert output.count("╔") == output.count("╚"), "Unbalanced double left corners"
    assert output.count("╗") == output.count("╝"), "Unbalanced double right corners"
