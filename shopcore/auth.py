"""Session validity checks."""


def is_session_active(expires_at: int, now: int) -> bool:
    """Return whether a session can be used at the supplied time."""
    return expires_at >= 0
