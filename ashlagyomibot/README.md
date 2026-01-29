<div align="center">

# Ashlag Yomi

**Daily Kabbalistic wisdom from the Ashlag lineage**

[![MIT License](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.11+](https://img.shields.io/badge/Python-3.11+-3776ab.svg)](https://python.org)
[![Telegram Bot](https://img.shields.io/badge/Telegram-Bot-0088cc.svg)](https://t.me/AshlagYomiBot)
[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED.svg)](Dockerfile)

[Start the Bot](https://t.me/AshlagYomiBot) &bull; [Report Issue](https://github.com/naorbrown/ashlag-yomi/issues) &bull; [Contribute](CONTRIBUTING.md)

</div>

---

## Overview

Ashlag Yomi delivers daily spiritual teachings from six lineages of Kabbalistic masters to Telegram users. The bot sends six quotes each day at 6:00 AM Israel time, with each quote linking to its original source.

**Key numbers:**
- 2,011 curated quotes
- 6 spiritual lineages
- 365 days of unique content

---

## Quick Start

### For Users

1. Open Telegram
2. Search for `@AshlagYomiBot` or [click here](https://t.me/AshlagYomiBot)
3. Send `/start`

### For Developers

```bash
git clone https://github.com/naorbrown/ashlag-yomi.git
cd ashlag-yomi/ashlagyomibot
pip install -e ".[dev]"
cp .env.example .env  # Add your bot token
python -m src.bot.main
```

---

## Commands

| Command | Description |
|---------|-------------|
| `/start` | Welcome message and command list |
| `/today` | Receive all 6 daily quotes |
| `/quote` | Receive one random quote |
| `/about` | Learn about the spiritual lineage |
| `/help` | Show available commands |
| `/feedback` | Report issues or suggest features |

---

## Quote Sources

| Lineage | Teacher | Period | Quotes |
|---------|---------|--------|:------:|
| Arizal | Rabbi Isaac Luria | 1534-1572 | 365 |
| Baal Shem Tov | Rabbi Israel ben Eliezer | 1698-1760 | 365 |
| Polish Chassidut | Maggid, Kotzk, Peshischa | 1700-1900 | 365 |
| Baal HaSulam | Rabbi Yehuda Ashlag | 1884-1954 | 365 |
| Rabash | Rabbi Baruch Shalom Ashlag | 1907-1991 | 365 |
| Chasdei Ashlag | Contemporary students | Present | 186 |

All quotes link to original sources on [Sefaria](https://www.sefaria.org/) or [Or HaSulam](https://www.orhassulam.com/).

---

## Deployment

### Option 1: GitHub Actions (Recommended)

Runs on GitHub's free tier with no server required.

1. Fork this repository
2. Add repository secrets:
   - `TELEGRAM_BOT_TOKEN` from [@BotFather](https://t.me/BotFather)
   - `TELEGRAM_CHANNEL_ID` (e.g., `@YourChannel`)
3. Enable GitHub Actions

The workflow sends daily quotes at 6:00 AM Israel time.

### Option 2: Docker

```bash
# Using Docker Compose
docker-compose up -d

# Or directly
docker build -t ashlag-yomi .
docker run -d --env-file .env ashlag-yomi
```

### Option 3: Manual

```bash
# Install
pip install -e .

# Configure
export TELEGRAM_BOT_TOKEN="your-token"
export TELEGRAM_CHAT_ID="@your-channel"

# Run
python -m src.bot.main
```

---

## Configuration

| Variable | Required | Default | Description |
|----------|:--------:|---------|-------------|
| `TELEGRAM_BOT_TOKEN` | Yes | — | Bot token from @BotFather |
| `TELEGRAM_CHAT_ID` | Yes | — | Target channel or chat ID |
| `TELEGRAM_CHANNEL_ID` | No | — | Public channel for broadcasts |
| `ENVIRONMENT` | No | `development` | `development`, `staging`, or `production` |
| `DRY_RUN` | No | `false` | Log messages instead of sending |
| `LOG_LEVEL` | No | `INFO` | `DEBUG`, `INFO`, `WARNING`, `ERROR` |

Create a `.env` file from `.env.example`:

```bash
cp .env.example .env
```

---

## Architecture

```
src/
├── bot/
│   ├── main.py          # Application entry point
│   ├── handlers.py      # Command handlers
│   ├── formatters.py    # Message formatting
│   ├── rate_limit.py    # Request rate limiting
│   ├── broadcaster.py   # Channel broadcasts
│   └── scheduler.py     # Scheduled tasks
├── data/
│   ├── models.py        # Pydantic data models
│   └── repository.py    # Data access layer
└── utils/
    ├── config.py        # Settings management
    └── logger.py        # Structured logging

data/quotes/             # JSON quote files (one per lineage)
tests/                   # Unit and integration tests
scripts/                 # Utility scripts
```

### Technology Stack

| Component | Technology |
|-----------|------------|
| Language | Python 3.11+ |
| Bot Framework | python-telegram-bot 20+ |
| Data Validation | Pydantic 2 |
| Configuration | pydantic-settings |
| Logging | structlog |
| Testing | pytest, pytest-asyncio |
| Linting | ruff, black, mypy |
| CI/CD | GitHub Actions |
| Containerization | Docker |

---

## Development

### Setup

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install with dev dependencies
pip install -e ".[dev]"

# Set up pre-commit hooks
pre-commit install
```

### Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=term-missing

# Run specific test file
pytest tests/unit/test_handlers.py -v
```

Coverage requirement: 80% minimum.

### Code Quality

```bash
# Lint
ruff check src tests

# Format
black src tests

# Type check
mypy src

# Run all checks
pre-commit run --all-files
```

### Diagnostics

```bash
# Verify all components work
python scripts/diagnose.py
```

---

## API Rate Limits

The bot implements rate limiting to comply with Telegram API restrictions:

- **User rate limit:** 5 requests per minute per user
- **Message delay:** 0.3 seconds between messages in `/today`
- **Telegram limits:** Respects 30 messages/second global limit

---

## Security

### Reporting Vulnerabilities

Report security issues to the maintainers via [GitHub Security Advisories](https://github.com/naorbrown/ashlag-yomi/security/advisories/new).

Do not disclose security vulnerabilities in public issues.

### Security Measures

- Bot tokens stored as secrets, never committed
- Non-root user in Docker container
- Input validation via Pydantic models
- Rate limiting prevents abuse
- No user data collection or storage

See [SECURITY.md](SECURITY.md) for the full security policy.

---

## Contributing

Contributions are welcome. See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

**Ways to contribute:**
- Curate quotes from primary sources
- Proofread Hebrew text
- Improve documentation
- Add features or fix bugs
- Write tests

### Code of Conduct

This project follows the [Contributor Covenant](CODE_OF_CONDUCT.md). All contributors are expected to uphold this code.

---

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for the full text.

### Quote Content

The spiritual texts quoted in this project are in the public domain. Translations and commentary are attributed to their respective sources:

- [Sefaria](https://www.sefaria.org/) — CC-BY-NC
- [Or HaSulam](https://www.orhassulam.com/) — Used with attribution

---

## Acknowledgments

- [Sefaria](https://www.sefaria.org/) for open-source Jewish texts
- [Or HaSulam](https://www.orhassulam.com/) for Ashlag writings
- [python-telegram-bot](https://python-telegram-bot.org/) for the bot framework

---

## Support

- **Issues:** [GitHub Issues](https://github.com/naorbrown/ashlag-yomi/issues)
- **Discussions:** [GitHub Discussions](https://github.com/naorbrown/ashlag-yomi/discussions)

---

<div align="center">

_"The purpose of creation is to benefit the created beings."_

— Baal HaSulam

</div>
