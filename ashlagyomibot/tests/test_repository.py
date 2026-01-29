"""Tests for the quote repository."""

from datetime import date

from src.data.models import Quote, QuoteCategory
from src.data.repository import QuoteRepository


class TestQuoteRepository:
    """Tests for QuoteRepository class."""

    def test_get_all_by_category(self, mock_repository: QuoteRepository) -> None:
        """Should return all quotes for a category."""
        quotes = mock_repository.get_all_by_category(QuoteCategory.BAAL_HASULAM)
        assert isinstance(quotes, list)
        assert len(quotes) == 1
        assert quotes[0].category == QuoteCategory.BAAL_HASULAM

    def test_get_all_by_category_empty(self, mock_repository: QuoteRepository) -> None:
        """Should return empty list for category with no quotes."""
        # Remove all quotes from cache to simulate empty category
        mock_repository._quotes_cache = {cat: [] for cat in QuoteCategory}
        quotes = mock_repository.get_all_by_category(QuoteCategory.ARIZAL)
        assert quotes == []

    def test_get_random_by_category(self, mock_repository: QuoteRepository) -> None:
        """Should return a random quote from category."""
        quote = mock_repository.get_random_by_category(QuoteCategory.BAAL_HASULAM)
        assert quote is not None
        assert quote.category == QuoteCategory.BAAL_HASULAM

    def test_get_random_respects_exclusions(
        self, mock_repository: QuoteRepository
    ) -> None:
        """Should exclude specified quote IDs."""
        # Get the only quote in the category
        quotes = mock_repository.get_all_by_category(QuoteCategory.BAAL_HASULAM)
        assert len(quotes) == 1

        # Exclude it - should still return it (rotation reset)
        quote = mock_repository.get_random_by_category(
            QuoteCategory.BAAL_HASULAM,
            exclude_ids={quotes[0].id},
        )
        # With only one quote, excluding it triggers rotation reset
        assert quote is not None

    def test_get_random_returns_none_for_empty_category(
        self, mock_repository: QuoteRepository
    ) -> None:
        """Should return None if category has no quotes."""
        mock_repository._quotes_cache = {cat: [] for cat in QuoteCategory}
        quote = mock_repository.get_random_by_category(QuoteCategory.ARIZAL)
        assert quote is None

    def test_get_random_quote(self, mock_repository: QuoteRepository) -> None:
        """Should return a random quote from any category."""
        quote = mock_repository.get_random_quote()
        assert quote is not None
        assert isinstance(quote, Quote)

    def test_get_random_quote_returns_none_when_empty(
        self, mock_repository: QuoteRepository
    ) -> None:
        """Should return None if no quotes available."""
        mock_repository._quotes_cache = {cat: [] for cat in QuoteCategory}
        quote = mock_repository.get_random_quote()
        assert quote is None

    def test_mark_as_sent(self, mock_repository: QuoteRepository) -> None:
        """Should record sent quote in history."""
        quote = mock_repository.get_random_by_category(QuoteCategory.BAAL_HASULAM)
        assert quote is not None

        mock_repository.mark_as_sent(quote, date(2024, 1, 15))

        sent_ids = mock_repository.get_sent_ids_by_category(QuoteCategory.BAAL_HASULAM)
        assert quote.id in sent_ids

    def test_get_daily_bundle(self, mock_repository: QuoteRepository) -> None:
        """Should generate a daily bundle with quotes from all categories."""
        bundle = mock_repository.get_daily_bundle(date(2024, 1, 15))

        assert bundle.date == date(2024, 1, 15)
        assert len(bundle.quotes) == 6  # One per category

        # Check all categories are represented
        categories = {q.category for q in bundle.quotes}
        assert categories == set(QuoteCategory)

    def test_clear_history(self, mock_repository: QuoteRepository) -> None:
        """Should clear all sent history."""
        # First, mark some quotes as sent
        quote = mock_repository.get_random_by_category(QuoteCategory.BAAL_HASULAM)
        assert quote is not None
        mock_repository.mark_as_sent(quote, date.today())

        # Verify it was recorded
        assert (
            len(mock_repository.get_sent_ids_by_category(QuoteCategory.BAAL_HASULAM))
            > 0
        )

        # Clear and verify
        mock_repository.clear_history()
        assert (
            len(mock_repository.get_sent_ids_by_category(QuoteCategory.BAAL_HASULAM))
            == 0
        )

    def test_validate_all(self, mock_repository: QuoteRepository) -> None:
        """Should return statistics about loaded quotes."""
        stats = mock_repository.validate_all()

        assert "total" in stats
        assert stats["total"] == 6  # One per category
        assert stats["baal_hasulam"] == 1


class TestRepositoryPersistence:
    """Tests for repository persistence (loading/saving JSON)."""

    def test_loads_quotes_from_json_files(
        self, mock_repository: QuoteRepository
    ) -> None:
        """Should load quotes from JSON files on initialization."""
        # Force reload
        mock_repository._quotes_cache = None
        quotes = mock_repository.get_all_by_category(QuoteCategory.BAAL_HASULAM)
        assert len(quotes) == 1

    def test_saves_and_loads_history(self, mock_repository: QuoteRepository) -> None:
        """History should persist across repository instances."""
        # Mark a quote as sent
        quote = mock_repository.get_random_by_category(QuoteCategory.BAAL_HASULAM)
        assert quote is not None
        mock_repository.mark_as_sent(quote, date(2024, 1, 15))

        # Create new repository instance with same files
        new_repo = QuoteRepository(
            quotes_dir=mock_repository._quotes_dir,
            history_file=mock_repository._history_file,
        )

        # Should have the same history
        sent_ids = new_repo.get_sent_ids_by_category(QuoteCategory.BAAL_HASULAM)
        assert quote.id in sent_ids
