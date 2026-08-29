"""E2E: stale-review-failsafe test. Bewuste fout voor een finding+suggestie."""


def compute(weight: float, base: int) -> int:
    # Bewuste fout: verdubbelt onbedoeld (ontbrekende deling door 1/2)
    result = weight * 2 * base  # bug: mist factor-toepassing
    return int(result)
