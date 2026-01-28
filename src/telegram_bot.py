"""
Telegram Bot Module
Handles all Telegram bot interactions and commands.
"""

import os
import logging
from typing import Optional
import asyncio

from telegram import Update, BotCommand
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)
from telegram.constants import ParseMode

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
/quote - ציטוט אקראי
/daily - הציטוטים של היום
/stats - סטטיסטיקות
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
/quote - קבל ציטוט אקראי
/daily - קבל את כל הציטוטים של היום
/stats - צפה בסטטיסטיקות הציטוטים
/help - הצג הודעה זו

{rtl}*אודות:*
{rtl}הציטוטים נשלחים אוטומטית כל יום בשעה 6:00 בבוקר (שעון ישראל).

{rtl}כל הציטוטים כוללים קישור למקור המקורי.

{rtl}*קישורים שימושיים:*
• [Sefaria](https://www.sefaria.org/)
• [Kabbalah.info](https://www.kabbalah.info/)

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
    
    async def daily_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle the /daily command - sends all daily quotes."""
        message = self.quote_manager.format_daily_message()
        
        # Split message if too long (Telegram limit is 4096 characters)
        if len(message) > 4000:
            quotes = self.quote_manager.get_daily_quotes()
            
            # Send header
            rtl = "\u200F"
            from datetime import date
            today = date.today()
            header = f"🌅 *{rtl}ציטוט יומי - {today.strftime('%d/%m/%Y')}*\n"
            header += f"{rtl}השראה מגדולי ישראל"
            await update.message.reply_text(header, parse_mode=ParseMode.MARKDOWN)
            
            # Send each quote separately
            for quote in quotes:
                quote_msg = self.quote_manager.format_quote_message(quote)
                await update.message.reply_text(
                    quote_msg,
                    parse_mode=ParseMode.MARKDOWN,
                    disable_web_page_preview=True
                )
                await asyncio.sleep(0.5)  # Avoid rate limiting
        else:
            await update.message.reply_text(
                message,
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
        """Set up bot commands in Telegram."""
        commands = [
            BotCommand("start", "התחלה והסבר על הבוט"),
            BotCommand("quote", "ציטוט אקראי"),
            BotCommand("daily", "הציטוטים של היום"),
            BotCommand("stats", "סטטיסטיקות"),
            BotCommand("help", "עזרה"),
        ]
        await self.application.bot.set_my_commands(commands)
    
    def run(self) -> None:
        """Run the bot in polling mode."""
        self.application = Application.builder().token(self.token).build()
        
        # Register handlers
        self.application.add_handler(CommandHandler("start", self.start_command))
        self.application.add_handler(CommandHandler("help", self.help_command))
        self.application.add_handler(CommandHandler("quote", self.quote_command))
        self.application.add_handler(CommandHandler("daily", self.daily_command))
        self.application.add_handler(CommandHandler("stats", self.stats_command))
        
        # Handle unknown commands
        self.application.add_handler(
            MessageHandler(filters.COMMAND, self.unknown_command)
        )
        
        # Set up commands in Telegram
        self.application.post_init = self.setup_commands
        
        logger.info("Starting bot in polling mode...")
        self.application.run_polling(allowed_updates=Update.ALL_TYPES)


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
