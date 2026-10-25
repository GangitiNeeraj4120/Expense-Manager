
from datetime import datetime, timedelta, timezone

from database.database import get_analysis_state


REFRESH_INTERVAL = timedelta(days=7)


def needs_analysis_refresh(
    user_id: str,
    now: datetime | None = None,
) -> bool:
    """
    Return True if the user has no successful analysis
    or the last successful analysis was at least 7 days ago.
    """
    state = get_analysis_state(user_id)

    if not state:
        return True

    last_success = state.get("last_successful_analysis_at")

    if last_success is None:
        return True

    # Support both datetime objects and ISO-formatted strings.
    if isinstance(last_success, str):
        last_success = datetime.fromisoformat(
            last_success.replace("Z", "+00:00")
        )

    if not isinstance(last_success, datetime):
        raise TypeError(
            "last_successful_analysis_at must be a datetime or ISO string"
        )

    # Treat naive datetimes as UTC.
    if last_success.tzinfo is None:
        last_success = last_success.replace(tzinfo=timezone.utc)

    if now is None:
        now = datetime.now(timezone.utc)
    elif now.tzinfo is None:
        now = now.replace(tzinfo=timezone.utc)

    return now - last_success >= REFRESH_INTERVAL
