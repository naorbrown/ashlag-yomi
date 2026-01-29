"""Tests for the maamar repository."""

from datetime import date

from src.data.maamar_repository import MaamarRepository
from src.data.models import Maamar, SourceCategory


class TestMaamarRepository:
    """Tests for MaamarRepository class."""

    def test_get_all_by_source(self, mock_maamar_repository: MaamarRepository) -> None:
        """Should return all maamarim for a source."""
        maamarim = mock_maamar_repository.get_all_by_source(SourceCategory.BAAL_HASULAM)
        assert isinstance(maamarim, list)
        assert len(maamarim) == 1
        assert maamarim[0].source == SourceCategory.BAAL_HASULAM

    def test_get_all_by_source_empty(
        self, mock_maamar_repository: MaamarRepository
    ) -> None:
        """Should return empty list for source with no maamarim."""
        # Clear the cache to simulate empty
        mock_maamar_repository._maamarim_cache = {cat: [] for cat in SourceCategory}
        maamarim = mock_maamar_repository.get_all_by_source(SourceCategory.BAAL_HASULAM)
        assert maamarim == []

    def test_get_all_maamarim(self, mock_maamar_repository: MaamarRepository) -> None:
        """Should return all maamarim from all sources."""
        maamarim = mock_maamar_repository.get_all_maamarim()
        assert len(maamarim) == 2  # One from each source

    def test_get_random_by_source(
        self, mock_maamar_repository: MaamarRepository
    ) -> None:
        """Should return a random maamar from source."""
        maamar = mock_maamar_repository.get_random_by_source(
            SourceCategory.BAAL_HASULAM
        )
        assert maamar is not None
        assert maamar.source == SourceCategory.BAAL_HASULAM

    def test_get_random_respects_exclusions(
        self, mock_maamar_repository: MaamarRepository
    ) -> None:
        """Should exclude specified maamar IDs."""
        # Get the only maamar in the source
        maamarim = mock_maamar_repository.get_all_by_source(SourceCategory.BAAL_HASULAM)
        assert len(maamarim) == 1

        # Exclude it - should still return it (rotation reset)
        maamar = mock_maamar_repository.get_random_by_source(
            SourceCategory.BAAL_HASULAM,
            exclude_ids={maamarim[0].id},
        )
        # With only one maamar, excluding it triggers rotation reset
        assert maamar is not None

    def test_get_random_returns_none_for_empty_source(
        self, mock_maamar_repository: MaamarRepository
    ) -> None:
        """Should return None if source has no maamarim."""
        mock_maamar_repository._maamarim_cache = {cat: [] for cat in SourceCategory}
        maamar = mock_maamar_repository.get_random_by_source(
            SourceCategory.BAAL_HASULAM
        )
        assert maamar is None

    def test_get_random_maamar(self, mock_maamar_repository: MaamarRepository) -> None:
        """Should return a random maamar from any source."""
        maamar = mock_maamar_repository.get_random_maamar()
        assert maamar is not None
        assert isinstance(maamar, Maamar)

    def test_get_random_maamar_returns_none_when_empty(
        self, mock_maamar_repository: MaamarRepository
    ) -> None:
        """Should return None if no maamarim available."""
        mock_maamar_repository._maamarim_cache = {cat: [] for cat in SourceCategory}
        maamar = mock_maamar_repository.get_random_maamar()
        assert maamar is None

    def test_mark_as_sent(self, mock_maamar_repository: MaamarRepository) -> None:
        """Should record sent maamar in history."""
        maamar = mock_maamar_repository.get_random_by_source(
            SourceCategory.BAAL_HASULAM
        )
        assert maamar is not None

        mock_maamar_repository.mark_as_sent(maamar, date(2024, 1, 15))

        sent_ids = mock_maamar_repository.get_sent_ids_by_source(
            SourceCategory.BAAL_HASULAM
        )
        assert maamar.id in sent_ids

    def test_get_daily_maamarim(self, mock_maamar_repository: MaamarRepository) -> None:
        """Should return one maamar from each source."""
        maamarim = mock_maamar_repository.get_daily_maamarim()

        assert len(maamarim) == 2  # One per source

        # Check all sources are represented
        sources = {m.source for m in maamarim}
        assert sources == set(SourceCategory)

    def test_get_daily_maamarim_respects_fair_rotation(
        self, mock_maamar_repository: MaamarRepository
    ) -> None:
        """Should use fair rotation to avoid repeating maamarim."""
        # Get daily maamarim
        maamarim = mock_maamar_repository.get_daily_maamarim()

        # Mark them as sent
        for maamar in maamarim:
            mock_maamar_repository.mark_as_sent(maamar, date.today())

        # Get daily maamarim again - should still return (rotation reset with 1 per source)
        maamarim2 = mock_maamar_repository.get_daily_maamarim()
        assert len(maamarim2) == 2

    def test_clear_history(self, mock_maamar_repository: MaamarRepository) -> None:
        """Should clear all sent history."""
        # First, mark some maamarim as sent
        maamar = mock_maamar_repository.get_random_by_source(
            SourceCategory.BAAL_HASULAM
        )
        assert maamar is not None
        mock_maamar_repository.mark_as_sent(maamar, date.today())

        # Verify it was recorded
        assert (
            len(
                mock_maamar_repository.get_sent_ids_by_source(
                    SourceCategory.BAAL_HASULAM
                )
            )
            > 0
        )

        # Clear and verify
        mock_maamar_repository.clear_history()
        assert (
            len(
                mock_maamar_repository.get_sent_ids_by_source(
                    SourceCategory.BAAL_HASULAM
                )
            )
            == 0
        )

    def test_get_stats(self, mock_maamar_repository: MaamarRepository) -> None:
        """Should return statistics about loaded maamarim."""
        stats = mock_maamar_repository.get_stats()

        assert "total" in stats
        assert stats["total"] == 2  # One per source
        assert stats["baal_hasulam"] == 1
        assert stats["rabash"] == 1

    def test_was_maamar_sent_today(
        self, mock_maamar_repository: MaamarRepository
    ) -> None:
        """Should check if maamar was sent for date."""
        today = date.today()

        # Initially no maamar sent
        assert not mock_maamar_repository.was_maamar_sent_today(today)

        # Mark a maamar as sent
        maamar = mock_maamar_repository.get_random_maamar()
        assert maamar is not None
        mock_maamar_repository.mark_as_sent(maamar, today)

        # Now should return True
        assert mock_maamar_repository.was_maamar_sent_today(today)


class TestMaamarRepositoryPersistence:
    """Tests for repository persistence (loading/saving JSON)."""

    def test_loads_maamarim_from_json_files(
        self, mock_maamar_repository: MaamarRepository
    ) -> None:
        """Should load maamarim from JSON files on initialization."""
        # Force reload
        mock_maamar_repository._maamarim_cache = None
        maamarim = mock_maamar_repository.get_all_by_source(SourceCategory.BAAL_HASULAM)
        assert len(maamarim) == 1

    def test_saves_and_loads_history(
        self, mock_maamar_repository: MaamarRepository
    ) -> None:
        """History should persist across repository instances."""
        # Mark a maamar as sent
        maamar = mock_maamar_repository.get_random_by_source(
            SourceCategory.BAAL_HASULAM
        )
        assert maamar is not None
        mock_maamar_repository.mark_as_sent(maamar, date(2024, 1, 15))

        # Create new repository instance with same files
        new_repo = MaamarRepository(
            maamarim_dir=mock_maamar_repository._maamarim_dir,
            history_file=mock_maamar_repository._history_file,
        )

        # Should have the same history
        sent_ids = new_repo.get_sent_ids_by_source(SourceCategory.BAAL_HASULAM)
        assert maamar.id in sent_ids

    def test_reload_cache(self, mock_maamar_repository: MaamarRepository) -> None:
        """Should be able to reload cache from disk."""
        # Get initial count
        initial_count = len(mock_maamar_repository.get_all_maamarim())

        # Reload cache
        mock_maamar_repository.reload_cache()

        # Count should be the same
        assert len(mock_maamar_repository.get_all_maamarim()) == initial_count
