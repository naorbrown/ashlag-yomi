"""Tests for Telegram command handlers."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.bot.handlers import (
    about_command,
    feedback_command,
    help_command,
    maamar_command,
    quote_command,
    start_command,
    today_command,
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


@pytest.fixture(autouse=True)
def mock_rate_limit():
    """Mock rate limiting to always allow requests."""
    with patch("src.bot.handlers.is_rate_limited", return_value=False):
        yield


class TestStartCommand:
    """Tests for /start command."""

    @pytest.mark.asyncio
    async def test_sends_welcome_message(self, mock_update, mock_context):
        """Should send a welcome message."""
        await start_command(mock_update, mock_context)

        mock_update.effective_message.reply_text.assert_called_once()
        call_args = mock_update.effective_message.reply_text.call_args
        message = call_args[0][0]

        assert "אשלג יומי" in message

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
        assert "/maamar" in message
        assert "/about" in message


class TestTodayCommand:
    """Tests for /today command."""

    @pytest.fixture(autouse=True)
    def mock_sleep(self):
        """Mock asyncio.sleep to speed up tests."""
        with patch("src.bot.handlers.asyncio.sleep", new_callable=AsyncMock):
            yield

    @pytest.mark.asyncio
    async def test_sends_daily_maamarim(
        self, mock_update, mock_context, sample_maamarim
    ):
        """Should send 2 maamarim (one from each source)."""
        mock_repo = MagicMock()
        mock_repo.get_daily_maamarim.return_value = sample_maamarim

        with patch("src.bot.handlers.get_maamar_repository", return_value=mock_repo):
            await today_command(mock_update, mock_context)

        # Should send multiple messages (header + maamarim + footer)
        assert mock_update.effective_message.reply_text.call_count > 1

    @pytest.mark.asyncio
    async def test_sends_both_sources(
        self, mock_update, mock_context, sample_maamar, sample_maamar_rabash
    ):
        """Should send one maamar from Baal Hasulam and one from Rabash."""
        maamarim = [sample_maamar, sample_maamar_rabash]
        mock_repo = MagicMock()
        mock_repo.get_daily_maamarim.return_value = maamarim

        with patch("src.bot.handlers.get_maamar_repository", return_value=mock_repo):
            await today_command(mock_update, mock_context)

        # Check that both sources are mentioned in the messages
        all_messages = [
            call[0][0]
            for call in mock_update.effective_message.reply_text.call_args_list
        ]
        combined = "\n".join(all_messages)
        assert "בעל הסולם" in combined
        assert 'הרב"ש' in combined

    @pytest.mark.asyncio
    async def test_handles_missing_message(self, mock_context):
        """Should handle update without effective_message."""
        update = MagicMock()
        update.effective_message = None
        update.effective_user = MagicMock()
        update.effective_user.id = 12345

        # Should not raise
        await today_command(update, mock_context)

    @pytest.mark.asyncio
    async def test_handles_no_maamarim(self, mock_update, mock_context):
        """Should handle case when no maamarim available."""
        mock_repo = MagicMock()
        mock_repo.get_daily_maamarim.return_value = []

        with patch("src.bot.handlers.get_maamar_repository", return_value=mock_repo):
            await today_command(mock_update, mock_context)

        message = mock_update.effective_message.reply_text.call_args[0][0]
        assert "אין מאמרים" in message or "No maamarim" in message

    @pytest.mark.asyncio
    async def test_uses_html_parse_mode(
        self, mock_update, mock_context, sample_maamarim
    ):
        """Should use HTML parse mode for all messages."""
        mock_repo = MagicMock()
        mock_repo.get_daily_maamarim.return_value = sample_maamarim

        with patch("src.bot.handlers.get_maamar_repository", return_value=mock_repo):
            await today_command(mock_update, mock_context)

        for call in mock_update.effective_message.reply_text.call_args_list:
            if call[1]:  # Has kwargs
                assert call[1].get("parse_mode") == "HTML"


class TestMaamarCommand:
    """Tests for /maamar command (random maamar)."""

    @pytest.fixture(autouse=True)
    def mock_sleep(self):
        """Mock asyncio.sleep to speed up tests."""
        with patch("src.bot.handlers.asyncio.sleep", new_callable=AsyncMock):
            yield

    @pytest.mark.asyncio
    async def test_sends_single_maamar(self, mock_update, mock_context, sample_maamar):
        """Should send a single random maamar."""
        mock_repo = MagicMock()
        mock_repo.get_random_maamar.return_value = sample_maamar

        with patch("src.bot.handlers.get_maamar_repository", return_value=mock_repo):
            await maamar_command(mock_update, mock_context)

        # Should send at least one message
        assert mock_update.effective_message.reply_text.call_count >= 1

    @pytest.mark.asyncio
    async def test_handles_no_maamarim(self, mock_update, mock_context):
        """Should handle case when no maamarim available."""
        mock_repo = MagicMock()
        mock_repo.get_random_maamar.return_value = None

        with patch("src.bot.handlers.get_maamar_repository", return_value=mock_repo):
            await maamar_command(mock_update, mock_context)

        message = mock_update.effective_message.reply_text.call_args[0][0]
        assert "אין מאמרים" in message or "No maamarim" in message

    @pytest.mark.asyncio
    async def test_uses_html_parse_mode(self, mock_update, mock_context, sample_maamar):
        """Should use HTML parse mode."""
        mock_repo = MagicMock()
        mock_repo.get_random_maamar.return_value = sample_maamar

        with patch("src.bot.handlers.get_maamar_repository", return_value=mock_repo):
            await maamar_command(mock_update, mock_context)

        for call in mock_update.effective_message.reply_text.call_args_list:
            if call[1]:  # Has kwargs
                assert call[1].get("parse_mode") == "HTML"

    @pytest.mark.asyncio
    async def test_includes_inline_keyboard(
        self, mock_update, mock_context, sample_maamar
    ):
        """Should include inline keyboard for source link."""
        mock_repo = MagicMock()
        mock_repo.get_random_maamar.return_value = sample_maamar

        with patch("src.bot.handlers.get_maamar_repository", return_value=mock_repo):
            await maamar_command(mock_update, mock_context)

        # Last message should have keyboard
        last_call_kwargs = mock_update.effective_message.reply_text.call_args_list[-1][
            1
        ]
        assert "reply_markup" in last_call_kwargs

    @pytest.mark.asyncio
    async def test_handles_missing_message(self, mock_context):
        """Should handle update without effective_message."""
        update = MagicMock()
        update.effective_message = None

        # Should not raise
        await maamar_command(update, mock_context)


class TestQuoteCommandAlias:
    """Tests for /quote command (alias for /maamar)."""

    @pytest.fixture(autouse=True)
    def mock_sleep(self):
        """Mock asyncio.sleep to speed up tests."""
        with patch("src.bot.handlers.asyncio.sleep", new_callable=AsyncMock):
            yield

    @pytest.mark.asyncio
    async def test_quote_is_alias_for_maamar(
        self, mock_update, mock_context, sample_maamar
    ):
        """quote_command should be an alias for maamar_command."""
        mock_repo = MagicMock()
        mock_repo.get_random_maamar.return_value = sample_maamar

        with patch("src.bot.handlers.get_maamar_repository", return_value=mock_repo):
            await quote_command(mock_update, mock_context)

        # Should send maamar content
        assert mock_update.effective_message.reply_text.call_count >= 1


class TestAboutCommand:
    """Tests for /about command."""

    @pytest.mark.asyncio
    async def test_includes_baal_hasulam_info(self, mock_update, mock_context):
        """Should include information about Baal Hasulam."""
        await about_command(mock_update, mock_context)

        message = mock_update.effective_message.reply_text.call_args[0][0]
        assert "בעל הסולם" in message

    @pytest.mark.asyncio
    async def test_includes_rabash_info(self, mock_update, mock_context):
        """Should include information about Rabash."""
        await about_command(mock_update, mock_context)

        message = mock_update.effective_message.reply_text.call_args[0][0]
        assert 'רב"ש' in message or 'הרב"ש' in message

    @pytest.mark.asyncio
    async def test_includes_links(self, mock_update, mock_context):
        """Should include resource links."""
        await about_command(mock_update, mock_context)

        message = mock_update.effective_message.reply_text.call_args[0][0]
        assert "orhasulam" in message.lower() or "ashlagbaroch" in message.lower()

    @pytest.mark.asyncio
    async def test_uses_html_parse_mode(self, mock_update, mock_context):
        """Should use HTML parse mode."""
        await about_command(mock_update, mock_context)

        call_kwargs = mock_update.effective_message.reply_text.call_args[1]
        assert call_kwargs.get("parse_mode") == "HTML"


class TestHelpCommand:
    """Tests for /help command."""

    @pytest.mark.asyncio
    async def test_lists_all_commands(self, mock_update, mock_context):
        """Should list all available commands."""
        await help_command(mock_update, mock_context)

        message = mock_update.effective_message.reply_text.call_args[0][0]
        assert "/today" in message
        assert "/maamar" in message
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
