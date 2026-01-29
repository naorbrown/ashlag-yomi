<div align="center">

# Ashlag Yomi

**Daily maamarim from the Ashlag lineage.**

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.11+](https://img.shields.io/badge/Python-3.11+-3776ab.svg)](https://python.org)
[![Telegram Bot](https://img.shields.io/badge/Telegram-Bot-blue.svg)](https://t.me/AshlagYomiBot)
[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED.svg)](ashlagyomibot/Dockerfile)

[**Start Learning**](https://t.me/AshlagYomiBot) · [Report Bug](https://github.com/naorbrown/ashlag-yomi/issues) · [Request Feature](https://github.com/naorbrown/ashlag-yomi/issues)

</div>

---

## What is Ashlag Yomi?

Ashlag Yomi delivers **two complete maamarim (articles) daily** from the masters of the Ashlag lineage — one from Baal HaSulam and one from Rabash every morning at 6:00 AM Israel time. Each maamar links directly to its original source.

### Why Use This Bot?

- **Learn** — Two complete maamarim daily from Baal HaSulam and Rabash
- **Source** — Every maamar links to the original Hebrew text
- **Depth** — Full articles, not just short quotes
- **Free** — Open source, run your own instance

---

## Deploy Your Own

### Option 1: GitHub Actions (Free, Recommended)

The bot runs entirely on GitHub Actions — no server required!

1. Fork this repository
2. Go to **Settings → Secrets and variables → Actions**
3. Add these secrets:
   - `TELEGRAM_BOT_TOKEN` — Get from [@BotFather](https://t.me/BotFather)
   - `TELEGRAM_CHANNEL_ID` — Your channel ID (e.g., `@YourChannel`)
4. Enable GitHub Actions in your fork

Daily quotes will be sent automatically at 6:00 AM Israel time.

### Option 2: Docker

```bash
cd ashlagyomibot
docker-compose up -d

# Or directly
docker build -t ashlag-yomi .
docker run -d --env-file .env ashlag-yomi
```

### Option 3: Python

```bash
cd ashlagyomibot
pip install -e .
export TELEGRAM_BOT_TOKEN="your-token"
export TELEGRAM_CHAT_ID="@your-channel"
python -m src.bot.main
```

---

## Commands

| Command | Description |
|---------|-------------|
| `/start` | Welcome message and commands |
| `/today` | Get today's 2 maamarim (Baal Hasulam + Rabash) |
| `/maamar` | Get a random maamar |
| `/about` | Learn about the sources |
| `/help` | Show available commands |
| `/feedback` | Report issues or suggest features |

---

## Maamar Coverage

| Source | Master | Period | Content |
|--------|--------|--------|---------|
| 📖 **Baal HaSulam** | Rabbi Yehuda Ashlag | 1884-1954 | Complete maamarim from כתבי בעל הסולם |
| 💎 **Rabash** | Rabbi Baruch Shalom Ashlag | 1907-1991 | Complete maamarim from ברכת שלום |

**Two complete maamarim daily — fair rotation ensures no repetition**

---

## Architecture

```
┌──────────────────────────────────────────────────────────────────────────┐
│                            Ashlag Yomi Bot                                │
├──────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  ┌─────────────────────────────────────────────────────────────────────┐│
│  │                        GitHub Actions                                ││
│  │  ┌─────────────────┐              ┌─────────────────────────────┐  ││
│  │  │ daily-quote.yml │              │          ci.yml             │  ││
│  │  │  (6 AM Israel)  │              │  (lint, test, type-check)   │  ││
│  │  └────────┬────────┘              └─────────────────────────────┘  ││
│  └───────────┼────────────────────────────────────────────────────────┘│
│              │                                                          │
│              ▼                                                          │
│  ┌─────────────────────────────────────────────────────────────────────┐│
│  │                          Bot Layer                                  ││
│  │   main.py ──── handlers.py ──── broadcaster.py ──── scheduler.py   ││
│  │                      │                                              ││
│  │                      ▼                                              ││
│  │          formatters.py (HTML + inline keyboards)                    ││
│  └─────────────────────────────────────────────────────────────────────┘│
│              │                                                          │
│              ▼                                                          │
│  ┌─────────────────────────────────────────────────────────────────────┐│
│  │                         Data Layer                                  ││
│  │   maamar_repository.py ──── models.py                               ││
│  │         │                                                           ││
│  │         ▼                                                           ││
│  │   data/maamarim/*.json (scraped maamarim from 2 sources)            ││
│  └─────────────────────────────────────────────────────────────────────┘│
│                                                                          │
└──────────────────────────────────────────────────────────────────────────┘
                              │
                              ▼
                     ┌─────────────────┐
                     │    Telegram     │
                     │    Bot API      │
                     └─────────────────┘
```

### Directory Structure

```
ashlag-yomi/
├── ashlagyomibot/
│   ├── src/
│   │   ├── bot/
│   │   │   ├── main.py           # Bot entry, command registration
│   │   │   ├── handlers.py       # /start, /today, /quote, etc.
│   │   │   ├── formatters.py     # HTML formatting, inline keyboards
│   │   │   ├── rate_limit.py     # Request rate limiting
│   │   │   ├── broadcaster.py    # Channel broadcasts
│   │   │   └── scheduler.py      # Scheduled daily posts
│   │   ├── data/
│   │   │   ├── models.py              # Pydantic models (Maamar, SourceCategory)
│   │   │   ├── maamar_repository.py   # Data access, fair rotation
│   │   │   └── sources/               # Web scrapers (baal_hasulam.py, rabash.py)
│   │   └── utils/
│   │       ├── config.py         # Settings management
│   │       └── logger.py         # Structured logging
│   ├── data/maamarim/            # JSON cache of scraped maamarim
│   ├── tests/                    # Unit and integration tests
│   ├── scripts/
│   │   ├── diagnose.py           # Component diagnostics
│   │   └── test_bot.py           # Manual testing
│   ├── Dockerfile
│   └── docker-compose.yml
└── .github/workflows/            # CI + daily broadcast
```

### Tech Stack

| Component | Technology | Purpose |
|-----------|------------|---------|
| Runtime | Python 3.11+ | Async/await, type hints |
| Bot Framework | python-telegram-bot 20+ | Telegram integration |
| Data Validation | Pydantic 2 | Type-safe models |
| Configuration | pydantic-settings | Environment management |
| Logging | structlog | Structured JSON logs |
| Scheduler | GitHub Actions | Daily 6 AM posts |
| Containerization | Docker | Production deployment |
| Testing | pytest, pytest-asyncio | 80%+ coverage |
| Linting | ruff, black, mypy | Code quality |

---

## Configuration

| Variable | Required | Description |
|----------|:--------:|-------------|
| `TELEGRAM_BOT_TOKEN` | ✅ | Token from [@BotFather](https://t.me/BotFather) |
| `TELEGRAM_CHAT_ID` | ✅ | Target channel or chat ID |
| `TELEGRAM_CHANNEL_ID` | | Public channel for broadcasts |
| `ENVIRONMENT` | | `development` / `production` |
| `DRY_RUN` | | Set `true` to log instead of send |

```bash
cd ashlagyomibot
cp .env.example .env
# Edit .env with your values
```

---

## Development

```bash
cd ashlagyomibot

# Install with dev dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Lint and format
ruff check src tests
black src tests
mypy src

# Diagnose issues
python scripts/diagnose.py
```

---

## Data Sources

| Source | Purpose | Link |
|--------|---------|------|
| [Or HaSulam](https://search.orhasulam.org) | Baal Hasulam writings | Attribution |
| [Ashlag Baruch](https://ashlagbaroch.org) | Rabash writings (PDFs) | Attribution |

---

## Contributing

Contributions welcome! See [CONTRIBUTING.md](ashlagyomibot/CONTRIBUTING.md) for guidelines.

### Priority Areas

- 📖 **Quote curation** — Add authentic quotes from primary sources
- ✏️ **Hebrew proofreading** — Verify text accuracy
- 🐛 **Bug fixes** — Report or fix issues
- 📝 **Documentation** — Improve guides

---

## Security

See [SECURITY.md](ashlagyomibot/SECURITY.md) for reporting vulnerabilities.

---

## License

[MIT](LICENSE) — Free to use, modify, and distribute.

Quote sources are in the public domain or used with attribution.

---

## Acknowledgments

- **[Or HaSulam](https://search.orhasulam.org)** — Baal Hasulam writings archive
- **[Ashlag Baruch](https://ashlagbaroch.org)** — Rabash writings archive
- **[python-telegram-bot](https://python-telegram-bot.org)** — Bot framework

---

<div align="center">

_״תכלית הבריאה היא להיטיב לנבראיו״_

_"The purpose of creation is to benefit the created beings."_

— Baal HaSulam

**[Start learning with @AshlagYomiBot](https://t.me/AshlagYomiBot)**

</div>
