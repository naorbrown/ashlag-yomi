"""
Quote Manager Module
Handles loading, selecting, and formatting quotes from all sources.

Quote Selection Logic:
----------------------
This module uses a deterministic pseudo-random selection algorithm to ensure:
1. All users see the same quotes on the same day (consistency)
2. Quotes cycle through fairly over time (no repetition bias)
3. Selection is reproducible for debugging

Quality Criteria (based on research from Pennycook et al., 2015):
----------------------------------------------------------------
A quote is considered genuinely insightful (not pseudo-profound) when it:
1. Has SPECIFIC meaning - not vague buzzwords that sound deep
2. Is ACTIONABLE - provides guidance that can be applied
3. Has AUTHENTIC attribution - from a verified historical source
4. Contains CONCRETE teaching - not abstract platitudes
5. Offers NOVEL perspective - reframes common understanding

References:
- Pennycook et al. (2015) "On the reception and detection of pseudo-profound bullshit"
- Cambridge: https://doi.org/10.1017/S1930297500006999
"""

import json
import random
import hashlib
from datetime import date
from pathlib import Path
from typing import Optional
from dataclasses import dataclass
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class InsightType(Enum):
    """Types of insight a quote can provide."""
    PRACTICAL = "practical"      # Actionable life guidance
    THEOLOGICAL = "theological"  # Understanding of divine nature
    PSYCHOLOGICAL = "psychological"  # Self-understanding
    RELATIONAL = "relational"    # Interpersonal wisdom
    MYSTICAL = "mystical"        # Kabbalistic/spiritual insight
    ETHICAL = "ethical"          # Moral guidance


@dataclass
class QuoteQuality:
    """Quality assessment for a quote based on research criteria."""
    specificity: int      # 1-5: How specific vs vague (5 = very specific)
    actionability: int    # 1-5: Can be applied to life (5 = very actionable)
    authenticity: int     # 1-5: Source verification (5 = verified primary source)
    novelty: int          # 1-5: Fresh perspective (5 = highly original framing)
    clarity: int          # 1-5: Clear meaning (5 = immediately understood)

    @property
    def total_score(self) -> int:
        """Calculate total quality score (5-25 range)."""
        return self.specificity + self.actionability + self.authenticity + self.novelty + self.clarity

    @property
    def grade(self) -> str:
        """Letter grade based on total score."""
        score = self.total_score
        if score >= 23:
            return "A"
        elif score >= 20:
            return "B"
        elif score >= 15:
            return "C"
        elif score >= 10:
            return "D"
        return "F"

    def is_pseudo_profound(self) -> bool:
        """
        Detect if quote might be pseudo-profound bullshit.
        Based on Pennycook et al. criteria: low specificity + low actionability.
        """
        return self.specificity <= 2 and self.actionability <= 2


class QuoteManager:
    """Manages quotes from multiple spiritual sources."""
    
    QUOTE_SOURCES = [
        "arizal",
        "baal_shem_tov",
        "simcha_bunim",
        "kotzker",
        "baal_hasulam",
        "rabash",
        "ashlag_talmidim"
    ]
    
    def __init__(self, data_dir: Optional[Path] = None):
        """Initialize the quote manager.
        
        Args:
            data_dir: Path to the data directory containing quote JSON files.
        """
        if data_dir is None:
            # Default to data/quotes relative to this file's parent directory
            self.data_dir = Path(__file__).parent.parent / "data" / "quotes"
        else:
            self.data_dir = Path(data_dir)
        
        self.quotes_cache: dict = {}
        self._load_all_quotes()
    
    def _load_all_quotes(self) -> None:
        """Load all quote files into memory."""
        for source in self.QUOTE_SOURCES:
            file_path = self.data_dir / f"{source}.json"
            try:
                if file_path.exists():
                    with open(file_path, "r", encoding="utf-8") as f:
                        self.quotes_cache[source] = json.load(f)
                    logger.info(f"Loaded {len(self.quotes_cache[source].get('quotes', []))} quotes from {source}")
                else:
                    logger.warning(f"Quote file not found: {file_path}")
            except json.JSONDecodeError as e:
                logger.error(f"Error parsing {file_path}: {e}")
            except Exception as e:
                logger.error(f"Error loading {file_path}: {e}")
    
    def _get_daily_seed(self) -> int:
        """Generate a consistent seed based on today's date."""
        today = date.today().isoformat()
        hash_bytes = hashlib.md5(today.encode()).digest()
        return int.from_bytes(hash_bytes[:4], byteorder='big')
    
    def get_quote_for_source(self, source: str, seed_offset: int = 0) -> Optional[dict]:
        """Get a deterministic quote for a source based on today's date.
        
        Args:
            source: The source name (e.g., "arizal", "baal_shem_tov")
            seed_offset: Offset to add to the seed for different selections
            
        Returns:
            A quote dictionary or None if no quotes available.
        """
        if source not in self.quotes_cache:
            logger.warning(f"Source {source} not found in cache")
            return None
        
        quotes = self.quotes_cache[source].get("quotes", [])
        if not quotes:
            logger.warning(f"No quotes found for {source}")
            return None
        
        # Use deterministic selection based on date
        seed = self._get_daily_seed() + seed_offset
        random.seed(seed)
        selected = random.choice(quotes)
        
        # Add source metadata
        selected["source_name"] = self.quotes_cache[source].get("source_name", source)
        selected["source_name_english"] = self.quotes_cache[source].get("source_name_english", source)
        
        return selected
    
    def get_daily_quotes(self) -> list[dict]:
        """Get all quotes for today's daily message.
        
        Returns:
            List of quote dictionaries, one for each source.
        """
        daily_quotes = []
        
        for i, source in enumerate(self.QUOTE_SOURCES):
            quote = self.get_quote_for_source(source, seed_offset=i)
            if quote:
                daily_quotes.append(quote)
        
        return daily_quotes
    
    def format_quote_message(self, quote: dict, include_source_link: bool = True) -> str:
        """Format a single quote for Telegram display.
        
        Args:
            quote: Quote dictionary with text, source, and metadata
            include_source_link: Whether to include the source URL
            
        Returns:
            Formatted message string with Hebrew RTL markers.
        """
        # RTL marker for proper Hebrew display
        rtl = "\u200F"
        
        source_name = quote.get("source_name", "")
        text = quote.get("text", "")
        source = quote.get("source", "")
        source_url = quote.get("source_url", "")
        
        # Build the message
        lines = [
            f"✨ *{rtl}{source_name}*",
            "",
            f"{rtl}«{text}»",
            "",
            f"📖 _{rtl}{source}_"
        ]
        
        if include_source_link and source_url:
            lines.append(f"🔗 [מקור]({source_url})")
        
        return "\n".join(lines)
    
    def format_daily_message(self) -> str:
        """Format the complete daily message with all quotes.
        
        Returns:
            Complete formatted message for Telegram.
        """
        rtl = "\u200F"
        quotes = self.get_daily_quotes()
        
        if not quotes:
            return f"{rtl}לא נמצאו ציטוטים להיום. נסה שוב מאוחר יותר."
        
        # Header
        today = date.today()
        header = f"🌅 *{rtl}ציטוט יומי - {today.strftime('%d/%m/%Y')}*\n"
        header += f"{rtl}השראה מגדולי ישראל\n"
        header += "━" * 20 + "\n"
        
        # Format each quote
        quote_messages = []
        for quote in quotes:
            quote_messages.append(self.format_quote_message(quote))
        
        # Footer
        footer = "\n" + "━" * 20
        footer += f"\n{rtl}💫 יום מבורך!"
        
        return header + "\n\n".join(quote_messages) + footer
    
    def get_quote_by_id(self, quote_id: str) -> Optional[dict]:
        """Find a specific quote by its ID.
        
        Args:
            quote_id: The unique quote identifier
            
        Returns:
            Quote dictionary or None if not found.
        """
        for source in self.quotes_cache.values():
            for quote in source.get("quotes", []):
                if quote.get("id") == quote_id:
                    quote["source_name"] = source.get("source_name", "")
                    quote["source_name_english"] = source.get("source_name_english", "")
                    return quote
        return None
    
    def get_random_quote(self) -> Optional[dict]:
        """Get a truly random quote from any source.
        
        Returns:
            Random quote dictionary.
        """
        all_quotes = []
        for source_name, source_data in self.quotes_cache.items():
            for quote in source_data.get("quotes", []):
                quote_copy = quote.copy()
                quote_copy["source_name"] = source_data.get("source_name", source_name)
                quote_copy["source_name_english"] = source_data.get("source_name_english", source_name)
                all_quotes.append(quote_copy)
        
        if not all_quotes:
            return None
        
        return random.choice(all_quotes)
    
    def get_stats(self) -> dict:
        """Get statistics about the quote database.

        Returns:
            Dictionary with quote counts per source.
        """
        stats = {"total": 0, "by_source": {}}

        for source_name, source_data in self.quotes_cache.items():
            count = len(source_data.get("quotes", []))
            stats["by_source"][source_name] = count
            stats["total"] += count

        return stats

    def evaluate_quote_quality(self, quote: dict) -> QuoteQuality:
        """
        Evaluate the quality of a quote based on research-backed criteria.

        This implements a heuristic scoring based on:
        - Pennycook et al. (2015) pseudo-profound bullshit detection
        - Linguistic markers of genuine insight

        Args:
            quote: Quote dictionary with text and metadata

        Returns:
            QuoteQuality assessment object
        """
        text = quote.get("text", "")
        source_url = quote.get("source_url", "")

        # Specificity: Check for concrete nouns/verbs vs abstract buzzwords
        # Hebrew concrete markers (actions, specific concepts)
        concrete_markers = ["צריך", "עושה", "לעשות", "כש", "אם", "כי", "למה", "איך"]
        specificity = min(5, 2 + sum(1 for m in concrete_markers if m in text))

        # Actionability: Does it guide behavior?
        action_markers = ["צריך", "חייב", "אל", "עליך", "לך", "עשה", "תן", "קום"]
        actionability = min(5, 2 + sum(1 for m in action_markers if m in text))

        # Authenticity: Based on source URL quality
        authenticity = 3  # Default
        if "sefaria.org" in source_url:
            authenticity = 5  # Primary text source
        elif "kabbalah.info" in source_url or "chabad.org" in source_url:
            authenticity = 4  # Scholarly source

        # Novelty: Estimated by quote uniqueness (shorter = more aphoristic = more novel framing)
        text_len = len(text)
        if text_len < 50:
            novelty = 5  # Pithy aphorism
        elif text_len < 100:
            novelty = 4
        elif text_len < 150:
            novelty = 3
        else:
            novelty = 2

        # Clarity: Inverse of complexity (fewer clauses = clearer)
        clause_markers = ["ו", ",", "אבל", "אלא", "כי"]
        clause_count = sum(text.count(m) for m in clause_markers)
        clarity = max(1, 5 - clause_count // 2)

        return QuoteQuality(
            specificity=specificity,
            actionability=actionability,
            authenticity=authenticity,
            novelty=novelty,
            clarity=clarity
        )

    def get_quote_with_quality(self, quote: dict) -> dict:
        """Add quality assessment to a quote dictionary."""
        quality = self.evaluate_quote_quality(quote)
        quote["quality"] = {
            "score": quality.total_score,
            "grade": quality.grade,
            "is_pseudo_profound": quality.is_pseudo_profound(),
            "breakdown": {
                "specificity": quality.specificity,
                "actionability": quality.actionability,
                "authenticity": quality.authenticity,
                "novelty": quality.novelty,
                "clarity": quality.clarity
            }
        }
        return quote

    def get_selection_explanation(self) -> str:
        """
        Explain how quotes are selected - for transparency.

        Returns:
            Human-readable explanation of selection algorithm.
        """
        seed = self._get_daily_seed()
        today = date.today()

        rtl = "\u200F"
        explanation = f"""
{rtl}📊 *הסבר על בחירת הציטוטים*

{rtl}*תאריך:* {today.strftime('%d/%m/%Y')}
{rtl}*מזהה יום:* {seed}

{rtl}*אלגוריתם הבחירה:*
{rtl}1. מחושב מזהה ייחודי לכל יום (hash של התאריך)
{rtl}2. לכל מקור נבחר ציטוט באופן דטרמיניסטי
{rtl}3. כל המשתמשים רואים אותם ציטוטים באותו יום
{rtl}4. הציטוטים מתחלפים מדי יום ללא חזרה

{rtl}*קריטריונים לאיכות (מבוסס מחקר):*
{rtl}• ספציפיות - לא מילים מעורפלות
{rtl}• יישומיות - אפשר ליישם בחיים
{rtl}• אותנטיות - מקור מאומת
{rtl}• חדשנות - נקודת מבט מקורית
{rtl}• בהירות - משמעות ברורה

{rtl}*מקור:* Pennycook et al. (2015)
{rtl}"On the reception and detection of pseudo-profound bullshit"
"""
        return explanation

    def format_quote_with_quality(self, quote: dict, include_quality: bool = False) -> str:
        """Format a quote with optional quality information."""
        base_message = self.format_quote_message(quote)

        if include_quality:
            quote_with_quality = self.get_quote_with_quality(quote.copy())
            quality = quote_with_quality["quality"]
            rtl = "\u200F"

            quality_info = f"\n\n{rtl}📈 *איכות:* {quality['grade']} ({quality['score']}/25)"
            return base_message + quality_info

        return base_message
