"""Stock reservation calculations."""


def stock_after_reservation(available: int, requested: int) -> int | None:
    """Return remaining stock, or None when the request cannot be fulfilled."""
    if available < 0 or requested <= 0:
        return None
    return available - requested
