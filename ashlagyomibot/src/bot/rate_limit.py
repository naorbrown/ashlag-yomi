"""
Rate limiting for Telegram bot commands.

Implements a sliding window rate limiter (nachyomi-bot pattern)
to prevent abuse and comply with Telegram API limits.
"""

from collections import defaultdict
from datetime import datetime, timedelta

# Rate limiting configuration
RATE_LIMIT = 5  # requests per window
RATE_WINDOW = timedelta(minutes=1)

# Storage for rate limit tracking (user_id -> list of timestamps)
_rate_limits: dict[int, list[datetime]] = defaultdict(list)


def is_rate_limited(user_id: int) -> bool:
    """
    Check if a user has exceeded the rate limit.

    Uses a sliding window approach:
    - Track timestamps of recent requests per user
    - Clean up old entries outside the window
    - Return True if limit exceeded

    Args:
        user_id: Telegram user ID

    Returns:
        True if rate limited, False otherwise
    """
    now = datetime.now()
    window_start = now - RATE_WINDOW

    # Filter to only recent requests within window
    recent = [t for t in _rate_limits[user_id] if t > window_start]
    _rate_limits[user_id] = recent

    if len(recent) >= RATE_LIMIT:
        return True

    # Add current request
    recent.append(now)
    _rate_limits[user_id] = recent

    # Cleanup old users (prevent memory leak)
    if len(_rate_limits) > 1000:
        for uid in list(_rate_limits.keys()):
            if not _rate_limits[uid]:
                del _rate_limits[uid]

    return False


def clear_rate_limits() -> None:
    """Clear all rate limits (useful for testing)."""
    _rate_limits.clear()
