#!/usr/bin/env python3
"""
Send daily quotes to the Telegram channel.

This script is called by GitHub Actions cron job at 6am Israel time (3am UTC).
Can also be run manually for testing.

Usage:
    python scripts/send_daily.py

Environment Variables:
    TELEGRAM_BOT_TOKEN: Bot token from @BotFather
    TELEGRAM_CHAT_ID: Target channel/chat ID
    DRY_RUN: Set to "true" to log instead of sending (optional)
"""

import asyncio
import sys
from pathlib import Path

# Add project root to path for imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from telegram import Bot

from src.bot.scheduler import send_daily_quotes
from src.utils.config import get_settings
from src.utils.logger import get_logger, setup_logging


async def main() -> int:
    """Main entry point for the daily send script."""
    setup_logging()
    logger = get_logger(__name__)

    settings = get_settings()

    logger.info(
        "daily_send_starting",
        environment=settings.environment,
        dry_run=settings.dry_run,
    )

    # Create bot instance
    bot = Bot(token=settings.telegram_bot_token.get_secret_value())

    # Send the daily quotes
    success = await send_daily_quotes(bot, settings.telegram_chat_id)

    if success:
        logger.info("daily_send_completed")
        return 0
    else:
        logger.error("daily_send_failed")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
