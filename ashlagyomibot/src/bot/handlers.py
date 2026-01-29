"""
Telegram command handlers for Ashlag Yomi.

Handlers:
- /start - Welcome message with brief explanation
- /today - Send today's 2 quotes (Baal Hasulam + Rabash)

Each quote displays:
- Title (source book + section)
- Full Hebrew text
- Clickable source link
"""

import asyncio
from datetime import date

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes

from src.data.models import Quote
from src.data.quote_repository import get_quote_repository
from src.utils.config import get_settings
from src.utils.logger import get_logger

logger = get_logger(__name__)

# Delay between sending messages to avoid Telegram rate limits
MESSAGE_DELAY = 0.1


def format_quote_message(quote: Quote) -> str:
    """
    Format a quote for Telegram display.

    Shows:
    - Title: source_book, source_section
    - Full text
    - Source attribution

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
    """
    Build inline keyboard with source link button.

    Args:
        quote: The quote to build a keyboard for

    Returns:
        InlineKeyboardMarkup with source button, or None if no URL
    """
    if not quote.source_url:
        return None

    keyboard = [[InlineKeyboardButton(text="📖 מקור מלא", url=quote.source_url)]]
    return InlineKeyboardMarkup(keyboard)


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handle /start command - welcome new users.

    This is the first message users see when they start the bot.
    """
    if not update.effective_message:
        return

    welcome_text = """🕯️ <b>אשלג יומי</b>

ציטוטים יומיים מבעל הסולם והרב"ש.

/today - קבלו את הציטוטים של היום

📅 כל יום ב-6:00 בבוקר
"""

    await update.effective_message.reply_text(
        welcome_text,
        parse_mode="HTML",
    )

    logger.info(
        "start_command",
        user_id=update.effective_user.id if update.effective_user else None,
    )


async def today_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handle /today command - send today's 2 quotes.

    Sends one quote from Baal Hasulam and one from Rabash.
    Each quote shows: title, full text, and clickable source link.
    """
    if not update.effective_message:
        return

    settings = get_settings()

    try:
        repository = get_quote_repository()
        quotes = repository.get_daily_quotes()

        if not quotes:
            await update.effective_message.reply_text("😔 אין ציטוטים זמינים כרגע.")
            return

        if settings.dry_run:
            titles = [f"{q.source_book}, {q.source_section}" for q in quotes]
            await update.effective_message.reply_text(
                f"[DRY RUN] Would send {len(quotes)} quotes: {titles}"
            )
            return

        # Send header
        date_str = date.today().strftime("%d.%m.%Y")
        header = f"🌅 <b>אשלג יומי - {date_str}</b>\n\n═══════════════════"
        await update.effective_message.reply_text(header, parse_mode="HTML")

        # Send each quote with source link button
        for quote in quotes:
            await asyncio.sleep(MESSAGE_DELAY)

            message = format_quote_message(quote)
            keyboard = build_source_keyboard(quote)

            await update.effective_message.reply_text(
                message,
                parse_mode="HTML",
                reply_markup=keyboard,
                disable_web_page_preview=True,
            )

        # Send footer
        await asyncio.sleep(MESSAGE_DELAY)
        await update.effective_message.reply_text("═══════════════════")

        logger.info(
            "today_command",
            user_id=update.effective_user.id if update.effective_user else None,
            quote_count=len(quotes),
        )

    except Exception as e:
        logger.error(
            "today_command_error",
            error=str(e),
            user_id=update.effective_user.id if update.effective_user else None,
        )
        await update.effective_message.reply_text("😔 אירעה שגיאה. נסו שוב מאוחר יותר.")
