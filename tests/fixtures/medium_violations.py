"""Fixture with moderate complexity and style issues."""


def calculate_total(items):
    return sum(item * 2 if item % 2 == 0 else item for item in items if item > 0)
