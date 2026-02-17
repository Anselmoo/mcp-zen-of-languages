"""Fixture with moderate complexity and style issues."""


def calculate_total(items):
    total = 0
    for item in items:
        if item > 0:
            if item % 2 == 0:
                total += item * 2
            else:
                total += item
    return total
