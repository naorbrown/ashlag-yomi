#!/usr/bin/env python3
"""
Ashlag Yomi - Daily Kabbalistic Quotes Telegram Bot

A Telegram bot that sends daily inspirational quotes from the Ashlag lineage
and related Kabbalistic masters at 6:00 AM Israel time.

Authors: Cross-functional Team (UX, Engineering, QA, Security, DevOps)
License: MIT
"""

import os
import sys
import json
import random
import logging
import asyncio
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional, Dict, List, Any

from telegram import Update, BotCommand
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)
from telegram.constants import ParseMode

# Configure logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

# Constants
QUOTES_DIR = Path(__file__).parent.parent / "data" / "quotes"
MAX_MESSAGE_LENGTH = 4096  # Telegram message limit
ISRAEL_TZ_OFFSET = 2  # UTC+2 (standard), UTC+3 (DST)


class QuotesManager:
    """Manages loading and selecting quotes from the database."""

    def __init__(self, quotes_dir: Path):
        self.quotes_dir = quotes_dir
        self.quotes_cache: Dict[str, List[Dict[str, Any]]] = {}
        self.rabbis_metadata: Dict[str, Dict[str, str]] = {}
        self._load_quotes()

    def _load_quotes(self) -> None:
        """Load all quotes from JSON files."""
        if not self.quotes_dir.exists():
            logger.error(f"Quotes directory not found: {self.quotes_dir}")
            return

        # Load metadata
        metadata_file = self.quotes_dir / "metadata.json"
        if metadata_file.exists():
            with open(metadata_file, "r", encoding="utf-8") as f:
                self.rabbis_metadata = json.load(f)

        # Load quotes for each rabbi
        for quote_file in self.quotes_dir.glob("*.json"):
            if quote_file.name == "metadata.json":
                continue
            rabbi_key = quote_file.stem
            try:
                with open(quote_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.quotes_cache[rabbi_key] = data.get("quotes", [])
                    logger.info(
                        f"Loaded {len(self.quotes_cache[rabbi_key])} quotes for {rabbi_key}"
                    )
            except (json.JSONDecodeError, IOError) as e:
                logger.error(f"Error loading quotes from {quote_file}: {e}")

    def get_random_quote(self, rabbi_key: str) -> Optional[Dict[str, Any]]:
        """Get a random quote for a specific rabbi."""
        quotes = self.quotes_cache.get(rabbi_key, [])
        if not quotes:
            logger.warning(f"No quotes found for {rabbi_key}")
            return None
        return random.choice(quotes)

    def get_all_rabbi_keys(self) -> List[str]:
        """Get all available rabbi keys."""
        return list(self.quotes_cache.keys())

    def get_rabbi_display_name(self, rabbi_key: str) -> str:
        """Get the display name for a rabbi."""
        if rabbi_key in self.rabbis_metadata:
            return self.rabbis_metadata[rabbi_key].get("name_hebrew", rabbi_key)
        return rabbi_key

    def get_daily_quotes(self) -> List[Dict[str, Any]]:
        """Get daily quotes from all required rabbis."""
        required_rabbis = [
            "arizal",
            "baal_shem_tov",
            "simcha_bunim",
            "kotzker_rebbe",
            "baal_hasulam",
            "rabash",
            "ashlag_talmidim",
        ]

        daily_quotes = []
        for rabbi_key in required_rabbis:
            quote = self.get_random_quote(rabbi_key)
            if quote:
                quote["rabbi_key"] = rabbi_key
                quote["rabbi_name"] = self.get_rabbi_display_name(rabbi_key)
                daily_quotes.append(quote)

        return daily_quotes


def format_quote_message(quote: Dict[str, Any], rabbi_name: str) -> str:
    """Format a single quote for Telegram display."""
    text = quote.get("text", "")
    source = quote.get("source", "")
    source_url = quote.get("source_url", "")
    author = quote.get("author", rabbi_name)

    # Build the message
    lines = [
        f"📜 *{author}*",
        "",
        text,
        "",
    ]

    if source:
        if source_url:
            lines.append(f"📖 [מקור: {source}]({source_url})")
        else:
            lines.append(f"📖 מקור: {source}")

    return "\n".join(lines)


def split_long_message(message: str, max_length: int = MAX_MESSAGE_LENGTH) -> List[str]:
    """Split a message that exceeds Telegram's character limit."""
    if len(message) <= max_length:
        return [message]

    messages = []
    current = ""
    for line in message.split("\n"):
        if len(current) + len(line) + 1 > max_length:
            if current:
                messages.append(current.strip())
            current = line
        else:
            current = current + "\n" + line if current else line

    if current:
        messages.append(current.strip())

    return messages


class AshlagYomiBot:
    """Main bot class handling all Telegram interactions."""

    def __init__(self, token: str):
        self.token = token
        self.quotes_manager = QuotesManager(QUOTES_DIR)
        self.application: Optional[Application] = None
        self.subscribed_chats: set = set()
        self._load_subscriptions()

    def _get_subscriptions_file(self) -> Path:
        """Get path to subscriptions file."""
        return Path(__file__).parent.parent / "data" / "subscriptions.json"

    def _load_subscriptions(self) -> None:
        """Load subscribed chat IDs from file."""
        subs_file = self._get_subscriptions_file()
        if subs_file.exists():
            try:
                with open(subs_file, "r") as f:
                    data = json.load(f)
                    self.subscribed_chats = set(data.get("chat_ids", []))
                logger.info(f"Loaded {len(self.subscribed_chats)} subscriptions")
            except (json.JSONDecodeError, IOError) as e:
                logger.error(f"Error loading subscriptions: {e}")

    def _save_subscriptions(self) -> None:
        """Save subscribed chat IDs to file."""
        subs_file = self._get_subscriptions_file()
        subs_file.parent.mkdir(parents=True, exist_ok=True)
        try:
            with open(subs_file, "w") as f:
                json.dump({"chat_ids": list(self.subscribed_chats)}, f)
            logger.info(f"Saved {len(self.subscribed_chats)} subscriptions")
        except IOError as e:
            logger.error(f"Error saving subscriptions: {e}")

    async def start_command(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ) -> None:
        """Handle /start command."""
        chat_id = update.effective_chat.id
        self.subscribed_chats.add(chat_id)
        self._save_subscriptions()

        welcome_message = """
🕎 *ברוכים הבאים לאשלג יומי!*

Welcome to Ashlag Yomi - your daily dose of Kabbalistic wisdom!

כל יום בשעה 6:00 בבוקר (שעון ישראל) תקבלו ציטוטים מהמקורות הבאים:
Every day at 6:00 AM Israel time, you'll receive quotes from:

• האר"י הקדוש (The Arizal)
• הבעל שם טוב (Baal Shem Tov)
• רבי שמחה בונים מפשיסחא (Simcha Bunim)
• רבי מנחם מנדל מקוצק (Kotzker Rebbe)
• בעל הסולם (Baal Hasulam)
• הרב"ש (Rabash)
• תלמידי קו אשלג (Ashlag Lineage Students)

*פקודות זמינות / Available Commands:*
/today - קבל את הציטוטים של היום
/quote - קבל ציטוט אקראי
/help - עזרה
/about - אודות הבוט
/stop - הפסק מנוי

📚 כל הציטוטים מקושרים למקורותיהם המקוריים.
All quotes are linked to their original sources.
"""
        await update.message.reply_text(
            welcome_message, parse_mode=ParseMode.MARKDOWN
        )
        logger.info(f"New subscription from chat_id: {chat_id}")

    async def stop_command(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ) -> None:
        """Handle /stop command."""
        chat_id = update.effective_chat.id
        if chat_id in self.subscribed_chats:
            self.subscribed_chats.discard(chat_id)
            self._save_subscriptions()
            await update.message.reply_text(
                "👋 הוסרת מרשימת התפוצה. להתראות!\n"
                "You've been unsubscribed. Goodbye!\n\n"
                "שלח /start כדי להצטרף שוב.\n"
                "Send /start to rejoin."
            )
            logger.info(f"Unsubscribed chat_id: {chat_id}")
        else:
            await update.message.reply_text(
                "אינך רשום כרגע. שלח /start כדי להצטרף.\n"
                "You're not currently subscribed. Send /start to join."
            )

    async def today_command(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ) -> None:
        """Handle /today command - send all daily quotes."""
        await self._send_daily_quotes(update.effective_chat.id)

    async def quote_command(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ) -> None:
        """Handle /quote command - send a random quote."""
        rabbi_keys = self.quotes_manager.get_all_rabbi_keys()
        if not rabbi_keys:
            await update.message.reply_text(
                "❌ לא נמצאו ציטוטים. אנא נסה שוב מאוחר יותר.\n"
                "No quotes found. Please try again later."
            )
            return

        rabbi_key = random.choice(rabbi_keys)
        quote = self.quotes_manager.get_random_quote(rabbi_key)
        if quote:
            rabbi_name = self.quotes_manager.get_rabbi_display_name(rabbi_key)
            message = format_quote_message(quote, rabbi_name)
            await update.message.reply_text(
                message,
                parse_mode=ParseMode.MARKDOWN,
                disable_web_page_preview=True,
            )

    async def help_command(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ) -> None:
        """Handle /help command."""
        help_text = """
🔧 *עזרה / Help*

*פקודות זמינות / Available Commands:*

/start - הצטרף לקבלת ציטוטים יומיים
         Subscribe to daily quotes

/stop - הפסק את קבלת הציטוטים
        Unsubscribe from daily quotes

/today - קבל את כל הציטוטים של היום
         Get all today's quotes now

/quote - קבל ציטוט אקראי
         Get a random quote

/about - מידע אודות הבוט
         Information about this bot

/help - הצג הודעה זו
        Show this help message

/test - (מנהלים) בדיקת הבוט
        (Admin) Test the bot

📬 הציטוטים היומיים נשלחים ב-6:00 בבוקר (שעון ישראל)
Daily quotes are sent at 6:00 AM Israel time.
"""
        await update.message.reply_text(help_text, parse_mode=ParseMode.MARKDOWN)

    async def about_command(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ) -> None:
        """Handle /about command."""
        about_text = """
📖 *אודות אשלג יומי / About Ashlag Yomi*

בוט זה נועד להפיץ את חכמת הקבלה בקו אשלג ורבותיו הקדושים.
This bot spreads the wisdom of Kabbalah from the Ashlag lineage.

*מקורות הציטוטים / Quote Sources:*
• [אור הסולם](https://www.orhasulam.org/)
• [אשלג ברוך](https://ashlagbaroch.com/)
• [קבלה אינפו](https://www.kabbalahinfo.org/)
• [ספריא](https://www.sefaria.org/)

*קוד פתוח / Open Source:*
[GitHub Repository](https://github.com/naorbrown/ashlag-yomi)

*נבנה עם / Built with:*
Python, python-telegram-bot, GitHub Actions

*רישיון / License:* MIT

🙏 לזכות כל ישראל
"""
        await update.message.reply_text(
            about_text,
            parse_mode=ParseMode.MARKDOWN,
            disable_web_page_preview=True,
        )

    async def test_command(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ) -> None:
        """Handle /test command - admin test functionality."""
        admin_ids = os.environ.get("ADMIN_CHAT_IDS", "").split(",")
        chat_id = str(update.effective_chat.id)

        if admin_ids and admin_ids[0] and chat_id not in admin_ids:
            await update.message.reply_text(
                "⛔ פקודה זו זמינה למנהלים בלבד.\n"
                "This command is for admins only."
            )
            return

        await update.message.reply_text(
            "🔄 מתחיל בדיקת מערכת מלאה...\n"
            "Starting full system test..."
        )

        # Test quote loading
        rabbi_keys = self.quotes_manager.get_all_rabbi_keys()
        status_lines = ["*📊 סטטוס מערכת / System Status:*\n"]

        for rabbi_key in rabbi_keys:
            quotes = self.quotes_manager.quotes_cache.get(rabbi_key, [])
            rabbi_name = self.quotes_manager.get_rabbi_display_name(rabbi_key)
            status_lines.append(f"✅ {rabbi_name}: {len(quotes)} ציטוטים")

        status_lines.append(f"\n📬 מנויים פעילים: {len(self.subscribed_chats)}")
        status_lines.append(f"🕐 שעה נוכחית (UTC): {datetime.now(timezone.utc).strftime('%H:%M:%S')}")

        await update.message.reply_text(
            "\n".join(status_lines), parse_mode=ParseMode.MARKDOWN
        )

        # Send sample daily quotes
        await update.message.reply_text(
            "📜 שולח ציטוטים לדוגמה...\nSending sample quotes..."
        )
        await self._send_daily_quotes(update.effective_chat.id)

    async def _send_daily_quotes(self, chat_id: int) -> None:
        """Send daily quotes to a specific chat."""
        quotes = self.quotes_manager.get_daily_quotes()

        if not quotes:
            logger.error("No quotes available for daily sending")
            return

        # Send header
        header = (
            "🌅 *אשלג יומי - לימוד יומי בקבלה*\n"
            f"📅 {datetime.now().strftime('%d/%m/%Y')}\n"
            "─────────────────────"
        )
        await self.application.bot.send_message(
            chat_id=chat_id,
            text=header,
            parse_mode=ParseMode.MARKDOWN,
        )

        # Send each quote as a separate message
        for quote in quotes:
            rabbi_name = quote.get("rabbi_name", "Unknown")
            message = format_quote_message(quote, rabbi_name)

            # Split if too long
            message_parts = split_long_message(message)
            for part in message_parts:
                try:
                    await self.application.bot.send_message(
                        chat_id=chat_id,
                        text=part,
                        parse_mode=ParseMode.MARKDOWN,
                        disable_web_page_preview=True,
                    )
                    await asyncio.sleep(0.5)  # Rate limiting
                except Exception as e:
                    logger.error(f"Error sending quote to {chat_id}: {e}")

        # Send footer
        footer = (
            "─────────────────────\n"
            "🙏 יום טוב ומבורך!\n"
            "Have a blessed day!\n\n"
            "_שלח /quote לציטוט נוסף_"
        )
        await self.application.bot.send_message(
            chat_id=chat_id,
            text=footer,
            parse_mode=ParseMode.MARKDOWN,
        )

    async def broadcast_daily_quotes(self) -> None:
        """Broadcast daily quotes to all subscribed chats."""
        logger.info(f"Broadcasting daily quotes to {len(self.subscribed_chats)} chats")

        for chat_id in list(self.subscribed_chats):
            try:
                await self._send_daily_quotes(chat_id)
                logger.info(f"Sent daily quotes to chat_id: {chat_id}")
            except Exception as e:
                logger.error(f"Failed to send to chat_id {chat_id}: {e}")
                # Remove invalid chat IDs
                if "chat not found" in str(e).lower() or "blocked" in str(e).lower():
                    self.subscribed_chats.discard(chat_id)
                    self._save_subscriptions()

    async def unknown_command(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ) -> None:
        """Handle unknown commands."""
        await update.message.reply_text(
            "❓ פקודה לא מוכרת. שלח /help לרשימת הפקודות.\n"
            "Unknown command. Send /help for available commands."
        )

    async def setup_commands(self) -> None:
        """Set up bot commands for Telegram menu."""
        commands = [
            BotCommand("start", "הצטרף / Subscribe"),
            BotCommand("today", "ציטוטים של היום / Today's quotes"),
            BotCommand("quote", "ציטוט אקראי / Random quote"),
            BotCommand("help", "עזרה / Help"),
            BotCommand("about", "אודות / About"),
            BotCommand("stop", "הפסק מנוי / Unsubscribe"),
        ]
        await self.application.bot.set_my_commands(commands)
        logger.info("Bot commands registered successfully")

    def build(self) -> Application:
        """Build and configure the application."""
        self.application = Application.builder().token(self.token).build()

        # Add command handlers
        self.application.add_handler(CommandHandler("start", self.start_command))
        self.application.add_handler(CommandHandler("stop", self.stop_command))
        self.application.add_handler(CommandHandler("today", self.today_command))
        self.application.add_handler(CommandHandler("quote", self.quote_command))
        self.application.add_handler(CommandHandler("help", self.help_command))
        self.application.add_handler(CommandHandler("about", self.about_command))
        self.application.add_handler(CommandHandler("test", self.test_command))

        # Handle unknown commands
        self.application.add_handler(
            MessageHandler(filters.COMMAND, self.unknown_command)
        )

        return self.application

    async def run_polling(self) -> None:
        """Run the bot in polling mode."""
        self.build()
        await self.setup_commands()
        logger.info("Starting bot in polling mode...")
        await self.application.run_polling(drop_pending_updates=True)


async def send_scheduled_broadcast(token: str) -> None:
    """Send scheduled broadcast (called by GitHub Actions)."""
    bot = AshlagYomiBot(token)
    bot.build()

    async with bot.application:
        await bot.application.start()
        await bot.broadcast_daily_quotes()
        await bot.application.stop()


def main():
    """Main entry point."""
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    if not token:
        logger.error("TELEGRAM_BOT_TOKEN environment variable not set")
        sys.exit(1)

    # Check for broadcast mode (used by GitHub Actions)
    if len(sys.argv) > 1 and sys.argv[1] == "--broadcast":
        logger.info("Running in broadcast mode")
        asyncio.run(send_scheduled_broadcast(token))
    else:
        # Run in polling mode for development/testing
        bot = AshlagYomiBot(token)
        asyncio.run(bot.run_polling())


if __name__ == "__main__":
    main()
