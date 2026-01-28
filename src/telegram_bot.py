"""
Telegram Bot Module
Handles all Telegram bot interactions and commands.

Standard Telegram Bot Commands (following best practices):
- /start - Initialize bot, show welcome message
- /help - Show all available commands
- /today - Get today's quotes (primary daily command)
- /daily - Alias for /today (backwards compatibility)
- /quote - Get a single random quote
- /stats - Show statistics
- /about - About the bot and sources
- /quality - Explain quote selection algorithm
"""

import os
import logging
from typing import Optional
import asyncio
from datetime import date

from telegram import Update, BotCommand
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)
from telegram.constants import ParseMode
from telegram.error import TelegramError

from .quote_manager import QuoteManager

logger = logging.getLogger(__name__)


class AshlagYomiBot:
    """Telegram bot for daily Ashlag quotes."""
    
    def __init__(self, token: str, chat_id: Optional[str] = None):
        """Initialize the bot.
        
        Args:
            token: Telegram bot token from BotFather
            chat_id: Optional default chat ID for scheduled messages
        """
        self.token = token
        self.chat_id = chat_id
        self.quote_manager = QuoteManager()
        self.application: Optional[Application] = None
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle the /start command."""
        rtl = "\u200F"
        welcome_message = f"""
{rtl}🌟 *ברוכים הבאים לאשלג יומי!*

{rtl}בוט זה שולח ציטוטים יומיים מגדולי ישראל:
• האר״י הקדוש
• הבעל שם טוב
• רבי שמחה בונים מפשיסחא
• הרבי מקוצק
• בעל הסולם
• הרב״ש
• תלמידי קו אשלג

{rtl}*פקודות זמינות:*
/today - הציטוטים של היום
/quote - ציטוט אקראי
/stats - סטטיסטיקות
/about - אודות הבוט
/quality - איך נבחרים הציטוטים
/help - עזרה

{rtl}💫 יום מבורך!
"""
        await update.message.reply_text(
            welcome_message,
            parse_mode=ParseMode.MARKDOWN
        )
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle the /help command."""
        rtl = "\u200F"
        help_text = f"""
{rtl}📚 *עזרה - אשלג יומי*

{rtl}*פקודות:*
/start - התחלה והסבר על הבוט
/today - הציטוטים של היום ⭐
/quote - ציטוט אקראי
/stats - סטטיסטיקות
/about - אודות הבוט והמקורות
/quality - הסבר על אלגוריתם הבחירה
/help - הצג הודעה זו

{rtl}*אודות:*
{rtl}הציטוטים נשלחים אוטומטית כל יום בשעה 6:00 בבוקר (שעון ישראל).

{rtl}כל הציטוטים כוללים קישור למקור המקורי.

{rtl}*קישורים שימושיים:*
• [Sefaria](https://www.sefaria.org/)
• [Kabbalah.info](https://www.kabbalah.info/)
• [Chabad.org](https://www.chabad.org/)

{rtl}🙏 לתיקון עולם
"""
        await update.message.reply_text(
            help_text,
            parse_mode=ParseMode.MARKDOWN,
            disable_web_page_preview=True
        )
    
    async def quote_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle the /quote command - sends a random quote."""
        quote = self.quote_manager.get_random_quote()
        
        if quote:
            message = self.quote_manager.format_quote_message(quote)
            await update.message.reply_text(
                message,
                parse_mode=ParseMode.MARKDOWN,
                disable_web_page_preview=True
            )
        else:
            rtl = "\u200F"
            await update.message.reply_text(
                f"{rtl}❌ לא נמצאו ציטוטים. נסה שוב מאוחר יותר."
            )
    
    async def today_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle the /today command - sends all daily quotes (primary command)."""
        await self._send_daily_quotes_to_chat(update)

    async def daily_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle the /daily command - alias for /today."""
        await self._send_daily_quotes_to_chat(update)

    async def _send_daily_quotes_to_chat(self, update: Update) -> None:
        """Internal method to send daily quotes to a chat."""
        try:
            quotes = self.quote_manager.get_daily_quotes()

            if not quotes:
                rtl = "\u200F"
                await update.message.reply_text(
                    f"{rtl}❌ לא נמצאו ציטוטים להיום.",
                    parse_mode=ParseMode.MARKDOWN
                )
                return

            # Send header
            rtl = "\u200F"
            today = date.today()
            header = f"🌅 *{rtl}ציטוט יומי - {today.strftime('%d/%m/%Y')}*\n"
            header += f"{rtl}השראה מגדולי ישראל\n"
            header += f"{rtl}_{len(quotes)} ציטוטים מ-{len(quotes)} מקורות_"
            await update.message.reply_text(header, parse_mode=ParseMode.MARKDOWN)

            # Send each quote separately for better readability
            for quote in quotes:
                quote_msg = self.quote_manager.format_quote_message(quote)
                await update.message.reply_text(
                    quote_msg,
                    parse_mode=ParseMode.MARKDOWN,
                    disable_web_page_preview=True
                )
                await asyncio.sleep(0.3)  # Avoid rate limiting

            # Send footer
            footer = f"{rtl}━━━━━━━━━━━━━━━━━━━━\n{rtl}💫 יום מבורך!"
            await update.message.reply_text(footer)

        except TelegramError as e:
            logger.error(f"Telegram error in today_command: {e}")
            await update.message.reply_text("❌ Error sending quotes. Please try again.")

    async def about_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle the /about command - information about the bot."""
        rtl = "\u200F"
        stats = self.quote_manager.get_stats()

        about_text = f"""
{rtl}📖 *אודות אשלג יומי*

{rtl}בוט זה מביא ציטוטים יומיים מגדולי הקבלה והחסידות.

{rtl}*המקורות:*
• האר״י הקדוש (המאה ה-16)
• הבעל שם טוב (1698-1760)
• רבי שמחה בונים מפשיסחא (1765-1827)
• הרבי מקוצק (1787-1859)
• בעל הסולם - רבי יהודה אשלג (1885-1954)
• הרב״ש - רבי ברוך שלום אשלג (1907-1991)
• תלמידי קו אשלג

{rtl}*מאגר הציטוטים:*
{rtl}סה״כ {stats['total']} ציטוטים מאומתים

{rtl}*מקורות אקדמיים:*
• [Sefaria](https://www.sefaria.org/) - ספריית טקסטים יהודיים
• [Kabbalah.info](https://www.kabbalah.info/) - מכון בני ברוך
• [Chabad.org](https://www.chabad.org/) - ספריית חב״ד

{rtl}*קוד פתוח:*
[GitHub](https://github.com/naorbrown/ashlag-yomi)

{rtl}🙏 לתיקון עולם
"""
        await update.message.reply_text(
            about_text,
            parse_mode=ParseMode.MARKDOWN,
            disable_web_page_preview=True
        )

    async def quality_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle the /quality command - explain quote selection algorithm."""
        explanation = self.quote_manager.get_selection_explanation()
        await update.message.reply_text(
            explanation,
            parse_mode=ParseMode.MARKDOWN,
            disable_web_page_preview=True
        )
    
    async def stats_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle the /stats command."""
        stats = self.quote_manager.get_stats()
        rtl = "\u200F"
        
        stats_message = f"{rtl}📊 *סטטיסטיקות ציטוטים*\n\n"
        
        source_names = {
            "arizal": "האר״י הקדוש",
            "baal_shem_tov": "הבעל שם טוב",
            "simcha_bunim": "רבי שמחה בונים",
            "kotzker": "הרבי מקוצק",
            "baal_hasulam": "בעל הסולם",
            "rabash": "הרב״ש",
            "ashlag_talmidim": "תלמידי קו אשלג"
        }
        
        for source, count in stats["by_source"].items():
            display_name = source_names.get(source, source)
            stats_message += f"• {rtl}{display_name}: {count} ציטוטים\n"
        
        stats_message += f"\n{rtl}*סה״כ: {stats['total']} ציטוטים*"
        
        await update.message.reply_text(
            stats_message,
            parse_mode=ParseMode.MARKDOWN
        )
    
    async def unknown_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle unknown commands."""
        rtl = "\u200F"
        await update.message.reply_text(
            f"{rtl}❓ פקודה לא מוכרת. השתמש ב-/help לרשימת הפקודות."
        )
    
    async def send_daily_quotes(self, chat_id: Optional[str] = None) -> bool:
        """Send daily quotes to a specific chat.
        
        Args:
            chat_id: Target chat ID. Uses default if not specified.
            
        Returns:
            True if message was sent successfully.
        """
        target_chat = chat_id or self.chat_id
        
        if not target_chat:
            logger.error("No chat ID provided for daily quotes")
            return False
        
        try:
            message = self.quote_manager.format_daily_message()
            quotes = self.quote_manager.get_daily_quotes()
            
            # Build the application if not already built
            if self.application is None:
                self.application = Application.builder().token(self.token).build()
            
            # Initialize the application
            await self.application.initialize()
            
            # Split if message is too long
            if len(message) > 4000:
                rtl = "\u200F"
                from datetime import date
                today = date.today()
                header = f"🌅 *{rtl}ציטוט יומי - {today.strftime('%d/%m/%Y')}*\n"
                header += f"{rtl}השראה מגדולי ישראל"
                await self.application.bot.send_message(
                    chat_id=target_chat,
                    text=header,
                    parse_mode=ParseMode.MARKDOWN
                )
                
                for quote in quotes:
                    quote_msg = self.quote_manager.format_quote_message(quote)
                    await self.application.bot.send_message(
                        chat_id=target_chat,
                        text=quote_msg,
                        parse_mode=ParseMode.MARKDOWN,
                        disable_web_page_preview=True
                    )
                    await asyncio.sleep(0.5)
            else:
                await self.application.bot.send_message(
                    chat_id=target_chat,
                    text=message,
                    parse_mode=ParseMode.MARKDOWN,
                    disable_web_page_preview=True
                )
            
            logger.info(f"Daily quotes sent successfully to {target_chat}")
            return True
            
        except Exception as e:
            logger.error(f"Error sending daily quotes: {e}")
            return False
        finally:
            if self.application:
                await self.application.shutdown()
    
    async def setup_commands(self) -> None:
        """Set up bot commands in Telegram menu."""
        commands = [
            BotCommand("today", "הציטוטים של היום"),
            BotCommand("quote", "ציטוט אקראי"),
            BotCommand("stats", "סטטיסטיקות"),
            BotCommand("about", "אודות הבוט"),
            BotCommand("quality", "איך נבחרים הציטוטים"),
            BotCommand("help", "עזרה"),
        ]
        try:
            await self.application.bot.set_my_commands(commands)
            logger.info("Bot commands registered successfully")
        except TelegramError as e:
            logger.error(f"Failed to set bot commands: {e}")
    
    def run(self) -> None:
        """Run the bot in polling mode."""
        self.application = Application.builder().token(self.token).build()

        # Register command handlers (order matters - specific before general)
        self.application.add_handler(CommandHandler("start", self.start_command))
        self.application.add_handler(CommandHandler("help", self.help_command))
        self.application.add_handler(CommandHandler("today", self.today_command))
        self.application.add_handler(CommandHandler("daily", self.daily_command))  # Alias
        self.application.add_handler(CommandHandler("quote", self.quote_command))
        self.application.add_handler(CommandHandler("stats", self.stats_command))
        self.application.add_handler(CommandHandler("about", self.about_command))
        self.application.add_handler(CommandHandler("quality", self.quality_command))

        # Handle unknown commands (must be last)
        self.application.add_handler(
            MessageHandler(filters.COMMAND, self.unknown_command)
        )

        # Set up commands menu in Telegram
        self.application.post_init = self.setup_commands

        # Add error handler
        self.application.add_error_handler(self._error_handler)

        logger.info("Starting bot in polling mode...")
        self.application.run_polling(allowed_updates=Update.ALL_TYPES)

    async def _error_handler(self, update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle errors in the bot."""
        logger.error(f"Exception while handling an update: {context.error}")

        if update and isinstance(update, Update) and update.effective_message:
            rtl = "\u200F"
            await update.effective_message.reply_text(
                f"{rtl}❌ אירעה שגיאה. אנא נסה שוב."
            )


def create_bot() -> AshlagYomiBot:
    """Create a bot instance from environment variables.
    
    Returns:
        Configured AshlagYomiBot instance.
    
    Raises:
        ValueError: If required environment variables are not set.
    """
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    if not token:
        raise ValueError("TELEGRAM_BOT_TOKEN environment variable is required")
    
    chat_id = os.environ.get("TELEGRAM_CHAT_ID")
    
    return AshlagYomiBot(token=token, chat_id=chat_id)
