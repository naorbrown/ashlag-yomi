"""
Data access layer for Ashlag Yomi maamarim.

The repository pattern abstracts away storage details:
- Uses JSON files cached from scraping
- Implements fair rotation to avoid repeating maamarim
- Provides fast access via caching

Design Decisions:
- JSON cache files stored in data/maamarim/ directory
- Each source category has its own cache file
- Sent history tracked to implement fair rotation
"""

from __future__ import annotations

import json
import random
from datetime import date
from functools import lru_cache
from pathlib import Path

from src.data.models import (
    DailyMaamar,
    Maamar,
    MaamarCollection,
    MaamarSentRecord,
    SourceCategory,
)
from src.utils.logger import get_logger

logger = get_logger(__name__)


@lru_cache(maxsize=1)
def get_maamar_repository() -> MaamarRepository:
    """
    Get cached singleton maamar repository instance.

    This avoids re-creating the repository and re-loading maamarim
    on every command, significantly improving response time.
    """
    repo = MaamarRepository()
    repo._load_all_maamarim()
    return repo


class MaamarRepository:
    """
    Repository for accessing and managing maamarim.

    Implements "fair rotation" - maamarim are not repeated until all
    maamarim from a source have been used.
    """

    def __init__(
        self,
        maamarim_dir: Path | None = None,
        history_file: Path | None = None,
    ) -> None:
        """
        Initialize the repository.

        Args:
            maamarim_dir: Directory containing maamar cache JSON files.
                         Defaults to data/maamarim/ in project root.
            history_file: File tracking sent maamarim.
                         Defaults to data/maamar_history.json
        """
        self._project_root = self._find_project_root()

        self._maamarim_dir = maamarim_dir or self._project_root / "data" / "maamarim"
        self._history_file = (
            history_file or self._project_root / "data" / "maamar_history.json"
        )

        # Cache for loaded maamarim
        self._maamarim_cache: dict[SourceCategory, list[Maamar]] | None = None
        self._history_cache: list[MaamarSentRecord] | None = None

        logger.debug(
            "maamar_repository_initialized",
            maamarim_dir=str(self._maamarim_dir),
            history_file=str(self._history_file),
        )

    def _find_project_root(self) -> Path:
        """Find the project root directory."""
        current = Path(__file__).resolve()
        for parent in current.parents:
            if (parent / "pyproject.toml").exists():
                return parent
        return Path.cwd()

    def _load_all_maamarim(self) -> dict[SourceCategory, list[Maamar]]:
        """Load all maamarim from JSON cache files."""
        if self._maamarim_cache is not None:
            return self._maamarim_cache

        maamarim: dict[SourceCategory, list[Maamar]] = {
            cat: [] for cat in SourceCategory
        }

        if not self._maamarim_dir.exists():
            logger.warning("maamarim_dir_not_found", path=str(self._maamarim_dir))
            self._maamarim_cache = maamarim
            return maamarim

        for json_file in self._maamarim_dir.glob("*.json"):
            try:
                with open(json_file, encoding="utf-8") as f:
                    data = json.load(f)

                collection = MaamarCollection.model_validate(data)
                maamarim[collection.source] = collection.maamarim

                logger.debug(
                    "loaded_maamarim_file",
                    file=json_file.name,
                    source=collection.source.value,
                    count=len(collection.maamarim),
                )
            except (json.JSONDecodeError, ValueError) as e:
                logger.error(
                    "failed_to_load_maamarim",
                    file=json_file.name,
                    error=str(e),
                )

        self._maamarim_cache = maamarim

        total = sum(len(m) for m in maamarim.values())
        logger.info("maamarim_loaded", total=total, sources=len(SourceCategory))

        return maamarim

    def _load_history(self) -> list[MaamarSentRecord]:
        """Load sent history from JSON file."""
        if self._history_cache is not None:
            return self._history_cache

        if not self._history_file.exists():
            self._history_cache = []
            return self._history_cache

        try:
            with open(self._history_file, encoding="utf-8") as f:
                data = json.load(f)

            self._history_cache = [
                MaamarSentRecord.model_validate(record)
                for record in data.get("sent", [])
            ]
            logger.debug("maamar_history_loaded", count=len(self._history_cache))
        except (json.JSONDecodeError, ValueError) as e:
            logger.error("failed_to_load_maamar_history", error=str(e))
            self._history_cache = []

        return self._history_cache

    def _save_history(self) -> None:
        """Save sent history to JSON file."""
        if self._history_cache is None:
            return

        self._history_file.parent.mkdir(parents=True, exist_ok=True)

        data = {
            "sent": [record.model_dump(mode="json") for record in self._history_cache]
        }

        with open(self._history_file, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        logger.debug("maamar_history_saved", count=len(self._history_cache))

    def get_all_by_source(self, source: SourceCategory) -> list[Maamar]:
        """Get all maamarim for a specific source."""
        maamarim = self._load_all_maamarim()
        return maamarim.get(source, [])

    def get_all_maamarim(self) -> list[Maamar]:
        """Get all maamarim from all sources."""
        maamarim = self._load_all_maamarim()
        all_maamarim: list[Maamar] = []
        for source_maamarim in maamarim.values():
            all_maamarim.extend(source_maamarim)
        return all_maamarim

    def get_random_by_source(
        self,
        source: SourceCategory,
        *,
        exclude_ids: set[str] | None = None,
    ) -> Maamar | None:
        """
        Get a random maamar from a source, optionally excluding certain IDs.

        Implements fair rotation by excluding recently sent maamarim.

        Args:
            source: The source to get a maamar from
            exclude_ids: Maamar IDs to exclude from selection

        Returns:
            A random maamar, or None if no maamarim available
        """
        all_maamarim = self.get_all_by_source(source)

        if not all_maamarim:
            logger.warning("no_maamarim_available", source=source.value)
            return None

        # Filter out excluded IDs
        available = all_maamarim
        if exclude_ids:
            available = [m for m in all_maamarim if m.id not in exclude_ids]

        # If all maamarim have been used, reset (fair rotation complete)
        if not available:
            logger.info("maamar_rotation_complete", source=source.value)
            available = all_maamarim

        return random.choice(available)

    def get_random_maamar(self) -> Maamar | None:
        """
        Get a single random maamar from any source.

        Useful for the /maamar command to show a quick sample.

        Returns:
            A random maamar, or None if no maamarim available
        """
        all_maamarim = self.get_all_maamarim()

        if not all_maamarim:
            logger.warning("no_maamarim_available_for_random")
            return None

        return random.choice(all_maamarim)

    def get_sent_ids_by_source(self, source: SourceCategory) -> set[str]:
        """Get IDs of maamarim that have been sent for a source."""
        history = self._load_history()
        return {r.maamar_id for r in history if r.source == source}

    def mark_as_sent(self, maamar: Maamar, sent_date: date) -> None:
        """Record that a maamar was sent."""
        history = self._load_history()
        record = MaamarSentRecord.from_maamar(maamar, sent_date)
        history.append(record)
        self._history_cache = history
        self._save_history()
        logger.info("maamar_marked_sent", maamar_id=maamar.id, date=str(sent_date))

    def get_daily_maamar(self, target_date: date) -> DailyMaamar | None:
        """
        Get a maamar for the day, using fair rotation.

        Randomly selects between Baal Hasulam and Rabash sources,
        then picks a maamar that hasn't been sent recently.

        Args:
            target_date: The date to get a maamar for

        Returns:
            DailyMaamar, or None if no maamarim available
        """
        # Randomly pick a source
        source = random.choice(list(SourceCategory))

        # Get sent IDs for this source
        sent_ids = self.get_sent_ids_by_source(source)

        # Get a random maamar
        maamar = self.get_random_by_source(source, exclude_ids=sent_ids)

        if not maamar:
            # Try the other source
            other_source = (
                SourceCategory.RABASH
                if source == SourceCategory.BAAL_HASULAM
                else SourceCategory.BAAL_HASULAM
            )
            sent_ids = self.get_sent_ids_by_source(other_source)
            maamar = self.get_random_by_source(other_source, exclude_ids=sent_ids)

        if not maamar:
            logger.warning("no_maamar_available_for_daily")
            return None

        return DailyMaamar(date=target_date, maamar=maamar)

    def was_maamar_sent_today(self, target_date: date) -> bool:
        """Check if any maamar was already sent for this date."""
        history = self._load_history()
        return any(r.sent_date == target_date for r in history)

    def clear_history(self) -> None:
        """Clear all sent history (use with caution!)."""
        self._history_cache = []
        self._save_history()
        logger.warning("maamar_history_cleared")

    def get_stats(self) -> dict[str, int]:
        """
        Get statistics about the maamarim collection.

        Returns:
            Dict with counts per source and total
        """
        maamarim = self._load_all_maamarim()
        stats = {
            "total": sum(len(m) for m in maamarim.values()),
        }
        for source in SourceCategory:
            stats[source.value] = len(maamarim.get(source, []))

        return stats

    def reload_cache(self) -> None:
        """Force reload of maamarim cache from disk."""
        self._maamarim_cache = None
        self._load_all_maamarim()
        logger.info("maamar_cache_reloaded")
