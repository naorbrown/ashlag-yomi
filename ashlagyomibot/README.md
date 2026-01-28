# 🕯️ Ashlag Yomi

**Daily spiritual nourishment from the Ashlag Kabbalistic lineage**

[![CI](https://github.com/yourusername/ashlag-yomi/actions/workflows/ci.yml/badge.svg)](https://github.com/yourusername/ashlag-yomi/actions/workflows/ci.yml)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A Telegram bot that delivers daily quotes from the Ashlag spiritual lineage every morning at 6:00 AM Israel time.

## 🌟 The Lineage

The bot shares wisdom from seven generations of Kabbalistic masters:

| Rabbi | Years | Contribution |
|-------|-------|--------------|
| 🕯️ **האר״י הקדוש** | 1534-1572 | Foundation of Lurianic Kabbalah |
| ✨ **הבעל שם טוב** | 1698-1760 | Founder of Chassidut |
| 🌟 **רבי שמחה בונים** | 1765-1827 | Peshischa school |
| 🔥 **הרבי מקוצק** | 1787-1859 | Uncompromising truth |
| 📖 **בעל הסולם** | 1884-1954 | Modern Kabbalah systematizer |
| 💎 **הרב״ש** | 1907-1991 | Practical application |
| 🌱 **התלמידים** | Present | Contemporary students |

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

## 📁 Project Structure

```
ashlag-yomi/
├── src/
│   ├── bot/           # Telegram bot logic
│   ├── data/          # Models, repository, data sources
│   └── utils/         # Configuration, logging
├── data/quotes/       # Quote JSON files
├── scripts/           # CLI scripts
├── tests/             # Test suite
└── .github/workflows/ # CI/CD pipelines
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
   - `TELEGRAM_BOT_TOKEN`
   - `TELEGRAM_CHAT_ID`
3. Enable GitHub Actions

The daily quote workflow runs at 3:00 AM UTC (6:00 AM Israel time).

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
