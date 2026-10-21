"""One-based catalog pagination."""


def page_items(items: list[int], page: int, page_size: int) -> list[int]:
    """Return one page, with the first page numbered 1."""
    if page < 1 or page_size < 1:
        raise ValueError("page and page_size must be positive")
    start = page * page_size
    return items[start:start + page_size]
