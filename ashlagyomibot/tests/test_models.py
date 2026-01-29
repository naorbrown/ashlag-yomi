"""Tests for data models."""

from datetime import date

import pytest
from pydantic import ValidationError

from src.data.models import (
    DailyBundle,
    DailyMaamar,
    Maamar,
    MaamarCollection,
    MaamarSentRecord,
    Quote,
    QuoteCategory,
    SentRecord,
    SourceCategory,
)

# =============================================================================
# NEW MAAMAR MODEL TESTS
# =============================================================================


class TestSourceCategory:
    """Tests for SourceCategory enum."""

    def test_all_sources_have_hebrew_names(self) -> None:
        """Every source should have a Hebrew display name."""
        for source in SourceCategory:
            assert source.display_name_hebrew
            # Hebrew text should contain Hebrew characters
            assert any("\u0590" <= c <= "\u05ff" for c in source.display_name_hebrew)

    def test_all_sources_have_english_names(self) -> None:
        """Every source should have an English display name."""
        for source in SourceCategory:
            assert source.display_name_english
            # English text should contain ASCII letters
            assert any(c.isascii() and c.isalpha() for c in source.display_name_english)

    def test_all_sources_have_website(self) -> None:
        """Every source should have a website URL."""
        for source in SourceCategory:
            assert source.source_website
            assert source.source_website.startswith("https://")

    def test_source_count(self) -> None:
        """There should be exactly 2 sources (Baal Hasulam + Rabash)."""
        assert len(SourceCategory) == 2

    def test_baal_hasulam_hebrew_name(self) -> None:
        """Baal Hasulam should have correct Hebrew name."""
        assert SourceCategory.BAAL_HASULAM.display_name_hebrew == "בעל הסולם"

    def test_rabash_hebrew_name(self) -> None:
        """Rabash should have correct Hebrew name."""
        assert SourceCategory.RABASH.display_name_hebrew == 'הרב"ש'


class TestMaamar:
    """Tests for Maamar model."""

    def test_valid_maamar_creation(self, sample_maamar: Maamar) -> None:
        """A valid maamar should be created successfully."""
        assert sample_maamar.id == "baal_hasulam_test_001"
        assert sample_maamar.source == SourceCategory.BAAL_HASULAM
        assert "ערבות" in sample_maamar.title

    def test_maamar_is_immutable(self, sample_maamar: Maamar) -> None:
        """Maamarim should be immutable (frozen)."""
        with pytest.raises(ValidationError):
            sample_maamar.title = "new title"  # type: ignore[misc]

    def test_maamar_word_count(self, sample_maamar: Maamar) -> None:
        """Word count should be calculated correctly."""
        assert sample_maamar.word_count > 0

    def test_maamar_char_count(self, sample_maamar: Maamar) -> None:
        """Character count should be calculated correctly."""
        assert sample_maamar.char_count == len(sample_maamar.text)

    def test_maamar_estimated_reading_minutes(self, sample_maamar: Maamar) -> None:
        """Reading time should be calculated (150 words/min)."""
        expected = round(sample_maamar.word_count / 150, 1)
        assert sample_maamar.estimated_reading_minutes == expected

    def test_maamar_telegram_message_count(self, sample_maamar: Maamar) -> None:
        """Should estimate Telegram messages needed."""
        assert sample_maamar.telegram_message_count >= 1

    def test_maamar_full_source_citation(self, sample_maamar: Maamar) -> None:
        """Full citation should include source, book, and page."""
        citation = sample_maamar.full_source_citation
        assert "בעל הסולם" in citation
        assert sample_maamar.book in citation
        assert sample_maamar.page in citation

    def test_maamar_string_representation(self, sample_maamar: Maamar) -> None:
        """String representation should include ID and title."""
        str_repr = str(sample_maamar)
        assert "baal_hasulam_test_001" in str_repr

    def test_maamar_requires_valid_url(self) -> None:
        """Maamar source_url must be a valid HTTP(S) URL."""
        with pytest.raises(ValidationError):
            Maamar(
                id="test",
                source=SourceCategory.BAAL_HASULAM,
                title="Test Title",
                text="Some text here for testing " * 5,
                book="Test Book",
                source_url="not-a-url",  # Invalid!
            )

    def test_maamar_requires_minimum_text_length(self) -> None:
        """Maamar text must have minimum length."""
        with pytest.raises(ValidationError):
            Maamar(
                id="test",
                source=SourceCategory.BAAL_HASULAM,
                title="Test Title",
                text="short",  # Too short!
                book="Test Book",
                source_url="https://example.com",
            )

    def test_maamar_pdf_fields(self, sample_maamar_rabash: Maamar) -> None:
        """PDF-sourced maamarim should have PDF metadata."""
        assert sample_maamar_rabash.pdf_filename == "test.pdf"
        assert sample_maamar_rabash.pdf_start_page == 15
        assert sample_maamar_rabash.pdf_end_page == 17


class TestDailyMaamar:
    """Tests for DailyMaamar model."""

    def test_valid_daily_maamar_creation(
        self, sample_daily_maamar: DailyMaamar
    ) -> None:
        """A valid daily maamar should be created successfully."""
        assert sample_daily_maamar.date == date(2024, 1, 15)
        assert sample_daily_maamar.maamar is not None

    def test_source_name_computed(self, sample_daily_maamar: DailyMaamar) -> None:
        """Source name should be computed from maamar."""
        assert sample_daily_maamar.source_name == "בעל הסולם"


class TestMaamarSentRecord:
    """Tests for MaamarSentRecord model."""

    def test_create_from_maamar(self, sample_maamar: Maamar) -> None:
        """Should create record from maamar."""
        record = MaamarSentRecord.from_maamar(sample_maamar, date(2024, 1, 15))
        assert record.maamar_id == sample_maamar.id
        assert record.sent_date == date(2024, 1, 15)
        assert record.source == sample_maamar.source


class TestMaamarCollection:
    """Tests for MaamarCollection model."""

    def test_valid_collection_creation(self, sample_maamarim: list[Maamar]) -> None:
        """A valid collection should be created successfully."""
        baal_hasulam_maamarim = [
            m for m in sample_maamarim if m.source == SourceCategory.BAAL_HASULAM
        ]
        collection = MaamarCollection(
            source=SourceCategory.BAAL_HASULAM,
            maamarim=baal_hasulam_maamarim,
        )
        assert collection.count == 1
        assert collection.source == SourceCategory.BAAL_HASULAM


# =============================================================================
# LEGACY QUOTE MODEL TESTS (kept for backward compatibility)
# =============================================================================


class TestQuoteCategory:
    """Tests for QuoteCategory enum (legacy)."""

    def test_all_categories_have_hebrew_names(self) -> None:
        """Every category should have a Hebrew display name."""
        for category in QuoteCategory:
            assert category.display_name_hebrew
            # Hebrew text should contain Hebrew characters
            assert any("\u0590" <= c <= "\u05ff" for c in category.display_name_hebrew)

    def test_all_categories_have_english_names(self) -> None:
        """Every category should have an English display name."""
        for category in QuoteCategory:
            assert category.display_name_english
            # English text should contain ASCII letters
            assert any(
                c.isascii() and c.isalpha() for c in category.display_name_english
            )

    def test_category_count(self) -> None:
        """There should be exactly 6 categories."""
        assert len(QuoteCategory) == 6


class TestQuote:
    """Tests for Quote model."""

    def test_valid_quote_creation(self, sample_quote: Quote) -> None:
        """A valid quote should be created successfully."""
        assert sample_quote.id == "test-quote-001"
        assert sample_quote.category == QuoteCategory.BAAL_HASULAM
        assert "שלמות" in sample_quote.text

    def test_quote_is_immutable(self, sample_quote: Quote) -> None:
        """Quotes should be immutable (frozen)."""
        with pytest.raises(ValidationError):
            sample_quote.text = "new text"  # type: ignore[misc]

    def test_quote_word_count(self, sample_quote: Quote) -> None:
        """Word count should be calculated correctly."""
        assert sample_quote.word_count > 0

    def test_quote_string_representation(self, sample_quote: Quote) -> None:
        """String representation should include ID and text preview."""
        str_repr = str(sample_quote)
        assert "test-quote-001" in str_repr

    def test_quote_requires_valid_url(self) -> None:
        """Quote source_url must be a valid HTTP(S) URL."""
        with pytest.raises(ValidationError):
            Quote(
                id="test",
                text="Some text here for testing",
                source_rabbi="Test Rabbi",
                source_url="not-a-url",  # Invalid!
                category=QuoteCategory.BAAL_HASULAM,
            )

    def test_quote_requires_minimum_text_length(self) -> None:
        """Quote text must have minimum length."""
        with pytest.raises(ValidationError):
            Quote(
                id="test",
                text="short",  # Too short!
                source_rabbi="Test Rabbi",
                source_url="https://example.com",
                category=QuoteCategory.BAAL_HASULAM,
            )

    def test_quote_length_estimate_bounds(self) -> None:
        """Length estimate must be within valid bounds."""
        with pytest.raises(ValidationError):
            Quote(
                id="test",
                text="Some valid text for testing",
                source_rabbi="Test Rabbi",
                source_url="https://example.com",
                category=QuoteCategory.BAAL_HASULAM,
                length_estimate=500,  # Too high!
            )


class TestDailyBundle:
    """Tests for DailyBundle model."""

    def test_valid_bundle_creation(self, sample_bundle: DailyBundle) -> None:
        """A valid bundle should be created successfully."""
        assert sample_bundle.date == date(2024, 1, 15)
        assert len(sample_bundle.quotes) == 6

    def test_bundle_total_reading_time(self, sample_bundle: DailyBundle) -> None:
        """Total reading time should be sum of all quote estimates."""
        expected = sum(q.length_estimate for q in sample_bundle.quotes)
        assert sample_bundle.total_reading_time == expected

    def test_bundle_reading_time_in_minutes(self, sample_bundle: DailyBundle) -> None:
        """Reading time in minutes should be calculated correctly."""
        assert sample_bundle.total_reading_time_minutes == round(
            sample_bundle.total_reading_time / 60, 1
        )

    def test_bundle_categories_included(self, sample_bundle: DailyBundle) -> None:
        """Categories included should list all quote categories."""
        categories = sample_bundle.categories_included
        assert len(categories) == 6
        assert QuoteCategory.BAAL_HASULAM in categories

    def test_get_quote_by_category(self, sample_bundle: DailyBundle) -> None:
        """Should be able to retrieve quote by category."""
        quote = sample_bundle.get_quote_by_category(QuoteCategory.BAAL_HASULAM)
        assert quote is not None
        assert quote.category == QuoteCategory.BAAL_HASULAM

    def test_get_quote_by_missing_category(self, sample_quote: Quote) -> None:
        """Should return None for missing category."""
        # Bundle with only one quote
        bundle = DailyBundle(date=date.today(), quotes=[sample_quote])
        quote = bundle.get_quote_by_category(QuoteCategory.ARIZAL)
        assert quote is None


class TestSentRecord:
    """Tests for SentRecord model."""

    def test_create_from_quote(self, sample_quote: Quote) -> None:
        """Should create record from quote."""
        record = SentRecord.from_quote(sample_quote, date(2024, 1, 15))
        assert record.quote_id == sample_quote.id
        assert record.sent_date == date(2024, 1, 15)
        assert record.category == sample_quote.category
