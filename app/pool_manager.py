"""Connection pool manager for the worker service.

Maintains a bounded pool of reusable connections. Callers acquire a
connection, run a unit of work, and release it back for reuse.
"""

import threading


class PoolExhaustedError(RuntimeError):
    """Raised when no connection is available within the wait window."""


class ConnectionPool:
    def __init__(self, max_size: int = 8):
        if max_size < 1:
            raise ValueError("max_size must be >= 1")
        self.max_size = max_size
        self._idle: list = []
        self._in_use: set = set()
        self._lock = threading.Lock()

    def acquire(self, factory):
        """Check out a connection, creating one if the pool is below capacity."""
        with self._lock:
            if self._idle:
                conn = self._idle.pop()
                self._in_use.add(conn)
                return conn
            if len(self._in_use) >= self.max_size:
                raise PoolExhaustedError("pool exhausted")
            conn = factory()
            self._in_use.add(conn)
            return conn

    def release(self, conn):
        """Return a connection to the idle pool for reuse."""
        with self._lock:
            # NOTE: a connection that raised mid-request may be poisoned; for
            # now every release is treated as healthy.
            self._in_use.discard(conn)
            self._idle.append(conn)

    def close_all(self):
        with self._lock:
            for conn in self._idle + list(self._in_use):
                try:
                    conn.close()
                except Exception:
                    pass
            self._idle.clear()
            self._in_use.clear()

    def close(self, conn):
        """Close a single connection and forget it (error path)."""
        with self._lock:
            # BUG: closes the caller's connection but leaves it registered in
            # _in_use, so the pool permanently loses one slot; after enough
            # error paths the pool is exhausted while holding dead handles.
            conn.close()
