"""
Pytest configuration and fixtures for Ashlag Yomi tests.

Fixtures are reusable test components that provide:
- Sample data
- Mock objects
- Test infrastructure

Usage in tests:
    def test_something(sample_maamar, mock_maamar_repository):
        assert sample_maamar.title == "..."
"""

from datetime import date, datetime
from pathlib import Path
from unittest.mock import MagicMock

import pytest

from src.data.maamar_repository import MaamarRepository
from src.data.models import (
    DailyBundle,
    DailyMaamar,
    Maamar,
    MaamarCollection,
    Quote,
    QuoteCategory,
    SourceCategory,
)
from src.utils.config import get_settings


@pytest.fixture(autouse=True, scope="function")
def clear_settings_cache():
    """Clear settings cache before and after each test."""
    get_settings.cache_clear()
    yield
    get_settings.cache_clear()


@pytest.fixture(autouse=True, scope="function")
def clear_repository_cache():
    """Clear maamar repository singleton cache."""
    from src.data.maamar_repository import get_maamar_repository

    get_maamar_repository.cache_clear()
    yield
    get_maamar_repository.cache_clear()


# =============================================================================
# NEW MAAMAR FIXTURES
# =============================================================================


@pytest.fixture
def sample_maamar() -> Maamar:
    """Create a sample maamar for testing."""
    return Maamar(
        id="baal_hasulam_test_001",
        source=SourceCategory.BAAL_HASULAM,
        title="מאמר הערבות",
        subtitle="על האחדות והערבות ההדדית",
        text="כל ישראל ערבים זה בזה. " * 50,  # Enough text
        book="מאמרי הסולם",
        page="42",
        source_url="https://search.orhasulam.org/test",
        scraped_at=datetime(2024, 1, 1, 12, 0, 0),
    )


@pytest.fixture
def sample_maamar_rabash() -> Maamar:
    """Create a sample Rabash maamar for testing."""
    return Maamar(
        id="rabash_test_001",
        source=SourceCategory.RABASH,
        title="מהו מצוה קלה",
        text="צריך להבין מהו מצוה קלה שאדם דש בעקביו. " * 50,
        book="ברכת שלום",
        page="15",
        source_url="https://ashlagbaroch.org/test.pdf",
        pdf_filename="test.pdf",
        pdf_start_page=15,
        pdf_end_page=17,
        scraped_at=datetime(2024, 1, 1, 12, 0, 0),
    )


@pytest.fixture
def sample_maamarim(
    sample_maamar: Maamar, sample_maamar_rabash: Maamar
) -> list[Maamar]:
    """Create a list of sample maamarim, one per source category."""
    return [sample_maamar, sample_maamar_rabash]


@pytest.fixture
def sample_daily_maamar(sample_maamar: Maamar) -> DailyMaamar:
    """Create a sample daily maamar for testing."""
    return DailyMaamar(
        date=date(2024, 1, 15),
        maamar=sample_maamar,
    )


@pytest.fixture
def temp_maamarim_dir(tmp_path: Path) -> Path:
    """Create a temporary directory for maamar cache files."""
    maamarim_dir = tmp_path / "maamarim"
    maamarim_dir.mkdir()
    return maamarim_dir


@pytest.fixture
def temp_maamar_history_file(tmp_path: Path) -> Path:
    """Create a temporary file path for maamar sent history."""
    return tmp_path / "maamar_history.json"


@pytest.fixture
def mock_maamar_repository(
    temp_maamarim_dir: Path,
    temp_maamar_history_file: Path,
    sample_maamarim: list[Maamar],
) -> MaamarRepository:
    """Create a maamar repository with temporary storage and sample data."""
    import json

    # Create maamar collection files by source
    for source in SourceCategory:
        source_maamarim = [m for m in sample_maamarim if m.source == source]
        if source_maamarim:
            collection = MaamarCollection(
                source=source,
                maamarim=source_maamarim,
                last_updated=datetime.utcnow(),
            )
            file_path = temp_maamarim_dir / f"{source.value}.json"
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(collection.model_dump(mode="json"), f, ensure_ascii=False)

    repo = MaamarRepository(
        maamarim_dir=temp_maamarim_dir,
        history_file=temp_maamar_history_file,
    )
    repo._load_all_maamarim()
    return repo


# =============================================================================
# LEGACY QUOTE FIXTURES (kept for backward compatibility)
# =============================================================================


@pytest.fixture
def sample_quote() -> Quote:
    """Create a sample quote for testing (legacy)."""
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
    """Create a list of sample quotes, one per category (legacy)."""
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
    """Create a sample daily bundle for testing (legacy)."""
    return DailyBundle(
        date=date(2024, 1, 15),
        quotes=sample_quotes,
    )


@pytest.fixture
def temp_quotes_dir(tmp_path: Path) -> Path:
    """Create a temporary directory for quote files (legacy)."""
    quotes_dir = tmp_path / "quotes"
    quotes_dir.mkdir()
    return quotes_dir


@pytest.fixture
def temp_history_file(tmp_path: Path) -> Path:
    """Create a temporary file path for sent history (legacy)."""
    return tmp_path / "sent_history.json"


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
