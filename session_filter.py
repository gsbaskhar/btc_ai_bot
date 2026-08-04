from datetime import datetime, timezone
from config import LONDON_END_UTC, LONDON_START_UTC, NY_END_UTC, NY_START_UTC


def session_ok(now=None):
    """Return whether now falls in the configured UTC London/NY windows."""
    hour = (now or datetime.now(timezone.utc)).hour
    return LONDON_START_UTC <= hour <= LONDON_END_UTC or NY_START_UTC <= hour <= NY_END_UTC
