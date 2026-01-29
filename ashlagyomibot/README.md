# Ashlag Yomi Bot

This directory contains the Telegram bot implementation.

**See the main [README](../README.md) for full documentation.**

## Quick Start

```bash
# Install
pip install -e ".[dev]"

# Configure
cp .env.example .env
# Edit .env with your bot token

# Run
python -m src.bot.main
```

## Bot Commands

| Command | Description |
|---------|-------------|
| `/start` | Welcome message and subscription info |
| `/today` | Get today's 2 quotes (Baal Hasulam + Rabash) |

## Scripts

| Script | Purpose |
|--------|---------|
| `python -m src.bot.main` | Run bot in polling mode |
| `python scripts/test_output.py` | Preview today's quotes |
| `python scripts/diagnose.py` | Verify all components |

## Testing

```bash
# Run all tests
pytest

# With coverage
pytest --cov=src --cov-report=term-missing

# Preview quote output
python scripts/test_output.py
```

## Data

- **730 quotes** total (365 per source)
- Located in `data/quotes/baal_hasulam.json` and `data/quotes/rabash.json`
- Random daily selection based on date seed
- Each quote includes source book, section, and URL
