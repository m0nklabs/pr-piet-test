"""Tests for pkg.format."""

import pytest

from pkg.format import clamp


@pytest.mark.parametrize(
    ("value", "expected"),
    [(-5, 0), (0, 0), (5, 5), (15, 10), (1000, 10)],
)
def test_clamp_bounds(value, expected):
    assert clamp(value, 0, 10) == expected


def test_clamp_rejects_inverted_bounds():
    with pytest.raises(ValueError, match="low must not exceed high"):
        clamp(5, 10, 0)
