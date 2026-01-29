"""
Mock Telegram objects for testing.

Provides reusable mock objects for:
- Update (incoming messages)
- Context (bot context)
- Message (Telegram messages)
- User (Telegram users)
"""

from unittest.mock import AsyncMock, MagicMock


def create_mock_update(
    user_id: int = 12345,
    chat_id: int = 12345,
    message_text: str = "/start",
) -> MagicMock:
    """
    Create a mock Telegram Update object.

    Args:
        user_id: Mock user ID
        chat_id: Mock chat ID
        message_text: Text of the message

    Returns:
        Mock Update object
    """
    update = MagicMock()

    # Mock effective_message
    update.effective_message = MagicMock()
    update.effective_message.reply_text = AsyncMock()
    update.effective_message.text = message_text
    update.effective_message.chat_id = chat_id

    # Mock effective_user
    update.effective_user = MagicMock()
    update.effective_user.id = user_id
    update.effective_user.username = "test_user"
    update.effective_user.first_name = "Test"

    # Mock effective_chat
    update.effective_chat = MagicMock()
    update.effective_chat.id = chat_id
    update.effective_chat.type = "private"

    return update


def create_mock_context() -> MagicMock:
    """
    Create a mock Telegram Context object.

    Returns:
        Mock ContextTypes.DEFAULT_TYPE object
    """
    context = MagicMock()
    context.bot = MagicMock()
    context.bot.send_message = AsyncMock()
    context.args = []
    return context


def create_mock_bot() -> MagicMock:
    """
    Create a mock Telegram Bot object.

    Returns:
        Mock Bot object with async methods
    """
    bot = MagicMock()
    bot.send_message = AsyncMock()
    bot.send_photo = AsyncMock()
    bot.send_document = AsyncMock()
    bot.get_me = AsyncMock(return_value=MagicMock(username="test_bot"))
    return bot
