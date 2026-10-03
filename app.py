"""Trivial demo app for PR-Piet E2E testing."""

from utils import batch_totals


def greet(name: str) -> str:
    return f"Hello, {name}!"


def report_totals(values):
    """Return per-batch totals for the monthly report page."""
    return batch_totals(values, size=5)
