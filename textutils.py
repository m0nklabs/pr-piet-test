"""Small text helpers used by the test app."""

import re


def slugify(text):
    """Return a URL-safe slug for ASCII *text*.

    The text is lowercased, every run of characters that are neither
    ASCII letters nor digits is collapsed into a single hyphen, and
    leading and trailing hyphens are stripped. Input is expected to be
    ASCII-only: non-ASCII letters are treated as separators by design.

    >>> slugify("Hello, PR-Piet World!")
    'hello-pr-piet-world'
    """
    slug = re.sub(r"[^a-z0-9]+", "-", text.strip().lower())
    return slug.strip("-")
