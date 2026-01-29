"""Tests for unified channel publisher."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from src.unified.publisher import (
    BADGE,
    BOT_USERNAME,
    TorahYomiPublisher,
    format_for_unified_channel,
    is_unified_channel_enabled,
)


class TestFormatForUnifiedChannel:
    """Tests for format_for_unified_channel function."""

    def test_adds_header(self):
        """Should add header with badge."""
        content = "Test content"
        formatted = format_for_unified_channel(content)
        assert BADGE in formatted

    def test_adds_footer(self):
        """Should add footer with bot username."""
        content = "Test content"
        formatted = format_for_unified_channel(content)
        assert f"@{BOT_USERNAME}" in formatted

    def test_preserves_content(self):
        """Should preserve original content."""
        content = "Original test content"
        formatted = format_for_unified_channel(content)
        assert content in formatted

    def test_adds_separators(self):
        """Should add visual separators."""
        content = "Test"
        formatted = format_for_unified_channel(content)
        assert "─" in formatted or "━" in formatted


class TestIsUnifiedChannelEnabled:
    """Tests for is_unified_channel_enabled function."""

    def test_returns_boolean(self):
        """Should return a boolean value."""
        result = is_unified_channel_enabled()
        assert isinstance(result, bool)


class TestTorahYomiPublisher:
    """Tests for TorahYomiPublisher class."""

    def test_init(self):
        """Should initialize with no bot."""
        publisher = TorahYomiPublisher()
        assert publisher._bot is None

    @pytest.mark.asyncio
    async def test_publish_text_disabled(self):
        """Should return False when disabled."""
        with patch("src.unified.publisher.is_unified_channel_enabled", return_value=False):
            publisher = TorahYomiPublisher()
            result = await publisher.publish_text("Test")
            assert result is False

    @pytest.mark.asyncio
    async def test_publish_text_no_token(self):
        """Should return False when no token configured."""
        with (
            patch("src.unified.publisher.is_unified_channel_enabled", return_value=True),
            patch("src.unified.publisher.UNIFIED_BOT_TOKEN", None),
        ):
            publisher = TorahYomiPublisher()
            publisher._bot = None
            result = await publisher.publish_text("Test")
            assert result is False

    @pytest.mark.asyncio
    async def test_publish_text_success(self):
        """Should return True on successful publish."""
        mock_bot = MagicMock()
        mock_bot.send_message = AsyncMock()

        with (
            patch("src.unified.publisher.is_unified_channel_enabled", return_value=True),
            patch("src.unified.publisher.UNIFIED_CHANNEL_ID", "@test_channel"),
        ):
            publisher = TorahYomiPublisher()
            publisher._bot = mock_bot
            result = await publisher.publish_text("Test content")
            assert result is True
            mock_bot.send_message.assert_called_once()

    @pytest.mark.asyncio
    async def test_publish_text_retries_on_error(self):
        """Should retry on error."""
        mock_bot = MagicMock()
        # Fail twice, succeed third time
        from telegram.error import TelegramError
        mock_bot.send_message = AsyncMock(side_effect=[
            TelegramError("Error 1"),
            TelegramError("Error 2"),
            None  # Success
        ])

        with (
            patch("src.unified.publisher.is_unified_channel_enabled", return_value=True),
            patch("src.unified.publisher.UNIFIED_CHANNEL_ID", "@test_channel"),
            patch("src.unified.publisher.RETRY_DELAY", 0.001),  # Fast retries for tests
        ):
            publisher = TorahYomiPublisher()
            publisher._bot = mock_bot
            result = await publisher.publish_text("Test")
            assert result is True
            assert mock_bot.send_message.call_count == 3

    @pytest.mark.asyncio
    async def test_publish_text_fails_after_max_retries(self):
        """Should return False after max retries exceeded."""
        mock_bot = MagicMock()
        from telegram.error import TelegramError
        mock_bot.send_message = AsyncMock(side_effect=TelegramError("Persistent error"))

        with (
            patch("src.unified.publisher.is_unified_channel_enabled", return_value=True),
            patch("src.unified.publisher.UNIFIED_CHANNEL_ID", "@test_channel"),
            patch("src.unified.publisher.RETRY_DELAY", 0.001),
        ):
            publisher = TorahYomiPublisher()
            publisher._bot = mock_bot
            result = await publisher.publish_text("Test")
            assert result is False

    @pytest.mark.asyncio
    async def test_publish_batch_disabled(self):
        """Should return zero counts when disabled."""
        with patch("src.unified.publisher.is_unified_channel_enabled", return_value=False):
            publisher = TorahYomiPublisher()
            result = await publisher.publish_batch(["msg1", "msg2"])
            assert result == {"success": 0, "failed": 0}

    @pytest.mark.asyncio
    async def test_publish_batch_counts(self):
        """Should return correct success/failed counts."""
        mock_bot = MagicMock()
        # First succeeds, second fails
        from telegram.error import TelegramError
        mock_bot.send_message = AsyncMock(side_effect=[
            None,  # Success
            TelegramError("Error"),
            TelegramError("Error"),
            TelegramError("Error"),  # 3 retries
        ])

        with (
            patch("src.unified.publisher.is_unified_channel_enabled", return_value=True),
            patch("src.unified.publisher.UNIFIED_CHANNEL_ID", "@test_channel"),
            patch("src.unified.publisher.RETRY_DELAY", 0.001),
        ):
            publisher = TorahYomiPublisher()
            publisher._bot = mock_bot
            result = await publisher.publish_batch(["msg1", "msg2"])
            assert result["success"] == 1
            assert result["failed"] == 1
