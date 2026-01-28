# Ashlag Yomi - אשלג יומי

[![CI](https://github.com/naorbrown/ashlag-yomi/actions/workflows/ci.yml/badge.svg)](https://github.com/naorbrown/ashlag-yomi/actions/workflows/ci.yml)
[![Daily Quotes](https://github.com/naorbrown/ashlag-yomi/actions/workflows/daily_quotes.yml/badge.svg)](https://github.com/naorbrown/ashlag-yomi/actions/workflows/daily_quotes.yml)

A Telegram bot that sends daily inspirational quotes from great Jewish spiritual leaders at 6:00 AM Israel time.

## Sources / מקורות

The bot delivers daily wisdom from these luminaries:

| Hebrew | English | Era |
|--------|---------|-----|
| האר״י הקדוש | The Arizal (Rabbi Isaac Luria) | 16th century |
| הבעל שם טוב | The Baal Shem Tov | 1698-1760 |
| רבי שמחה בונים מפשיסחא | Rabbi Simcha Bunim of Peshischa | 1765-1827 |
| הרבי מקוצק | The Kotzker Rebbe | 1787-1859 |
| בעל הסולם | Baal HaSulam (Rabbi Yehuda Ashlag) | 1885-1954 |
| הרב״ש | Rabash (Rabbi Baruch Shalom Ashlag) | 1907-1991 |
| תלמידי קו אשלג | Students of the Ashlag Lineage | Various |

All quotes are in Hebrew with links to their original sources including:
- [Sefaria](https://www.sefaria.org/)
- [Kabbalah.info](https://www.kabbalah.info/)
- [Chabad.org](https://www.chabad.org/)

## Features

- **Daily Automated Messages**: Quotes sent at 6:00 AM Israel time
- **Interactive Commands**: Get quotes on demand
- **Hebrew RTL Support**: Proper right-to-left text formatting
- **Source Links**: Every quote links to its original source
- **Free Hosting**: Runs entirely on GitHub Actions

## Bot Commands

| Command | Description |
|---------|-------------|
| `/start` | Welcome message and bot info |
| `/quote` | Get a random quote |
| `/daily` | Get today's collection of quotes |
| `/stats` | View quote statistics |
| `/help` | Help and usage information |

## Setup

### Prerequisites

- Python 3.11+
- A Telegram Bot Token (from [@BotFather](https://t.me/botfather))

### Local Development

1. Clone the repository:
   ```bash
   git clone https://github.com/naorbrown/ashlag-yomi.git
   cd ashlag-yomi
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Set up environment variables:
   ```bash
   cp .env.example .env
   # Edit .env with your bot token and chat ID
   ```

5. Run the bot:
   ```bash
   python -m src.main --mode polling
   ```

### GitHub Actions Deployment

1. Fork this repository

2. Add secrets in your repository settings:
   - `TELEGRAM_BOT_TOKEN`: Your bot token from BotFather
   - `TELEGRAM_CHAT_ID`: The chat/channel ID to send messages to

3. Enable GitHub Actions - the bot will automatically:
   - Send daily quotes at 6:00 AM Israel time
   - Run CI tests on every push

### Getting Your Chat ID

1. Start a chat with your bot
2. Send any message
3. Visit: `https://api.telegram.org/bot<YOUR_TOKEN>/getUpdates`
4. Find the `chat.id` field in the response

For channels, use the channel's @username or numeric ID.

## Project Structure

```
ashlag-yomi/
├── .github/
│   └── workflows/
│       ├── ci.yml           # Continuous integration
│       └── daily_quotes.yml # Scheduled quote sending
├── data/
│   └── quotes/
│       ├── arizal.json
│       ├── baal_shem_tov.json
│       ├── simcha_bunim.json
│       ├── kotzker.json
│       ├── baal_hasulam.json
│       ├── rabash.json
│       └── ashlag_talmidim.json
├── src/
│   ├── __init__.py
│   ├── main.py              # Entry point
│   ├── quote_manager.py     # Quote handling logic
│   └── telegram_bot.py      # Telegram bot implementation
├── tests/
│   └── test_quote_manager.py
├── requirements.txt
├── send_daily.py            # Script for GitHub Actions
└── README.md
```

## Quote Format

Each quote includes:
- **Text**: The quote in Hebrew
- **Source**: Book or document name
- **Source URL**: Link to the original source
- **Topic**: Thematic category

Example message:
```
✨ *הבעל שם טוב*

«שכחה היא גלות, וזיכרון הוא גאולה.»

📖 _כתר שם טוב_
🔗 [מקור](https://www.sefaria.org/Keter_Shem_Tov)
```

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Add or improve quotes (ensure authentic sources)
4. Submit a pull request

### Adding Quotes

To add new quotes, edit the relevant JSON file in `data/quotes/`:

```json
{
  "id": "unique_id",
  "text": "Hebrew quote text",
  "source": "Book or document name",
  "source_url": "https://link.to/source",
  "topic": "Theme",
  "length": "short|medium|long"
}
```

## Testing

Run the test suite:
```bash
pytest tests/ -v
```

With coverage:
```bash
pytest tests/ -v --cov=src --cov-report=term-missing
```

## Security

- Never commit tokens or secrets
- Use GitHub Secrets for sensitive data
- The `.gitignore` excludes common secret files
- CI includes security scanning

## License

MIT License - See [LICENSE](LICENSE) for details.

## Acknowledgments

- Quote sources: Sefaria, Kabbalah.info, Chabad.org
- Built with [python-telegram-bot](https://python-telegram-bot.org/)
- Hosted on GitHub Actions

---

*לתיקון עולם* 💫