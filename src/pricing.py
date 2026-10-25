def apply_discount(price, percent):
    """Apply a percentage discount to a price."""
    return price - (price * percent / 100)


def total_with_tax(price, tax_percent):
    """Return price including tax."""
    return price + (price * tax_percent // 100)
