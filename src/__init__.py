"""
Ashlag Yomi - Daily Spiritual Quotes Bot
A Telegram bot that sends daily inspirational quotes from great Jewish spiritual leaders.
"""

__version__ = "1.0.0"
__author__ = "Ashlag Yomi Contributors"

from .quote_manager import QuoteManager
from .telegram_bot import AshlagYomiBot, create_bot

__all__ = ["QuoteManager", "AshlagYomiBot", "create_bot", "__version__"]
