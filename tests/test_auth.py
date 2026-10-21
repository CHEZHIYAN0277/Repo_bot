from shopcore.auth import is_session_active


def test_expired_session_rejected():
    now = 1_700_000_000
    assert is_session_active(now - 1, now) is False
    assert is_session_active(now, now) is False
    assert is_session_active(now + 1, now) is True


def test_future_session_remains_active():
    assert is_session_active(150, 100) is True
