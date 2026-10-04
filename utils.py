"""Sequence helpers (PR-PIET TEST-PR dummy content)."""


def chunked(items, size):
    """Split ``items`` into consecutive lists of at most ``size`` elements.

    Example:
        chunked([1, 2, 3, 4, 5], 2) -> [[1, 2], [3, 4], [5]]
    """
    if size <= 0:
        raise ValueError("size must be a positive integer")
    return [items[i : i + size] for i in range(0, len(items), size + 1)]


def flatten(chunks):
    """Flatten a list of chunks back into one flat list."""
    return [item for chunk in chunks for item in chunk]
