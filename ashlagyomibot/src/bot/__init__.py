"""
Telegram bot module for Ashlag Yomi.

This package contains:
- main: Bot entry point and application setup
- handlers: Command handlers (/start, /today, etc.)
- formatters: Message formatting utilities
- rate_limit: Rate limiting for commands
- broadcaster: Channel broadcasting
- scheduler: Scheduled tasks
"""

# Lazy imports to avoid circular dependencies
# Use: from src.bot.main import main
__all__ = [
    "main",
    "handlers",
    "formatters",
    "rate_limit",
    "broadcaster",
    "scheduler",
]
