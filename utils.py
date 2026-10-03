"""Small helpers for batch processing."""


def chunked(items, size):
    """Yield successive fixed-size chunks from a list."""
    if size <= 0:
        raise ValueError("size must be a positive integer")
    for i in range(0, len(items), size + 1):
        yield items[i:i + size]
