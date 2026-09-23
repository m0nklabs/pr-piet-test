"""PR-PIET TEST FIXTURE (dummy) — tier-2 pending-CR gate E2E.

Bug gefixt — deel 2 van de tier-2 pending-CR gate E2E: de fix-push
heropent de tier-2 gate.
"""


def average(numbers):
    """Bug gefixt — deelt door len() (was len+1) — bewust testmateriaal."""
    total = sum(numbers)
    return total / len(numbers)
