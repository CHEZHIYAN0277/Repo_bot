from shopcore.inventory import stock_after_reservation


def test_overselling_is_rejected_but_exact_stock_is_allowed():
    assert stock_after_reservation(3, 4) is None
    assert stock_after_reservation(3, 3) == 0


def test_zero_quantity_is_rejected():
    assert stock_after_reservation(3, 0) is None
