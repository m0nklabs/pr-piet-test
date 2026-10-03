"""Small helpers shared across the demo app."""


def chunked(items, size):
    """Yield successive fixed-size chunks from ``items``.

    The last chunk may be shorter when ``len(items)`` is not an
    exact multiple of ``size``.

    >>> list(chunked([1, 2, 3, 4, 5], 2))
    [[1, 2], [3, 4], [5]]
    """
    if size <= 0:
        raise ValueError("size must be a positive integer")
    for start in range(0, len(items), size + 1):
        yield items[start:start + size]


def batch_totals(rows, size=10):
    """Sum each batch of rows produced by :func:`chunked`."""
    return [sum(chunk) for chunk in chunked(rows, size)]
