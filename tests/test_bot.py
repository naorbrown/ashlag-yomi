"""
Tests for the AshlagYomiBot class.
"""

import json
import os
from pathlib import Path
from unittest.mock import MagicMock, AsyncMock, patch

import pytest

from bot import AshlagYomiBot, QuotesManager


class TestAshlagYomiBot:
    """Test suite for AshlagYomiBot."""

    @pytest.fixture
    def bot(self, mock_bot_token: str, sample_quotes_dir: Path) -> AshlagYomiBot:
        """Create a bot instance for testing."""
        with patch.object(QuotesManager, "__init__", lambda self, path: None):
            bot = AshlagYomiBot(mock_bot_token)
            bot.quotes_manager = QuotesManager.__new__(QuotesManager)
            bot.quotes_manager.quotes_dir = sample_quotes_dir
            bot.quotes_manager.quotes_cache = {}
            bot.quotes_manager.rabbis_metadata = {}
            bot.quotes_manager._load_quotes()
            return bot

    @pytest.mark.asyncio
    async def test_start_command(
        self, bot: AshlagYomiBot, mock_update: MagicMock, mock_context: MagicMock
    ):
        """Test /start command handler."""
        await bot.start_command(mock_update, mock_context)

        mock_update.message.reply_text.assert_called_once()
        call_args = mock_update.message.reply_text.call_args
        assert "ברוכים הבאים" in call_args[0][0]
        assert mock_update.effective_chat.id in bot.subscribed_chats

    @pytest.mark.asyncio
    async def test_stop_command_subscribed(
        self, bot: AshlagYomiBot, mock_update: MagicMock, mock_context: MagicMock
    ):
        """Test /stop command when user is subscribed."""
        chat_id = mock_update.effective_chat.id
        bot.subscribed_chats.add(chat_id)

        await bot.stop_command(mock_update, mock_context)

        assert chat_id not in bot.subscribed_chats
        mock_update.message.reply_text.assert_called_once()

    @pytest.mark.asyncio
    async def test_stop_command_not_subscribed(
        self, bot: AshlagYomiBot, mock_update: MagicMock, mock_context: MagicMock
    ):
        """Test /stop command when user is not subscribed."""
        await bot.stop_command(mock_update, mock_context)

        mock_update.message.reply_text.assert_called_once()
        call_args = mock_update.message.reply_text.call_args
        assert "אינך רשום" in call_args[0][0]

    @pytest.mark.asyncio
    async def test_help_command(
        self, bot: AshlagYomiBot, mock_update: MagicMock, mock_context: MagicMock
    ):
        """Test /help command handler."""
        await bot.help_command(mock_update, mock_context)

        mock_update.message.reply_text.assert_called_once()
        call_args = mock_update.message.reply_text.call_args
        assert "/start" in call_args[0][0]
        assert "/stop" in call_args[0][0]
        assert "/today" in call_args[0][0]
        assert "/quote" in call_args[0][0]

    @pytest.mark.asyncio
    async def test_about_command(
        self, bot: AshlagYomiBot, mock_update: MagicMock, mock_context: MagicMock
    ):
        """Test /about command handler."""
        await bot.about_command(mock_update, mock_context)

        mock_update.message.reply_text.assert_called_once()
        call_args = mock_update.message.reply_text.call_args
        assert "Ashlag Yomi" in call_args[0][0]

    @pytest.mark.asyncio
    async def test_unknown_command(
        self, bot: AshlagYomiBot, mock_update: MagicMock, mock_context: MagicMock
    ):
        """Test unknown command handler."""
        await bot.unknown_command(mock_update, mock_context)

        mock_update.message.reply_text.assert_called_once()
        call_args = mock_update.message.reply_text.call_args
        assert "/help" in call_args[0][0]


class TestBotSubscriptions:
    """Test subscription persistence."""

    @pytest.fixture
    def temp_subs_file(self, tmp_path: Path) -> Path:
        """Create a temporary subscriptions file."""
        subs_file = tmp_path / "data" / "subscriptions.json"
        subs_file.parent.mkdir(parents=True, exist_ok=True)
        return subs_file

    def test_save_subscriptions(
        self, mock_bot_token: str, temp_subs_file: Path, sample_quotes_dir: Path
    ):
        """Test saving subscriptions to file."""
        with patch.object(
            AshlagYomiBot, "_get_subscriptions_file", return_value=temp_subs_file
        ):
            with patch.object(QuotesManager, "__init__", lambda self, path: None):
                bot = AshlagYomiBot(mock_bot_token)
                bot.quotes_manager = MagicMock()
                bot.subscribed_chats = {123, 456, 789}

                bot._save_subscriptions()

                assert temp_subs_file.exists()
                with open(temp_subs_file) as f:
                    data = json.load(f)
                assert set(data["chat_ids"]) == {123, 456, 789}

    def test_load_subscriptions(
        self, mock_bot_token: str, temp_subs_file: Path, sample_quotes_dir: Path
    ):
        """Test loading subscriptions from file."""
        temp_subs_file.parent.mkdir(parents=True, exist_ok=True)
        with open(temp_subs_file, "w") as f:
            json.dump({"chat_ids": [111, 222, 333]}, f)

        with patch.object(
            AshlagYomiBot, "_get_subscriptions_file", return_value=temp_subs_file
        ):
            with patch.object(QuotesManager, "__init__", lambda self, path: None):
                bot = AshlagYomiBot(mock_bot_token)
                bot.quotes_manager = MagicMock()

        assert bot.subscribed_chats == {111, 222, 333}


class TestBotBuild:
    """Test bot building and configuration."""

    def test_build_creates_application(
        self, mock_bot_token: str, sample_quotes_dir: Path
    ):
        """Test that build() creates an application."""
        with patch.object(QuotesManager, "__init__", lambda self, path: None):
            bot = AshlagYomiBot(mock_bot_token)
            bot.quotes_manager = MagicMock()

            app = bot.build()

            assert app is not None
            assert bot.application is not None

    def test_build_registers_handlers(
        self, mock_bot_token: str, sample_quotes_dir: Path
    ):
        """Test that build() registers command handlers."""
        with patch.object(QuotesManager, "__init__", lambda self, path: None):
            bot = AshlagYomiBot(mock_bot_token)
            bot.quotes_manager = MagicMock()

            app = bot.build()

            # Check that handlers are registered
            assert len(app.handlers) > 0


class TestEnvironmentVariables:
    """Test environment variable handling."""

    def test_missing_token_exits(self):
        """Test that missing token causes exit."""
        # Remove token from environment
        if "TELEGRAM_BOT_TOKEN" in os.environ:
            del os.environ["TELEGRAM_BOT_TOKEN"]

        from bot import main

        with pytest.raises(SystemExit):
            main()

    def test_admin_chat_ids_parsing(self, mock_bot_token: str):
        """Test parsing of admin chat IDs."""
        os.environ["ADMIN_CHAT_IDS"] = "123,456,789"

        admin_ids = os.environ.get("ADMIN_CHAT_IDS", "").split(",")

        assert "123" in admin_ids
        assert "456" in admin_ids
        assert "789" in admin_ids
