"""Tests for main bot module."""

import pytest
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch

from telegram import BotCommand, Update

from src.bot.main import (
    BOT_COMMANDS,
    create_application,
    error_handler,
    register_commands,
)
from src.bot.rate_limit import (
    RATE_LIMIT,
    RATE_WINDOW,
    _rate_limits,
    clear_rate_limits,
    is_rate_limited,
)


class TestBotCommands:
    """Tests for bot command configuration."""

    def test_commands_defined(self):
        """Should have bot commands defined."""
        assert len(BOT_COMMANDS) == 6

    def test_commands_are_bot_command_type(self):
        """Commands should be BotCommand instances."""
        for cmd in BOT_COMMANDS:
            assert isinstance(cmd, BotCommand)

    def test_required_commands_present(self):
        """Should have all required commands."""
        command_names = [cmd.command for cmd in BOT_COMMANDS]
        assert "start" in command_names
        assert "today" in command_names
        assert "quote" in command_names
        assert "about" in command_names
        assert "help" in command_names
        assert "feedback" in command_names

    def test_commands_have_descriptions(self):
        """All commands should have descriptions."""
        for cmd in BOT_COMMANDS:
            assert cmd.description
            assert len(cmd.description) > 0

    def test_descriptions_are_short_english(self):
        """Command descriptions should be short and in English."""
        for cmd in BOT_COMMANDS:
            # Should be under 30 chars (nachyomi-bot pattern)
            assert len(cmd.description) <= 30
            # Should be ASCII (English, not Hebrew)
            assert cmd.description.isascii() or "&" in cmd.description


class TestRateLimiting:
    """Tests for rate limiting functionality."""

    def setup_method(self):
        """Clear rate limits before each test."""
        clear_rate_limits()

    def test_first_request_not_limited(self):
        """First request should not be rate limited."""
        assert is_rate_limited(12345) is False

    def test_under_limit_not_limited(self):
        """Requests under limit should not be rate limited."""
        user_id = 12345
        for _ in range(RATE_LIMIT - 1):
            assert is_rate_limited(user_id) is False

    def test_at_limit_becomes_limited(self):
        """Request at limit should be rate limited."""
        user_id = 12345
        for _ in range(RATE_LIMIT):
            is_rate_limited(user_id)
        # Next request should be limited
        assert is_rate_limited(user_id) is True

    def test_different_users_independent(self):
        """Different users should have independent limits."""
        user1, user2 = 111, 222

        # Fill up user1's limit
        for _ in range(RATE_LIMIT):
            is_rate_limited(user1)

        # User1 should be limited, user2 should not
        assert is_rate_limited(user1) is True
        assert is_rate_limited(user2) is False

    def test_old_requests_cleaned_up(self):
        """Old requests outside window should be cleaned up."""
        user_id = 12345

        # Manually add old timestamps
        old_time = datetime.now() - RATE_WINDOW - timedelta(seconds=1)
        _rate_limits[user_id] = [old_time] * RATE_LIMIT

        # Should not be rate limited because old requests are cleaned
        assert is_rate_limited(user_id) is False


class TestCreateApplication:
    """Tests for application creation."""

    def test_creates_application(self, mock_settings):
        """Should create an Application instance."""
        app = create_application()
        assert app is not None

    def test_registers_handlers(self, mock_settings):
        """Should register all command handlers."""
        app = create_application()
        # Should have 6 handlers (start, today, quote, about, help, feedback)
        assert len(app.handlers[0]) == 6


class TestRegisterCommands:
    """Tests for command registration."""

    @pytest.mark.asyncio
    async def test_registers_commands_successfully(self):
        """Should register commands with the bot."""
        mock_app = MagicMock()
        mock_app.bot.set_my_commands = AsyncMock()

        await register_commands(mock_app)

        mock_app.bot.set_my_commands.assert_called_once_with(BOT_COMMANDS)

    @pytest.mark.asyncio
    async def test_handles_registration_error(self):
        """Should handle errors during command registration."""
        mock_app = MagicMock()
        mock_app.bot.set_my_commands = AsyncMock(side_effect=Exception("API Error"))

        # Should not raise
        await register_commands(mock_app)


class TestErrorHandler:
    """Tests for global error handler."""

    @pytest.mark.asyncio
    async def test_handles_none_update(self):
        """Should handle None update gracefully."""
        mock_context = MagicMock()
        mock_context.error = Exception("Test error")

        # Should not raise
        await error_handler(None, mock_context)

    @pytest.mark.asyncio
    async def test_handles_update_without_message(self):
        """Should handle update without message."""
        mock_update = MagicMock(spec=Update)
        mock_update.effective_message = None

        mock_context = MagicMock()
        mock_context.error = Exception("Test error")

        # Should not raise
        await error_handler(mock_update, mock_context)
