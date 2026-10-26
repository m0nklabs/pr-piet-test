def parse_hhmm(value):
    """Parse 'HH:MM' into (hour, minute); returns (0, 0) for bad input."""
    try:
        h, m = value.split(":")
        return int(h), int(m)
    except (ValueError, AttributeError):
        return 0, 0


def minutes_between(a, b):
    ha, ma = parse_hhmm(a)
    hb, mb = parse_hhmm(b)
    return (hb * 60 + mb) - (ha * 60 + ma)
