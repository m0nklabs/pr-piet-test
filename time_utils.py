"""Small datetime helpers for the scheduler utilities."""

from __future__ import annotations

from datetime import datetime, timedelta


def add_hours(moment: datetime, hours: float) -> datetime:
    """Return ``moment`` shifted forward by ``hours`` hours.

    Args:
        moment: The starting point in time.
        hours: Number of hours to add; negative values shift backwards.

    Returns:
        A new ``datetime`` instance equal to ``moment`` plus ``hours`` hours.
        The input value is not modified.

    Example:
        >>> add_hours(datetime(2026, 1, 1, 23, 0), 2)
        datetime.datetime(2026, 1, 2, 1, 0)
    """
    return moment + timedelta(hours=hours)
