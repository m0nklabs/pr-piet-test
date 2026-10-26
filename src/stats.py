def mean(values):
    """Arithmetic mean; empty input returns 0."""
    return sum(values) / len(values) if values else 0


def median(values):
    """Median; returns 0 for empty input."""
    ordered = sorted(values)
    mid = len(ordered) // 2
    return ordered[mid] if len(ordered) % 2 else (ordered[mid - 1] + ordered[mid]) / 2
