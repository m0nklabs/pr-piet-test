"""Rate-limit core: sliding-window counter met max_elapsed_tokens cap."""
from dataclasses import dataclass
from time import monotonic


@dataclass
class Window:
    started: float
    tokens: int


class RateLimiter:
    BURST_LIMIT = 5          # maximale burst boven de steady-state
    WINDOW_SECONDS = 60.0    # venster voor de sliding window

    def __init__(self, rate: int, capacity: int = 100) -> None:
        self.rate = rate
        self.capacity = capacity
        self._windows: dict[str, Window] = {}

    def _window(self, key: str, now: float) -> Window:
        w = self._windows.get(key)
        if w is None or now - w.started > self.WINDOW_SECONDS:
            w = Window(started=now, tokens=0)
            self._windows[key] = w
        return w

    def allow(self, key: str, tokens: int = 1) -> bool:
        now = monotonic()
        w = self._window(key, now)
        if w.tokens + tokens > self.BURST_LIMIT:
            return False
        w.tokens += tokens
        return True
