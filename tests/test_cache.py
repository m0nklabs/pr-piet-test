"""Tests for pkg.cache."""

import asyncio

from pkg.cache import get_or_load


def test_get_or_load_returns_loaded_value():
    async def loader(key):
        return f"value-{key}"

    assert asyncio.run(get_or_load("a", loader)) == "value-a"
