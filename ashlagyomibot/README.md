<div align="center">

# 🕯️ Ashlag Yomi

**Daily Kabbalistic Wisdom • Six Lineages • One Message**

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.11+](https://img.shields.io/badge/Python-3.11+-green.svg)](https://python.org)
[![Telegram Bot](https://img.shields.io/badge/Telegram-@AshlagYomiBot-blue.svg)](https://t.me/AshlagYomiBot)
[![CI](https://github.com/naorbrown/ashlag-yomi/actions/workflows/ci.yml/badge.svg)](https://github.com/naorbrown/ashlag-yomi/actions)
[![Docker](https://img.shields.io/badge/Docker-ghcr.io-2496ED.svg)](https://github.com/naorbrown/ashlag-yomi/pkgs/container/ashlag-yomi)
[![Coverage](https://img.shields.io/badge/Coverage-80%25+-brightgreen.svg)](https://github.com/naorbrown/ashlag-yomi/actions)

[**Start Learning**](https://t.me/AshlagYomiBot) · [**Report Bug**](https://github.com/naorbrown/ashlag-yomi/issues/new?template=bug_report.md) · [**Request Feature**](https://github.com/naorbrown/ashlag-yomi/issues/new?template=feature_request.md)

</div>

---

A Telegram bot delivering **2,011 curated quotes** from the Kabbalistic masters of the Ashlag lineage. New wisdom every morning at 6:00 AM Israel time—a direct transmission from the Arizal through Baal HaSulam to the present day.

---

## Table of Contents

- [Features](#features)
- [Commands](#commands)
- [The Lineage](#the-lineage)
- [Quote Coverage](#quote-coverage)
- [Deploy Your Own](#deploy-your-own)
- [Configuration](#configuration)
- [Architecture](#architecture)
- [Development](#development)
- [Data Sources](#data-sources)
- [Security](#security)
- [Contributing](#contributing)
- [License](#license)
- [Acknowledgments](#acknowledgments)

---

## Features

| | | |
|:---:|:---:|:---:|
| 📅 **Daily Quotes** | 🔗 **Source Links** | ⚡ **Rate Limited** |
| 6:00 AM Israel time | Sefaria & Or HaSulam | 5 requests/minute |
| | | |
| 🔄 **Fair Rotation** | 🐳 **Docker Ready** | 🌍 **DST-Aware** |
| No repeats until cycle complete | ghcr.io registry | Dual cron scheduling |

---

## Commands

| Command | Action | Response |
|---------|--------|----------|
| `/start` | Get today's wisdom | Welcome message + daily quotes |
| `/today` | Get today's 6 quotes | Full daily bundle from all lineages |
| `/quote` | Get a random quote | Single quote with source link |
| `/about` | Learn about the lineage | History of the Ashlag masters |
| `/help` | Show all commands | Command reference |
| `/feedback` | Send feedback | GitHub issues link |

---

## The Lineage

The Ashlag lineage represents a direct transmission of Kabbalistic wisdom spanning five centuries:

```
                    ┌─────────────────────────────┐
                    │      🕯️ The Holy Arizal     │
                    │   Rabbi Isaac Luria (1534-1572)   │
                    │    Father of Lurianic Kabbalah    │
                    └──────────────┬──────────────┘
                                   │
                                   ▼
                    ┌─────────────────────────────┐
                    │    ✨ The Baal Shem Tov     │
                    │ Rabbi Israel ben Eliezer (1698-1760) │
                    │     Founder of Chassidut    │
                    └──────────────┬──────────────┘
                                   │
                                   ▼
                    ┌─────────────────────────────┐
                    │    🔥 Polish Chassidut      │
                    │    Maggid, Kotzk, Peshischa    │
                    │    Lublin, Piaseczno (1700-1900) │
                    └──────────────┬──────────────┘
                                   │
                                   ▼
                    ┌─────────────────────────────┐
                    │     📖 Baal HaSulam         │
                    │ Rabbi Yehuda Ashlag (1884-1954) │
                    │  Sulam Commentary on Zohar  │
                    └──────────────┬──────────────┘
                                   │
                                   ▼
                    ┌─────────────────────────────┐
                    │        💎 Rabash            │
                    │ Rabbi Baruch Shalom Ashlag (1907-1991) │
                    │    Practical Application    │
                    └──────────────┬──────────────┘
                                   │
                                   ▼
                    ┌─────────────────────────────┐
                    │    🌱 Chasdei Ashlag        │
                    │   Contemporary Students     │
                    │   Continuing the Path       │
                    └─────────────────────────────┘
```

---

## Quote Coverage

| | Category | Masters | Quotes | Coverage |
|:--:|----------|---------|:------:|:--------:|
| 🕯️ | **Arizal** | Rabbi Isaac Luria — Lurianic Kabbalah | 365 | Full Year |
| ✨ | **Baal Shem Tov** | Rabbi Israel ben Eliezer — Founder of Chassidut | 365 | Full Year |
| 🔥 | **Polish Chassidut** | Maggid, Kotzk, Peshischa, Piaseczno | 365 | Full Year |
| 📖 | **Baal HaSulam** | Rabbi Yehuda Ashlag — Sulam commentary | 365 | Full Year |
| 💎 | **Rabash** | Rabbi Baruch Shalom Ashlag — Practical application | 365 | Full Year |
| 🌱 | **Chasdei Ashlag** | Contemporary students | 186 | Partial |
| | | **Total** | **2,011** | |

---

## Deploy Your Own

### Option 1: GitHub Actions (Recommended)

Zero-infrastructure deployment using GitHub's free tier.

1. **Fork** this repository
2. **Add secrets** in Settings → Secrets → Actions:
   - `TELEGRAM_BOT_TOKEN` — from [@BotFather](https://t.me/BotFather)
   - `TELEGRAM_CHANNEL_ID` — your channel (e.g., `@YourChannel`)
3. **Enable** GitHub Actions

Daily quotes are sent automatically at 6:00 AM Israel time via dual-cron DST handling (3:00 AM + 4:00 AM UTC).

### Option 2: Docker

```bash
# Using docker-compose (recommended)
docker-compose up -d

# Or pull from GitHub Container Registry
docker pull ghcr.io/naorbrown/ashlag-yomi:latest
docker run -d --env-file .env ghcr.io/naorbrown/ashlag-yomi:latest
```

### Option 3: Local Development

```bash
# Clone the repository
git clone https://github.com/naorbrown/ashlag-yomi.git
cd ashlag-yomi

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -e .

# Configure environment
cp .env.example .env
# Edit .env with your bot token

# Run the bot
python -m src.bot.main
```

---

## Configuration

| Variable | Required | Default | Description |
|----------|:--------:|---------|-------------|
| `TELEGRAM_BOT_TOKEN` | ✅ | — | Bot token from [@BotFather](https://t.me/BotFather) |
| `TELEGRAM_CHANNEL_ID` | ✅ | — | Channel ID for daily broadcasts |
| `TELEGRAM_CHAT_ID` | ✅ | — | Chat ID for bot interactions |
| `ENVIRONMENT` | | `development` | `development` / `staging` / `production` |
| `DRY_RUN` | | `false` | Log messages instead of sending |
| `LOG_LEVEL` | | `INFO` | `DEBUG` / `INFO` / `WARNING` / `ERROR` |
| `SENTRY_DSN` | | — | Sentry DSN for error tracking |

---

## Architecture

```
┌──────────────────────────────────────────────────────────────────┐
│                        GitHub Actions                            │
│  ┌──────────────────────┐    ┌─────────────────────────────────┐│
│  │   daily-quote.yml    │    │           ci.yml                ││
│  │  ────────────────    │    │  ─────────────────────────────  ││
│  │  Dual Cron (DST):    │    │  • Lint (ruff)                  ││
│  │  • 3:00 AM UTC       │    │  • Format (black)               ││
│  │  • 4:00 AM UTC       │    │  • Type check (mypy)            ││
│  │  → 6:00 AM Israel    │    │  • Test (pytest, 80%+ coverage) ││
│  └──────────┬───────────┘    └─────────────────────────────────┘│
└─────────────┼────────────────────────────────────────────────────┘
              │
              ▼
┌──────────────────────────────────────────────────────────────────┐
│                         Bot Layer                                │
│  ┌─────────────┐  ┌──────────────┐  ┌────────────────────────┐  │
│  │   main.py   │  │ handlers.py  │  │   broadcaster.py       │  │
│  │ ─────────── │  │ ──────────── │  │ ────────────────────── │  │
│  │ • Entry     │  │ • /start     │  │ • Channel broadcasts   │  │
│  │ • Rate      │  │ • /today     │  │ • Idempotent sends     │  │
│  │   limiting  │  │ • /quote     │  │ • Retry logic          │  │
│  │   (5/min)   │  │ • /about     │  │                        │  │
│  │ • Command   │  │ • /help      │  └────────────────────────┘  │
│  │   register  │  │ • /feedback  │                              │
│  └─────────────┘  └──────┬───────┘                              │
│                          │                                       │
│                          ▼                                       │
│                   ┌──────────────┐                               │
│                   │formatters.py │                               │
│                   │ ──────────── │                               │
│                   │ • HTML format│                               │
│                   │ • Inline     │                               │
│                   │   keyboards  │                               │
│                   │ • Source     │                               │
│                   │   URL buttons│                               │
│                   └──────────────┘                               │
└──────────────────────────┬───────────────────────────────────────┘
                           │
                           ▼
┌──────────────────────────────────────────────────────────────────┐
│                        Data Layer                                │
│  ┌────────────────┐         ┌─────────────────────────────────┐ │
│  │  repository.py │         │          models.py              │ │
│  │ ────────────── │         │ ─────────────────────────────── │ │
│  │ • Fair rotation│ ◄─────► │ • Quote (Pydantic v2, frozen)   │ │
│  │ • Sent history │         │ • DailyBundle                   │ │
│  │ • Category     │         │ • SentRecord                    │ │
│  │   selection    │         │ • QuoteCategory (enum)          │ │
│  └───────┬────────┘         └─────────────────────────────────┘ │
│          │                                                       │
│          ▼                                                       │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │              data/quotes/*.json                            │ │
│  │              ──────────────────                            │ │
│  │              6 files • 2,011 quotes • Hebrew text          │ │
│  └────────────────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────────────┘
```

### Project Structure

```
ashlag-yomi/
├── src/
│   ├── bot/
│   │   ├── main.py           # Entry point, rate limiting, command registration
│   │   ├── handlers.py       # Command handlers (/start, /today, /quote, etc.)
│   │   ├── broadcaster.py    # Channel broadcasts with idempotency
│   │   └── formatters.py     # HTML formatting, inline keyboards
│   ├── data/
│   │   ├── models.py         # Pydantic models (Quote, DailyBundle, SentRecord)
│   │   └── repository.py     # Data access, fair rotation algorithm
│   ├── unified/
│   │   └── publisher.py      # Torah Yomi unified channel integration
│   └── utils/
│       ├── config.py         # Pydantic Settings, SecretStr handling
│       └── logger.py         # Structured logging
├── data/
│   └── quotes/               # 6 JSON files with 2,011 quotes
├── tests/                    # 116 tests, 80%+ coverage requirement
│   ├── unit/                 # Unit tests for all modules
│   └── conftest.py           # Pytest fixtures
├── .github/
│   ├── workflows/
│   │   ├── ci.yml            # Lint, test, type-check
│   │   ├── daily-quote.yml   # Daily broadcast (dual cron)
│   │   └── docker.yml        # Build and push to ghcr.io
│   └── ISSUE_TEMPLATE/       # Bug report, feature request
├── Dockerfile                # Non-root user, health checks
├── docker-compose.yml        # Local deployment
└── pyproject.toml            # Project metadata, dependencies
```

### Tech Stack

| Layer | Technology | Purpose |
|-------|------------|---------|
| **Runtime** | Python 3.11+ | Modern async/await, type hints |
| **Bot Framework** | python-telegram-bot v20+ | Async Telegram API |
| **Validation** | Pydantic v2 | Type-safe models, frozen immutability |
| **Security** | SecretStr | Token masking in logs |
| **Testing** | pytest + pytest-cov | 80%+ coverage requirement |
| **Linting** | ruff | Fast Python linting |
| **Formatting** | black | Consistent code style |
| **Type Checking** | mypy | Static type analysis |
| **CI/CD** | GitHub Actions | Automated testing and deployment |
| **Container** | Docker | ghcr.io registry, non-root user |

---

## Development

```bash
# Run all tests with coverage
pytest --cov=src --cov-report=term-missing

# Lint
ruff check src tests

# Format
black src tests

# Type check
mypy src

# Run all checks (lint, format, type, test)
make all
```

**Coverage Requirement:** 80% minimum (enforced in CI)

**Rate Limiting:** 5 requests per minute per user (sliding window algorithm)

**Fair Rotation:** Quotes are not repeated until all quotes in a category have been used

---

## Data Sources

| Source | Content | Link |
|--------|---------|------|
| **Sefaria** | Original Hebrew texts, Talmud, Midrash | [sefaria.org](https://www.sefaria.org/) |
| **Or HaSulam** | Ashlag writings, Sulam commentary | [orhassulam.com](https://www.orhassulam.com/) |

---

## Security

| Feature | Implementation |
|---------|----------------|
| 🔐 **Token Protection** | SecretStr masks tokens in logs |
| 👤 **Container Security** | Non-root Docker user |
| ⚡ **Abuse Prevention** | Rate limiting (5 req/min) |
| ✅ **No Secrets in Logs** | Pydantic SecretStr handling |

For vulnerability reporting, see [SECURITY.md](SECURITY.md).

---

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

**Ways to contribute:**

| Area | Description |
|------|-------------|
| 📖 **Quote Curation** | Add authentic quotes from primary sources |
| ✏️ **Hebrew Proofreading** | Review and correct Hebrew text |
| 💻 **Feature Development** | Implement new bot features |
| 📝 **Documentation** | Improve README, guides, translations |
| 🐛 **Bug Reports** | Report issues via GitHub |

---

## License

MIT License — see [LICENSE](LICENSE) for details.

Quote texts are sourced from works in the public domain or used with appropriate permissions.

---

## Acknowledgments

- [Sefaria](https://www.sefaria.org/) — Open-source Jewish texts
- [Or HaSulam](https://www.orhassulam.com/) — Ashlag writings and teachings
- [python-telegram-bot](https://python-telegram-bot.org/) — Excellent bot framework
- The Ashlag lineage teachers for preserving and transmitting this wisdom

---

<div align="center">

_״תכלית הבריאה היא להיטיב לנבראיו״_

_"The purpose of creation is to benefit the created beings."_

— **Baal HaSulam**

---

Built with ❤️ for spreading spiritual wisdom

</div>
