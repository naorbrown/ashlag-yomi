"""
Scheduling utilities for daily quote delivery.

Note: In production, we use GitHub Actions cron jobs instead of
APScheduler. This module is primarily for local development and testing.

Why GitHub Actions over APScheduler for production?
1. Free tier handles our needs
2. No need for persistent server
3. Built-in logging and monitoring
4. Simpler deployment (no long-running process)
"""

from datetime import date
from zoneinfo import ZoneInfo

from src.bot.formatters import format_daily_bundle
from src.data.repository import QuoteRepository
from src.utils.config import get_settings
from src.utils.logger import get_logger

logger = get_logger(__name__)

# Israel timezone for scheduling
ISRAEL_TZ = ZoneInfo("Asia/Jerusalem")


async def send_daily_quotes(bot: object, chat_id: str) -> bool:
    """
    Send the daily bundle of quotes to the specified chat.

    Args:
        bot: Telegram bot instance
        chat_id: Target chat/channel ID

    Returns:
        True if successful, False otherwise
    """
    settings = get_settings()

    try:
        repository = QuoteRepository()
        bundle = repository.get_daily_bundle(date.today())

        if not bundle.quotes:
            logger.warning("no_quotes_for_daily_send")
            return False

        messages = format_daily_bundle(bundle)

        if settings.dry_run:
            logger.info(
                "dry_run_send",
                chat_id=chat_id,
                message_count=len(messages),
            )
            return True

        # Send each message
        for message in messages:
            await bot.send_message(  # type: ignore[attr-defined]
                chat_id=chat_id,
                text=message,
                parse_mode="Markdown",
                disable_web_page_preview=True,
            )

        # Mark quotes as sent
        for quote in bundle.quotes:
            repository.mark_as_sent(quote, date.today())

        logger.info(
            "daily_quotes_sent",
            chat_id=chat_id,
            quote_count=len(bundle.quotes),
            date=str(date.today()),
        )

        return True

    except Exception as e:
        logger.exception("daily_send_failed", error=str(e))
        return False


def get_next_send_time() -> str:
    """
    Calculate the next scheduled send time.

    Returns:
        ISO format string of next send time
    """
    from datetime import datetime, timedelta

    settings = get_settings()

    # Parse send time (HH:MM format)
    hour, minute = map(int, settings.daily_send_time.split(":"))

    # Get current time in Israel
    now = datetime.now(ISRAEL_TZ)

    # Calculate next send time
    next_send = now.replace(hour=hour, minute=minute, second=0, microsecond=0)

    # If already past today's time, schedule for tomorrow
    if next_send <= now:
        next_send += timedelta(days=1)

    return next_send.isoformat()
