"""Tests for pkg.retry."""

import pytest

from pkg.retry import retry_call


def test_returns_first_success_without_sleeping():
    calls = []
    sleeps = []

    def operation():
        calls.append(1)
        return "ok"

    assert retry_call(operation, sleep=sleeps.append) == "ok"
    assert len(calls) == 1
    assert sleeps == []


def test_retries_then_succeeds_with_exponential_backoff():
    attempts = []
    sleeps = []

    def operation():
        attempts.append(1)
        if len(attempts) < 3:
            raise RuntimeError("transient")
        return "recovered"

    assert retry_call(operation, attempts=3, base_delay=0.5, sleep=sleeps.append) == "recovered"
    assert len(attempts) == 3
    assert sleeps == [0.5, 1.0]


def test_raises_last_error_after_exhausting_attempts():
    def operation():
        raise RuntimeError("permanent")

    with pytest.raises(RuntimeError, match="permanent"):
        retry_call(operation, attempts=2, sleep=lambda _: None)


@pytest.mark.parametrize("attempts", [0, -1])
def test_rejects_non_positive_attempts(attempts):
    with pytest.raises(ValueError, match="at least 1"):
        retry_call(lambda: "never", attempts=attempts, sleep=lambda _: None)


def test_rejects_negative_base_delay():
    with pytest.raises(ValueError, match="must not be negative"):
        retry_call(lambda: "never", base_delay=-1, sleep=lambda _: None)
