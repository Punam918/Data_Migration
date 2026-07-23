import pandas as pd

from migration_platform.quality.checks import check_min_rows, check_null_rate, check_unique_key


def test_check_min_rows() -> None:
    frame = pd.DataFrame({"a": [1, 2, 3]})
    result = check_min_rows(frame, minimum=2)
    assert result.passed is True


def test_check_null_rate_fails() -> None:
    frame = pd.DataFrame({"a": [1, None, None]})
    result = check_null_rate(frame, "a", max_null_rate=0.5)
    assert result.passed is False


def test_check_unique_key_fails_on_duplicates() -> None:
    frame = pd.DataFrame({"id": [1, 1, 2], "x": [5, 6, 7]})
    result = check_unique_key(frame, ["id"])
    assert result.passed is False
