import pytest

from track_site import filter_new_entries


@pytest.mark.parametrize("new_entries, expected", [
    (["a", "b", "d", "c"], ["d"]),
    (["a", "b", "d"], ["d"]),  # c is missing, but it doesn't matter
    (["new1", "a", "b", "new2", "c", "d"], ["new1", "new2", "d"]),
    (["new1", "a", "d", "b", "new2", "c", "d"], ["new1", "d", "new2", "d"]),
])
def test_new_filter(new_entries, expected):
    old_entries = ["a", "b", "c"]
    assert filter_new_entries(old_entries, new_entries) == expected
