from datetime import datetime, timedelta, timezone

from app.services.validation import validators


def test_missing_timestamps_detects_gaps():
    rows = [
        {"time": datetime(2023, 1, 1, tzinfo=timezone.utc)},
        {"time": datetime(2023, 1, 3, tzinfo=timezone.utc)},
    ]
    issues = validators.validate_missing_timestamps(1, rows, expected_interval=timedelta(days=1))
    assert len(issues) == 1
    assert issues[0]["issue_type"] == "missing_timestamp"


def test_non_monotonic_detects_out_of_order():
    rows = [
        {"time": datetime(2023, 1, 2, tzinfo=timezone.utc)},
        {"time": datetime(2023, 1, 1, tzinfo=timezone.utc)},
    ]
    issues = validators.validate_non_monotonic(1, rows)
    assert len(issues) == 1
    assert issues[0]["issue_type"] == "non_monotonic_timestamp"


def test_zero_negative_prices():
    rows = [{"time": datetime(2023, 1, 1, tzinfo=timezone.utc), "open": 1, "high": 2, "low": -1, "close": 1}]
    issues = validators.validate_zero_negative_prices(1, rows)
    assert len(issues) == 1
    assert issues[0]["issue_type"] == "invalid_price"

