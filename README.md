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

Ashlag Yomi delivers **two daily quotes** from the masters of the Ashlag lineage — one from Baal HaSulam and one from Rabash every morning at 6:00 AM Israel time. Each quote shows its source title and links directly to the original text.

### Why Use This Bot?

- **Learn** — Two quotes daily from Baal HaSulam and Rabash
- **Source** — Every quote links to the original Hebrew text
- **Simple** — Just two commands: `/start` and `/today`
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
| `/start` | Welcome message and subscription info |
| `/today` | Get today's 2 quotes (Baal Hasulam + Rabash) |

Each quote displays:
- **Title** — Source book and section (e.g., "פתיחה לחכמת הקבלה, אות א")
- **Text** — Full Hebrew quote
- **Link** — Clickable button to the original source

---

## Quote Coverage

| Source | Master | Period | Quotes |
|--------|--------|--------|--------|
| 📖 **Baal HaSulam** | Rabbi Yehuda Ashlag | 1884-1954 | 365 quotes from כתבי בעל הסולם |
| 💎 **Rabash** | Rabbi Baruch Shalom Ashlag | 1907-1991 | 365 quotes from שלבי הסולם ומאמרי חברה |

**730 total quotes — random daily selection based on date**

---

## Architecture

```
┌──────────────────────────────────────────────────────────────────────────┐
│                            Ashlag Yomi Bot                                │
├──────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  ┌─────────────────────────────────────────────────────────────────────┐│
│  │                        GitHub Actions                                ││
│  │  ┌─────────────────┐  ┌─────────────┐  ┌───────────────────────┐   ││
│  │  │ daily-quote.yml │  │ test-bot.yml│  │       ci.yml          │   ││
│  │  │  (6 AM Israel)  │  │ (bot tests) │  │ (lint, test, check)   │   ││
│  │  └────────┬────────┘  └─────────────┘  └───────────────────────┘   ││
│  └───────────┼────────────────────────────────────────────────────────┘│
│              │                                                          │
│              ▼                                                          │
│  ┌─────────────────────────────────────────────────────────────────────┐│
│  │                          Bot Layer                                  ││
│  │   main.py ──── handlers.py ──── broadcaster.py                      ││
│  │      │              │                                               ││
│  │      └──────────────┴──── /start, /today                            ││
│  └─────────────────────────────────────────────────────────────────────┘│
│              │                                                          │
│              ▼                                                          │
│  ┌─────────────────────────────────────────────────────────────────────┐│
│  │                         Data Layer                                  ││
│  │   quote_repository.py ──── models.py                                ││
│  │         │                                                           ││
│  │         ▼                                                           ││
│  │   data/quotes/*.json (730 quotes from 2 sources)                    ││
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
│   │   │   ├── main.py           # Bot entry (/start, /today only)
│   │   │   ├── handlers.py       # Command handlers
│   │   │   └── broadcaster.py    # Channel broadcasts
│   │   ├── data/
│   │   │   ├── models.py              # Pydantic models (Quote, QuoteCategory)
│   │   │   └── quote_repository.py    # Data access, random selection
│   │   └── utils/
│   │       ├── config.py         # Settings management
│   │       └── logger.py         # Structured logging
│   ├── data/quotes/              # JSON quote files (730 quotes)
│   │   ├── baal_hasulam.json     # 365 Baal Hasulam quotes
│   │   └── rabash.json           # 365 Rabash quotes
│   ├── tests/                    # Unit and integration tests
│   ├── scripts/
│   │   ├── test_output.py        # Preview daily quotes
│   │   └── diagnose.py           # Component diagnostics
│   ├── Dockerfile
│   └── docker-compose.yml
└── .github/workflows/
    ├── ci.yml                    # Lint, test, type-check
    ├── daily-quote.yml           # 6 AM daily broadcast
    └── test-bot.yml              # Bot command testing
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

- 📖 **Quote curation** — Add more authentic quotes from primary sources
- ✏️ **Hebrew proofreading** — Verify text accuracy
- 🔗 **Source links** — Ensure all links point to correct sources
- 🐛 **Bug fixes** — Report or fix issues

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
