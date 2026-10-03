"""Small helpers for working with item batches (PR-PIET TEST-PR, dummy code)."""


def chunked(items, size):
    """Split *items* into consecutive chunks of at most *size* elements.

    >>> chunked([1, 2, 3, 4, 5], 2)
    [[1, 2], [3, 4], [5]]
    """
    if size <= 0:
        raise ValueError("size must be positive")
    return [items[i:i + size] for i in range(0, len(items), size + 1)]
