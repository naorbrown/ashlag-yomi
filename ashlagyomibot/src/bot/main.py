"""
Main entry point for the Ashlag Yomi Telegram bot.

This module initializes the bot and registers all command handlers.
Uses python-telegram-bot v20+ with async/await pattern.

Bot Commands:
- /start - Welcome and subscribe to daily quotes
- /today - Get today's 2 quotes (Baal Hasulam + Rabash)

Usage:
    # Run directly
    python -m src.bot.main

    # Or via the installed command
    ashlag-yomi
"""

import asyncio
import signal
import sys
from typing import NoReturn

from telegram import BotCommand, Update
from telegram.ext import Application, CommandHandler, ContextTypes

from src.bot.handlers import start_command, today_command
from src.utils.config import get_settings
from src.utils.logger import get_logger, setup_logging

logger = get_logger(__name__)

# Bot commands - only /start and /today
BOT_COMMANDS = [
    BotCommand("start", "הרשמה לציטוטים יומיים"),
    BotCommand("today", "ציטוטים של היום"),
]


def create_application() -> Application:  # type: ignore[type-arg]
    """
    Create and configure the Telegram bot application.

    Returns:
        Configured Application instance ready to run.
    """
    settings = get_settings()

    # Build the application with the bot token
    application = (
        Application.builder()
        .token(settings.telegram_bot_token.get_secret_value())
        .build()
    )

    # Register command handlers - only /start and /today
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("today", today_command))

    logger.info("application_created", handlers=2)
    return application


async def register_commands(application: Application) -> None:  # type: ignore[type-arg]
    """
    Register bot commands with Telegram.

    This makes commands appear in the Telegram menu when users type '/'.
    """
    try:
        await application.bot.set_my_commands(BOT_COMMANDS)
        logger.info("commands_registered", count=len(BOT_COMMANDS))
    except Exception as e:
        logger.error("failed_to_register_commands", error=str(e))


async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Global error handler for the bot.

    Logs errors and sends user-friendly message to prevent confusion.
    """
    logger.error(
        "telegram_error",
        error=str(context.error),
        update=str(update) if update else None,
    )

    # Send user-friendly error message if we have an update with a message
    if isinstance(update, Update) and update.effective_message:
        try:
            await update.effective_message.reply_text(
                "😔 אירעה שגיאה. אנא נסו שוב מאוחר יותר."
            )
        except Exception:
            pass  # Don't fail on error message send failure


async def run_bot() -> None:
    """Run the bot in polling mode (for local development)."""
    settings = get_settings()

    logger.info(
        "starting_bot",
        environment=settings.environment,
        dry_run=settings.dry_run,
    )

    application = create_application()
    application.add_error_handler(error_handler)

    # Initialize and start polling
    await application.initialize()
    await application.start()

    # Register commands with Telegram
    await register_commands(application)

    logger.info("bot_started", mode="polling")

    # Start polling for updates
    await application.updater.start_polling(  # type: ignore[union-attr]
        allowed_updates=Update.ALL_TYPES,
        drop_pending_updates=True,  # Don't process old messages on restart
    )

    # Keep running until interrupted
    stop_event = asyncio.Event()

    def signal_handler(_sig: int, _frame: object) -> None:
        logger.info("shutdown_signal_received")
        stop_event.set()

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    await stop_event.wait()

    # Graceful shutdown
    logger.info("shutting_down")
    await application.updater.stop()  # type: ignore[union-attr]
    await application.stop()
    await application.shutdown()

    logger.info("bot_stopped")


def main() -> NoReturn:
    """Main entry point."""
    setup_logging()

    try:
        asyncio.run(run_bot())
    except KeyboardInterrupt:
        logger.info("keyboard_interrupt")
    except Exception as e:
        logger.exception("fatal_error", error=str(e))
        sys.exit(1)

    sys.exit(0)


if __name__ == "__main__":
    main()
