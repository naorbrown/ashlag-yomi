"""
Telegram Bot Module - Daily Quote Sender

Sends scheduled daily quotes from Jewish spiritual leaders.
Runs via GitHub Actions at 6:00 AM Israel time.
"""

import logging
import asyncio
from datetime import date
from typing import Optional

from telegram import Bot
from telegram.constants import ParseMode
from telegram.error import TelegramError

from .quote_manager import QuoteManager

logger = logging.getLogger(__name__)


class AshlagYomiBot:
    """Telegram bot for sending daily Ashlag quotes."""

    def __init__(self, token: str, chat_id: str):
        """Initialize the bot.

        Args:
            token: Telegram bot token from BotFather
            chat_id: Target chat/channel ID for messages
        """
        self.token = token
        self.chat_id = chat_id
        self.quote_manager = QuoteManager()
        self._bot: Optional[Bot] = None

    @property
    def bot(self) -> Bot:
        """Lazy-load the Bot instance."""
        if self._bot is None:
            self._bot = Bot(token=self.token)
        return self._bot

    async def send_daily_quotes(self) -> bool:
        """Send the daily quote collection to the configured chat.

        Returns:
            True if all messages were sent successfully.
        """
        try:
            quotes = self.quote_manager.get_daily_quotes()

            if not quotes:
                logger.error("No quotes available for today")
                return False

            # Send header
            header = self._format_header(len(quotes))
            await self._send_message(header)
            await asyncio.sleep(0.5)

            # Send each quote
            for i, quote in enumerate(quotes):
                message = self.quote_manager.format_quote_message(quote)
                await self._send_message(message, disable_preview=True)

                # Rate limiting: small delay between messages
                if i < len(quotes) - 1:
                    await asyncio.sleep(0.5)

            # Send footer
            footer = self._format_footer()
            await self._send_message(footer)

            logger.info(f"Successfully sent {len(quotes)} quotes to {self.chat_id}")
            return True

        except TelegramError as e:
            logger.error(f"Telegram API error: {e}")
            return False
        except Exception as e:
            logger.exception(f"Unexpected error sending quotes: {e}")
            return False

    async def _send_message(
        self,
        text: str,
        disable_preview: bool = False
    ) -> None:
        """Send a message to the configured chat.

        Args:
            text: Message text (Markdown formatted)
            disable_preview: Whether to disable link previews
        """
        await self.bot.send_message(
            chat_id=self.chat_id,
            text=text,
            parse_mode=ParseMode.MARKDOWN,
            disable_web_page_preview=disable_preview
        )

    def _format_header(self, quote_count: int) -> str:
        """Format the daily message header.

        Args:
            quote_count: Number of quotes being sent

        Returns:
            Formatted header string
        """
        rtl = "\u200F"
        today = date.today()

        return (
            f"{rtl}*אשלג יומי*\n"
            f"{rtl}_{today.strftime('%d/%m/%Y')}_\n\n"
            f"{rtl}השראה יומית מגדולי ישראל"
        )

    def _format_footer(self) -> str:
        """Format the daily message footer.

        Returns:
            Formatted footer string
        """
        rtl = "\u200F"
        return f"{rtl}יום מבורך"
