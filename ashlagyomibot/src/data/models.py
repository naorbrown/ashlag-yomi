"""
Domain models for Ashlag Yomi quotes.

This module defines the core data structures using Pydantic for:
- Type safety and validation
- JSON serialization/deserialization
- Self-documenting schemas

Design Philosophy:
- Models are immutable (frozen=True) - quotes don't change once created
- All fields have explicit types - catches errors early
- Validation happens at construction time - invalid data never enters system
"""

from datetime import date, datetime
from enum import Enum
from typing import Annotated

from pydantic import BaseModel, Field, computed_field


class QuoteCategory(str, Enum):
    """
    Categories of quotes based on the spiritual lineage.

    The order represents the historical flow of Kabbalistic wisdom:
    1. Arizal (1534-1572) - Foundation of Lurianic Kabbalah
    2. Baal Shem Tov (1698-1760) - Founder of Chassidut
    3. Simcha Bunim (1765-1827) - Peshischa school
    4. Kotzker (1787-1859) - Student of Simcha Bunim
    5. Baal HaSulam (1884-1954) - Modern Kabbalah systematizer
    6. Rabash (1907-1991) - Son of Baal HaSulam
    7. Talmidim - Contemporary students
    """

    ARIZAL = "arizal"
    BAAL_SHEM_TOV = "baal_shem_tov"
    SIMCHA_BUNIM = "simcha_bunim"
    KOTZKER = "kotzker"
    BAAL_HASULAM = "baal_hasulam"
    RABASH = "rabash"
    TALMIDIM = "talmidim"

    @property
    def display_name_hebrew(self) -> str:
        """Get the Hebrew display name for this category."""
        names = {
            QuoteCategory.ARIZAL: "האר״י הקדוש",
            QuoteCategory.BAAL_SHEM_TOV: "הבעל שם טוב",
            QuoteCategory.SIMCHA_BUNIM: "רבי שמחה בונים מפשיסחא",
            QuoteCategory.KOTZKER: "הרבי מקוצק",
            QuoteCategory.BAAL_HASULAM: "בעל הסולם",
            QuoteCategory.RABASH: 'הרב"ש',
            QuoteCategory.TALMIDIM: "התלמידים",
        }
        return names[self]

    @property
    def display_name_english(self) -> str:
        """Get the English display name for this category."""
        names = {
            QuoteCategory.ARIZAL: "The Holy Arizal",
            QuoteCategory.BAAL_SHEM_TOV: "The Baal Shem Tov",
            QuoteCategory.SIMCHA_BUNIM: "Rebbe Simcha Bunim of Peshischa",
            QuoteCategory.KOTZKER: "The Kotzker Rebbe",
            QuoteCategory.BAAL_HASULAM: "Baal HaSulam",
            QuoteCategory.RABASH: "Rabash",
            QuoteCategory.TALMIDIM: "The Students",
        }
        return names[self]


class Quote(BaseModel):
    """
    A single quote from the Ashlag lineage.

    This is the core domain model - everything revolves around quotes.
    Immutable to ensure data integrity once loaded.
    """

    model_config = {"frozen": True, "extra": "ignore"}

    # Unique identifier (use UUID or slug like "baal-hasulam-tes-001")
    id: Annotated[str, Field(min_length=1, max_length=100)]

    # The actual quote text in Hebrew
    text: Annotated[str, Field(min_length=10, max_length=5000)]

    # Source attribution
    source_rabbi: Annotated[str, Field(min_length=1, max_length=200)]
    source_book: str | None = None
    source_section: str | None = None  # Chapter, page, or section reference

    # Link to original source (Sefaria, OrHaSulam, etc.)
    source_url: Annotated[str, Field(pattern=r"^https?://")]

    # Classification
    category: QuoteCategory

    # Tags for future filtering (e.g., ["love", "unity", "creation"])
    tags: list[str] = Field(default_factory=list)

    # Estimated reading time in seconds (for pacing daily bundles)
    # Rule of thumb: ~5 seconds per Hebrew word
    length_estimate: Annotated[int, Field(ge=5, le=300)] = 30

    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)

    @computed_field
    @property
    def word_count(self) -> int:
        """Approximate word count of the quote."""
        return len(self.text.split())

    def __str__(self) -> str:
        """Human-readable representation."""
        preview = self.text[:50] + "..." if len(self.text) > 50 else self.text
        return f"Quote({self.id}): {preview}"


class DailyBundle(BaseModel):
    """
    A collection of quotes for a single day.

    Each day gets one quote from each category (7 quotes total).
    This ensures balanced representation of the lineage.
    """

    model_config = {"frozen": True}

    # The date this bundle is for
    date: date

    # One quote from each category
    quotes: Annotated[list[Quote], Field(min_length=1, max_length=7)]

    @computed_field
    @property
    def total_reading_time(self) -> int:
        """Total estimated reading time in seconds."""
        return sum(q.length_estimate for q in self.quotes)

    @computed_field
    @property
    def total_reading_time_minutes(self) -> float:
        """Total estimated reading time in minutes."""
        return round(self.total_reading_time / 60, 1)

    @computed_field
    @property
    def categories_included(self) -> list[QuoteCategory]:
        """List of categories represented in this bundle."""
        return [q.category for q in self.quotes]

    def get_quote_by_category(self, category: QuoteCategory) -> Quote | None:
        """Get the quote for a specific category, if present."""
        for quote in self.quotes:
            if quote.category == category:
                return quote
        return None


class SentRecord(BaseModel):
    """
    Record of a quote that was sent to the channel.

    Used to implement "fair rotation" - ensuring all quotes are used
    before any repeats.
    """

    model_config = {"frozen": True}

    quote_id: str
    sent_date: date
    category: QuoteCategory

    @classmethod
    def from_quote(cls, quote: Quote, sent_date: date) -> "SentRecord":
        """Create a sent record from a quote."""
        return cls(
            quote_id=quote.id,
            sent_date=sent_date,
            category=quote.category,
        )
