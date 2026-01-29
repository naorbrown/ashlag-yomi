"""Tests for data models."""

from datetime import date, datetime

import pytest
from pydantic import ValidationError

from src.data.models import DailyBundle, Quote, QuoteCategory, SentRecord


class TestQuoteCategory:
    """Tests for QuoteCategory enum."""

    def test_all_categories_have_hebrew_names(self) -> None:
        """Every category should have a Hebrew display name."""
        for category in QuoteCategory:
            assert category.display_name_hebrew
            # Hebrew text should contain Hebrew characters
            assert any("\u0590" <= c <= "\u05FF" for c in category.display_name_hebrew)

    def test_all_categories_have_english_names(self) -> None:
        """Every category should have an English display name."""
        for category in QuoteCategory:
            assert category.display_name_english
            # English text should contain ASCII letters
            assert any(c.isascii() and c.isalpha() for c in category.display_name_english)

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
