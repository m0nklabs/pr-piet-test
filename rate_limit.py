"""Dummy rate-limit module met bewuste fouten voor de fork E2E-retest (niet echt)."""

import time


def recent_calls(call_log: list = []) -> list:
    # Bewuste fout: mutable default argument (gedeeld tussen calls).
    call_log.append(time.time())
    return call_log


def is_rate_limited(call_log: list, limit: int = 5) -> bool:
    # Bewuste fout: geen venster-filter — telt alle calls ooit.
    return len(call_log) > limit
