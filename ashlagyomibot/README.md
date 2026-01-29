# 🕯️ Ashlag Yomi

**Daily Kabbalistic wisdom from the Ashlag lineage**

[![CI](https://github.com/naorbrown/ashlag-yomi/actions/workflows/ci.yml/badge.svg)](https://github.com/naorbrown/ashlag-yomi/actions/workflows/ci.yml)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Telegram Bot](https://img.shields.io/badge/Telegram-@AshlagYomiBot-blue.svg)](https://t.me/AshlagYomiBot)

A Telegram bot delivering daily quotes from the Kabbalistic masters of the Ashlag lineage. New quotes every morning at 6:00 AM Israel time.

**[→ Start the bot on Telegram](https://t.me/AshlagYomiBot)**

## ✨ Features

- **6 daily quotes** — One from each category of the spiritual lineage
- **2,000+ quotes** — Full year of unique daily content
- **Clickable sources** — Direct links to original texts on Sefaria and Or HaSulam
- **Simple commands** — `/today` for all quotes, `/quote` for a quick read
- **No account needed** — Just open Telegram and start

## 📜 The Lineage

| Emoji | Category | Masters |
|:-----:|----------|---------|
| 🕯️ | **Arizal** | Rabbi Isaac Luria — Foundation of Lurianic Kabbalah |
| ✨ | **Baal Shem Tov** | Rabbi Israel ben Eliezer — Founder of Chassidut |
| 🔥 | **Polish Chassidut** | Maggid of Mezeritch, Kotzk, Peshischa, Piaseczno |
| 📖 | **Baal HaSulam** | Rabbi Yehuda Ashlag — Modern Kabbalah systematizer |
| 💎 | **Rabash** | Rabbi Baruch Shalom Ashlag — Practical application |
| 🌱 | **Chasdei Ashlag** | Contemporary students of the lineage |

## 🤖 Bot Commands

| Command | Description |
|---------|-------------|
| `/start` | Welcome message and quick start |
| `/today` | Get today's 6 quotes |
| `/quote` | Get a single random quote |
| `/about` | Learn about the lineage |
| `/help` | Show all commands |
| `/feedback` | Send feedback or report issues |

## 🚀 Quick Start (Developers)

### Prerequisites

- Python 3.11+
- Telegram bot token from [@BotFather](https://t.me/BotFather)

### Setup

```bash
# Clone
git clone https://github.com/naorbrown/ashlag-yomi.git
cd ashlag-yomi

# Install
python -m venv venv
source venv/bin/activate
pip install -e ".[dev]"

# Configure
cp .env.example .env
# Edit .env with your bot token

# Run
python -m src.bot.main
```

### Development

```bash
make test        # Run tests (80% coverage required)
make lint        # Lint with ruff
make format      # Format with black
make all         # All of the above
```

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     GitHub Actions                          │
│  ┌─────────────────┐        ┌─────────────────────────────┐│
│  │ daily-quote.yml │        │        ci.yml               ││
│  │ (3am + 4am UTC) │        │ (lint, test, type-check)    ││
│  └────────┬────────┘        └─────────────────────────────┘│
└───────────┼────────────────────────────────────────────────┘
            │
            ▼
┌─────────────────────────────────────────────────────────────┐
│                      Bot Layer                              │
│   main.py ──── handlers.py ──── broadcaster.py              │
│                     │                                       │
│                     ▼                                       │
│              formatters.py (inline keyboards)               │
└─────────────────────────────────────────────────────────────┘
            │
            ▼
┌─────────────────────────────────────────────────────────────┐
│                     Data Layer                              │
│   repository.py ──── models.py                              │
│         │                                                   │
│         ▼                                                   │
│   data/quotes/*.json (2,011 quotes)                         │
└─────────────────────────────────────────────────────────────┘
```

## 📁 Project Structure

```
ashlag-yomi/
├── src/
│   ├── bot/
│   │   ├── main.py         # Entry point, command registration
│   │   ├── handlers.py     # /start, /today, /quote, etc.
│   │   ├── broadcaster.py  # Channel broadcasts
│   │   └── formatters.py   # HTML formatting, inline keyboards
│   ├── data/
│   │   ├── models.py       # Quote, DailyBundle (Pydantic)
│   │   └── repository.py   # Data access, fair rotation
│   └── utils/
│       ├── config.py       # Settings from environment
│       └── logger.py       # Structured logging
├── data/quotes/            # 6 JSON files, 365 quotes each
├── tests/                  # 116 tests, 80%+ coverage
└── .github/workflows/      # CI + daily broadcast
```

## 🔧 Configuration

| Variable | Required | Description |
|----------|:--------:|-------------|
| `TELEGRAM_BOT_TOKEN` | ✅ | Token from @BotFather |
| `TELEGRAM_CHANNEL_ID` | ✅ | Channel for broadcasts (e.g., `@AshlagYomi`) |
| `ENVIRONMENT` | | `development`, `staging`, `production` |
| `DRY_RUN` | | Set `true` to log instead of send |

## 🚢 Deployment

The bot runs serverless via GitHub Actions — no hosting required.

1. Fork this repository
2. Add secrets: `TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHANNEL_ID`
3. Enable GitHub Actions

**Daily Broadcast Timing:**

The bot sends at **6:00 AM Israel time** year-round using dual-cron (3am + 4am UTC) to handle daylight saving. The broadcaster is idempotent — duplicate triggers are safely ignored.

## 🤝 Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

**Ways to help:**
- Curate authentic quotes from primary sources
- Hebrew proofreading
- Feature development
- Documentation

## 📄 License

MIT License — see [LICENSE](LICENSE) for details.

Quote sources are in the public domain. See LICENSE for attribution.

## 🙏 Acknowledgments

- [Sefaria](https://www.sefaria.org/) — Open-source Jewish texts
- [Or HaSulam](https://www.orhassulam.com/) — Ashlag writings
- [python-telegram-bot](https://python-telegram-bot.org/) — Bot framework

---

_״אין אור גדול יותר מהאור היוצא מתוך החושך״_
— Baal HaSulam

Built with ❤️ for spreading spiritual wisdom.
