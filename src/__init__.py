"""
Ashlag Yomi - Daily Spiritual Quotes

Telegram bot that sends daily inspirational quotes
from Jewish spiritual leaders at 6:00 AM Israel time.
"""

__version__ = "2.0.0"

from .quote_manager import QuoteManager
from .telegram_bot import AshlagYomiBot

__all__ = ["QuoteManager", "AshlagYomiBot"]
