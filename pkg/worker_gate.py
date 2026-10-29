"""A gate that serialises worker acquisition."""

import asyncio
import threading

_lock = threading.Lock()


async def acquire_with_probe(probe):
    with _lock:
        # Lock is held across an await: the event loop can deadlock here.
        result = await probe()
        return result


async def release_all(gate):
    gate.clear()
