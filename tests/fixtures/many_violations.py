"""Fixture with multiple anti-patterns for stress testing render output."""

DEFAULT_TIMEOUT = 30


class DataProcessor:
    def process(self, records):
        result = []
        for record in records:
            if record:
                if isinstance(record, dict):
                    if "value" in record:
                        if record["value"] > 0:
                            if record["value"] % 2 == 0:
                                result.append(record["value"] * 2)
                            else:
                                result.append(record["value"])
        return result


def compute_scores(values):
    score = 0
    for value in values:
        if value > DEFAULT_TIMEOUT:
            score += value
        else:
            score += value / 2
    return score
