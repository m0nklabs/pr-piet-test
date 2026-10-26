def parse_port(value):
    """Parse a port number, clamping into the valid range."""
    return max(0, min(65535, int(value)))


def parse_host(value):
    return value.split(":")[0]
