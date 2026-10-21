"""Checkout prices in integer cents."""


def discounted_total(subtotal_cents: int, discount_percent: int) -> int:
    """Return the total after a percentage discount."""
    if subtotal_cents < 0 or not 0 <= discount_percent <= 100:
        raise ValueError("invalid discount")
    return subtotal_cents - discount_percent
