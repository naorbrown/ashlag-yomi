"""
Broadcaster for sending daily quotes to Telegram channel.

Sends 2 quotes daily (Baal Hasulam + Rabash) with:
- Title (source book + section)
- Full text
- Clickable source link
"""

import asyncio
from datetime import date

from telegram import Bot, InlineKeyboardButton, InlineKeyboardMarkup

from src.data.models import Quote
from src.data.quote_repository import get_quote_repository
from src.utils.config import get_settings
from src.utils.logger import get_logger

logger = get_logger(__name__)

# Delay between messages to avoid Telegram rate limits
MESSAGE_DELAY = 0.5


def format_quote_message(quote: Quote) -> str:
    """
    Format a quote for Telegram channel broadcast.

    Args:
        quote: The quote to format

    Returns:
        Formatted HTML string
    """
    # Build title from source book and section
    title_parts = []
    if quote.source_book:
        title_parts.append(quote.source_book)
    if quote.source_section:
        title_parts.append(quote.source_section)

    title = ", ".join(title_parts) if title_parts else quote.source_rabbi

    # Format the message
    parts = [
        f"📖 <b>{title}</b>",
        "",
        quote.text,
        "",
        f"— {quote.source_rabbi}",
    ]

    return "\n".join(parts)


def build_source_keyboard(quote: Quote) -> InlineKeyboardMarkup | None:
    """Build inline keyboard with source link."""
    if not quote.source_url:
        return None

    keyboard = [[InlineKeyboardButton(text="📖 מקור מלא", url=quote.source_url)]]
    return InlineKeyboardMarkup(keyboard)


async def broadcast_daily_quotes(
    target_date: date | None = None,
    *,
    dry_run: bool = False,
) -> bool:
    """
    Broadcast today's quotes to the Telegram channel.

    Sends 2 quotes (Baal Hasulam + Rabash) with source links.

    Args:
        target_date: Date to broadcast for. Defaults to today.
        dry_run: If True, don't actually send messages, just log.

    Returns:
        True if broadcast was successful, False otherwise.
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

    # Get today's quotes
    repository = get_quote_repository()
    quotes = repository.get_daily_quotes(target_date)

    if not quotes:
        logger.warning("no_quotes_available_for_broadcast", date=str(target_date))
        return False

    logger.info(
        "broadcasting_daily_quotes",
        date=str(target_date),
        quote_count=len(quotes),
        dry_run=dry_run or settings.dry_run,
    )

    if dry_run or settings.dry_run:
        for quote in quotes:
            logger.info(
                "would_send_quote",
                quote_id=quote.id,
                source=quote.source_rabbi,
                book=quote.source_book,
                section=quote.source_section,
            )
        return True

    # Actually send to Telegram
    try:
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

        # Send each quote
        for quote in quotes:
            message = format_quote_message(quote)
            keyboard = build_source_keyboard(quote)

            await bot.send_message(
                chat_id=channel_id,
                text=message,
                parse_mode="HTML",
                reply_markup=keyboard,
                disable_web_page_preview=True,
            )

            logger.info(
                "sent_quote",
                quote_id=quote.id,
                source=quote.source_rabbi,
            )
            await asyncio.sleep(MESSAGE_DELAY)

        # Send footer
        await bot.send_message(
            chat_id=channel_id,
            text="═══════════════════",
            parse_mode="HTML",
        )

        logger.info("broadcast_complete", quote_count=len(quotes))
        return True

    except Exception as e:
        logger.error("broadcast_failed", error=str(e))
        return False


# Backward compatibility alias
broadcast_daily_maamarim = broadcast_daily_quotes


# CLI entry point for GitHub Actions
if __name__ == "__main__":
    import sys

    from src.utils.logger import setup_logging

    setup_logging()

    dry = "--dry-run" in sys.argv or "-n" in sys.argv

    success = asyncio.run(broadcast_daily_quotes(dry_run=dry))
    sys.exit(0 if success else 1)
