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

## Scripts

| Script | Purpose |
|--------|---------|
| `python -m src.bot.main` | Run bot in polling mode |
| `python scripts/diagnose.py` | Verify all components |
| `python scripts/test_bot.py` | Send test message |
| `python scripts/send_daily.py` | Manual daily broadcast |

## Testing

```bash
# Run all tests
pytest

# With coverage
pytest --cov=src --cov-report=term-missing
```
