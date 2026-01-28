#!/usr/bin/env python3
"""
Manual bot testing script.

Use this to test the bot locally before deploying.
Sends a test message to verify everything works.

Usage:
    python scripts/test_bot.py
"""

import asyncio
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from telegram import Bot

from src.bot.formatters import format_quote, format_single_quote_message
from src.data.models import Quote, QuoteCategory
from src.utils.config import get_settings
from src.utils.logger import get_logger, setup_logging


async def test_connection() -> bool:
    """Test basic connection to Telegram API."""
    settings = get_settings()
    bot = Bot(token=settings.telegram_bot_token.get_secret_value())

    try:
        me = await bot.get_me()
        print(f"✅ Connected to bot: @{me.username}")
        return True
    except Exception as e:
        print(f"❌ Failed to connect: {e}")
        return False


async def send_test_message() -> bool:
    """Send a test message to the configured channel."""
    settings = get_settings()
    bot = Bot(token=settings.telegram_bot_token.get_secret_value())

    # Create a test quote
    test_quote = Quote(
        id="test-001",
        text="זוהי הודעת בדיקה מבוט אשלג יומי. אם אתם רואים הודעה זו, הבוט עובד כראוי!",
        source_rabbi="מערכת הבדיקות",
        source_url="https://github.com/yourusername/ashlag-yomi",
        category=QuoteCategory.BAAL_HASULAM,
        tags=["test"],
        length_estimate=10,
    )

    message = format_single_quote_message(test_quote)

    try:
        if settings.dry_run:
            print(f"[DRY RUN] Would send:\n{message}")
            return True

        await bot.send_message(
            chat_id=settings.telegram_chat_id,
            text=message,
            parse_mode="Markdown",
            disable_web_page_preview=True,
        )
        print(f"✅ Test message sent to {settings.telegram_chat_id}")
        return True
    except Exception as e:
        print(f"❌ Failed to send: {e}")
        return False


async def main() -> int:
    """Run all tests."""
    setup_logging()
    logger = get_logger(__name__)

    print("\n🧪 Ashlag Yomi Bot Test Suite\n")
    print("=" * 40)

    # Test 1: Connection
    print("\n📡 Test 1: API Connection")
    if not await test_connection():
        return 1

    # Test 2: Send message
    print("\n📤 Test 2: Send Test Message")
    if not await send_test_message():
        return 1

    print("\n" + "=" * 40)
    print("✅ All tests passed!")
    print("\nNext steps:")
    print("  1. Check your Telegram channel for the test message")
    print("  2. Run 'make run' to start the bot in polling mode")
    print("  3. Test /start, /today, /about commands")

    return 0


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
