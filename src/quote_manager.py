"""
Quote Manager Module
Handles loading, selecting, and formatting quotes from all sources.
"""

import json
import random
import hashlib
from datetime import date
from pathlib import Path
from typing import Optional
import logging

logger = logging.getLogger(__name__)


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
