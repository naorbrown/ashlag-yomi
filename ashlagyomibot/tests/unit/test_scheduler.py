"""Tests for scheduling utilities."""

import pytest
from datetime import date
from unittest.mock import AsyncMock, MagicMock, patch

from src.bot.scheduler import send_daily_quotes, get_next_send_time


class TestSendDailyQuotes:
    """Tests for send_daily_quotes function."""

    @pytest.mark.asyncio
    async def test_returns_false_when_no_quotes(self, mock_settings):
        """Should return False when no quotes available."""
        mock_bot = MagicMock()
        mock_repo = MagicMock()
        mock_bundle = MagicMock()
        mock_bundle.quotes = []
        mock_repo.get_daily_bundle.return_value = mock_bundle

        with patch("src.bot.scheduler.QuoteRepository", return_value=mock_repo):
            result = await send_daily_quotes(mock_bot, "@test_channel")

        assert result is False

    @pytest.mark.asyncio
    async def test_dry_run_does_not_send(self, mock_settings, monkeypatch):
        """Should not send messages in dry run mode."""
        monkeypatch.setenv("DRY_RUN", "true")

        from src.utils.config import get_settings
        get_settings.cache_clear()

        mock_bot = MagicMock()
        mock_bot.send_message = AsyncMock()

        mock_repo = MagicMock()
        mock_bundle = MagicMock()
        mock_bundle.quotes = [MagicMock()]
        mock_repo.get_daily_bundle.return_value = mock_bundle

        with patch("src.bot.scheduler.QuoteRepository", return_value=mock_repo):
            result = await send_daily_quotes(mock_bot, "@test_channel")

        assert result is True
        mock_bot.send_message.assert_not_called()

    @pytest.mark.asyncio
    async def test_sends_messages_in_normal_mode(
        self, mock_settings, mock_repository, monkeypatch
    ):
        """Should send messages when not in dry run."""
        monkeypatch.setenv("DRY_RUN", "false")

        from src.utils.config import get_settings
        get_settings.cache_clear()

        mock_bot = MagicMock()
        mock_bot.send_message = AsyncMock()

        with patch("src.bot.scheduler.QuoteRepository", return_value=mock_repository):
            result = await send_daily_quotes(mock_bot, "@test_channel")

        assert result is True
        assert mock_bot.send_message.call_count > 0

    @pytest.mark.asyncio
    async def test_uses_html_parse_mode(
        self, mock_settings, mock_repository, monkeypatch
    ):
        """Should use HTML parse mode."""
        monkeypatch.setenv("DRY_RUN", "false")

        from src.utils.config import get_settings
        get_settings.cache_clear()

        mock_bot = MagicMock()
        mock_bot.send_message = AsyncMock()

        with patch("src.bot.scheduler.QuoteRepository", return_value=mock_repository):
            await send_daily_quotes(mock_bot, "@test_channel")

        for call in mock_bot.send_message.call_args_list:
            kwargs = call[1]
            assert kwargs.get("parse_mode") == "HTML"


class TestGetNextSendTime:
    """Tests for get_next_send_time function."""

    def test_returns_iso_format(self, mock_settings):
        """Should return ISO format datetime string."""
        next_time = get_next_send_time()

        # Should contain T separator for ISO format
        assert "T" in next_time

        # Should be parseable
        from datetime import datetime
        datetime.fromisoformat(next_time)

    def test_returns_future_time(self, mock_settings):
        """Should return a time in the future."""
        from datetime import datetime
        from zoneinfo import ZoneInfo

        next_time_str = get_next_send_time()
        next_time = datetime.fromisoformat(next_time_str)

        # Should be in the future (or at least not in the past)
        now = datetime.now(ZoneInfo("Asia/Jerusalem"))
        assert next_time >= now.replace(second=0, microsecond=0)
