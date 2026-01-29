"""
Pytest configuration and fixtures for Ashlag Yomi tests.

Fixtures are reusable test components that provide:
- Sample data
- Mock objects
- Test infrastructure

Usage in tests:
    def test_something(sample_quote, mock_repository):
        assert sample_quote.text == "..."
"""

from datetime import date, datetime
from pathlib import Path
from unittest.mock import MagicMock

import pytest

from src.data.models import DailyBundle, Quote, QuoteCategory
from src.data.repository import QuoteRepository
from src.utils.config import get_settings


@pytest.fixture(autouse=True, scope="function")
def clear_settings_cache():
    """Clear settings cache before and after each test."""
    get_settings.cache_clear()
    yield
    get_settings.cache_clear()


@pytest.fixture
def sample_quote() -> Quote:
    """Create a sample quote for testing."""
    return Quote(
        id="test-quote-001",
        text="הסתכלות בתכלית מביאה את האדם לשלמות",
        source_rabbi="בעל הסולם",
        source_book="מאמרי הסולם",
        source_section="מאמר א׳",
        source_url="https://www.orhassulam.com/test",
        category=QuoteCategory.BAAL_HASULAM,
        tags=["תכלית", "שלמות"],
        length_estimate=15,
        created_at=datetime(2024, 1, 1, 12, 0, 0),
    )


@pytest.fixture
def sample_quotes() -> list[Quote]:
    """Create a list of sample quotes, one per category."""
    quotes = []
    for i, category in enumerate(QuoteCategory):
        quotes.append(
            Quote(
                id=f"test-{category.value}-{i:03d}",
                text=f"ציטוט לדוגמא מקטגוריה {category.display_name_hebrew}",
                source_rabbi=category.display_name_hebrew,
                source_url=f"https://example.com/{category.value}",
                category=category,
                tags=["test"],
                length_estimate=15,
            )
        )
    return quotes


@pytest.fixture
def sample_bundle(sample_quotes: list[Quote]) -> DailyBundle:
    """Create a sample daily bundle for testing."""
    return DailyBundle(
        date=date(2024, 1, 15),
        quotes=sample_quotes,
    )


@pytest.fixture
def temp_quotes_dir(tmp_path: Path) -> Path:
    """Create a temporary directory for quote files."""
    quotes_dir = tmp_path / "quotes"
    quotes_dir.mkdir()
    return quotes_dir


@pytest.fixture
def temp_history_file(tmp_path: Path) -> Path:
    """Create a temporary file path for sent history."""
    return tmp_path / "sent_history.json"


@pytest.fixture
def mock_repository(
    temp_quotes_dir: Path,
    temp_history_file: Path,
    sample_quotes: list[Quote],
) -> QuoteRepository:
    """Create a repository with temporary storage and sample data."""
    import json

    # Create quote files
    for category in QuoteCategory:
        category_quotes = [q for q in sample_quotes if q.category == category]
        if category_quotes:
            data = {
                "category": category.value,
                "quotes": [q.model_dump(mode="json") for q in category_quotes],
            }
            file_path = temp_quotes_dir / f"{category.value}.json"
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False)

    return QuoteRepository(
        quotes_dir=temp_quotes_dir,
        history_file=temp_history_file,
    )


@pytest.fixture
def mock_bot() -> MagicMock:
    """Create a mock Telegram bot for testing."""
    bot = MagicMock()
    bot.send_message = MagicMock(return_value=None)
    bot.get_me = MagicMock(return_value=MagicMock(username="test_bot"))
    return bot


@pytest.fixture(autouse=True)
def mock_settings(monkeypatch: pytest.MonkeyPatch) -> None:
    """Set up mock environment variables for testing.

    This is autouse=True to ensure all tests have valid env vars
    since Settings requires TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID.
    """
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "test_token_12345")
    monkeypatch.setenv("TELEGRAM_CHAT_ID", "@test_channel")
    monkeypatch.setenv("ENVIRONMENT", "development")
    monkeypatch.setenv("LOG_LEVEL", "DEBUG")
    monkeypatch.setenv("DRY_RUN", "true")
