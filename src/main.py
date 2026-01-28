#!/usr/bin/env python3
"""
Main entry point for the Ashlag Yomi Telegram bot.
Can run in two modes:
1. Polling mode: Continuous operation, listening for commands
2. Scheduled mode: Send daily quotes and exit (for GitHub Actions)
"""

import os
import sys
import logging
import argparse
import asyncio

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)


def main() -> int:
    """Main entry point.
    
    Returns:
        Exit code (0 for success, 1 for error).
    """
    parser = argparse.ArgumentParser(
        description="Ashlag Yomi - Daily Spiritual Quotes Bot",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  Run in polling mode (interactive):
    python -m src.main --mode polling
    
  Send scheduled daily message:
    python -m src.main --mode scheduled
    
Environment Variables:
  TELEGRAM_BOT_TOKEN  - Required: Your Telegram bot token from BotFather
  TELEGRAM_CHAT_ID    - Required for scheduled mode: Target chat/channel ID
        """
    )
    
    parser.add_argument(
        "--mode",
        choices=["polling", "scheduled"],
        default="polling",
        help="Bot operation mode (default: polling)"
    )
    
    parser.add_argument(
        "--chat-id",
        help="Override TELEGRAM_CHAT_ID environment variable"
    )
    
    args = parser.parse_args()
    
    # Validate environment
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    if not token:
        logger.error("TELEGRAM_BOT_TOKEN environment variable is not set")
        return 1
    
    chat_id = args.chat_id or os.environ.get("TELEGRAM_CHAT_ID")
    
    if args.mode == "scheduled" and not chat_id:
        logger.error("TELEGRAM_CHAT_ID is required for scheduled mode")
        return 1
    
    try:
        from .telegram_bot import AshlagYomiBot
        
        bot = AshlagYomiBot(token=token, chat_id=chat_id)
        
        if args.mode == "polling":
            logger.info("Starting bot in polling mode...")
            bot.run()
        else:
            logger.info("Running scheduled daily quotes...")
            success = asyncio.run(bot.send_daily_quotes())
            if not success:
                logger.error("Failed to send daily quotes")
                return 1
            logger.info("Daily quotes sent successfully!")
        
        return 0
        
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
        return 0
    except Exception as e:
        logger.exception(f"Unexpected error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
