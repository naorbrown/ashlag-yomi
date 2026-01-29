"""
Telegram command handlers for Ashlag Yomi.

Each handler corresponds to a bot command (e.g., /start, /today).
Handlers should be:
- Async (uses await)
- Focused (one responsibility)
- Graceful (handle errors without crashing)
"""

import asyncio
import traceback
from datetime import date

from telegram import Update
from telegram.ext import ContextTypes

from src.bot.formatters import build_source_keyboard, format_quote
from src.bot.rate_limit import is_rate_limited
from src.data.repository import get_repository
from src.utils.config import get_settings
from src.utils.logger import get_logger

logger = get_logger(__name__)

# Delay between sending messages to avoid Telegram rate limits (seconds)
# Telegram allows ~30 msg/sec for private chats, 0.05s is safe and fast
MESSAGE_DELAY = 0.05

# Rate limit message
RATE_LIMIT_MSG = "⏳ אנא המתינו מעט לפני שליחת פקודה נוספת.\nPlease wait before sending another command."


async def _log_and_reply_error(
    update: Update,
    command: str,
    error: Exception,
) -> None:
    """Log error with full traceback and send user-friendly message."""
    error_tb = traceback.format_exc()
    logger.error(
        f"{command}_error",
        error=str(error),
        error_type=type(error).__name__,
        traceback=error_tb,
        user_id=update.effective_user.id if update.effective_user else None,
    )

    # In development, show the actual error
    settings = get_settings()
    if settings.is_development:
        error_msg = f"❌ Error in /{command}:\n{type(error).__name__}: {error}"
    else:
        error_msg = "😔 Error. Please try again.\nאירעה שגיאה. נסו שוב."

    if update.effective_message:
        await update.effective_message.reply_text(error_msg)


async def _check_rate_limit(update: Update) -> bool:
    """
    Check if user is rate limited and send message if so.

    Returns True if rate limited (command should not proceed).
    """
    if not update.effective_user:
        return False

    if is_rate_limited(update.effective_user.id):
        if update.effective_message:
            await update.effective_message.reply_text(RATE_LIMIT_MSG)
        return True
    return False


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handle /start command - welcome new users.

    This is the first message users see when they start the bot.
    """
    if not update.effective_message:
        return

    if await _check_rate_limit(update):
        return

    welcome_text = """🕯️ <b>Ashlag Yomi</b>

Daily Kabbalistic wisdom from six spiritual lineages.

<b>Commands:</b>
/today – Get today's 6 quotes
/quote – Get a random quote
/about – Learn about the lineage
/help – Show all commands

📅 New quotes daily at 6:00 AM Israel time
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
    Handle /today command - send today's quotes immediately.

    Useful for testing or catching up on missed quotes.
    """
    if not update.effective_message:
        return

    if await _check_rate_limit(update):
        return

    settings = get_settings()

    try:
        # Use cached repository for fast access
        repository = get_repository()
        bundle = repository.get_daily_bundle(date.today())

        if not bundle.quotes:
            await update.effective_message.reply_text(
                "😔 No quotes available.\n אין ציטוטים זמינים."
            )
            return

        if settings.dry_run:
            logger.info("dry_run_today", quote_count=len(bundle.quotes))
            await update.effective_message.reply_text(
                f"[DRY RUN] Would send {len(bundle.quotes)} quotes"
            )
            return

        # Send header
        date_str = bundle.date.strftime("%d.%m.%Y")
        header = f"🌅 <b>אשלג יומי - {date_str}</b>\n\n═══════════════════"
        await update.effective_message.reply_text(
            header,
            parse_mode="HTML",
        )

        # Send each quote with its inline keyboard (nachyomi-bot pattern)
        # Add delay between messages to avoid Telegram rate limits
        for quote in bundle.quotes:
            await asyncio.sleep(MESSAGE_DELAY)

            message = format_quote(quote)
            keyboard = build_source_keyboard(quote)

            await update.effective_message.reply_text(
                message,
                parse_mode="HTML",
                reply_markup=keyboard,  # Inline keyboard for source link
                disable_web_page_preview=True,
            )

        # Send footer
        await asyncio.sleep(MESSAGE_DELAY)
        await update.effective_message.reply_text(
            "═══════════════════",
            parse_mode="HTML",
        )

        logger.info(
            "today_command",
            user_id=update.effective_user.id if update.effective_user else None,
            quote_count=len(bundle.quotes),
        )

    except Exception as e:
        await _log_and_reply_error(update, "today", e)


async def quote_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handle /quote command - send a single random quote.

    Quick way to get a taste of the content without the full daily bundle.
    """
    if not update.effective_message:
        return

    if await _check_rate_limit(update):
        return

    try:
        # Use cached repository for fast access
        repository = get_repository()
        quote = repository.get_random_quote()

        if not quote:
            await update.effective_message.reply_text(
                "😔 No quotes available.\n אין ציטוטים זמינים."
            )
            return

        message = format_quote(quote)
        keyboard = build_source_keyboard(quote)

        await update.effective_message.reply_text(
            message,
            parse_mode="HTML",
            reply_markup=keyboard,
            disable_web_page_preview=True,
        )

        logger.info(
            "quote_command",
            user_id=update.effective_user.id if update.effective_user else None,
            quote_id=quote.id,
        )

    except Exception as e:
        await _log_and_reply_error(update, "quote", e)


async def about_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /about command - explain the project and lineage."""
    if not update.effective_message:
        return

    if await _check_rate_limit(update):
        return

    about_text = """📚 <b>על אשלג יומי</b>

פרויקט זה נועד להפיץ את תורת הקבלה של שושלת אשלג - קו ישיר של חכמה רוחנית מהאר״י הקדוש ועד ימינו.

<b>השושלת:</b>

🕯️ <b>האר״י הקדוש</b> (1534-1572)
רבי יצחק לוריא אשכנזי - אבי הקבלה הלוריאנית

✨ <b>הבעל שם טוב</b> (1698-1760)
רבי ישראל בן אליעזר - מייסד תנועת החסידות

🔥 <b>חסידות פולין</b> (1700-1900)
המגיד ממזריטש, פשיסחא, קוצק ועוד

📖 <b>בעל הסולם</b> (1884-1954)
רבי יהודה אשלג - מחבר פירוש הסולם על הזוהר

💎 <b>הרב״ש</b> (1907-1991)
רבי ברוך שלום אשלג - בנו ותלמידו של בעל הסולם

🌱 <b>חסידי אשלג</b>
ממשיכי הדרך בדורנו

<b>קישורים:</b>
• <a href="https://www.orhassulam.com/">אור הסולם</a>
• <a href="https://www.sefaria.org/">ספריא</a>

<i>קוד פתוח - נבנה באהבה</i>
"""

    await update.effective_message.reply_text(
        about_text,
        parse_mode="HTML",
        disable_web_page_preview=True,
    )

    logger.info(
        "about_command",
        user_id=update.effective_user.id if update.effective_user else None,
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /help command - list available commands."""
    if not update.effective_message:
        return

    if await _check_rate_limit(update):
        return

    help_text = """<b>Commands:</b>

/today – Get today's 6 quotes
/quote – Get a random quote
/about – Learn about the lineage
/feedback – Send feedback

📅 New quotes daily at 6:00 AM Israel time
"""

    await update.effective_message.reply_text(
        help_text,
        parse_mode="HTML",
    )

    logger.info(
        "help_command",
        user_id=update.effective_user.id if update.effective_user else None,
    )


async def feedback_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /feedback command - explain how to send feedback."""
    if not update.effective_message:
        return

    if await _check_rate_limit(update):
        return

    feedback_text = """💬 <b>Feedback</b>

We'd love to hear from you!

📧 To send feedback, report bugs, or suggest features:
Open an issue on GitHub:
https://github.com/naorbrown/ashlag-yomi/issues

Thank you for helping improve the project! 🙏
"""

    await update.effective_message.reply_text(
        feedback_text,
        parse_mode="HTML",
        disable_web_page_preview=True,
    )

    logger.info(
        "feedback_command",
        user_id=update.effective_user.id if update.effective_user else None,
    )
