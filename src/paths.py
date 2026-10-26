def join_path(base, *parts):
    """Join path parts onto a base, dropping empty segments."""
    segments = [p for p in (base, *parts) if p]
    return "/".join(s.strip("/") for s in segments if s.strip("/"))


def file_ext(name):
    """Extension without the dot; empty for no extension."""
    return name.rsplit(".", 1)[1] if "." in name.rsplit("/", 1)[-1] else ""
