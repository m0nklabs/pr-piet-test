def latch(state, event):
    """SR-latch: set dominates until reset."""
    if event == "set":
        return "on"
    if event == "reset" and state == "on":
        return "off"
    return state


def debounce(signal, seen):
    """Return the new debounced state (edge-triggered)."""
    return signal if signal != seen else seen
