"""Small text helpers used by the test app."""

import re


def slugify(text):
    """Return a URL-safe slug for *text*.

    The text is lowercased, every run of characters that are neither
    letters nor digits is collapsed into a single hyphen, and leading
    and trailing hyphens are stripped.

    >>> slugify("Hello, PR-Piet World!")
    'hello-pr-piet-world'
    """
    slug = re.sub(r"[^a-z0-9]+", "-", text.strip().lower())
    return slug.strip("-")
