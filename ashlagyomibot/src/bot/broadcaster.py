"""
Channel broadcaster for daily maamarim.

Handles:
- Sending daily maamarim to the Telegram channel
- One maamar from Baal Hasulam + one from Rabash
- Rate limiting and error handling
"""

import asyncio
from datetime import date

from telegram import Bot

from src.bot.formatters import build_maamar_keyboard, format_maamar
from src.data.maamar_repository import get_maamar_repository
from src.utils.config import get_settings
from src.utils.logger import get_logger

logger = get_logger(__name__)

# Delay between messages to avoid Telegram rate limits
MESSAGE_DELAY = 0.5


async def broadcast_daily_maamarim(
    target_date: date | None = None,
    *,
    dry_run: bool = False,
) -> bool:
    """
    Broadcast today's 2 maamarim (Baal Hasulam + Rabash) to the channel.

    Args:
        target_date: The date for this broadcast (defaults to today)
        dry_run: If True, log instead of sending

    Returns:
        True if successful, False otherwise
    """
    if target_date is None:
        target_date = date.today()

    settings = get_settings()
    channel_id = settings.telegram_channel_id

    if not channel_id:
        logger.warning(
            "no_channel_configured",
            message="Set TELEGRAM_CHANNEL_ID to enable broadcasts",
        )
        return False

    try:
        repository = get_maamar_repository()

        # Idempotency check - don't send twice in one day
        if repository.was_maamar_sent_today(target_date):
            logger.info("already_broadcast_today", date=str(target_date))
            return True

        # Get one maamar from each source
        maamarim = repository.get_daily_maamarim()

        if not maamarim:
            logger.error("no_maamarim_available")
            return False

        if dry_run or settings.dry_run:
            titles = [m.title for m in maamarim]
            logger.info(
                "dry_run_broadcast",
                channel=channel_id,
                maamar_count=len(maamarim),
                titles=titles,
            )
            return True

        bot = Bot(token=settings.telegram_bot_token.get_secret_value())

        # Send header
        date_str = target_date.strftime("%d.%m.%Y")
        header = f"🌅 <b>אשלג יומי - {date_str}</b>\n\n═══════════════════"
        await bot.send_message(
            chat_id=channel_id,
            text=header,
            parse_mode="HTML",
        )
        await asyncio.sleep(MESSAGE_DELAY)

        # Send each maamar
        for maamar in maamarim:
            messages = format_maamar(maamar)
            keyboard = build_maamar_keyboard(maamar)

            for i, message in enumerate(messages):
                reply_markup = keyboard if i == len(messages) - 1 else None
                await bot.send_message(
                    chat_id=channel_id,
                    text=message,
                    parse_mode="HTML",
                    reply_markup=reply_markup,
                    disable_web_page_preview=True,
                )
                await asyncio.sleep(MESSAGE_DELAY)

            # Mark as sent for fair rotation
            repository.mark_as_sent(maamar, target_date)

        # Send footer
        await bot.send_message(
            chat_id=channel_id,
            text="═══════════════════",
        )

        logger.info(
            "broadcast_success",
            channel=channel_id,
            maamar_count=len(maamarim),
            date=str(target_date),
        )

        return True

    except Exception as e:
        logger.error("broadcast_error", error=str(e), error_type=type(e).__name__)
        return False


# CLI entry point for GitHub Actions
if __name__ == "__main__":
    import sys

    dry = "--dry-run" in sys.argv

    success = asyncio.run(broadcast_daily_maamarim(dry_run=dry))

    sys.exit(0 if success else 1)
