"""
Integration tests for /today command.

These tests verify the entire flow of the /today command
from receiving the update to sending the response.
"""

import json
from datetime import date
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.bot.formatters import build_source_keyboard, format_quote
from src.bot.handlers import today_command
from src.data.models import DailyBundle, Quote, QuoteCategory
from src.data.repository import QuoteRepository


class TestTodayCommandIntegration:
    """Integration tests for /today command."""

    @pytest.fixture
    def temp_quotes_dir(self, tmp_path):
        """Create a temporary directory with valid quote files."""
        quotes_dir = tmp_path / "quotes"
        quotes_dir.mkdir()

        # Create valid quote data for each category
        for category in QuoteCategory:
            quote_data = {
                "category": category.value,
                "quotes": [
                    {
                        "id": f"{category.value}-test-001",
                        "text": f"Test quote text for {category.value}. This is a valid quote with enough characters to pass validation.",
                        "source_rabbi": f"Test Rabbi for {category.value}",
                        "source_book": "Test Book",
                        "source_section": "Chapter 1",
                        "source_url": f"https://example.com/{category.value}",
                        "category": category.value,
                        "tags": ["test"],
                        "length_estimate": 30,
                    }
                ],
            }
            file_path = quotes_dir / f"{category.value}.json"
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(quote_data, f, ensure_ascii=False)

        return quotes_dir

    @pytest.fixture
    def temp_history_file(self, tmp_path):
        """Create a temporary history file."""
        return tmp_path / "sent_history.json"

    @pytest.fixture
    def mock_repository(self, temp_quotes_dir, temp_history_file):
        """Create a repository with temporary storage."""
        return QuoteRepository(
            quotes_dir=temp_quotes_dir,
            history_file=temp_history_file,
        )

    @pytest.fixture
    def mock_update(self):
        """Create a mock Telegram Update."""
        update = MagicMock()
        update.effective_message = MagicMock()
        update.effective_message.reply_text = AsyncMock()
        update.effective_user = MagicMock()
        update.effective_user.id = 12345
        return update

    @pytest.fixture
    def mock_context(self):
        """Create a mock Telegram context."""
        return MagicMock()

    def test_repository_loads_quotes(self, mock_repository):
        """Repository should load quotes from all categories."""
        stats = mock_repository.validate_all()

        assert (
            stats["total"] == 6
        ), f"Expected 6 quotes (one per category), got {stats['total']}"

        for category in QuoteCategory:
            assert stats[category.value] == 1, f"Expected 1 quote for {category.value}"

    def test_repository_gets_daily_bundle(self, mock_repository):
        """Repository should return a daily bundle with 6 quotes."""
        bundle = mock_repository.get_daily_bundle(date.today())

        assert isinstance(bundle, DailyBundle)
        assert len(bundle.quotes) == 6, f"Expected 6 quotes, got {len(bundle.quotes)}"

        # Verify all categories are represented
        categories = [q.category for q in bundle.quotes]
        for category in QuoteCategory:
            assert category in categories, f"Missing category: {category.value}"

    def test_format_quote_returns_valid_html(self, mock_repository):
        """format_quote should return valid HTML string."""
        bundle = mock_repository.get_daily_bundle(date.today())

        for quote in bundle.quotes:
            formatted = format_quote(quote)

            # Should be a non-empty string
            assert isinstance(formatted, str)
            assert len(formatted) > 0

            # Should contain HTML tags
            assert "<b>" in formatted
            assert "</b>" in formatted

            # Should contain the quote text (in Hebrew quotes)
            assert "״" in formatted

            print(f"Category {quote.category.value}: {len(formatted)} chars")

    def test_build_source_keyboard_returns_markup(self, mock_repository):
        """build_source_keyboard should return InlineKeyboardMarkup."""
        bundle = mock_repository.get_daily_bundle(date.today())

        for quote in bundle.quotes:
            keyboard = build_source_keyboard(quote)

            # Should return a keyboard (since all test quotes have source_url)
            assert keyboard is not None
            assert hasattr(keyboard, "inline_keyboard")

    @pytest.mark.asyncio
    async def test_today_command_sends_messages(
        self, mock_update, mock_context, mock_repository
    ):
        """today_command should send header, 6 quotes, and footer."""
        with patch("src.bot.handlers.QuoteRepository", return_value=mock_repository):
            with patch("src.bot.handlers.get_settings") as mock_settings:
                settings = MagicMock()
                settings.dry_run = False
                mock_settings.return_value = settings

                with patch("src.bot.handlers.is_rate_limited", return_value=False):
                    with patch(
                        "src.bot.handlers.asyncio.sleep", new_callable=AsyncMock
                    ):
                        await today_command(mock_update, mock_context)

        # Should have sent: 1 header + 6 quotes + 1 footer = 8 messages
        call_count = mock_update.effective_message.reply_text.call_count
        assert call_count == 8, f"Expected 8 messages, got {call_count}"

        # Verify first message is the header
        first_call = mock_update.effective_message.reply_text.call_args_list[0]
        header_text = first_call[0][0]
        assert "אשלג יומי" in header_text
        assert "═══════════════════" in header_text

        # Verify last message is the footer
        last_call = mock_update.effective_message.reply_text.call_args_list[-1]
        footer_text = last_call[0][0]
        assert footer_text == "═══════════════════"

    @pytest.mark.asyncio
    async def test_today_command_uses_html_parse_mode(
        self, mock_update, mock_context, mock_repository
    ):
        """All messages should use HTML parse mode."""
        with patch("src.bot.handlers.QuoteRepository", return_value=mock_repository):
            with patch("src.bot.handlers.get_settings") as mock_settings:
                settings = MagicMock()
                settings.dry_run = False
                mock_settings.return_value = settings

                with patch("src.bot.handlers.is_rate_limited", return_value=False):
                    with patch(
                        "src.bot.handlers.asyncio.sleep", new_callable=AsyncMock
                    ):
                        await today_command(mock_update, mock_context)

        # All calls should have parse_mode="HTML"
        for call in mock_update.effective_message.reply_text.call_args_list:
            kwargs = call[1]
            assert (
                kwargs.get("parse_mode") == "HTML"
            ), f"Missing HTML parse mode in: {call}"

    @pytest.mark.asyncio
    async def test_today_command_dry_run_mode(
        self, mock_update, mock_context, mock_repository
    ):
        """In dry_run mode, should only send a single message."""
        with patch("src.bot.handlers.QuoteRepository", return_value=mock_repository):
            with patch("src.bot.handlers.get_settings") as mock_settings:
                settings = MagicMock()
                settings.dry_run = True  # Enable dry run
                mock_settings.return_value = settings

                with patch("src.bot.handlers.is_rate_limited", return_value=False):
                    await today_command(mock_update, mock_context)

        # Should only send one message (the dry run message)
        call_count = mock_update.effective_message.reply_text.call_count
        assert call_count == 1, f"Expected 1 message in dry run, got {call_count}"

        # Verify it's the dry run message
        message = mock_update.effective_message.reply_text.call_args[0][0]
        assert "[DRY RUN]" in message
        assert "6 quotes" in message

    @pytest.mark.asyncio
    async def test_today_command_respects_rate_limit(
        self, mock_update, mock_context, mock_repository
    ):
        """When rate limited, should not send quotes."""
        with patch("src.bot.handlers.QuoteRepository", return_value=mock_repository):
            with patch("src.bot.handlers.get_settings") as mock_settings:
                settings = MagicMock()
                settings.dry_run = False
                mock_settings.return_value = settings

                with patch("src.bot.handlers.is_rate_limited", return_value=True):
                    await today_command(mock_update, mock_context)

        # Should only send rate limit message
        call_count = mock_update.effective_message.reply_text.call_count
        assert (
            call_count == 1
        ), f"Expected 1 message when rate limited, got {call_count}"

        message = mock_update.effective_message.reply_text.call_args[0][0]
        assert "אנא המתינו" in message or "Please wait" in message

    @pytest.mark.asyncio
    async def test_today_command_handles_empty_bundle(self, mock_update, mock_context):
        """Should handle case when no quotes are available."""
        empty_bundle = DailyBundle(date=date.today(), quotes=[])

        mock_repo = MagicMock()
        mock_repo.get_daily_bundle.return_value = empty_bundle

        with patch("src.bot.handlers.QuoteRepository", return_value=mock_repo):
            with patch("src.bot.handlers.get_settings") as mock_settings:
                settings = MagicMock()
                settings.dry_run = False
                mock_settings.return_value = settings

                with patch("src.bot.handlers.is_rate_limited", return_value=False):
                    await today_command(mock_update, mock_context)

        # Should send "no quotes available" message
        call_count = mock_update.effective_message.reply_text.call_count
        assert call_count == 1

        message = mock_update.effective_message.reply_text.call_args[0][0]
        assert "No quotes available" in message or "אין ציטוטים" in message


class TestQuoteDataValidation:
    """Tests for validating the actual quote data files."""

    def test_all_quote_files_are_valid_json(self):
        """All quote files should be valid JSON."""
        quotes_dir = Path(__file__).parent.parent.parent / "data" / "quotes"

        if not quotes_dir.exists():
            pytest.skip("Quotes directory not found")

        for json_file in quotes_dir.glob("*.json"):
            with open(json_file, encoding="utf-8") as f:
                try:
                    data = json.load(f)
                    assert "quotes" in data, f"{json_file.name} missing 'quotes' key"
                except json.JSONDecodeError as e:
                    pytest.fail(f"{json_file.name} is not valid JSON: {e}")

    def test_all_quotes_have_required_fields(self):
        """All quotes should have required fields."""
        quotes_dir = Path(__file__).parent.parent.parent / "data" / "quotes"

        if not quotes_dir.exists():
            pytest.skip("Quotes directory not found")

        required_fields = ["id", "text", "source_rabbi", "source_url", "category"]

        for json_file in quotes_dir.glob("*.json"):
            with open(json_file, encoding="utf-8") as f:
                data = json.load(f)

            for i, quote in enumerate(data.get("quotes", [])):
                for field in required_fields:
                    assert (
                        field in quote
                    ), f"{json_file.name} quote {i} missing '{field}'"

    def test_all_quotes_can_be_loaded_as_models(self):
        """All quotes should be valid according to the Quote model."""
        quotes_dir = Path(__file__).parent.parent.parent / "data" / "quotes"

        if not quotes_dir.exists():
            pytest.skip("Quotes directory not found")

        total_loaded = 0
        errors = []

        for json_file in quotes_dir.glob("*.json"):
            with open(json_file, encoding="utf-8") as f:
                data = json.load(f)

            for i, quote_data in enumerate(data.get("quotes", [])):
                try:
                    Quote.model_validate(quote_data)
                    total_loaded += 1
                except Exception as e:
                    errors.append(f"{json_file.name} quote {i}: {e}")

        if errors:
            pytest.fail(
                f"Found {len(errors)} invalid quotes:\n" + "\n".join(errors[:10])
            )

        print(f"Successfully validated {total_loaded} quotes")
        assert total_loaded > 0, "No quotes were loaded"

    def test_all_categories_have_quotes(self):
        """Each category should have at least one quote."""
        quotes_dir = Path(__file__).parent.parent.parent / "data" / "quotes"

        if not quotes_dir.exists():
            pytest.skip("Quotes directory not found")

        categories_found = set()

        for json_file in quotes_dir.glob("*.json"):
            with open(json_file, encoding="utf-8") as f:
                data = json.load(f)

            for quote_data in data.get("quotes", []):
                category = quote_data.get("category")
                if category:
                    categories_found.add(category)

        expected_categories = {cat.value for cat in QuoteCategory}
        missing = expected_categories - categories_found

        if missing:
            pytest.fail(f"Missing quotes for categories: {missing}")


class TestFormattersWithRealData:
    """Test formatters with real quote data."""

    def test_format_quote_with_all_categories(self):
        """format_quote should work for all category types."""
        quotes_dir = Path(__file__).parent.parent.parent / "data" / "quotes"

        if not quotes_dir.exists():
            pytest.skip("Quotes directory not found")

        repo = QuoteRepository(quotes_dir=quotes_dir)

        for category in QuoteCategory:
            quotes = repo.get_all_by_category(category)
            if quotes:
                quote = quotes[0]
                formatted = format_quote(quote)

                assert isinstance(formatted, str)
                assert len(formatted) > 0
                assert "<b>" in formatted

                # Verify HTML is valid (no unclosed tags)
                assert formatted.count("<b>") == formatted.count("</b>")

    def test_build_source_keyboard_with_real_urls(self):
        """build_source_keyboard should work with real quote URLs."""
        quotes_dir = Path(__file__).parent.parent.parent / "data" / "quotes"

        if not quotes_dir.exists():
            pytest.skip("Quotes directory not found")

        repo = QuoteRepository(quotes_dir=quotes_dir)

        for category in QuoteCategory:
            quotes = repo.get_all_by_category(category)
            if quotes:
                quote = quotes[0]
                keyboard = build_source_keyboard(quote)

                # All real quotes should have source URLs
                assert keyboard is not None
                assert hasattr(keyboard, "inline_keyboard")
                assert len(keyboard.inline_keyboard) > 0
