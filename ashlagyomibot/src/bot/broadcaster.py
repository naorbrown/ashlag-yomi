"""
Channel broadcaster for daily quotes.

Handles:
- Sending daily quotes to the Telegram channel
- Random quote selection for variety
- Rate limiting and error handling
"""

import asyncio
import random
from datetime import date

from telegram import Bot

from src.bot.formatters import format_channel_message
from src.data.models import QuoteCategory
from src.data.repository import QuoteRepository
from src.utils.config import get_settings
from src.utils.logger import get_logger

logger = get_logger(__name__)


async def broadcast_daily_quote(
    target_date: date | None = None,
    *,
    dry_run: bool = False,
) -> bool:
    """
    Broadcast a single daily quote to the channel.

    Selects a random quote from a random category each day,
    ensuring variety and engagement.

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
        logger.warning("no_channel_configured", message="Set TELEGRAM_CHANNEL_ID to enable broadcasts")
        return False

    try:
        repository = QuoteRepository()

        # Select a random category, weighted toward core Ashlag teachers
        weighted_categories = [
            QuoteCategory.BAAL_HASULAM,  # Higher weight
            QuoteCategory.BAAL_HASULAM,
            QuoteCategory.RABASH,
            QuoteCategory.RABASH,
            QuoteCategory.ARIZAL,
            QuoteCategory.BAAL_SHEM_TOV,
            QuoteCategory.KOTZKER,
            QuoteCategory.SIMCHA_BUNIM,
            QuoteCategory.TALMIDIM,
        ]

        # Use day of year for deterministic but varied selection
        day_of_year = target_date.timetuple().tm_yday
        random.seed(day_of_year)  # Reproducible for same day
        category = random.choice(weighted_categories)

        # Get a random quote from this category (using fair rotation)
        sent_ids = repository.get_sent_ids_by_category(category)
        quote = repository.get_random_by_category(category, exclude_ids=sent_ids)

        if not quote:
            logger.error("no_quote_available", category=category.value)
            return False

        # Format the message
        message = format_channel_message(quote, target_date)

        if dry_run or settings.dry_run:
            logger.info(
                "dry_run_broadcast",
                channel=channel_id,
                category=category.value,
                quote_id=quote.id,
                message_preview=message[:100],
            )
            return True

        # Send to channel
        bot = Bot(token=settings.telegram_bot_token.get_secret_value())
        await bot.send_message(
            chat_id=channel_id,
            text=message,
            parse_mode="Markdown",
            disable_web_page_preview=True,
        )

        # Mark as sent for fair rotation
        repository.mark_as_sent(quote, target_date)

        logger.info(
            "broadcast_success",
            channel=channel_id,
            category=category.value,
            quote_id=quote.id,
            date=str(target_date),
        )

        return True

    except Exception as e:
        logger.error("broadcast_error", error=str(e))
        return False


async def broadcast_daily_bundle(
    target_date: date | None = None,
    *,
    dry_run: bool = False,
) -> bool:
    """
    Broadcast a full bundle of quotes (one from each category) to the channel.

    Alternative to single quote - for more comprehensive daily content.

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
        logger.warning("no_channel_configured")
        return False

    try:
        repository = QuoteRepository()
        bundle = repository.get_daily_bundle(target_date)

        if not bundle.quotes:
            logger.error("no_quotes_for_bundle")
            return False

        if dry_run or settings.dry_run:
            logger.info(
                "dry_run_bundle_broadcast",
                channel=channel_id,
                quote_count=len(bundle.quotes),
            )
            return True

        bot = Bot(token=settings.telegram_bot_token.get_secret_value())

        # Send header
        date_str = target_date.strftime("%d.%m.%Y")
        header = f"🌅 *אשלג יומי - {date_str}*\n\n═══════════════════"
        await bot.send_message(
            chat_id=channel_id,
            text=header,
            parse_mode="Markdown",
        )

        # Send each quote with a small delay
        for quote in bundle.quotes:
            message = format_channel_message(quote, target_date)
            await bot.send_message(
                chat_id=channel_id,
                text=message,
                parse_mode="Markdown",
                disable_web_page_preview=True,
            )
            repository.mark_as_sent(quote, target_date)
            await asyncio.sleep(1)  # Rate limiting

        logger.info(
            "bundle_broadcast_success",
            channel=channel_id,
            quote_count=len(bundle.quotes),
            date=str(target_date),
        )

        return True

    except Exception as e:
        logger.error("bundle_broadcast_error", error=str(e))
        return False


# CLI entry point for GitHub Actions
if __name__ == "__main__":
    import sys

    mode = sys.argv[1] if len(sys.argv) > 1 else "single"
    dry = "--dry-run" in sys.argv

    if mode == "bundle":
        success = asyncio.run(broadcast_daily_bundle(dry_run=dry))
    else:
        success = asyncio.run(broadcast_daily_quote(dry_run=dry))

    sys.exit(0 if success else 1)
