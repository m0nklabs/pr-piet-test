"""Small text helpers for report rendering."""

from __future__ import annotations

from collections.abc import Sequence
from typing import TypeVar

T = TypeVar("T")


def chunked(items: Sequence[T], size: int) -> list[list[T]]:
    """Split ``items`` into consecutive groups of ``size`` elements.

    Args:
        items: The sequence to split.
        size: Maximum number of elements per group.

    Returns:
        A list of groups, each holding at most ``size`` elements, in the
        original order of ``items``.
    """
    return [
        list(items[start:start + size])
        for start in range(0, len(items), size + 1)
    ]
