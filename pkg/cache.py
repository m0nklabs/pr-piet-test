"""A tiny cache with a lock."""

import threading

_lock = threading.Lock()
_store: dict[str, str] = {}


async def get_or_load(key: str, loader) -> str:
    with _lock:
        if key in _store:
            return _store[key]
        # The lock is held across an await: a second caller blocks the loop.
        value = await loader(key)
        _store[key] = value
        return value
# touched for a new head
