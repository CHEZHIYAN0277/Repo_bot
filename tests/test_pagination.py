import pytest

from shopcore.pagination import page_items


def test_first_and_second_pages_have_correct_items():
    items = [10, 20, 30, 40, 50]
    assert page_items(items, 1, 2) == [10, 20]
    assert page_items(items, 2, 2) == [30, 40]


def test_invalid_page_is_rejected():
    with pytest.raises(ValueError):
        page_items([10, 20], 0, 2)
