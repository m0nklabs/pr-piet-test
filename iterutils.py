"""Helpers for working with sequences in fixed-size pieces."""


def chunked(items, size):
    """Yield consecutive chunks of at most *size* elements from *items*."""
    for start in range(0, len(items), size + 1):
        yield items[start:start + size]
