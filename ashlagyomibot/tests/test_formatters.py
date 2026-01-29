"""Tests for message formatters."""

from datetime import date

import pytest

from src.bot.formatters import (
    CATEGORY_EMOJI,
    build_source_keyboard,
    escape_markdown,
    format_daily_bundle,
    format_quote,
    format_single_quote_message,
)
from src.data.models import DailyBundle, Quote, QuoteCategory


class TestFormatQuote:
    """Tests for format_quote function."""

    def test_includes_rabbi_name(self, sample_quote: Quote) -> None:
        """Formatted quote should include the rabbi's name."""
        formatted = format_quote(sample_quote)
        assert sample_quote.category.display_name_hebrew in formatted

    def test_includes_quote_text(self, sample_quote: Quote) -> None:
        """Formatted quote should include the quote text."""
        formatted = format_quote(sample_quote)
        # Text is wrapped in Hebrew quotation marks
        assert "״" in formatted
        assert sample_quote.text in formatted

    def test_no_inline_link_in_text(self, sample_quote: Quote) -> None:
        """Source link should NOT be in text (moved to keyboard per nachyomi-bot pattern)."""
        formatted = format_quote(sample_quote)
        # Links are now in inline keyboard, not in message text
        assert '<a href="' not in formatted

    def test_source_book_in_text(self, sample_quote: Quote) -> None:
        """Source book attribution should still be in text."""
        formatted = format_quote(sample_quote)
        assert "📚" in formatted
        assert sample_quote.source_book in formatted

    def test_includes_category_emoji(self, sample_quote: Quote) -> None:
        """Formatted quote should include the category emoji."""
        formatted = format_quote(sample_quote)
        expected_emoji = CATEGORY_EMOJI[sample_quote.category]
        assert expected_emoji in formatted

    def test_includes_source_book_when_present(self, sample_quote: Quote) -> None:
        """Should include source book if present."""
        formatted = format_quote(sample_quote)
        assert sample_quote.source_book in formatted  # type: ignore[operator]

    def test_includes_source_section_when_present(self, sample_quote: Quote) -> None:
        """Should include source section if present."""
        formatted = format_quote(sample_quote)
        assert sample_quote.source_section in formatted  # type: ignore[operator]


class TestFormatDailyBundle:
    """Tests for format_daily_bundle function."""

    def test_returns_list_of_messages(self, sample_bundle: DailyBundle) -> None:
        """Should return a list of messages."""
        messages = format_daily_bundle(sample_bundle)
        assert isinstance(messages, list)
        assert all(isinstance(m, str) for m in messages)

    def test_includes_header(self, sample_bundle: DailyBundle) -> None:
        """First message should be a header with date."""
        messages = format_daily_bundle(sample_bundle)
        header = messages[0]
        assert "אשלג יומי" in header
        assert "15.01.2024" in header

    def test_header_format(self, sample_bundle: DailyBundle) -> None:
        """Header should include date and separator."""
        messages = format_daily_bundle(sample_bundle)
        header = messages[0]
        assert "═══════════════════" in header

    def test_includes_all_quotes(self, sample_bundle: DailyBundle) -> None:
        """Should include all quotes from the bundle."""
        messages = format_daily_bundle(sample_bundle)
        # Header + 6 quotes + footer = 8 messages
        assert len(messages) == 8

    def test_includes_footer(self, sample_bundle: DailyBundle) -> None:
        """Last message should be a footer separator."""
        messages = format_daily_bundle(sample_bundle)
        footer = messages[-1]
        assert "═══════════════════" in footer

    def test_empty_bundle_handling(self, sample_quotes: list[Quote]) -> None:
        """Should handle bundle with single quote gracefully."""
        # Cannot create empty bundle due to validation, test with minimal
        single_bundle = DailyBundle(date=date.today(), quotes=[sample_quotes[0]])
        messages = format_daily_bundle(single_bundle)
        assert len(messages) >= 3  # header, quote, footer


class TestFormatSingleQuoteMessage:
    """Tests for format_single_quote_message function."""

    def test_includes_header(self, sample_quote: Quote) -> None:
        """Should include a header."""
        formatted = format_single_quote_message(sample_quote)
        assert "ציטוט יומי" in formatted

    def test_includes_formatted_quote(self, sample_quote: Quote) -> None:
        """Should include the formatted quote."""
        formatted = format_single_quote_message(sample_quote)
        assert sample_quote.text in formatted

    def test_includes_footer_separator(self, sample_quote: Quote) -> None:
        """Should include footer separator."""
        formatted = format_single_quote_message(sample_quote)
        assert "═══════════════════" in formatted


class TestEscapeHtml:
    """Tests for escape_html function (alias: escape_markdown)."""

    def test_escapes_ampersand(self) -> None:
        """Should escape ampersands."""
        assert escape_markdown("a & b") == "a &amp; b"

    def test_escapes_less_than(self) -> None:
        """Should escape less-than signs."""
        assert escape_markdown("<tag>") == "&lt;tag&gt;"

    def test_escapes_greater_than(self) -> None:
        """Should escape greater-than signs."""
        assert escape_markdown("a > b") == "a &gt; b"

    def test_preserves_regular_text(self) -> None:
        """Should not modify regular text."""
        text = "שלום עולם"
        assert escape_markdown(text) == text


class TestBuildSourceKeyboard:
    """Tests for build_source_keyboard function (nachyomi-bot pattern)."""

    def test_returns_keyboard_when_source_url_exists(self, sample_quote: Quote) -> None:
        """Should return InlineKeyboardMarkup when quote has source_url."""
        keyboard = build_source_keyboard(sample_quote)
        assert keyboard is not None
        # Verify it's the correct type
        from telegram import InlineKeyboardMarkup
        assert isinstance(keyboard, InlineKeyboardMarkup)

    def test_keyboard_structure_is_valid(self, sample_quote: Quote) -> None:
        """Keyboard should have proper structure (single row, single button)."""
        keyboard = build_source_keyboard(sample_quote)
        assert keyboard is not None
        # Should have exactly one row
        assert len(keyboard.inline_keyboard) == 1
        # Row should have exactly one button
        assert len(keyboard.inline_keyboard[0]) == 1

    def test_keyboard_contains_source_url(self, sample_quote: Quote) -> None:
        """Keyboard button should contain the source URL."""
        keyboard = build_source_keyboard(sample_quote)
        assert keyboard is not None
        # Access the button
        button = keyboard.inline_keyboard[0][0]
        assert button.url == sample_quote.source_url

    def test_keyboard_button_text_is_hebrew(self, sample_quote: Quote) -> None:
        """Keyboard button should have Hebrew text 'מקור'."""
        keyboard = build_source_keyboard(sample_quote)
        assert keyboard is not None
        button = keyboard.inline_keyboard[0][0]
        assert "מקור" in button.text


class TestCategoryEmoji:
    """Tests for category emoji mapping."""

    def test_all_categories_have_emoji(self) -> None:
        """Every category should have an emoji."""
        for category in QuoteCategory:
            assert category in CATEGORY_EMOJI
            emoji = CATEGORY_EMOJI[category]
            assert emoji
            # Emoji should be a single or double-width character
            assert len(emoji) <= 4
