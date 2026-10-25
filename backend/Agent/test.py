
from datetime import datetime, timedelta, timezone
from unittest.mock import patch

from .analysis_state import needs_analysis_refresh


NOW = datetime(2026, 10, 25, 12, 0, tzinfo=timezone.utc)


def test_no_analysis_state():
    with patch(
        "Agent.analysis_state.get_analysis_state",
        return_value=None,
    ):
        assert needs_analysis_refresh("test_user", NOW) is True


def test_no_successful_analysis():
    with patch(
        "Agent.analysis_state.get_analysis_state",
        return_value={"status": "failed"},
    ):
        assert needs_analysis_refresh("test_user", NOW) is True


def test_analysis_six_days_ago():
    with patch(
        "Agent.analysis_state.get_analysis_state",
        return_value={
            "last_successful_analysis_at": NOW - timedelta(days=6)
        },
    ):
        assert needs_analysis_refresh("test_user", NOW) is False


def test_analysis_exactly_seven_days_ago():
    with patch(
        "Agent.analysis_state.get_analysis_state",
        return_value={
            "last_successful_analysis_at": NOW - timedelta(days=7)
        },
    ):
        assert needs_analysis_refresh("test_user", NOW) is True


def test_analysis_ten_days_ago_but_latest_attempt_failed():
    with patch(
        "Agent.analysis_state.get_analysis_state",
        return_value={
            "last_successful_analysis_at": NOW - timedelta(days=10),
            "status": "failed",
        },
    ):
        assert needs_analysis_refresh("test_user", NOW) is True


def test_iso_formatted_timestamp():
    last_success = NOW - timedelta(days=6)

    with patch(
        "Agent.analysis_state.get_analysis_state",
        return_value={
            "last_successful_analysis_at": last_success.isoformat()
        },
    ):
        assert needs_analysis_refresh("test_user", NOW) is False


if __name__ == "__main__":
    tests = [
        test_no_analysis_state,
        test_no_successful_analysis,
        test_analysis_six_days_ago,
        test_analysis_exactly_seven_days_ago,
        test_analysis_ten_days_ago_but_latest_attempt_failed,
        test_iso_formatted_timestamp,
    ]

    for test in tests:
        test()
        print(f"PASS: {test.__name__}")

    print("\nAll analysis freshness tests passed.")
