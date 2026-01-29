<div align="center">

# 🕯️ Ashlag Yomi

**Daily Kabbalistic wisdom. Six lineages. One message.**

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.11+](https://img.shields.io/badge/Python-3.11+-green.svg)](https://python.org)
[![Telegram Bot](https://img.shields.io/badge/Telegram-@AshlagYomiBot-blue.svg)](https://t.me/AshlagYomiBot)
[![CI](https://github.com/naorbrown/ashlag-yomi/actions/workflows/ci.yml/badge.svg)](https://github.com/naorbrown/ashlag-yomi/actions)

[**Start Learning**](https://t.me/AshlagYomiBot) · [**Report Bug**](https://github.com/naorbrown/ashlag-yomi/issues) · [**Request Feature**](https://github.com/naorbrown/ashlag-yomi/issues)

</div>

---

## What is Ashlag Yomi?

A Telegram bot delivering **6 daily quotes** from the Kabbalistic masters of the Ashlag lineage. New wisdom every morning at 6:00 AM Israel time.

- 📖 **2,011 quotes** across 6 spiritual lineages
- 🔗 **Clickable sources** linking to Sefaria and Or HaSulam
- ⚡ **Simple commands** — `/today` for all quotes, `/quote` for a quick read
- 🌍 **Free and open source** — run your own instance

---

## Commands

| Command | Description |
|---------|-------------|
| `/start` | Get today's wisdom |
| `/today` | Get today's 6 quotes |
| `/quote` | Get a random quote |
| `/about` | Learn about the lineage |
| `/help` | Show all commands |
| `/feedback` | Send feedback |

---

## Quote Coverage

| Category | Masters | Quotes |
|----------|---------|:------:|
| 🕯️ **Arizal** | Rabbi Isaac Luria — Lurianic Kabbalah | 365 |
| ✨ **Baal Shem Tov** | Rabbi Israel ben Eliezer — Founder of Chassidut | 365 |
| 🔥 **Polish Chassidut** | Maggid, Kotzk, Peshischa, Piaseczno | 365 |
| 📖 **Baal HaSulam** | Rabbi Yehuda Ashlag — Sulam commentary | 365 |
| 💎 **Rabash** | Rabbi Baruch Shalom Ashlag — Practical application | 365 |
| 🌱 **Chasdei Ashlag** | Contemporary students | 186 |

**Total: 2,011 quotes** — Full year coverage with unique daily content.

---

## Deploy Your Own

### Option 1: GitHub Actions (Recommended)

No server required. Runs on GitHub's free tier.

1. Fork this repository
2. Add repository secrets:
   - `TELEGRAM_BOT_TOKEN` — from [@BotFather](https://t.me/BotFather)
   - `TELEGRAM_CHANNEL_ID` — your channel (e.g., `@YourChannel`)
3. Enable GitHub Actions

Daily quotes will be sent automatically at 6:00 AM Israel time.

### Option 2: Run Locally

```bash
# Clone
git clone https://github.com/naorbrown/ashlag-yomi.git
cd ashlag-yomi

# Install
python -m venv venv
source venv/bin/activate
pip install -e .

# Configure
cp .env.example .env
# Edit .env with your bot token

# Run
python -m src.bot.main
```

---

## Configuration

| Variable | Required | Description |
|----------|:--------:|-------------|
| `TELEGRAM_BOT_TOKEN` | ✅ | Token from @BotFather |
| `TELEGRAM_CHANNEL_ID` | ✅ | Channel for broadcasts |
| `ENVIRONMENT` | | `development` or `production` |
| `DRY_RUN` | | Set `true` to log instead of send |

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     GitHub Actions                          │
│  ┌─────────────────┐        ┌─────────────────────────────┐│
│  │ daily-quote.yml │        │        ci.yml               ││
│  │ (6am Israel)    │        │ (lint, test, type-check)    ││
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

### Project Structure

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
│   └── unified/
│       └── publisher.py    # Torah Yomi channel integration
├── data/quotes/            # 6 JSON files, 365 quotes each
├── tests/                  # 116 tests, 80%+ coverage
└── .github/workflows/      # CI + daily broadcast
```

### Tech Stack

| Component | Technology |
|-----------|------------|
| Runtime | Python 3.11+ |
| Bot Framework | python-telegram-bot v20+ |
| Data Validation | Pydantic v2 |
| Testing | pytest + pytest-cov |
| CI/CD | GitHub Actions |

---

## Development

```bash
# Run tests with coverage
pytest

# Lint
ruff check src tests

# Format
black src tests

# Type check
mypy src

# All checks
make all
```

**Coverage requirement:** 80% minimum

---

## Data Sources

| Source | Purpose | Link |
|--------|---------|------|
| Sefaria | Original Hebrew texts | [sefaria.org](https://www.sefaria.org/) |
| Or HaSulam | Ashlag writings | [orhassulam.com](https://www.orhassulam.com/) |

---

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

**Ways to help:**
- 📖 Curate authentic quotes from primary sources
- ✏️ Hebrew proofreading
- 💻 Feature development
- 📝 Documentation

---

## Security

See [SECURITY.md](SECURITY.md) for vulnerability reporting.

---

## License

MIT License — see [LICENSE](LICENSE) for details.

Quote sources are in the public domain.

---

## Acknowledgments

- [Sefaria](https://www.sefaria.org/) — Open-source Jewish texts
- [Or HaSulam](https://www.orhassulam.com/) — Ashlag writings
- [python-telegram-bot](https://python-telegram-bot.org/) — Bot framework

---

<div align="center">

_״תכלית הבריאה היא להיטיב לנבראיו״_

_"The purpose of creation is to benefit the created beings."_ — Baal HaSulam

Built with ❤️ for spreading spiritual wisdom.

</div>
