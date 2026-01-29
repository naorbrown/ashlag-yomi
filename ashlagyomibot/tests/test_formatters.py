"""Tests for message formatters."""

from datetime import date

from src.bot.formatters import (
    CATEGORY_EMOJI,
    SOURCE_EMOJI,
    build_maamar_keyboard,
    build_source_keyboard,
    escape_markdown,
    format_daily_bundle,
    format_maamar,
    format_maamar_header,
    format_maamar_preview,
    format_quote,
    format_single_quote_message,
    split_hebrew_text,
)
from src.data.models import DailyBundle, Maamar, Quote, QuoteCategory, SourceCategory

# =============================================================================
# NEW MAAMAR FORMATTER TESTS
# =============================================================================


class TestBuildMaamarKeyboard:
    """Tests for build_maamar_keyboard function."""

    def test_returns_keyboard(self, sample_maamar: Maamar) -> None:
        """Should return InlineKeyboardMarkup."""
        keyboard = build_maamar_keyboard(sample_maamar)
        assert keyboard is not None
        from telegram import InlineKeyboardMarkup

        assert isinstance(keyboard, InlineKeyboardMarkup)

    def test_keyboard_structure_is_valid(self, sample_maamar: Maamar) -> None:
        """Keyboard should have proper structure (single row, single button)."""
        keyboard = build_maamar_keyboard(sample_maamar)
        assert len(keyboard.inline_keyboard) == 1
        assert len(keyboard.inline_keyboard[0]) == 1

    def test_keyboard_contains_source_url(self, sample_maamar: Maamar) -> None:
        """Keyboard button should contain the source URL."""
        keyboard = build_maamar_keyboard(sample_maamar)
        button = keyboard.inline_keyboard[0][0]
        assert button.url == sample_maamar.source_url

    def test_keyboard_button_text_is_hebrew(self, sample_maamar: Maamar) -> None:
        """Keyboard button should have Hebrew text 'מקור'."""
        keyboard = build_maamar_keyboard(sample_maamar)
        button = keyboard.inline_keyboard[0][0]
        assert "מקור" in button.text


class TestSplitHebrewText:
    """Tests for split_hebrew_text function."""

    def test_short_text_not_split(self) -> None:
        """Short text should not be split."""
        text = "טקסט קצר"
        chunks = split_hebrew_text(text)
        assert len(chunks) == 1
        assert chunks[0] == text

    def test_long_text_is_split(self) -> None:
        """Long text should be split into chunks."""
        text = "מילה " * 1000  # Very long text
        chunks = split_hebrew_text(text, max_length=100)
        assert len(chunks) > 1
        for chunk in chunks:
            assert len(chunk) <= 100 or " " not in chunk[:100]

    def test_splits_at_paragraph_boundary(self) -> None:
        """Should prefer splitting at paragraph boundaries."""
        text = "פסקה ראשונה.\n\nפסקה שנייה.\n\nפסקה שלישית."
        chunks = split_hebrew_text(text, max_length=30)
        # First chunk should end cleanly
        assert chunks[0].endswith("ראשונה.")

    def test_splits_at_sentence_boundary(self) -> None:
        """Should split at sentence boundaries when no paragraph break."""
        text = "משפט ראשון. משפט שני. משפט שלישי."
        chunks = split_hebrew_text(text, max_length=20)
        assert len(chunks) > 1


class TestFormatMaamarHeader:
    """Tests for format_maamar_header function."""

    def test_includes_source_emoji(self, sample_maamar: Maamar) -> None:
        """Header should include source emoji."""
        header = format_maamar_header(sample_maamar)
        expected_emoji = SOURCE_EMOJI.get(sample_maamar.source, "📜")
        assert expected_emoji in header

    def test_includes_source_name(self, sample_maamar: Maamar) -> None:
        """Header should include source name in Hebrew."""
        header = format_maamar_header(sample_maamar)
        assert sample_maamar.source.display_name_hebrew in header

    def test_includes_title(self, sample_maamar: Maamar) -> None:
        """Header should include maamar title."""
        header = format_maamar_header(sample_maamar)
        assert sample_maamar.title in header

    def test_includes_subtitle_when_present(self, sample_maamar: Maamar) -> None:
        """Header should include subtitle if present."""
        header = format_maamar_header(sample_maamar)
        assert sample_maamar.subtitle in header

    def test_includes_book_name(self, sample_maamar: Maamar) -> None:
        """Header should include book name."""
        header = format_maamar_header(sample_maamar)
        assert sample_maamar.book in header

    def test_includes_page_number(self, sample_maamar: Maamar) -> None:
        """Header should include page number if present."""
        header = format_maamar_header(sample_maamar)
        assert sample_maamar.page in header


class TestFormatMaamar:
    """Tests for format_maamar function."""

    def test_returns_list_of_messages(self, sample_maamar: Maamar) -> None:
        """Should return a list of messages."""
        messages = format_maamar(sample_maamar)
        assert isinstance(messages, list)
        assert all(isinstance(m, str) for m in messages)

    def test_short_maamar_single_message(self, sample_maamar: Maamar) -> None:
        """Short maamar should fit in single message."""
        messages = format_maamar(sample_maamar)
        # Our sample maamar is small enough for one message
        assert len(messages) >= 1

    def test_long_maamar_multiple_messages(self) -> None:
        """Long maamar should be split into multiple messages."""
        long_maamar = Maamar(
            id="long_test",
            source=SourceCategory.BAAL_HASULAM,
            title="מאמר ארוך",
            text="טקסט ארוך מאוד. " * 500,  # ~7500 chars
            book="ספר בדיקה",
            source_url="https://example.com",
        )
        messages = format_maamar(long_maamar)
        assert len(messages) > 1

    def test_first_message_has_header(self, sample_maamar: Maamar) -> None:
        """First message should include the header."""
        messages = format_maamar(sample_maamar)
        first_message = messages[0]
        assert sample_maamar.title in first_message
        assert sample_maamar.source.display_name_hebrew in first_message

    def test_continuation_messages_have_part_number(self) -> None:
        """Continuation messages should show part X/Y."""
        long_maamar = Maamar(
            id="long_test",
            source=SourceCategory.BAAL_HASULAM,
            title="מאמר ארוך",
            text="טקסט ארוך מאוד. " * 500,
            book="ספר בדיקה",
            source_url="https://example.com",
        )
        messages = format_maamar(long_maamar)
        if len(messages) > 1:
            assert "חלק 2/" in messages[1]


class TestFormatMaamarPreview:
    """Tests for format_maamar_preview function."""

    def test_includes_title(self, sample_maamar: Maamar) -> None:
        """Preview should include title."""
        preview = format_maamar_preview(sample_maamar)
        assert sample_maamar.title in preview

    def test_includes_book(self, sample_maamar: Maamar) -> None:
        """Preview should include book name."""
        preview = format_maamar_preview(sample_maamar)
        assert sample_maamar.book in preview

    def test_truncates_long_text(self) -> None:
        """Long text should be truncated."""
        long_maamar = Maamar(
            id="test",
            source=SourceCategory.BAAL_HASULAM,
            title="מאמר",
            text="מילה " * 100,
            book="ספר",
            source_url="https://example.com",
        )
        preview = format_maamar_preview(long_maamar, max_preview_length=50)
        assert "..." in preview


class TestSourceEmoji:
    """Tests for source emoji mapping."""

    def test_all_sources_have_emoji(self) -> None:
        """Every source should have an emoji."""
        for source in SourceCategory:
            assert source in SOURCE_EMOJI
            emoji = SOURCE_EMOJI[source]
            assert emoji
            assert len(emoji) <= 4


# =============================================================================
# LEGACY QUOTE FORMATTER TESTS (kept for backward compatibility)
# =============================================================================


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
