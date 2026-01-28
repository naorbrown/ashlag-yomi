"""
Pytest configuration and fixtures for Ashlag Yomi tests.
"""

import json
import os
import sys
import tempfile
from pathlib import Path
from typing import Generator
from unittest.mock import MagicMock, AsyncMock

import pytest

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


@pytest.fixture
def sample_quotes_dir() -> Generator[Path, None, None]:
    """Create a temporary directory with sample quotes for testing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        quotes_dir = Path(tmpdir)

        # Create metadata
        metadata = {
            "test_rabbi": {
                "name_hebrew": "רב לדוגמה",
                "name_english": "Test Rabbi",
                "years": "1900-2000",
                "description": "רב לצורך בדיקות",
            }
        }
        with open(quotes_dir / "metadata.json", "w", encoding="utf-8") as f:
            json.dump(metadata, f, ensure_ascii=False)

        # Create sample quotes
        quotes = {
            "rabbi_id": "test_rabbi",
            "quotes": [
                {
                    "text": "זהו ציטוט לדוגמה לבדיקות.",
                    "source": "ספר הבדיקות",
                    "source_url": "https://example.com/test",
                    "topic": "בדיקות",
                },
                {
                    "text": "ציטוט נוסף לבדיקה.",
                    "source": "מקור אחר",
                    "source_url": "https://example.com/test2",
                    "topic": "דוגמה",
                },
            ],
        }
        with open(quotes_dir / "test_rabbi.json", "w", encoding="utf-8") as f:
            json.dump(quotes, f, ensure_ascii=False)

        yield quotes_dir


@pytest.fixture
def mock_bot_token() -> str:
    """Return a mock bot token for testing."""
    return "1234567890:ABCdefGHIjklMNOpqrsTUVwxyz"


@pytest.fixture
def mock_update() -> MagicMock:
    """Create a mock Telegram Update object."""
    update = MagicMock()
    update.effective_chat.id = 123456789
    update.message.reply_text = AsyncMock()
    return update


@pytest.fixture
def mock_context() -> MagicMock:
    """Create a mock Telegram Context object."""
    context = MagicMock()
    return context


@pytest.fixture(autouse=True)
def clean_env():
    """Clean environment variables before and after tests."""
    original_env = os.environ.copy()
    yield
    os.environ.clear()
    os.environ.update(original_env)
