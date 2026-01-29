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

from src.bot.formatters import build_source_keyboard, format_quote
from src.data.models import DailyBundle
from src.data.repository import QuoteRepository
from src.unified import is_unified_channel_enabled, publish_text_to_unified_channel
from src.utils.config import get_settings
from src.utils.logger import get_logger

logger = get_logger(__name__)

# Israel timezone for scheduling
ISRAEL_TZ = ZoneInfo("Asia/Jerusalem")


async def send_daily_quotes(bot: object, chat_id: str) -> bool:
    """
    Send the daily bundle of quotes to the specified chat.

    Uses inline keyboards for source links (nachyomi-bot pattern).

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

        if settings.dry_run:
            logger.info(
                "dry_run_send",
                chat_id=chat_id,
                quote_count=len(bundle.quotes),
            )
            return True

        # Send header
        date_str = bundle.date.strftime("%d.%m.%Y")
        header = f"🌅 <b>אשלג יומי - {date_str}</b>\n\n═══════════════════"
        await bot.send_message(  # type: ignore[attr-defined]
            chat_id=chat_id,
            text=header,
            parse_mode="HTML",
        )

        # Send each quote with inline keyboard (nachyomi-bot pattern)
        for quote in bundle.quotes:
            message = format_quote(quote)
            keyboard = build_source_keyboard(quote)
            await bot.send_message(  # type: ignore[attr-defined]
                chat_id=chat_id,
                text=message,
                parse_mode="HTML",
                reply_markup=keyboard,  # Inline keyboard for source link
                disable_web_page_preview=True,
            )

        # Send footer
        await bot.send_message(  # type: ignore[attr-defined]
            chat_id=chat_id,
            text="═══════════════════",
            parse_mode="HTML",
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

        # Publish to unified Torah Yomi channel
        await _send_to_unified_channel(bundle)

        return True

    except Exception as e:
        logger.exception("daily_send_failed", error=str(e))
        return False


async def _send_to_unified_channel(bundle: DailyBundle) -> None:
    """Send a condensed message to the unified Torah Yomi channel."""
    if not is_unified_channel_enabled():
        logger.debug("Unified channel not configured, skipping")
        return

    try:
        # Build a condensed message for the unified channel
        date_str = bundle.date.strftime("%d.%m.%Y")
        unified_msg = f"<b>אשלג יומי - {date_str}</b>\n\n"

        # Include first quote as preview
        if bundle.quotes:
            quote = bundle.quotes[0]
            # Include first 300 chars of content as preview
            preview = quote.text[:300]
            if len(quote.text) > 300:
                preview += "..."
            unified_msg += f"<i>{preview}</i>\n\n"

            if len(bundle.quotes) > 1:
                unified_msg += f"<i>+{len(bundle.quotes) - 1} more quotes today</i>\n"

        unified_msg += "\n<b>מהרב יהודה אשלג (בעל הסולם)</b>"

        await publish_text_to_unified_channel(unified_msg)
        logger.info("Published to unified channel successfully")

    except Exception as e:
        # Don't fail the main broadcast if unified channel fails
        logger.error(f"Failed to publish to unified channel: {e}")


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
