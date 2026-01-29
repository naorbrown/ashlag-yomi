"""
Telegram command handlers for Ashlag Yomi.

Each handler corresponds to a bot command (e.g., /start, /today, /maamar).
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

from src.bot.formatters import (
    build_maamar_keyboard,
    format_maamar,
)
from src.bot.rate_limit import is_rate_limited
from src.data.maamar_repository import get_maamar_repository
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

    welcome_text = """🕯️ <b>אשלג יומי</b>

חכמת הקבלה היומית משושלת אשלג.

<b>פקודות:</b>
/maamar – קבל מאמר אקראי
/today – קבל את המאמר של היום
/about – למד על השושלת
/help – הצג את כל הפקודות

📅 מאמר חדש כל יום ב-6:00 בבוקר

<b>מקורות:</b>
📖 בעל הסולם - כתבי רבי יהודה אשלג
💎 הרב"ש - כתבי רבי ברוך שלום אשלג
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
    Handle /today command - send today's maamar.

    Sends a complete maamar from Baal Hasulam or Rabash.
    """
    if not update.effective_message:
        return

    if await _check_rate_limit(update):
        return

    settings = get_settings()

    try:
        # Use cached maamar repository for fast access
        repository = get_maamar_repository()
        daily = repository.get_daily_maamar(date.today())

        if not daily:
            await update.effective_message.reply_text(
                "😔 אין מאמרים זמינים.\nNo maamarim available."
            )
            return

        if settings.dry_run:
            logger.info(
                "dry_run_today",
                maamar_id=daily.maamar.id,
                title=daily.maamar.title,
            )
            await update.effective_message.reply_text(
                f"[DRY RUN] Would send maamar: {daily.maamar.title}"
            )
            return

        # Format the maamar (may be split into multiple messages)
        messages = format_maamar(daily.maamar, daily.date)
        keyboard = build_maamar_keyboard(daily.maamar)

        # Send each message
        for i, message in enumerate(messages):
            if i > 0:
                await asyncio.sleep(MESSAGE_DELAY)

            # Only add keyboard to the last message
            reply_markup = keyboard if i == len(messages) - 1 else None

            await update.effective_message.reply_text(
                message,
                parse_mode="HTML",
                reply_markup=reply_markup,
                disable_web_page_preview=True,
            )

        logger.info(
            "today_command",
            user_id=update.effective_user.id if update.effective_user else None,
            maamar_id=daily.maamar.id,
            message_count=len(messages),
        )

    except Exception as e:
        await _log_and_reply_error(update, "today", e)


async def maamar_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handle /maamar command - send a random maamar.

    Sends a complete random maamar from Baal Hasulam or Rabash.
    """
    if not update.effective_message:
        return

    if await _check_rate_limit(update):
        return

    try:
        # Use cached maamar repository for fast access
        repository = get_maamar_repository()
        maamar = repository.get_random_maamar()

        if not maamar:
            await update.effective_message.reply_text(
                "😔 אין מאמרים זמינים.\nNo maamarim available."
            )
            return

        # Format the maamar (may be split into multiple messages)
        messages = format_maamar(maamar)
        keyboard = build_maamar_keyboard(maamar)

        # Send each message
        for i, message in enumerate(messages):
            if i > 0:
                await asyncio.sleep(MESSAGE_DELAY)

            # Only add keyboard to the last message
            reply_markup = keyboard if i == len(messages) - 1 else None

            await update.effective_message.reply_text(
                message,
                parse_mode="HTML",
                reply_markup=reply_markup,
                disable_web_page_preview=True,
            )

        logger.info(
            "maamar_command",
            user_id=update.effective_user.id if update.effective_user else None,
            maamar_id=maamar.id,
            message_count=len(messages),
        )

    except Exception as e:
        await _log_and_reply_error(update, "maamar", e)


# Keep quote_command as alias for backward compatibility
async def quote_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handle /quote command - alias for /maamar.

    Kept for backward compatibility.
    """
    await maamar_command(update, context)


async def about_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /about command - explain the project and lineage."""
    if not update.effective_message:
        return

    if await _check_rate_limit(update):
        return

    about_text = """📚 <b>על אשלג יומי</b>

פרויקט זה נועד להפיץ את תורת הקבלה של שושלת אשלג - חכמה רוחנית מעמיקה לימינו.

<b>המקורות:</b>

📖 <b>בעל הסולם</b> (1884-1954)
רבי יהודה לייב הלוי אשלג
מחבר פירוש "הסולם" על ספר הזוהר, "תלמוד עשר הספירות", ומאמרים רבים בחכמת הקבלה.
הנגיש את חכמת הקבלה לדורנו בשפה ברורה ומדויקת.

💎 <b>הרב"ש</b> (1907-1991)
רבי ברוך שלום הלוי אשלג
בנו ותלמידו המובהק של בעל הסולם.
המשיך את דרכו של אביו וכתב מאות מאמרים בעבודה הפנימית.

<b>קישורים:</b>
• <a href="https://search.orhasulam.org/">אור הסולם - כתבי בעל הסולם</a>
• <a href="https://ashlagbaroch.org/rbsMore/">אשלג ברוך - כתבי הרב"ש</a>

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

    help_text = """<b>פקודות:</b>

/maamar – קבל מאמר אקראי מבעל הסולם או הרב"ש
/today – קבל את המאמר היומי
/about – למד על המקורות והשושלת
/feedback – שלח משוב

📅 מאמר חדש כל יום ב-6:00 בבוקר (שעון ישראל)

<b>Commands:</b>
/maamar – Get a random maamar
/today – Get today's maamar
/about – Learn about the sources
/feedback – Send feedback
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
