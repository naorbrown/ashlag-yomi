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

# Signature line for messages
SIGNATURE = "\n\n🙏 <i>לזכות כל ישראל</i>"


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


def format_quote_html(quote: Dict[str, Any], rabbi_name: str) -> str:
    """Format a single quote for Telegram display using HTML."""
    text = quote.get("text", "")
    source = quote.get("source", "")
    source_url = quote.get("source_url", "")
    author = quote.get("author", rabbi_name)

    lines = [f"<b>📜 {author}</b>", "", text, ""]

    if source:
        if source_url:
            lines.append(f'📖 <a href="{source_url}">{source}</a>')
        else:
            lines.append(f"📖 <i>{source}</i>")

    return "\n".join(lines)


def format_welcome_message() -> str:
    """Format the welcome message."""
    return """🕎 <b>ברוכים הבאים לאשלג יומי!</b>

בכל יום בשעה 6:00 בבוקר (שעון ישראל) תקבלו שבעה ציטוטים מהמקורות הבאים:

• האר"י הקדוש
• הבעל שם טוב
• רבי שמחה בונים מפשיסחא
• רבי מנחם מנדל מקוצק
• בעל הסולם
• הרב"ש
• תלמידי קו אשלג

<b>פקודות:</b>
/today - קבל את הציטוטים של היום
/quote - קבל ציטוט אקראי
/about - אודות הבוט
/help - עזרה""" + SIGNATURE


def format_help_message() -> str:
    """Format the help message."""
    return """<b>עזרה</b>

<b>פקודות זמינות:</b>

/start - הרשמה לקבלת ציטוטים יומיים
/today - קבל את כל הציטוטים של היום
/quote - קבל ציטוט אקראי
/about - מידע אודות הבוט
/stop - ביטול מנוי

הציטוטים היומיים נשלחים בשעה 6:00 בבוקר (שעון ישראל).

לשאלות ובקשות: <a href="https://github.com/naorbrown/ashlag-yomi">GitHub</a>""" + SIGNATURE


def format_about_message() -> str:
    """Format the about message."""
    return """<b>אודות אשלג יומי</b>

בוט זה מפיץ חכמת הקבלה מקו אשלג ורבותיו הקדושים.

<b>בעל הסולם</b> (הרב יהודה אשלג, 1884-1954) חיבר את פירוש הסולם על ספר הזוהר והנגיש את חכמת הקבלה לכלל ישראל.

<b>הרב"ש</b> (הרב ברוך שלום אשלג, 1907-1991) המשיך את דרך אביו והרחיב את הלימוד.

<b>מקורות:</b>
• <a href="https://www.orhasulam.org/">אור הסולם</a>
• <a href="https://ashlagbaroch.com/">אשלג ברוך</a>
• <a href="https://www.kabbalahinfo.org/">קבלה אינפו</a>
• <a href="https://www.sefaria.org/">ספריא</a>

<b>קוד פתוח:</b>
<a href="https://github.com/naorbrown/ashlag-yomi">GitHub Repository</a>""" + SIGNATURE


def format_error_message() -> str:
    """Format an error message."""
    return """אירעה שגיאה בטעינת הציטוטים.
אנא נסה שוב מאוחר יותר.""" + SIGNATURE


def split_text(text: str, max_length: int = MAX_MESSAGE_LENGTH) -> List[str]:
    """Split text at word boundaries."""
    if len(text) <= max_length:
        return [text]

    parts = []
    current = ""

    for word in text.split():
        if len(current) + len(word) + 1 > max_length:
            if current:
                parts.append(current.strip())
            current = word
        else:
            current = f"{current} {word}" if current else word

    if current:
        parts.append(current.strip())

    return parts


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
        if not update.message:
            return

        chat_id = update.effective_chat.id
        self.subscribed_chats.add(chat_id)
        self._save_subscriptions()

        logger.info(f"New subscription from chat_id: {chat_id}")

        await update.message.reply_text(
            format_welcome_message(),
            parse_mode=ParseMode.HTML,
            disable_web_page_preview=True,
        )

    async def stop_command(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ) -> None:
        """Handle /stop command."""
        if not update.message:
            return

        chat_id = update.effective_chat.id

        if chat_id in self.subscribed_chats:
            self.subscribed_chats.discard(chat_id)
            self._save_subscriptions()
            logger.info(f"Unsubscribed chat_id: {chat_id}")

            await update.message.reply_text(
                "👋 הוסרת מרשימת התפוצה.\n\nשלח /start כדי להצטרף שוב." + SIGNATURE,
                parse_mode=ParseMode.HTML,
            )
        else:
            await update.message.reply_text(
                "אינך רשום כרגע.\n\nשלח /start כדי להצטרף." + SIGNATURE,
                parse_mode=ParseMode.HTML,
            )

    async def today_command(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ) -> None:
        """Handle /today command - send all daily quotes."""
        if not update.message:
            return

        logger.info(f"Today command from chat_id: {update.effective_chat.id}")

        try:
            await self._send_daily_quotes_to_chat(update.effective_chat.id)
        except Exception as e:
            logger.error(f"Error in today command: {e}")
            await update.message.reply_text(
                format_error_message(),
                parse_mode=ParseMode.HTML,
            )

    async def quote_command(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ) -> None:
        """Handle /quote command - send a random quote."""
        if not update.message:
            return

        logger.info(f"Quote command from chat_id: {update.effective_chat.id}")

        rabbi_keys = self.quotes_manager.get_all_rabbi_keys()
        if not rabbi_keys:
            await update.message.reply_text(
                format_error_message(),
                parse_mode=ParseMode.HTML,
            )
            return

        rabbi_key = random.choice(rabbi_keys)
        quote = self.quotes_manager.get_random_quote(rabbi_key)

        if quote:
            rabbi_name = self.quotes_manager.get_rabbi_display_name(rabbi_key)
            message = format_quote_html(quote, rabbi_name) + SIGNATURE
            await update.message.reply_text(
                message,
                parse_mode=ParseMode.HTML,
                disable_web_page_preview=True,
            )

    async def help_command(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ) -> None:
        """Handle /help command."""
        if not update.message:
            return

        logger.info(f"Help command from chat_id: {update.effective_chat.id}")

        await update.message.reply_text(
            format_help_message(),
            parse_mode=ParseMode.HTML,
            disable_web_page_preview=True,
        )

    async def about_command(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ) -> None:
        """Handle /about command."""
        if not update.message:
            return

        logger.info(f"About command from chat_id: {update.effective_chat.id}")

        await update.message.reply_text(
            format_about_message(),
            parse_mode=ParseMode.HTML,
            disable_web_page_preview=True,
        )

    async def test_command(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ) -> None:
        """Handle /test command - admin test functionality."""
        if not update.message:
            return

        admin_ids = os.environ.get("ADMIN_CHAT_IDS", "").split(",")
        chat_id = str(update.effective_chat.id)

        if admin_ids and admin_ids[0] and chat_id not in admin_ids:
            await update.message.reply_text(
                "⛔ פקודה זו זמינה למנהלים בלבד." + SIGNATURE,
                parse_mode=ParseMode.HTML,
            )
            return

        logger.info(f"Test command from admin chat_id: {chat_id}")

        # Test quote loading
        rabbi_keys = self.quotes_manager.get_all_rabbi_keys()
        status_lines = ["<b>📊 סטטוס מערכת</b>\n"]

        for rabbi_key in rabbi_keys:
            quotes = self.quotes_manager.quotes_cache.get(rabbi_key, [])
            rabbi_name = self.quotes_manager.get_rabbi_display_name(rabbi_key)
            status_lines.append(f"✅ {rabbi_name}: {len(quotes)} ציטוטים")

        status_lines.append(f"\n📬 מנויים: {len(self.subscribed_chats)}")
        status_lines.append(
            f"🕐 UTC: {datetime.now(timezone.utc).strftime('%H:%M:%S')}"
        )

        await update.message.reply_text(
            "\n".join(status_lines) + SIGNATURE,
            parse_mode=ParseMode.HTML,
        )

        # Send sample daily quotes
        await update.message.reply_text("📜 שולח ציטוטים לדוגמה...")
        await self._send_daily_quotes_to_chat(update.effective_chat.id)

    async def unknown_command(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ) -> None:
        """Handle unknown commands."""
        if not update.message:
            return

        await update.message.reply_text(
            "פקודה לא מוכרת. נסה /help לרשימת הפקודות." + SIGNATURE,
            parse_mode=ParseMode.HTML,
        )

    async def _send_daily_quotes_to_chat(self, chat_id: int) -> None:
        """Send daily quotes to a specific chat."""
        quotes = self.quotes_manager.get_daily_quotes()

        if not quotes:
            logger.error("No quotes available for daily sending")
            return

        # Send header
        header = (
            f"<b>🌅 אשלג יומי</b>\n"
            f"📅 {datetime.now().strftime('%d/%m/%Y')}\n"
            f"{'─' * 20}"
        )
        await self.application.bot.send_message(
            chat_id=chat_id,
            text=header,
            parse_mode=ParseMode.HTML,
        )

        # Send each quote as a separate message
        for quote in quotes:
            rabbi_name = quote.get("rabbi_name", "Unknown")
            message = format_quote_html(quote, rabbi_name)

            # Split if too long
            message_parts = split_text(message)
            for part in message_parts:
                try:
                    await self.application.bot.send_message(
                        chat_id=chat_id,
                        text=part,
                        parse_mode=ParseMode.HTML,
                        disable_web_page_preview=True,
                    )
                    await asyncio.sleep(0.3)  # Rate limiting
                except Exception as e:
                    logger.error(f"Error sending quote to {chat_id}: {e}")

        # Send footer
        footer = f"{'─' * 20}\n\n<i>שלח /quote לציטוט נוסף</i>" + SIGNATURE
        await self.application.bot.send_message(
            chat_id=chat_id,
            text=footer,
            parse_mode=ParseMode.HTML,
        )

    async def broadcast_daily_quotes(self) -> None:
        """Broadcast daily quotes to all subscribed chats."""
        logger.info(f"Broadcasting daily quotes to {len(self.subscribed_chats)} chats")

        for chat_id in list(self.subscribed_chats):
            try:
                await self._send_daily_quotes_to_chat(chat_id)
                logger.info(f"Sent daily quotes to chat_id: {chat_id}")
            except Exception as e:
                logger.error(f"Failed to send to chat_id {chat_id}: {e}")
                # Remove invalid chat IDs
                if "chat not found" in str(e).lower() or "blocked" in str(e).lower():
                    self.subscribed_chats.discard(chat_id)
                    self._save_subscriptions()

    async def setup_commands(self) -> None:
        """Set up bot commands for Telegram menu."""
        commands = [
            BotCommand("start", "הרשמה לציטוטים יומיים"),
            BotCommand("today", "ציטוטים של היום"),
            BotCommand("quote", "ציטוט אקראי"),
            BotCommand("help", "עזרה"),
            BotCommand("about", "אודות"),
            BotCommand("stop", "ביטול מנוי"),
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
