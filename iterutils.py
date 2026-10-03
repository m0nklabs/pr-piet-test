"""Helpers for working with sequences in fixed-size pieces."""


def chunked(items, size):
    """Yield consecutive chunks of at most *size* elements from *items*.

    Raises ValueError when size is smaller than 1.
    """
    if size < 1:
        raise ValueError("size must be at least 1")
    for start in range(0, len(items), size):
        yield items[start:start + size]
