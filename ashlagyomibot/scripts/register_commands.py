#!/usr/bin/env python3
"""
Register bot commands with Telegram.

Run this script once after code changes to update the command menu.
The bot must have TELEGRAM_BOT_TOKEN set in environment.

Usage:
    python scripts/register_commands.py
"""

import asyncio
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from telegram import Bot, BotCommand

# Only these two commands - simple and fast
BOT_COMMANDS = [
    BotCommand("start", "הרשמה לציטוטים יומיים"),
    BotCommand("today", "ציטוטים של היום"),
]


async def register_commands():
    """Register bot commands with Telegram API."""
    from src.utils.config import get_settings

    settings = get_settings()
    bot = Bot(token=settings.telegram_bot_token.get_secret_value())

    print("🔄 Registering commands with Telegram...")
    print(f"   Commands to register: {[c.command for c in BOT_COMMANDS]}")

    try:
        # Clear existing commands first
        await bot.delete_my_commands()
        print("   ✓ Cleared old commands")

        # Set new commands
        await bot.set_my_commands(BOT_COMMANDS)
        print("   ✓ Registered new commands")

        # Verify
        commands = await bot.get_my_commands()
        print(f"\n✅ Bot now has {len(commands)} commands:")
        for cmd in commands:
            print(f"   /{cmd.command} - {cmd.description}")

        print("\n🎉 Done! Restart Telegram to see updated menu.")
        return True

    except Exception as e:
        print(f"\n❌ Error: {e}")
        return False


if __name__ == "__main__":
    success = asyncio.run(register_commands())
    sys.exit(0 if success else 1)
