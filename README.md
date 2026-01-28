# Ashlag Yomi 🕎

[![CI](https://github.com/naorbrown/ashlag-yomi/actions/workflows/ci.yml/badge.svg)](https://github.com/naorbrown/ashlag-yomi/actions/workflows/ci.yml)
[![Daily Quotes](https://github.com/naorbrown/ashlag-yomi/actions/workflows/daily-quotes.yml/badge.svg)](https://github.com/naorbrown/ashlag-yomi/actions/workflows/daily-quotes.yml)

A Telegram bot that delivers daily inspirational quotes from the Ashlag Kabbalah lineage and related masters. Every day at 6:00 AM Israel time, subscribers receive wisdom from:

- **האר"י הקדוש** (The Arizal)
- **הבעל שם טוב** (Baal Shem Tov)
- **רבי שמחה בונים מפשיסחא** (Simcha Bunim of Peshischa)
- **רבי מנחם מנדל מקוצק** (The Kotzker Rebbe)
- **בעל הסולם** (Baal Hasulam - Rabbi Yehuda Ashlag)
- **הרב"ש** (RABASH - Rabbi Baruch Shalom Ashlag)
- **תלמידי קו אשלג** (Students of the Ashlag Lineage)

## Features

- 📅 Daily automated quotes at 6:00 AM Israel time
- 🔗 Each quote linked to its original source
- 🌐 Bilingual interface (Hebrew/English)
- 📱 Full Telegram command support
- ☁️ Runs entirely on GitHub Actions (free)
- 🔒 Secure secrets management
- ✅ Comprehensive test coverage

## Quick Start

### For Users

1. Open Telegram and search for your bot (once deployed)
2. Send `/start` to subscribe
3. Receive daily wisdom automatically!

### For Developers

```bash
# Clone the repository
git clone https://github.com/naorbrown/ashlag-yomi.git
cd ashlag-yomi

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your Telegram bot token

# Run locally for testing
python src/bot.py

# Run tests
pytest tests/ -v
```

## Telegram Commands

| Command | Description |
|---------|-------------|
| `/start` | Subscribe to daily quotes |
| `/stop` | Unsubscribe from daily quotes |
| `/today` | Get all today's quotes now |
| `/quote` | Get a random quote |
| `/help` | Show available commands |
| `/about` | Information about the bot |
| `/test` | (Admin) Run system diagnostics |

## Project Structure

```
ashlag-yomi/
├── .github/
│   └── workflows/
│       ├── ci.yml              # CI/CD pipeline
│       └── daily-quotes.yml    # Scheduled broadcasts
├── data/
│   ├── quotes/
│   │   ├── metadata.json       # Rabbi information
│   │   ├── arizal.json
│   │   ├── baal_shem_tov.json
│   │   ├── simcha_bunim.json
│   │   ├── kotzker_rebbe.json
│   │   ├── baal_hasulam.json
│   │   ├── rabash.json
│   │   └── ashlag_talmidim.json
│   └── subscriptions.json      # Subscriber list
├── src/
│   └── bot.py                  # Main bot code
├── tests/
│   ├── conftest.py
│   ├── test_bot.py
│   └── test_quotes.py
├── .env.example
├── .gitignore
├── requirements.txt
└── README.md
```

## Deployment

### Setting Up GitHub Secrets

1. Go to your repository Settings → Secrets and variables → Actions
2. Add the following secrets:
   - `TELEGRAM_BOT_TOKEN`: Your bot token from @BotFather
   - `ADMIN_CHAT_IDS`: (Optional) Comma-separated admin chat IDs

### Creating a Telegram Bot

1. Open Telegram and search for @BotFather
2. Send `/newbot` and follow the prompts
3. Copy the bot token provided
4. Add the token to GitHub Secrets

### Scheduling

The bot automatically runs via GitHub Actions:
- **Daily at 4:00 AM UTC** (6:00 AM Israel Standard Time)
- Can be manually triggered via Actions → Daily Quotes Broadcast → Run workflow

## Testing

### Run All Tests

```bash
pytest tests/ -v
```

### Run with Coverage

```bash
pytest tests/ -v --cov=src --cov-report=html
```

### Test the Bot Locally

```bash
# Set environment variable
export TELEGRAM_BOT_TOKEN="your_token_here"

# Run in polling mode
python src/bot.py

# In Telegram, send /test to your bot
```

### Manual Broadcast Test

```bash
# Trigger a broadcast (requires subscribed users)
python src/bot.py --broadcast
```

## Quote Sources

All quotes are sourced from authentic Kabbalistic texts:

- [אור הסולם (Or HaSulam)](https://www.orhasulam.org/)
- [אשלג ברוך (Ashlag Baroch)](https://ashlagbaroch.com/)
- [קבלה אינפו (Kabbalah Info)](https://www.kabbalahinfo.org/)
- [ספריא (Sefaria)](https://www.sefaria.org/)

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Adding New Quotes

1. Edit the appropriate JSON file in `data/quotes/`
2. Follow the existing format:
   ```json
   {
     "text": "Quote text in Hebrew",
     "source": "Source name",
     "source_url": "https://...",
     "topic": "Topic category"
   }
   ```
3. Run tests to validate: `pytest tests/test_quotes.py -v`

## Security

- Bot token stored in GitHub Secrets
- No sensitive data in repository
- Automated security scanning in CI
- Input validation on all user commands

## License

MIT License - see [LICENSE](LICENSE) for details.

## Acknowledgments

- The teachings of Baal HaSulam and RABASH
- The Ashlag lineage and all their students
- The open-source community

---

🙏 **לזכות כל ישראל** - For the merit of all Israel

📬 Questions? Open an issue or contribute to the project!
