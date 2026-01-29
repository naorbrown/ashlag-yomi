"""
Data access layer for Ashlag Yomi quotes.

The repository pattern abstracts away storage details:
- Currently uses JSON files (simple, version-controlled)
- Could easily switch to SQLite or PostgreSQL later
- Business logic doesn't need to know how data is stored

Design Decisions:
- JSON files are stored in data/quotes/ directory
- Each category has its own file (easier to edit manually)
- Sent history tracked separately to implement fair rotation
"""

from __future__ import annotations

import json
import random
from datetime import date
from functools import lru_cache
from pathlib import Path

from src.data.models import DailyBundle, Quote, QuoteCategory, SentRecord
from src.utils.logger import get_logger

logger = get_logger(__name__)


@lru_cache(maxsize=1)
def get_repository() -> QuoteRepository:
    """
    Get cached singleton repository instance.

    This avoids re-creating the repository and re-loading quotes
    on every command, significantly improving response time.
    """
    repo = QuoteRepository()
    # Pre-load quotes into cache for fast access
    repo._load_quotes()
    return repo


class QuoteRepository:
    """
    Repository for accessing and managing quotes.

    Implements "fair rotation" - quotes are not repeated until all
    quotes in a category have been used.
    """

    def __init__(
        self,
        quotes_dir: Path | None = None,
        history_file: Path | None = None,
    ) -> None:
        """
        Initialize the repository.

        Args:
            quotes_dir: Directory containing quote JSON files.
                       Defaults to data/quotes/ in project root.
            history_file: File tracking sent quotes.
                         Defaults to data/sent_history.json
        """
        # Find project root (where pyproject.toml lives)
        self._project_root = self._find_project_root()

        self._quotes_dir = quotes_dir or self._project_root / "data" / "quotes"
        self._history_file = (
            history_file or self._project_root / "data" / "sent_history.json"
        )

        # Cache for loaded quotes (lazy loading)
        self._quotes_cache: dict[QuoteCategory, list[Quote]] | None = None
        self._history_cache: list[SentRecord] | None = None

        logger.debug(
            "repository_initialized",
            quotes_dir=str(self._quotes_dir),
            history_file=str(self._history_file),
        )

    def _find_project_root(self) -> Path:
        """Find the project root directory."""
        current = Path(__file__).resolve()
        for parent in current.parents:
            if (parent / "pyproject.toml").exists():
                return parent
        # Fallback to current working directory
        return Path.cwd()

    def _load_quotes(self) -> dict[QuoteCategory, list[Quote]]:
        """Load all quotes from JSON files."""
        if self._quotes_cache is not None:
            return self._quotes_cache

        quotes: dict[QuoteCategory, list[Quote]] = {cat: [] for cat in QuoteCategory}

        if not self._quotes_dir.exists():
            logger.warning("quotes_dir_not_found", path=str(self._quotes_dir))
            return quotes

        for json_file in self._quotes_dir.glob("*.json"):
            try:
                with open(json_file, encoding="utf-8") as f:
                    data = json.load(f)

                for quote_data in data.get("quotes", []):
                    quote = Quote.model_validate(quote_data)
                    quotes[quote.category].append(quote)

                logger.debug(
                    "loaded_quotes_file",
                    file=json_file.name,
                    count=len(data.get("quotes", [])),
                )
            except (json.JSONDecodeError, ValueError) as e:
                logger.error("failed_to_load_quotes", file=json_file.name, error=str(e))

        self._quotes_cache = quotes

        total = sum(len(q) for q in quotes.values())
        logger.info("quotes_loaded", total=total, categories=len(quotes))

        return quotes

    def _load_history(self) -> list[SentRecord]:
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
                SentRecord.model_validate(record) for record in data.get("sent", [])
            ]
            logger.debug("history_loaded", count=len(self._history_cache))
        except (json.JSONDecodeError, ValueError) as e:
            logger.error("failed_to_load_history", error=str(e))
            self._history_cache = []

        return self._history_cache

    def _save_history(self) -> None:
        """Save sent history to JSON file."""
        if self._history_cache is None:
            return

        # Ensure directory exists
        self._history_file.parent.mkdir(parents=True, exist_ok=True)

        data = {
            "sent": [record.model_dump(mode="json") for record in self._history_cache]
        }

        with open(self._history_file, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        logger.debug("history_saved", count=len(self._history_cache))

    def get_all_by_category(self, category: QuoteCategory) -> list[Quote]:
        """Get all quotes for a specific category."""
        quotes = self._load_quotes()
        return quotes.get(category, [])

    def get_random_by_category(
        self,
        category: QuoteCategory,
        *,
        exclude_ids: set[str] | None = None,
    ) -> Quote | None:
        """
        Get a random quote from a category, optionally excluding certain IDs.

        Implements fair rotation by excluding recently sent quotes.

        Args:
            category: The category to get a quote from
            exclude_ids: Quote IDs to exclude from selection

        Returns:
            A random quote, or None if no quotes available
        """
        all_quotes = self.get_all_by_category(category)

        if not all_quotes:
            logger.warning("no_quotes_available", category=category.value)
            return None

        # Filter out excluded IDs
        available = all_quotes
        if exclude_ids:
            available = [q for q in all_quotes if q.id not in exclude_ids]

        # If all quotes have been used, reset (fair rotation complete)
        if not available:
            logger.info("rotation_complete", category=category.value)
            available = all_quotes

        return random.choice(available)

    def get_random_quote(self) -> Quote | None:
        """
        Get a single random quote from any category.

        Useful for the /quote command to show a quick sample.

        Returns:
            A random quote, or None if no quotes available
        """
        all_quotes: list[Quote] = []
        quotes_by_category = self._load_quotes()

        for category_quotes in quotes_by_category.values():
            all_quotes.extend(category_quotes)

        if not all_quotes:
            logger.warning("no_quotes_available_for_random")
            return None

        return random.choice(all_quotes)

    def get_sent_ids_by_category(self, category: QuoteCategory) -> set[str]:
        """Get IDs of quotes that have been sent for a category."""
        history = self._load_history()
        return {r.quote_id for r in history if r.category == category}

    def mark_as_sent(self, quote: Quote, sent_date: date) -> None:
        """Record that a quote was sent."""
        history = self._load_history()
        record = SentRecord.from_quote(quote, sent_date)
        history.append(record)
        self._history_cache = history
        self._save_history()
        logger.info("quote_marked_sent", quote_id=quote.id, date=str(sent_date))

    def get_daily_bundle(self, target_date: date) -> DailyBundle:
        """
        Generate a daily bundle with one quote from each category.

        Uses fair rotation to avoid repeating quotes.
        """
        quotes: list[Quote] = []

        for category in QuoteCategory:
            sent_ids = self.get_sent_ids_by_category(category)
            quote = self.get_random_by_category(category, exclude_ids=sent_ids)

            if quote:
                quotes.append(quote)
            else:
                logger.warning("missing_quote_for_category", category=category.value)

        return DailyBundle(date=target_date, quotes=quotes)

    def was_broadcast_today(self, target_date: date) -> bool:
        """Check if any quotes were already broadcast for this date."""
        history = self._load_history()
        return any(r.sent_date == target_date for r in history)

    def clear_history(self) -> None:
        """Clear all sent history (use with caution!)."""
        self._history_cache = []
        self._save_history()
        logger.warning("history_cleared")

    def validate_all(self) -> dict[str, int]:
        """
        Validate all quote files and return statistics.

        Useful for CI/CD checks.
        """
        quotes = self._load_quotes()
        stats = {
            "total": sum(len(q) for q in quotes.values()),
        }
        for category in QuoteCategory:
            stats[category.value] = len(quotes.get(category, []))

        logger.info("validation_complete", **stats)
        return stats
