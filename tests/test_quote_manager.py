"""Tests for the QuoteManager class."""

import json
import pytest
from pathlib import Path
from datetime import date

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.quote_manager import QuoteManager


class TestQuoteManager:
    """Test suite for QuoteManager."""
    
    @pytest.fixture
    def quote_manager(self):
        """Create a QuoteManager instance for testing."""
        return QuoteManager()
    
    def test_initialization(self, quote_manager):
        """Test that QuoteManager initializes correctly."""
        assert quote_manager.quotes_cache is not None
        assert len(quote_manager.quotes_cache) > 0
    
    def test_load_all_quotes(self, quote_manager):
        """Test that all quote sources are loaded."""
        expected_sources = [
            "arizal",
            "baal_shem_tov",
            "simcha_bunim",
            "kotzker",
            "baal_hasulam",
            "rabash",
            "ashlag_talmidim"
        ]
        
        for source in expected_sources:
            assert source in quote_manager.quotes_cache, f"Missing source: {source}"
    
    def test_get_stats(self, quote_manager):
        """Test statistics generation."""
        stats = quote_manager.get_stats()
        
        assert "total" in stats
        assert "by_source" in stats
        assert stats["total"] > 0
        
        # Should have quotes from all sources
        for source in QuoteManager.QUOTE_SOURCES:
            assert source in stats["by_source"]
            assert stats["by_source"][source] > 0
    
    def test_get_quote_for_source(self, quote_manager):
        """Test getting a quote from a specific source."""
        quote = quote_manager.get_quote_for_source("arizal")
        
        assert quote is not None
        assert "text" in quote
        assert "source" in quote
        assert "source_name" in quote
        assert len(quote["text"]) > 0
    
    def test_get_daily_quotes(self, quote_manager):
        """Test getting all daily quotes."""
        quotes = quote_manager.get_daily_quotes()
        
        # Should return one quote per source
        assert len(quotes) == len(QuoteManager.QUOTE_SOURCES)
        
        for quote in quotes:
            assert "text" in quote
            assert "source" in quote
            assert "source_name" in quote
    
    def test_daily_quotes_deterministic(self, quote_manager):
        """Test that daily quotes are deterministic for the same day."""
        quotes1 = quote_manager.get_daily_quotes()
        quotes2 = quote_manager.get_daily_quotes()
        
        # Should return the same quotes for the same day
        for q1, q2 in zip(quotes1, quotes2):
            assert q1["id"] == q2["id"]
    
    def test_format_quote_message(self, quote_manager):
        """Test quote message formatting."""
        quote = quote_manager.get_quote_for_source("kotzker")
        message = quote_manager.format_quote_message(quote)
        
        # Should contain key elements
        assert quote["source_name"] in message
        assert quote["text"] in message
        assert "📖" in message  # Source indicator
    
    def test_format_daily_message(self, quote_manager):
        """Test daily message formatting."""
        message = quote_manager.format_daily_message()
        
        # Should contain header
        assert "ציטוט יומי" in message
        
        # Should contain date
        today = date.today()
        assert today.strftime("%d/%m/%Y") in message
        
        # Message should not be empty
        assert len(message) > 100
    
    def test_get_random_quote(self, quote_manager):
        """Test random quote selection."""
        quote = quote_manager.get_random_quote()
        
        assert quote is not None
        assert "text" in quote
        assert "source" in quote
        assert "source_name" in quote
    
    def test_get_quote_by_id(self, quote_manager):
        """Test finding quote by ID."""
        # Get a known quote ID
        quotes = quote_manager.get_daily_quotes()
        known_id = quotes[0]["id"]
        
        found = quote_manager.get_quote_by_id(known_id)
        assert found is not None
        assert found["id"] == known_id
    
    def test_get_quote_by_invalid_id(self, quote_manager):
        """Test handling of invalid quote ID."""
        found = quote_manager.get_quote_by_id("nonexistent_id_12345")
        assert found is None
    
    def test_quote_structure(self, quote_manager):
        """Test that all quotes have required fields."""
        for source_name, source_data in quote_manager.quotes_cache.items():
            for quote in source_data.get("quotes", []):
                assert "id" in quote, f"Missing 'id' in {source_name}"
                assert "text" in quote, f"Missing 'text' in {source_name}"
                assert "source" in quote, f"Missing 'source' in {source_name}"
                assert "source_url" in quote, f"Missing 'source_url' in {source_name}"
                
                # Text should not be empty
                assert len(quote["text"]) > 0, f"Empty text in {source_name}"
    
    def test_source_urls_valid(self, quote_manager):
        """Test that all source URLs are valid format."""
        import re
        url_pattern = re.compile(
            r'^https?://'  # http:// or https://
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain
            r'localhost|'  # localhost
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # or IP
            r'(?::\d+)?'  # optional port
            r'(?:/?|[/?]\S+)$', re.IGNORECASE
        )
        
        for source_name, source_data in quote_manager.quotes_cache.items():
            for quote in source_data.get("quotes", []):
                url = quote.get("source_url", "")
                assert url_pattern.match(url), f"Invalid URL in {source_name}: {url}"


class TestQuoteValidation:
    """Tests for validating quote data files."""
    
    def test_json_files_valid(self):
        """Test that all JSON files are valid."""
        quotes_dir = Path(__file__).parent.parent / "data" / "quotes"
        
        for json_file in quotes_dir.glob("*.json"):
            with open(json_file, "r", encoding="utf-8") as f:
                data = json.load(f)  # Should not raise
                
                # Validate structure
                assert "source_name" in data
                assert "quotes" in data
                assert isinstance(data["quotes"], list)
    
    def test_minimum_quotes_per_source(self):
        """Test that each source has at least 10 quotes."""
        quotes_dir = Path(__file__).parent.parent / "data" / "quotes"
        min_quotes = 10
        
        for json_file in quotes_dir.glob("*.json"):
            with open(json_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                quote_count = len(data.get("quotes", []))
                
                assert quote_count >= min_quotes, \
                    f"{json_file.name} has only {quote_count} quotes (minimum: {min_quotes})"
    
    def test_unique_quote_ids(self):
        """Test that all quote IDs are unique."""
        quotes_dir = Path(__file__).parent.parent / "data" / "quotes"
        all_ids = set()
        
        for json_file in quotes_dir.glob("*.json"):
            with open(json_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                
                for quote in data.get("quotes", []):
                    quote_id = quote.get("id")
                    assert quote_id not in all_ids, f"Duplicate ID: {quote_id}"
                    all_ids.add(quote_id)
    
    def test_hebrew_text_present(self):
        """Test that quotes contain Hebrew text."""
        import re
        hebrew_pattern = re.compile(r'[\u0590-\u05FF]')
        
        quotes_dir = Path(__file__).parent.parent / "data" / "quotes"
        
        for json_file in quotes_dir.glob("*.json"):
            with open(json_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                
                for quote in data.get("quotes", []):
                    text = quote.get("text", "")
                    assert hebrew_pattern.search(text), \
                        f"No Hebrew text in quote {quote.get('id')} from {json_file.name}"
