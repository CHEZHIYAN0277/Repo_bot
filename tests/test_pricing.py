import pytest

from shopcore.pricing import discounted_total


def test_percentage_discount_uses_subtotal():
    assert discounted_total(2_000, 25) == 1_500
    assert discounted_total(2_000, 0) == 2_000


def test_invalid_discount_is_rejected():
    with pytest.raises(ValueError):
        discounted_total(2_000, 101)
