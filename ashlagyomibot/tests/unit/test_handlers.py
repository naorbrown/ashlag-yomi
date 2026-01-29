"""Tests for Telegram command handlers."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from src.bot.handlers import (
    start_command,
    today_command,
    quote_command,
    about_command,
    help_command,
    feedback_command,
)


@pytest.fixture
def mock_update():
    """Create a mock Telegram Update."""
    update = MagicMock()
    update.effective_message = MagicMock()
    update.effective_message.reply_text = AsyncMock()
    update.effective_user = MagicMock()
    update.effective_user.id = 12345
    return update


@pytest.fixture
def mock_context():
    """Create a mock Telegram context."""
    return MagicMock()


class TestStartCommand:
    """Tests for /start command."""

    @pytest.mark.asyncio
    async def test_sends_welcome_message(self, mock_update, mock_context):
        """Should send a welcome message."""
        await start_command(mock_update, mock_context)

        mock_update.effective_message.reply_text.assert_called_once()
        call_args = mock_update.effective_message.reply_text.call_args
        message = call_args[0][0]

        assert "Ashlag Yomi" in message

    @pytest.mark.asyncio
    async def test_uses_html_parse_mode(self, mock_update, mock_context):
        """Should use HTML parse mode."""
        await start_command(mock_update, mock_context)

        call_kwargs = mock_update.effective_message.reply_text.call_args[1]
        assert call_kwargs.get("parse_mode") == "HTML"

    @pytest.mark.asyncio
    async def test_handles_missing_message(self, mock_context):
        """Should handle update without effective_message."""
        update = MagicMock()
        update.effective_message = None

        # Should not raise
        await start_command(update, mock_context)

    @pytest.mark.asyncio
    async def test_includes_command_list(self, mock_update, mock_context):
        """Should include available commands."""
        await start_command(mock_update, mock_context)

        message = mock_update.effective_message.reply_text.call_args[0][0]
        assert "/today" in message
        assert "/quote" in message
        assert "/about" in message


class TestTodayCommand:
    """Tests for /today command."""

    @pytest.mark.asyncio
    async def test_sends_daily_quotes(
        self, mock_update, mock_context, mock_settings, mock_repository
    ):
        """Should send the daily bundle."""
        with patch("src.bot.handlers.QuoteRepository", return_value=mock_repository):
            await today_command(mock_update, mock_context)

        # Should send multiple messages (header + quotes + footer)
        assert mock_update.effective_message.reply_text.call_count > 1

    @pytest.mark.asyncio
    async def test_handles_missing_message(self, mock_context):
        """Should handle update without effective_message."""
        update = MagicMock()
        update.effective_message = None

        # Should not raise
        await today_command(update, mock_context)

    @pytest.mark.asyncio
    async def test_uses_html_parse_mode(
        self, mock_update, mock_context, mock_settings, mock_repository
    ):
        """Should use HTML parse mode for all messages."""
        with patch("src.bot.handlers.QuoteRepository", return_value=mock_repository):
            await today_command(mock_update, mock_context)

        for call in mock_update.effective_message.reply_text.call_args_list:
            if call[1]:  # Has kwargs
                assert call[1].get("parse_mode") == "HTML"


class TestAboutCommand:
    """Tests for /about command."""

    @pytest.mark.asyncio
    async def test_includes_lineage_info(self, mock_update, mock_context):
        """Should include information about the lineage."""
        await about_command(mock_update, mock_context)

        message = mock_update.effective_message.reply_text.call_args[0][0]
        assert "האר״י" in message
        assert "הבעל שם טוב" in message
        assert "בעל הסולם" in message

    @pytest.mark.asyncio
    async def test_includes_links(self, mock_update, mock_context):
        """Should include resource links."""
        await about_command(mock_update, mock_context)

        message = mock_update.effective_message.reply_text.call_args[0][0]
        assert "orhassulam.com" in message
        assert "sefaria.org" in message

    @pytest.mark.asyncio
    async def test_uses_html_parse_mode(self, mock_update, mock_context):
        """Should use HTML parse mode."""
        await about_command(mock_update, mock_context)

        call_kwargs = mock_update.effective_message.reply_text.call_args[1]
        assert call_kwargs.get("parse_mode") == "HTML"


class TestQuoteCommand:
    """Tests for /quote command."""

    @pytest.mark.asyncio
    async def test_sends_single_quote(
        self, mock_update, mock_context, mock_settings, sample_quote
    ):
        """Should send a single random quote."""
        mock_repo = MagicMock()
        mock_repo.get_random_quote.return_value = sample_quote

        with patch("src.bot.handlers.QuoteRepository", return_value=mock_repo):
            await quote_command(mock_update, mock_context)

        mock_update.effective_message.reply_text.assert_called_once()

    @pytest.mark.asyncio
    async def test_handles_no_quotes(self, mock_update, mock_context, mock_settings):
        """Should handle case when no quotes available."""
        mock_repo = MagicMock()
        mock_repo.get_random_quote.return_value = None

        with patch("src.bot.handlers.QuoteRepository", return_value=mock_repo):
            await quote_command(mock_update, mock_context)

        message = mock_update.effective_message.reply_text.call_args[0][0]
        assert "No quotes available" in message

    @pytest.mark.asyncio
    async def test_uses_html_parse_mode(
        self, mock_update, mock_context, mock_settings, sample_quote
    ):
        """Should use HTML parse mode."""
        mock_repo = MagicMock()
        mock_repo.get_random_quote.return_value = sample_quote

        with patch("src.bot.handlers.QuoteRepository", return_value=mock_repo):
            await quote_command(mock_update, mock_context)

        call_kwargs = mock_update.effective_message.reply_text.call_args[1]
        assert call_kwargs.get("parse_mode") == "HTML"

    @pytest.mark.asyncio
    async def test_includes_inline_keyboard(
        self, mock_update, mock_context, mock_settings, sample_quote
    ):
        """Should include inline keyboard for source link."""
        mock_repo = MagicMock()
        mock_repo.get_random_quote.return_value = sample_quote

        with patch("src.bot.handlers.QuoteRepository", return_value=mock_repo):
            await quote_command(mock_update, mock_context)

        call_kwargs = mock_update.effective_message.reply_text.call_args[1]
        assert "reply_markup" in call_kwargs

    @pytest.mark.asyncio
    async def test_handles_missing_message(self, mock_context):
        """Should handle update without effective_message."""
        update = MagicMock()
        update.effective_message = None

        # Should not raise
        await quote_command(update, mock_context)


class TestHelpCommand:
    """Tests for /help command."""

    @pytest.mark.asyncio
    async def test_lists_all_commands(self, mock_update, mock_context):
        """Should list all available commands."""
        await help_command(mock_update, mock_context)

        message = mock_update.effective_message.reply_text.call_args[0][0]
        assert "/today" in message
        assert "/quote" in message
        assert "/about" in message
        assert "/feedback" in message

    @pytest.mark.asyncio
    async def test_uses_html_parse_mode(self, mock_update, mock_context):
        """Should use HTML parse mode."""
        await help_command(mock_update, mock_context)

        call_kwargs = mock_update.effective_message.reply_text.call_args[1]
        assert call_kwargs.get("parse_mode") == "HTML"


class TestFeedbackCommand:
    """Tests for /feedback command."""

    @pytest.mark.asyncio
    async def test_provides_feedback_info(self, mock_update, mock_context):
        """Should explain how to send feedback."""
        await feedback_command(mock_update, mock_context)

        message = mock_update.effective_message.reply_text.call_args[0][0]
        assert "Feedback" in message
        assert "GitHub" in message

    @pytest.mark.asyncio
    async def test_uses_html_parse_mode(self, mock_update, mock_context):
        """Should use HTML parse mode."""
        await feedback_command(mock_update, mock_context)

        call_kwargs = mock_update.effective_message.reply_text.call_args[1]
        assert call_kwargs.get("parse_mode") == "HTML"
