"""Tests for message formatters."""

from datetime import date

import pytest

from src.bot.formatters import (
    CATEGORY_EMOJI,
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

    def test_includes_source_link(self, sample_quote: Quote) -> None:
        """Formatted quote should include source URL as markdown link."""
        formatted = format_quote(sample_quote)
        assert "מקור" in formatted
        assert sample_quote.source_url in formatted

    def test_excludes_source_link_when_disabled(self, sample_quote: Quote) -> None:
        """Should not include source link when disabled."""
        formatted = format_quote(sample_quote, include_source_link=False)
        assert "מקור]" not in formatted

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

    def test_includes_reading_time(self, sample_bundle: DailyBundle) -> None:
        """Header should include estimated reading time."""
        messages = format_daily_bundle(sample_bundle)
        header = messages[0]
        assert "דקות" in header

    def test_includes_all_quotes(self, sample_bundle: DailyBundle) -> None:
        """Should include all quotes from the bundle."""
        messages = format_daily_bundle(sample_bundle)
        # Header + 7 quotes + footer = 9 messages
        assert len(messages) == 9

    def test_includes_footer(self, sample_bundle: DailyBundle) -> None:
        """Last message should be a footer."""
        messages = format_daily_bundle(sample_bundle)
        footer = messages[-1]
        assert "/today" in footer
        assert "/about" in footer

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

    def test_includes_footer_commands(self, sample_quote: Quote) -> None:
        """Should include command references."""
        formatted = format_single_quote_message(sample_quote)
        assert "/today" in formatted
        assert "/about" in formatted


class TestEscapeMarkdown:
    """Tests for escape_markdown function."""

    def test_escapes_asterisks(self) -> None:
        """Should escape asterisks."""
        assert escape_markdown("*bold*") == "\\*bold\\*"

    def test_escapes_underscores(self) -> None:
        """Should escape underscores."""
        assert escape_markdown("_italic_") == "\\_italic\\_"

    def test_escapes_brackets(self) -> None:
        """Should escape brackets."""
        assert escape_markdown("[link](url)") == "\\[link\\]\\(url\\)"

    def test_preserves_regular_text(self) -> None:
        """Should not modify regular text."""
        text = "שלום עולם"
        assert escape_markdown(text) == text


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
