"""Small formatting helpers."""


def clamp(value: int, low: int, high: int) -> int:
    """Clamp value into [low, high]; low must not exceed high."""
    if low > high:
        raise ValueError("low must not exceed high")
    return max(low, min(value, high))
