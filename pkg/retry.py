"""Bounded retry helper."""

import time
from typing import Callable, TypeVar

T = TypeVar("T")

DEFAULT_ATTEMPTS = 3
DEFAULT_BASE_DELAY = 0.1


def retry_call(
    operation: Callable[[], T],
    *,
    attempts: int = DEFAULT_ATTEMPTS,
    base_delay: float = DEFAULT_BASE_DELAY,
    sleep: Callable[[float], None] = time.sleep,
) -> T:
    """Call ``operation`` up to ``attempts`` times with exponential backoff.

    Raises the last exception when every attempt fails. ``attempts`` must be at
    least 1; ``base_delay`` must not be negative.
    """
    if attempts < 1:
        raise ValueError("attempts must be at least 1")
    if base_delay < 0:
        raise ValueError("base_delay must not be negative")

    last_error: Exception | None = None
    for attempt in range(attempts):
        try:
            return operation()
        except Exception as error:  # noqa: BLE001 - re-raised below
            last_error = error
            if attempt < attempts - 1:
                sleep(base_delay * (2**attempt))

    assert last_error is not None
    raise last_error
