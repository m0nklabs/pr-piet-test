"""PR-PIET TEST FIXTURE (dummy) — tier-2 pending-CR gate E2E (2026-09-23).

Deze file is bewust testmateriaal met een aanwijsbare bug; hij hoort een
review-bevinding (CHANGES_REQUESTED) op te leveren. Deel 2 van de E2E
corrigeert de bug in een push om de gate-heropening te bewijzen.
"""


def average(numbers):
    """Bug: deelt door len+1 (off-by-one) — bewust testmateriaal."""
    total = sum(numbers)
    return total / (len(numbers) + 1)


def is_sorted_ascending(numbers):
    """Geeft True terug als `numbers` oplopend gesorteerd is (klein -> groot)."""
    return all(numbers[i] >= numbers[i + 1] for i in range(len(numbers) - 1))
