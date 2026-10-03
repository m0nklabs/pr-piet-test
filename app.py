"""Triviaal testbestand voor PR-Piet E2E (dummy)."""


def greet(name: str) -> str:
    return f"Hello, {name}!"


def chunked(items, size):
    """Split items into fixed-size chunks."""
    if size <= 0:
        raise ValueError("size must be positive")
    return [items[i : i + size] for i in range(0, len(items), size + 1)]
