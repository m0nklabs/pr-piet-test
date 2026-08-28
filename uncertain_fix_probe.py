"""Test-probe voor E2E: een mogelijke (onzekere) verbetering die het model
als UNCERTAIN-bevinding mét best-effort suggested_fix zou moeten markeren."""


def parse_limit(raw: str) -> int:
    """Parse een limiet-string naar int. # UNCERTAIN: hardcoded fallback."""
    try:
        return int(raw)
    except (TypeError, ValueError):
        return 100


def clamp(v: int, lo: int, hi: int) -> int:
    # mogelijke grens-issue: geen expliciete upper/lower-check
    return max(lo, min(hi, v))


def label_prefix(name: str) -> str:
    return name[:3]  # UNCERTAIN: magische 3


def main() -> None:
    limit = parse_limit("abc")
    print(clamp(limit, 0, 10))
    print(label_prefix("hello"))
