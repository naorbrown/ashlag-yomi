"""Tests for channel broadcaster."""

from datetime import date
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.bot.broadcaster import broadcast_daily_bundle, broadcast_daily_quote


class TestBroadcastDailyQuote:
    """Tests for broadcast_daily_quote function."""

    @pytest.mark.asyncio
    async def test_returns_false_without_channel_id(self, mock_settings, monkeypatch):
        """Should return False when no channel configured."""
        monkeypatch.setenv("TELEGRAM_CHANNEL_ID", "")

        # Clear the settings cache
        from src.utils.config import get_settings

        get_settings.cache_clear()

        result = await broadcast_daily_quote()
        assert result is False

    @pytest.mark.asyncio
    async def test_dry_run_returns_true(
        self, mock_settings, mock_repository, monkeypatch
    ):
        """Should return True in dry run mode without sending."""
        monkeypatch.setenv("TELEGRAM_CHANNEL_ID", "@test_channel")
        monkeypatch.setenv("DRY_RUN", "true")

        from src.utils.config import get_settings

        get_settings.cache_clear()

        with patch("src.bot.broadcaster.QuoteRepository", return_value=mock_repository):
            result = await broadcast_daily_quote(dry_run=True)

        assert result is True

    @pytest.mark.asyncio
    async def test_idempotent_skips_duplicate(
        self, mock_settings, mock_repository, monkeypatch
    ):
        """Should skip if already broadcast today."""
        monkeypatch.setenv("TELEGRAM_CHANNEL_ID", "@test_channel")
        monkeypatch.setenv("DRY_RUN", "false")

        from src.utils.config import get_settings

        get_settings.cache_clear()

        # Mock repository to indicate already broadcast
        mock_repo = MagicMock()
        mock_repo.was_broadcast_today.return_value = True

        with patch("src.bot.broadcaster.QuoteRepository", return_value=mock_repo):
            result = await broadcast_daily_quote(target_date=date(2024, 1, 15))

        assert result is True
        # Should not have tried to get a quote since already broadcast
        mock_repo.get_random_by_category.assert_not_called()

    @pytest.mark.asyncio
    async def test_marks_quote_as_sent(
        self, mock_settings, mock_repository, monkeypatch
    ):
        """Should mark quote as sent after successful broadcast."""
        monkeypatch.setenv("TELEGRAM_CHANNEL_ID", "@test_channel")
        monkeypatch.setenv("DRY_RUN", "false")

        from src.utils.config import get_settings

        get_settings.cache_clear()

        mock_bot = AsyncMock()
        mock_repo = MagicMock()
        mock_repo.was_broadcast_today.return_value = False
        mock_repo.get_sent_ids_by_category.return_value = set()

        # Create a mock quote
        mock_quote = MagicMock()
        mock_quote.id = "test-001"
        mock_quote.text = "Test quote"
        mock_quote.source_rabbi = "Test Rabbi"
        mock_quote.source_book = "Test Book"
        mock_quote.source_url = "https://example.com"
        mock_quote.category = MagicMock()
        mock_quote.category.value = "test"

        mock_repo.get_random_by_category.return_value = mock_quote

        with (
            patch("src.bot.broadcaster.QuoteRepository", return_value=mock_repo),
            patch("src.bot.broadcaster.Bot", return_value=mock_bot),
        ):
            result = await broadcast_daily_quote(target_date=date(2024, 1, 15))

        assert result is True
        mock_repo.mark_as_sent.assert_called_once()


class TestBroadcastDailyBundle:
    """Tests for broadcast_daily_bundle function."""

    @pytest.mark.asyncio
    async def test_returns_false_without_channel_id(self, mock_settings, monkeypatch):
        """Should return False when no channel configured."""
        monkeypatch.setenv("TELEGRAM_CHANNEL_ID", "")

        from src.utils.config import get_settings

        get_settings.cache_clear()

        result = await broadcast_daily_bundle()
        assert result is False

    @pytest.mark.asyncio
    async def test_dry_run_returns_true(
        self, mock_settings, mock_repository, monkeypatch
    ):
        """Should return True in dry run mode."""
        monkeypatch.setenv("TELEGRAM_CHANNEL_ID", "@test_channel")
        monkeypatch.setenv("DRY_RUN", "true")

        from src.utils.config import get_settings

        get_settings.cache_clear()

        with patch("src.bot.broadcaster.QuoteRepository", return_value=mock_repository):
            result = await broadcast_daily_bundle(dry_run=True)

        assert result is True

    @pytest.mark.asyncio
    async def test_returns_false_when_no_quotes(self, mock_settings, monkeypatch):
        """Should return False when no quotes available."""
        monkeypatch.setenv("TELEGRAM_CHANNEL_ID", "@test_channel")
        monkeypatch.setenv("DRY_RUN", "false")

        from src.utils.config import get_settings

        get_settings.cache_clear()

        mock_repo = MagicMock()
        mock_bundle = MagicMock()
        mock_bundle.quotes = []
        mock_repo.get_daily_bundle.return_value = mock_bundle

        with patch("src.bot.broadcaster.QuoteRepository", return_value=mock_repo):
            result = await broadcast_daily_bundle()

        assert result is False
