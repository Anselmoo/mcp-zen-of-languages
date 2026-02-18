"""Fixture with multiple anti-patterns for stress testing render output."""

DEFAULT_TIMEOUT = 30


class DataProcessor:
    def process(self, records):
        result = []
        for record in records:
            if (
                record
                and isinstance(record, dict)
                and "value" in record
                and record["value"] > 0
            ):
                if record["value"] % 2 == 0:
                    result.append(record["value"] * 2)
                else:
                    result.append(record["value"])
        return result


def compute_scores(values):
    return sum(value if value > DEFAULT_TIMEOUT else value / 2 for value in values)
