"""
Data access layer for Ashlag Yomi quotes.

Repository pattern for loading and selecting quotes from Baal Hasulam and Rabash.
Uses the existing quote JSON files with random selection capability.
"""

from __future__ import annotations

import json
import random
from datetime import date
from functools import lru_cache
from pathlib import Path

from src.data.models import Quote, QuoteCategory
from src.utils.logger import get_logger

logger = get_logger(__name__)

# Only these two sources are active
ACTIVE_CATEGORIES = [QuoteCategory.BAAL_HASULAM, QuoteCategory.RABASH]


@lru_cache(maxsize=1)
def get_quote_repository() -> QuoteRepository:
    """
    Get cached singleton quote repository instance.

    This avoids re-creating the repository and re-loading quotes
    on every command, significantly improving response time.
    """
    repo = QuoteRepository()
    repo._load_all_quotes()
    return repo


class QuoteRepository:
    """
    Repository for accessing quotes from Baal Hasulam and Rabash.

    Loads quotes from JSON files and provides random selection.
    """

    def __init__(self, quotes_dir: Path | None = None) -> None:
        """
        Initialize the repository.

        Args:
            quotes_dir: Directory containing quote JSON files.
                       Defaults to data/quotes/ in project root.
        """
        self._project_root = self._find_project_root()
        self._quotes_dir = quotes_dir or self._project_root / "data" / "quotes"

        # Cache for loaded quotes
        self._quotes_cache: dict[QuoteCategory, list[Quote]] | None = None

        logger.debug(
            "quote_repository_initialized",
            quotes_dir=str(self._quotes_dir),
        )

    def _find_project_root(self) -> Path:
        """Find the project root directory."""
        current = Path(__file__).resolve()
        for parent in current.parents:
            if (parent / "pyproject.toml").exists():
                return parent
        return Path.cwd()

    def _load_all_quotes(self) -> dict[QuoteCategory, list[Quote]]:
        """Load all quotes from JSON files for active categories."""
        if self._quotes_cache is not None:
            return self._quotes_cache

        quotes: dict[QuoteCategory, list[Quote]] = {
            cat: [] for cat in ACTIVE_CATEGORIES
        }

        if not self._quotes_dir.exists():
            logger.warning("quotes_dir_not_found", path=str(self._quotes_dir))
            self._quotes_cache = quotes
            return quotes

        # Load only Baal Hasulam and Rabash
        for category in ACTIVE_CATEGORIES:
            json_file = self._quotes_dir / f"{category.value}.json"
            if not json_file.exists():
                logger.warning("quote_file_not_found", file=str(json_file))
                continue

            try:
                with open(json_file, encoding="utf-8") as f:
                    data = json.load(f)

                # Parse quotes from the JSON structure
                raw_quotes = data.get("quotes", [])
                for raw_quote in raw_quotes:
                    try:
                        quote = Quote.model_validate(raw_quote)
                        quotes[category].append(quote)
                    except Exception as e:
                        logger.warning(
                            "failed_to_parse_quote",
                            quote_id=raw_quote.get("id", "unknown"),
                            error=str(e),
                        )

                logger.info(
                    "loaded_quotes_file",
                    file=json_file.name,
                    category=category.value,
                    count=len(quotes[category]),
                )
            except (json.JSONDecodeError, ValueError) as e:
                logger.error(
                    "failed_to_load_quotes",
                    file=json_file.name,
                    error=str(e),
                )

        self._quotes_cache = quotes

        total = sum(len(q) for q in quotes.values())
        logger.info("quotes_loaded", total=total, categories=len(ACTIVE_CATEGORIES))

        return quotes

    def get_all_quotes(self) -> list[Quote]:
        """Get all quotes from all active sources."""
        quotes = self._load_all_quotes()
        all_quotes: list[Quote] = []
        for category_quotes in quotes.values():
            all_quotes.extend(category_quotes)
        return all_quotes

    def get_quotes_by_category(self, category: QuoteCategory) -> list[Quote]:
        """Get all quotes for a specific category."""
        quotes = self._load_all_quotes()
        return quotes.get(category, [])

    def get_random_quote(self, category: QuoteCategory | None = None) -> Quote | None:
        """
        Get a random quote.

        Args:
            category: Optional category to filter by. If None, picks from any active source.

        Returns:
            A random quote, or None if no quotes available.
        """
        if category:
            available = self.get_quotes_by_category(category)
        else:
            available = self.get_all_quotes()

        if not available:
            logger.warning(
                "no_quotes_available", category=category.value if category else "all"
            )
            return None

        return random.choice(available)

    def get_daily_quotes(self, target_date: date | None = None) -> list[Quote]:
        """
        Get today's quotes - one random from Baal Hasulam and one from Rabash.

        Uses the date as a seed for consistent daily selection (same quotes
        throughout the day, different quotes each day).

        Args:
            target_date: The date to get quotes for. Defaults to today.

        Returns:
            List of 2 quotes (one per source), or fewer if unavailable.
        """
        if target_date is None:
            target_date = date.today()

        # Use date as seed for reproducible daily selection
        seed = target_date.toordinal()
        rng = random.Random(seed)

        quotes: list[Quote] = []

        for category in ACTIVE_CATEGORIES:
            category_quotes = self.get_quotes_by_category(category)
            if category_quotes:
                quote = rng.choice(category_quotes)
                quotes.append(quote)

        return quotes

    def get_stats(self) -> dict[str, int]:
        """
        Get statistics about the quotes collection.

        Returns:
            Dict with counts per category and total.
        """
        quotes = self._load_all_quotes()
        stats = {
            "total": sum(len(q) for q in quotes.values()),
        }
        for category in ACTIVE_CATEGORIES:
            stats[category.value] = len(quotes.get(category, []))

        return stats

    def reload_cache(self) -> None:
        """Force reload of quotes cache from disk."""
        self._quotes_cache = None
        self._load_all_quotes()
        logger.info("quote_cache_reloaded")
