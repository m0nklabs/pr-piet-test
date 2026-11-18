"""Synthetic sandbox fixture; no product data or secrets."""


def greeting():
    return "clean synthetic fixture"


print(greeting())

# Intentional ERROR-severity match: verifies the findings gate, not product code.
print("SEMGREP_REUSABLE_DELIBERATE_ERROR")
