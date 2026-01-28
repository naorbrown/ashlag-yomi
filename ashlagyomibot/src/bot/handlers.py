"""
Telegram command handlers for Ashlag Yomi.

Each handler corresponds to a bot command (e.g., /start, /today).
Handlers should be:
- Async (uses await)
- Focused (one responsibility)
- Graceful (handle errors without crashing)
"""

from datetime import date

from telegram import Update
from telegram.ext import ContextTypes

from src.bot.formatters import format_daily_bundle, format_quote
from src.data.repository import QuoteRepository
from src.utils.config import get_settings
from src.utils.logger import get_logger

logger = get_logger(__name__)


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handle /start command - welcome new users.

    This is the first message users see when they start the bot.
    """
    if not update.effective_message:
        return

    welcome_text = """🕯️ *ברוכים הבאים לאשלג יומי*

מדי יום נשלח אליכם ציטוט מתוך שושלת החכמה של אשלג:

• *האר״י הקדוש* - יסודות הקבלה הלוריאנית
• *הבעל שם טוב* - מייסד החסידות
• *רבי שמחה בונים מפשיסחא*
• *הרבי מקוצק*
• *בעל הסולם* - רבי יהודה אשלג
• *הרב״ש* - רבי ברוך שלום אשלג
• *התלמידים*

📖 הציטוטים נשלחים בכל בוקר בשעה 6:00 (שעון ישראל)

*פקודות זמינות:*
/today - קבלו את הציטוט של היום
/about - על הפרויקט
/help - עזרה

_״אין אור גדול יותר מהאור היוצא מתוך החושך״_
"""

    await update.effective_message.reply_text(
        welcome_text,
        parse_mode="Markdown",
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

    settings = get_settings()

    try:
        repository = QuoteRepository()
        bundle = repository.get_daily_bundle(date.today())

        if not bundle.quotes:
            await update.effective_message.reply_text(
                "😔 אין ציטוטים זמינים כרגע. אנא נסו שוב מאוחר יותר."
            )
            return

        # Send each quote as a separate message for better readability
        messages = format_daily_bundle(bundle)

        if settings.dry_run:
            logger.info("dry_run_today", message_count=len(messages))
            await update.effective_message.reply_text(
                f"[DRY RUN] Would send {len(messages)} messages"
            )
            return

        for message in messages:
            await update.effective_message.reply_text(
                message,
                parse_mode="Markdown",
                disable_web_page_preview=True,
            )

        logger.info(
            "today_command",
            user_id=update.effective_user.id if update.effective_user else None,
            quote_count=len(bundle.quotes),
        )

    except Exception as e:
        logger.error("today_command_error", error=str(e))
        await update.effective_message.reply_text(
            "😔 אירעה שגיאה. אנא נסו שוב מאוחר יותר."
        )


async def about_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /about command - explain the project and lineage."""
    if not update.effective_message:
        return

    about_text = """📚 *על אשלג יומי*

פרויקט זה נועד להפיץ את תורת הקבלה של שושלת אשלג - קו ישיר של חכמה רוחנית מהאר״י הקדוש ועד ימינו.

*השושלת:*

🕯️ *האר״י הקדוש* (1534-1572)
רבי יצחק לוריא אשכנזי - אבי הקבלה הלוריאנית

🕯️ *הבעל שם טוב* (1698-1760)
רבי ישראל בן אליעזר - מייסד תנועת החסידות

🕯️ *רבי שמחה בונים* (1765-1827)
מפשיסחא - מנהיג בית החסידות של פשיסחא

🕯️ *הרבי מקוצק* (1787-1859)
רבי מנחם מנדל מורגנשטרן - ידוע באמת הבלתי מתפשרת שלו

🕯️ *בעל הסולם* (1884-1954)
רבי יהודה אשלג - מחבר פירוש הסולם על הזוהר

🕯️ *הרב״ש* (1907-1991)
רבי ברוך שלום אשלג - בנו ותלמידו של בעל הסולם

🕯️ *התלמידים*
ממשיכי הדרך בדורנו

*קישורים:*
• [אור הסולם](https://www.orhassulam.com/)
• [ספריא](https://www.sefaria.org/)

_קוד פתוח - נבנה באהבה_
"""

    await update.effective_message.reply_text(
        about_text,
        parse_mode="Markdown",
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

    help_text = """📋 *פקודות זמינות:*

/start - הודעת פתיחה
/today - קבלו את הציטוטים של היום
/about - על הפרויקט ושושלת אשלג
/help - הצגת הודעה זו
/feedback - שליחת משוב

📖 *ציטוטים יומיים:*
הציטוטים נשלחים אוטומטית בכל בוקר בשעה 6:00 (שעון ישראל)

❓ *שאלות?*
השתמשו ב-/feedback לשליחת שאלות או הצעות
"""

    await update.effective_message.reply_text(
        help_text,
        parse_mode="Markdown",
    )

    logger.info(
        "help_command",
        user_id=update.effective_user.id if update.effective_user else None,
    )


async def feedback_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /feedback command - explain how to send feedback."""
    if not update.effective_message:
        return

    feedback_text = """💬 *משוב והצעות*

אנו שמחים לשמוע מכם!

📧 לשליחת משוב, באגים, או הצעות:
פתחו Issue ב-GitHub:
https://github.com/yourusername/ashlag-yomi/issues

או שלחו הודעה עם תוכן המשוב שלכם.

תודה על העזרה בשיפור הפרויקט! 🙏
"""

    await update.effective_message.reply_text(
        feedback_text,
        parse_mode="Markdown",
        disable_web_page_preview=True,
    )

    logger.info(
        "feedback_command",
        user_id=update.effective_user.id if update.effective_user else None,
    )
