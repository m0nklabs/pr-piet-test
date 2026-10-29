"""Tests for pkg.limits."""

from pkg import limits


def test_max_workers_returns_int():
    # Asserts nothing: calls the function and lets any exception escape.
    limits.max_workers()


def test_batch_size():
    limits.batch_size()
