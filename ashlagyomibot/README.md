# 🕯️ Ashlag Yomi

**Daily spiritual nourishment from the Ashlag Kabbalistic lineage**

[![CI](https://github.com/yourusername/ashlag-yomi/actions/workflows/ci.yml/badge.svg)](https://github.com/yourusername/ashlag-yomi/actions/workflows/ci.yml)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Telegram Bot](https://img.shields.io/badge/Telegram-Bot-blue.svg)](https://t.me/AshlagYomiBot)

A Telegram bot that delivers daily quotes from the Ashlag spiritual lineage every morning at 6:00 AM Israel time.

## 🌟 The Lineage

The bot shares wisdom from six categories of Kabbalistic masters:

| Category | Emoji | Description |
|----------|-------|-------------|
| 🕯️ **האר״י הקדוש** | ARIZAL | Foundation of Lurianic Kabbalah |
| ✨ **הבעל שם טוב** | BAAL_SHEM_TOV | Founder of Chassidut and his students |
| 🔥 **חסידות פולין** | POLISH_CHASSIDUT | Maggid, Peshischa, Kotzk and more |
| 📖 **בעל הסולם** | BAAL_HASULAM | Modern Kabbalah systematizer |
| 💎 **הרב״ש** | RABASH | Practical application |
| 🌱 **חסידי אשלג** | CHASDEI_ASHLAG | Contemporary students |

## 🚀 Quick Start

### Prerequisites

- Python 3.11 or higher
- A Telegram bot token (get one from [@BotFather](https://t.me/BotFather))
- A Telegram channel or group ID

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/ashlag-yomi.git
cd ashlag-yomi

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
make install-dev

# Copy environment template and fill in your values
cp .env.example .env
# Edit .env with your bot token and channel ID
```

### Running Locally

```bash
# Populate sample quotes
python scripts/populate_quotes.py

# Test the bot connection
python scripts/test_bot.py

# Run the bot in interactive mode
make run
```

### Available Commands

Once the bot is running, you can use these commands in Telegram:

- `/start` - Welcome message and introduction
- `/today` - Get today's quotes immediately
- `/about` - Learn about the project and lineage
- `/help` - Show available commands
- `/feedback` - How to send feedback

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
│      │              │                 │                     │
│      └──────────────┼─────────────────┘                     │
│                     ▼                                       │
│              formatters.py                                  │
└─────────────────────────────────────────────────────────────┘
            │
            ▼
┌─────────────────────────────────────────────────────────────┐
│                     Data Layer                              │
│   repository.py ──── models.py                              │
│         │                                                   │
│         ▼                                                   │
│   data/quotes/*.json (2000+ quotes)                         │
└─────────────────────────────────────────────────────────────┘
```

## 📁 Project Structure

```
ashlag-yomi/
├── src/
│   ├── bot/
│   │   ├── main.py         # Bot entry point
│   │   ├── handlers.py     # Command handlers (/start, /today, etc.)
│   │   ├── broadcaster.py  # Channel broadcasts
│   │   ├── scheduler.py    # Local scheduling (dev only)
│   │   └── formatters.py   # Message formatting (HTML)
│   ├── data/
│   │   ├── models.py       # Pydantic models
│   │   └── repository.py   # Data access layer
│   └── utils/
│       ├── config.py       # Settings (Pydantic Settings)
│       └── logger.py       # Structured logging
├── data/quotes/            # Quote JSON files (365 per category)
├── scripts/                # CLI scripts
├── tests/
│   ├── unit/              # Unit tests
│   └── fixtures/          # Test fixtures
└── .github/workflows/      # CI/CD pipelines
```

## 🧪 Development

```bash
# Run all quality checks
make all

# Individual commands
make test        # Run tests with coverage
make lint        # Run linter (ruff)
make format      # Format code (black + ruff)
make type-check  # Type checking (mypy)

# Send a test message
make test-bot
```

## 🔧 Configuration

All configuration is done through environment variables. See `.env.example` for the full list.

| Variable | Required | Description |
|----------|----------|-------------|
| `TELEGRAM_BOT_TOKEN` | Yes | Bot token from @BotFather |
| `TELEGRAM_CHAT_ID` | Yes | Target channel/group ID |
| `ENVIRONMENT` | No | `development`, `staging`, or `production` |
| `LOG_LEVEL` | No | Logging level (default: `INFO`) |
| `DRY_RUN` | No | Log instead of sending (default: `false`) |

## 📚 Adding Quotes

Quotes are stored in JSON files under `data/quotes/`. Each category has its own file:

```json
{
  "category": "baal_hasulam",
  "quotes": [
    {
      "id": "baal-hasulam-001",
      "text": "הסתכלות בתכלית מביאה את האדם לשלמות",
      "source_rabbi": "בעל הסולם",
      "source_book": "מאמרי הסולם",
      "source_url": "https://www.orhassulam.com/",
      "category": "baal_hasulam",
      "tags": ["תכלית", "שלמות"],
      "length_estimate": 15
    }
  ]
}
```

See `docs/QUOTES_FORMAT.md` for the complete schema.

## 🚢 Deployment

The bot runs via GitHub Actions cron job - no server required!

1. Fork this repository
2. Add secrets in repository settings:
   - `TELEGRAM_BOT_TOKEN` - from [@BotFather](https://t.me/BotFather)
   - `TELEGRAM_CHAT_ID` - your chat ID for testing
   - `TELEGRAM_CHANNEL_ID` - channel for daily broadcasts (e.g., `@AshlagYomi`)
3. Enable GitHub Actions

### Daily Broadcast Timing

The bot broadcasts at **6:00 AM Israel time** year-round. Due to Israel's daylight saving time changes, we use a dual-cron schedule:

| Season | Israel TZ | UTC Cron | Result |
|--------|-----------|----------|--------|
| Summer (IDT) | UTC+3 | `0 3 * * *` | 6:00 AM Israel |
| Winter (IST) | UTC+2 | `0 4 * * *` | 6:00 AM Israel |

The broadcaster is **idempotent** - if the same day's quote is already sent, duplicate cron triggers are safely ignored.

## 🤝 Contributing

Contributions are welcome! Please see `CONTRIBUTING.md` for guidelines.

Areas where help is needed:
- Curating authentic quotes from primary sources
- Hebrew proofreading and nikud
- Improving message formatting
- Adding new features

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [Sefaria](https://www.sefaria.org/) - Jewish texts API
- [Or HaSulam](https://www.orhassulam.com/) - Ashlag writings
- [python-telegram-bot](https://python-telegram-bot.org/) - Bot framework

---

_״אין אור גדול יותר מהאור היוצא מתוך החושך״_ - בעל הסולם

Built with ❤️ for the spreading of spiritual wisdom.
