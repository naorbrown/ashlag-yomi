"""
Tests for the QuotesManager class.
"""

import json
from pathlib import Path

import pytest

from bot import QuotesManager, format_quote_message, split_long_message


class TestQuotesManager:
    """Test suite for QuotesManager."""

    def test_load_quotes_from_directory(self, sample_quotes_dir: Path):
        """Test loading quotes from a directory."""
        manager = QuotesManager(sample_quotes_dir)

        assert "test_rabbi" in manager.quotes_cache
        assert len(manager.quotes_cache["test_rabbi"]) == 2

    def test_load_metadata(self, sample_quotes_dir: Path):
        """Test loading rabbi metadata."""
        manager = QuotesManager(sample_quotes_dir)

        assert "test_rabbi" in manager.rabbis_metadata
        assert manager.rabbis_metadata["test_rabbi"]["name_hebrew"] == "רב לדוגמה"

    def test_get_random_quote(self, sample_quotes_dir: Path):
        """Test getting a random quote."""
        manager = QuotesManager(sample_quotes_dir)

        quote = manager.get_random_quote("test_rabbi")

        assert quote is not None
        assert "text" in quote
        assert "source" in quote

    def test_get_random_quote_nonexistent_rabbi(self, sample_quotes_dir: Path):
        """Test getting a quote for a non-existent rabbi."""
        manager = QuotesManager(sample_quotes_dir)

        quote = manager.get_random_quote("nonexistent_rabbi")

        assert quote is None

    def test_get_all_rabbi_keys(self, sample_quotes_dir: Path):
        """Test getting all rabbi keys."""
        manager = QuotesManager(sample_quotes_dir)

        keys = manager.get_all_rabbi_keys()

        assert "test_rabbi" in keys

    def test_get_rabbi_display_name(self, sample_quotes_dir: Path):
        """Test getting rabbi display name."""
        manager = QuotesManager(sample_quotes_dir)

        name = manager.get_rabbi_display_name("test_rabbi")

        assert name == "רב לדוגמה"

    def test_get_rabbi_display_name_unknown(self, sample_quotes_dir: Path):
        """Test getting display name for unknown rabbi."""
        manager = QuotesManager(sample_quotes_dir)

        name = manager.get_rabbi_display_name("unknown_rabbi")

        assert name == "unknown_rabbi"

    def test_empty_quotes_directory(self, tmp_path: Path):
        """Test handling empty quotes directory."""
        manager = QuotesManager(tmp_path)

        assert len(manager.quotes_cache) == 0
        assert len(manager.rabbis_metadata) == 0

    def test_invalid_json_file(self, tmp_path: Path):
        """Test handling invalid JSON file."""
        invalid_file = tmp_path / "invalid.json"
        invalid_file.write_text("not valid json{")

        manager = QuotesManager(tmp_path)

        assert "invalid" not in manager.quotes_cache


class TestFormatQuoteMessage:
    """Test suite for format_quote_message function."""

    def test_format_basic_quote(self):
        """Test formatting a basic quote."""
        quote = {
            "text": "Test quote text",
            "source": "Test Source",
            "source_url": "https://example.com",
        }

        message = format_quote_message(quote, "Test Rabbi")

        assert "Test Rabbi" in message
        assert "Test quote text" in message
        assert "Test Source" in message
        assert "https://example.com" in message

    def test_format_quote_without_url(self):
        """Test formatting a quote without source URL."""
        quote = {
            "text": "Test quote text",
            "source": "Test Source",
        }

        message = format_quote_message(quote, "Test Rabbi")

        assert "Test quote text" in message
        assert "Test Source" in message

    def test_format_quote_with_custom_author(self):
        """Test formatting a quote with custom author."""
        quote = {
            "text": "Test quote text",
            "source": "Test Source",
            "author": "Custom Author",
        }

        message = format_quote_message(quote, "Test Rabbi")

        assert "Custom Author" in message


class TestSplitLongMessage:
    """Test suite for split_long_message function."""

    def test_short_message_not_split(self):
        """Test that short messages are not split."""
        message = "Short message"

        parts = split_long_message(message, max_length=100)

        assert len(parts) == 1
        assert parts[0] == message

    def test_long_message_split(self):
        """Test that long messages are split."""
        message = "Line 1\n" * 100

        parts = split_long_message(message, max_length=50)

        assert len(parts) > 1
        for part in parts:
            assert len(part) <= 50

    def test_empty_message(self):
        """Test handling empty message."""
        parts = split_long_message("")

        assert len(parts) == 1
        assert parts[0] == ""


class TestQuotesDatabaseIntegrity:
    """Test the actual quotes database for integrity."""

    @pytest.fixture
    def real_quotes_dir(self) -> Path:
        """Get the real quotes directory."""
        return Path(__file__).parent.parent / "data" / "quotes"

    def test_all_quote_files_valid_json(self, real_quotes_dir: Path):
        """Test that all quote files are valid JSON."""
        if not real_quotes_dir.exists():
            pytest.skip("Quotes directory not found")

        for quote_file in real_quotes_dir.glob("*.json"):
            with open(quote_file, encoding="utf-8") as f:
                data = json.load(f)
                assert isinstance(data, dict)

    def test_all_quotes_have_required_fields(self, real_quotes_dir: Path):
        """Test that all quotes have required fields."""
        if not real_quotes_dir.exists():
            pytest.skip("Quotes directory not found")

        for quote_file in real_quotes_dir.glob("*.json"):
            if quote_file.name == "metadata.json":
                continue

            with open(quote_file, encoding="utf-8") as f:
                data = json.load(f)

            assert "quotes" in data, f"{quote_file.name} missing 'quotes' key"
            assert len(data["quotes"]) > 0, f"{quote_file.name} has no quotes"

            for i, quote in enumerate(data["quotes"]):
                assert "text" in quote, f"{quote_file.name}[{i}] missing 'text'"
                assert "source" in quote, f"{quote_file.name}[{i}] missing 'source'"
                assert len(quote["text"]) > 0, f"{quote_file.name}[{i}] empty text"

    def test_metadata_file_exists(self, real_quotes_dir: Path):
        """Test that metadata file exists and is valid."""
        if not real_quotes_dir.exists():
            pytest.skip("Quotes directory not found")

        metadata_file = real_quotes_dir / "metadata.json"
        assert metadata_file.exists(), "metadata.json not found"

        with open(metadata_file, encoding="utf-8") as f:
            data = json.load(f)

        assert isinstance(data, dict)
        assert len(data) > 0

    def test_all_required_rabbis_present(self, real_quotes_dir: Path):
        """Test that all required rabbi quote files exist."""
        if not real_quotes_dir.exists():
            pytest.skip("Quotes directory not found")

        required_files = [
            "arizal.json",
            "baal_shem_tov.json",
            "simcha_bunim.json",
            "kotzker_rebbe.json",
            "baal_hasulam.json",
            "rabash.json",
            "ashlag_talmidim.json",
        ]

        for filename in required_files:
            file_path = real_quotes_dir / filename
            assert file_path.exists(), f"Missing required file: {filename}"
