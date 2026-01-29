"""Tests for channel broadcaster."""

from datetime import date
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.bot.broadcaster import broadcast_daily_maamarim


class TestBroadcastDailyMaamarim:
    """Tests for broadcast_daily_maamarim function."""

    @pytest.mark.asyncio
    async def test_returns_false_without_channel_id(self, mock_settings, monkeypatch):
        """Should return False when no channel configured."""
        monkeypatch.setenv("TELEGRAM_CHANNEL_ID", "")

        from src.utils.config import get_settings

        get_settings.cache_clear()

        result = await broadcast_daily_maamarim()
        assert result is False

    @pytest.mark.asyncio
    async def test_dry_run_returns_true(
        self, mock_settings, sample_maamarim, monkeypatch
    ):
        """Should return True in dry run mode without sending."""
        monkeypatch.setenv("TELEGRAM_CHANNEL_ID", "@test_channel")
        monkeypatch.setenv("DRY_RUN", "true")

        from src.utils.config import get_settings

        get_settings.cache_clear()

        mock_repo = MagicMock()
        mock_repo.was_maamar_sent_today.return_value = False
        mock_repo.get_daily_maamarim.return_value = sample_maamarim

        with patch("src.bot.broadcaster.get_maamar_repository", return_value=mock_repo):
            result = await broadcast_daily_maamarim(dry_run=True)

        assert result is True

    @pytest.mark.asyncio
    async def test_idempotent_skips_duplicate(self, mock_settings, monkeypatch):
        """Should skip if already broadcast today."""
        monkeypatch.setenv("TELEGRAM_CHANNEL_ID", "@test_channel")
        monkeypatch.setenv("DRY_RUN", "false")

        from src.utils.config import get_settings

        get_settings.cache_clear()

        # Mock repository to indicate already broadcast
        mock_repo = MagicMock()
        mock_repo.was_maamar_sent_today.return_value = True

        with patch("src.bot.broadcaster.get_maamar_repository", return_value=mock_repo):
            result = await broadcast_daily_maamarim(target_date=date(2024, 1, 15))

        assert result is True
        # Should not have tried to get maamarim since already broadcast
        mock_repo.get_daily_maamarim.assert_not_called()

    @pytest.mark.asyncio
    async def test_marks_maamarim_as_sent(
        self, mock_settings, sample_maamarim, monkeypatch
    ):
        """Should mark maamarim as sent after successful broadcast."""
        monkeypatch.setenv("TELEGRAM_CHANNEL_ID", "@test_channel")
        monkeypatch.setenv("DRY_RUN", "false")

        from src.utils.config import get_settings

        get_settings.cache_clear()

        mock_bot = AsyncMock()
        mock_repo = MagicMock()
        mock_repo.was_maamar_sent_today.return_value = False
        mock_repo.get_daily_maamarim.return_value = sample_maamarim

        with (
            patch("src.bot.broadcaster.get_maamar_repository", return_value=mock_repo),
            patch("src.bot.broadcaster.Bot", return_value=mock_bot),
        ):
            result = await broadcast_daily_maamarim(target_date=date(2024, 1, 15))

        assert result is True
        # Should have marked both maamarim as sent
        assert mock_repo.mark_as_sent.call_count == 2

    @pytest.mark.asyncio
    async def test_sends_both_sources(
        self, mock_settings, sample_maamarim, monkeypatch
    ):
        """Should send maamarim from both Baal Hasulam and Rabash."""
        monkeypatch.setenv("TELEGRAM_CHANNEL_ID", "@test_channel")
        monkeypatch.setenv("DRY_RUN", "false")

        from src.utils.config import get_settings

        get_settings.cache_clear()

        mock_bot = AsyncMock()
        mock_repo = MagicMock()
        mock_repo.was_maamar_sent_today.return_value = False
        mock_repo.get_daily_maamarim.return_value = sample_maamarim

        with (
            patch("src.bot.broadcaster.get_maamar_repository", return_value=mock_repo),
            patch("src.bot.broadcaster.Bot", return_value=mock_bot),
        ):
            await broadcast_daily_maamarim(target_date=date(2024, 1, 15))

        # Should have called send_message multiple times
        # (header + maamar messages + footer)
        assert mock_bot.send_message.call_count >= 3

    @pytest.mark.asyncio
    async def test_returns_false_when_no_maamarim(self, mock_settings, monkeypatch):
        """Should return False when no maamarim available."""
        monkeypatch.setenv("TELEGRAM_CHANNEL_ID", "@test_channel")
        monkeypatch.setenv("DRY_RUN", "false")

        from src.utils.config import get_settings

        get_settings.cache_clear()

        mock_repo = MagicMock()
        mock_repo.was_maamar_sent_today.return_value = False
        mock_repo.get_daily_maamarim.return_value = []

        with patch("src.bot.broadcaster.get_maamar_repository", return_value=mock_repo):
            result = await broadcast_daily_maamarim()

        assert result is False

    @pytest.mark.asyncio
    async def test_handles_exceptions_gracefully(self, mock_settings, monkeypatch):
        """Should handle exceptions and return False."""
        monkeypatch.setenv("TELEGRAM_CHANNEL_ID", "@test_channel")
        monkeypatch.setenv("DRY_RUN", "false")

        from src.utils.config import get_settings

        get_settings.cache_clear()

        mock_repo = MagicMock()
        mock_repo.was_maamar_sent_today.side_effect = Exception("Test error")

        with patch("src.bot.broadcaster.get_maamar_repository", return_value=mock_repo):
            result = await broadcast_daily_maamarim()

        assert result is False
