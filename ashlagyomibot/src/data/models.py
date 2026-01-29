"""
Domain models for Ashlag Yomi maamarim (articles).

This module defines the core data structures using Pydantic for:
- Type safety and validation
- JSON serialization/deserialization
- Self-documenting schemas

Design Philosophy:
- Models are immutable (frozen=True) - maamarim don't change once scraped
- All fields have explicit types - catches errors early
- Validation happens at construction time - invalid data never enters system

Data Sources:
- Baal Hasulam: https://search.orhasulam.org/ (כתבי בעל הסולם section)
- Rabash: https://ashlagbaroch.org/rbsMore/ (PDF articles)
"""

from datetime import date, datetime
from enum import Enum
from typing import Annotated

from pydantic import BaseModel, Field, computed_field


class SourceCategory(str, Enum):
    """
    Categories of maamarim based on the author.

    Only two sources:
    1. Baal HaSulam (1884-1954) - Rabbi Yehuda Ashlag, author of Sulam commentary
    2. Rabash (1907-1991) - Rabbi Baruch Shalom Ashlag, son of Baal HaSulam
    """

    BAAL_HASULAM = "baal_hasulam"
    RABASH = "rabash"

    @property
    def display_name_hebrew(self) -> str:
        """Get the Hebrew display name for this source."""
        names = {
            SourceCategory.BAAL_HASULAM: "בעל הסולם",
            SourceCategory.RABASH: 'הרב"ש',
        }
        return names[self]

    @property
    def display_name_english(self) -> str:
        """Get the English display name for this source."""
        names = {
            SourceCategory.BAAL_HASULAM: "Baal HaSulam",
            SourceCategory.RABASH: "Rabash",
        }
        return names[self]

    @property
    def source_website(self) -> str:
        """Get the source website URL for this category."""
        urls = {
            SourceCategory.BAAL_HASULAM: "https://search.orhasulam.org/",
            SourceCategory.RABASH: "https://ashlagbaroch.org/rbsMore/",
        }
        return urls[self]


# Keep old QuoteCategory for backward compatibility during migration
class QuoteCategory(str, Enum):
    """
    DEPRECATED: Use SourceCategory instead.

    Categories of quotes based on the spiritual lineage.
    Kept for backward compatibility during migration.
    """

    ARIZAL = "arizal"
    BAAL_SHEM_TOV = "baal_shem_tov"
    POLISH_CHASSIDUT = "polish_chassidut"
    BAAL_HASULAM = "baal_hasulam"
    RABASH = "rabash"
    CHASDEI_ASHLAG = "chasdei_ashlag"

    @property
    def display_name_hebrew(self) -> str:
        """Get the Hebrew display name for this category."""
        names = {
            QuoteCategory.ARIZAL: "האר״י הקדוש",
            QuoteCategory.BAAL_SHEM_TOV: "הבעל שם טוב",
            QuoteCategory.POLISH_CHASSIDUT: "חסידות פולין",
            QuoteCategory.BAAL_HASULAM: "בעל הסולם",
            QuoteCategory.RABASH: 'הרב"ש',
            QuoteCategory.CHASDEI_ASHLAG: "חסידי אשלג",
        }
        return names[self]

    @property
    def display_name_english(self) -> str:
        """Get the English display name for this category."""
        names = {
            QuoteCategory.ARIZAL: "The Holy Arizal",
            QuoteCategory.BAAL_SHEM_TOV: "The Baal Shem Tov",
            QuoteCategory.POLISH_CHASSIDUT: "Polish Chassidut",
            QuoteCategory.BAAL_HASULAM: "Baal HaSulam",
            QuoteCategory.RABASH: "Rabash",
            QuoteCategory.CHASDEI_ASHLAG: "Chasdei Ashlag",
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

    # Source attribution - the specific rabbi who said/wrote this
    source_rabbi: Annotated[str, Field(min_length=1, max_length=200)]
    source_book: str | None = None
    source_section: str | None = None  # Chapter, page, or section reference

    # Link to original source (Sefaria, OrHaSulam, AshlagBaruch, HebrewBooks, etc.)
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

    Each day gets one quote from each category (6 quotes total).
    This ensures balanced representation of the lineage.
    """

    model_config = {"frozen": True}

    # The date this bundle is for
    date: date

    # One quote from each category
    quotes: Annotated[list[Quote], Field(min_length=1, max_length=6)]

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


# =============================================================================
# NEW MODELS FOR MAAMARIM (ARTICLES) SYSTEM
# =============================================================================


class Maamar(BaseModel):
    """
    A complete maamar (article) from Baal Hasulam or Rabash.

    Unlike Quote which holds short excerpts, Maamar contains full article text
    that may span multiple Telegram messages.
    """

    model_config = {"frozen": True, "extra": "ignore"}

    # Unique identifier (format: {source}_{book_slug}_{index})
    id: Annotated[str, Field(min_length=1, max_length=200)]

    # Source category (Baal Hasulam or Rabash)
    source: SourceCategory

    # Article title in Hebrew
    title: Annotated[str, Field(min_length=1, max_length=500)]

    # Optional subtitle
    subtitle: str | None = None

    # The full article text in Hebrew
    text: Annotated[str, Field(min_length=10)]

    # Source book name in Hebrew
    book: Annotated[str, Field(min_length=1, max_length=300)]

    # Page number or section reference
    page: str | None = None

    # Direct URL to the source
    source_url: Annotated[str, Field(pattern=r"^https?://")]

    # For PDF sources: filename and page numbers
    pdf_filename: str | None = None
    pdf_start_page: int | None = None
    pdf_end_page: int | None = None

    # Metadata
    scraped_at: datetime = Field(default_factory=datetime.utcnow)

    @computed_field
    @property
    def word_count(self) -> int:
        """Approximate word count of the maamar."""
        return len(self.text.split())

    @computed_field
    @property
    def char_count(self) -> int:
        """Character count of the maamar text."""
        return len(self.text)

    @computed_field
    @property
    def estimated_reading_minutes(self) -> float:
        """Estimated reading time in minutes (Hebrew ~150 words/min)."""
        return round(self.word_count / 150, 1)

    @computed_field
    @property
    def telegram_message_count(self) -> int:
        """Estimated number of Telegram messages needed (4096 char limit)."""
        # Account for header/footer overhead (~300 chars)
        effective_limit = 3800
        return max(1, (self.char_count + effective_limit - 1) // effective_limit)

    @computed_field
    @property
    def full_source_citation(self) -> str:
        """Full Hebrew citation for the source."""
        citation = f"{self.source.display_name_hebrew}"
        citation += f", {self.book}"
        if self.page:
            citation += f", עמ׳ {self.page}"
        return citation

    def __str__(self) -> str:
        """Human-readable representation."""
        return f"Maamar({self.id}): {self.title[:50]}..."


class DailyMaamar(BaseModel):
    """
    A single maamar selected for a specific day.

    Replaces DailyBundle - instead of 6 short quotes,
    we now send one complete maamar.
    """

    model_config = {"frozen": True}

    # The date this maamar is for
    date: date

    # The selected maamar
    maamar: Maamar

    @computed_field
    @property
    def source_name(self) -> str:
        """The source name in Hebrew."""
        return self.maamar.source.display_name_hebrew


class MaamarSentRecord(BaseModel):
    """
    Record of a maamar that was sent to the channel.

    Used to implement "fair rotation" - ensuring all maamarim are used
    before any repeats.
    """

    model_config = {"frozen": True}

    maamar_id: str
    sent_date: date
    source: SourceCategory

    @classmethod
    def from_maamar(cls, maamar: Maamar, sent_date: date) -> "MaamarSentRecord":
        """Create a sent record from a maamar."""
        return cls(
            maamar_id=maamar.id,
            sent_date=sent_date,
            source=maamar.source,
        )


class MaamarCollection(BaseModel):
    """
    A collection of maamarim from a single source, stored as JSON cache.

    This is the format used for GitHub-hosted JSON cache files.
    """

    model_config = {"extra": "ignore"}

    # Source category
    source: SourceCategory

    # When the collection was last updated
    last_updated: datetime = Field(default_factory=datetime.utcnow)

    # All maamarim from this source
    maamarim: list[Maamar] = Field(default_factory=list)

    @computed_field
    @property
    def count(self) -> int:
        """Number of maamarim in this collection."""
        return len(self.maamarim)
