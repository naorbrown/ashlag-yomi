#!/usr/bin/env python3
"""
Standalone script for sending daily quotes.
Used by GitHub Actions scheduler.
"""

import os
import sys
import logging
import asyncio

# Add src to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)


async def send_daily_quotes() -> bool:
    """Send daily quotes to the configured chat."""
    from src.telegram_bot import AshlagYomiBot
    
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    chat_id = os.environ.get("TELEGRAM_CHAT_ID")
    
    if not token:
        logger.error("TELEGRAM_BOT_TOKEN is not set")
        return False
    
    if not chat_id:
        logger.error("TELEGRAM_CHAT_ID is not set")
        return False
    
    bot = AshlagYomiBot(token=token, chat_id=chat_id)
    return await bot.send_daily_quotes()


def main() -> int:
    """Main entry point."""
    logger.info("Starting daily quote sender...")
    
    try:
        success = asyncio.run(send_daily_quotes())
        if success:
            logger.info("Daily quotes sent successfully!")
            return 0
        else:
            logger.error("Failed to send daily quotes")
            return 1
    except Exception as e:
        logger.exception(f"Error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
