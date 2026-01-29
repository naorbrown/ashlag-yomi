"""
Scheduling utilities for daily maamar delivery.

Note: In production, we use GitHub Actions cron jobs instead of
APScheduler. This module is primarily for local development and testing.

Why GitHub Actions over APScheduler for production?
1. Free tier handles our needs
2. No need for persistent server
3. Built-in logging and monitoring
4. Simpler deployment (no long-running process)
"""

import asyncio
from datetime import date
from zoneinfo import ZoneInfo

from src.bot.formatters import build_maamar_keyboard, format_maamar
from src.data.maamar_repository import get_maamar_repository
from src.utils.config import get_settings
from src.utils.logger import get_logger

logger = get_logger(__name__)

# Israel timezone for scheduling
ISRAEL_TZ = ZoneInfo("Asia/Jerusalem")

# Delay between messages to avoid Telegram rate limits
MESSAGE_DELAY = 0.5


async def send_daily_maamarim(bot: object, chat_id: str) -> bool:
    """
    Send today's 2 maamarim (Baal Hasulam + Rabash) to the specified chat.

    Uses inline keyboards for source links.

    Args:
        bot: Telegram bot instance
        chat_id: Target chat/channel ID

    Returns:
        True if successful, False otherwise
    """
    settings = get_settings()

    try:
        # Use cached repository for fast access
        repository = get_maamar_repository()
        maamarim = repository.get_daily_maamarim()

        if not maamarim:
            logger.warning("no_maamarim_for_daily_send")
            return False

        if settings.dry_run:
            titles = [m.title for m in maamarim]
            logger.info(
                "dry_run_send",
                chat_id=chat_id,
                maamar_count=len(maamarim),
                titles=titles,
            )
            return True

        # Send header
        date_str = date.today().strftime("%d.%m.%Y")
        header = f"🌅 <b>אשלג יומי - {date_str}</b>\n\n═══════════════════"
        await bot.send_message(  # type: ignore[attr-defined]
            chat_id=chat_id,
            text=header,
            parse_mode="HTML",
        )
        await asyncio.sleep(MESSAGE_DELAY)

        # Send each maamar with inline keyboard
        for maamar in maamarim:
            messages = format_maamar(maamar)
            keyboard = build_maamar_keyboard(maamar)

            for i, message in enumerate(messages):
                reply_markup = keyboard if i == len(messages) - 1 else None
                await bot.send_message(  # type: ignore[attr-defined]
                    chat_id=chat_id,
                    text=message,
                    parse_mode="HTML",
                    reply_markup=reply_markup,
                    disable_web_page_preview=True,
                )
                await asyncio.sleep(MESSAGE_DELAY)

            # Mark as sent for fair rotation
            repository.mark_as_sent(maamar, date.today())

        # Send footer
        await bot.send_message(  # type: ignore[attr-defined]
            chat_id=chat_id,
            text="═══════════════════",
        )

        logger.info(
            "daily_maamarim_sent",
            chat_id=chat_id,
            maamar_count=len(maamarim),
            date=str(date.today()),
        )

        return True

    except Exception as e:
        logger.exception("daily_send_failed", error=str(e))
        return False


# Backward compatibility alias
async def send_daily_quotes(bot: object, chat_id: str) -> bool:
    """Alias for send_daily_maamarim (backward compatibility)."""
    return await send_daily_maamarim(bot, chat_id)


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
