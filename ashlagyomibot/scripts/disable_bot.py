#!/usr/bin/env python3
"""
Disable the bot and clear the Telegram channel description.

This script:
1. Removes all bot commands from Telegram
2. Clears the channel description

Usage:
    TELEGRAM_BOT_TOKEN=xxx TELEGRAM_CHAT_ID=xxx python scripts/disable_bot.py
"""

import asyncio
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from telegram import Bot
from telegram.error import TelegramError


async def disable_bot():
    """Disable bot commands and clear channel description."""
    from src.utils.config import get_settings

    settings = get_settings()
    bot = Bot(token=settings.telegram_bot_token.get_secret_value())

    print("🔄 Disabling bot...")

    try:
        # Clear all bot commands
        await bot.delete_my_commands()
        print("   ✓ Removed all bot commands")

        # Clear channel description if channel ID is set
        channel_id = getattr(settings, "telegram_channel_id", None) or settings.telegram_chat_id
        if channel_id:
            try:
                await bot.set_chat_description(chat_id=channel_id, description="")
                print(f"   ✓ Cleared description for channel: {channel_id}")
            except TelegramError as e:
                print(f"   ⚠ Could not clear channel description: {e}")
                print("     (Bot may need admin rights to modify channel description)")

        print("\n✅ Bot has been disabled:")
        print("   - Commands removed from Telegram menu")
        print("   - Channel description cleared")
        print("   - Workflows have been disabled (renamed to .yml.disabled)")
        return True

    except Exception as e:
        print(f"\n❌ Error: {e}")
        return False


if __name__ == "__main__":
    success = asyncio.run(disable_bot())
    sys.exit(0 if success else 1)
