# Ashlag Yomi

Daily inspirational quotes from Jewish spiritual leaders, delivered to Telegram at 6:00 AM Israel time.

[![Daily Quotes](https://github.com/naorbrown/ashlag-yomi/actions/workflows/daily_quotes.yml/badge.svg)](https://github.com/naorbrown/ashlag-yomi/actions/workflows/daily_quotes.yml)
[![CI](https://github.com/naorbrown/ashlag-yomi/actions/workflows/ci.yml/badge.svg)](https://github.com/naorbrown/ashlag-yomi/actions/workflows/ci.yml)

## Sources

| Hebrew | English | Era |
|--------|---------|-----|
| האר״י הקדוש | The Arizal | 16th century |
| הבעל שם טוב | Baal Shem Tov | 1698-1760 |
| רבי שמחה בונים מפשיסחא | Simcha Bunim of Peshischa | 1765-1827 |
| הרבי מקוצק | The Kotzker Rebbe | 1787-1859 |
| בעל הסולם | Baal HaSulam | 1885-1954 |
| הרב״ש | Rabash | 1907-1991 |
| תלמידי קו אשלג | Ashlag Lineage | Various |

All quotes include links to primary sources:
- [Sefaria](https://www.sefaria.org/)
- [Kabbalah.info](https://www.kabbalah.info/)
- [Chabad.org](https://www.chabad.org/)

## How It Works

GitHub Actions runs daily at 6:00 AM Israel time and sends a curated selection of quotes to a Telegram chat. Each day features one quote from each of the seven sources.

**Features:**
- Deterministic selection (same quotes for everyone each day)
- Hebrew RTL text formatting
- Source attribution with links
- Zero hosting costs

## Setup

### 1. Create a Telegram Bot

1. Message [@BotFather](https://t.me/botfather) on Telegram
2. Send `/newbot` and follow the prompts
3. Save the bot token

### 2. Get Your Chat ID

1. Start a chat with your new bot
2. Send any message
3. Visit `https://api.telegram.org/bot<TOKEN>/getUpdates`
4. Find `chat.id` in the response

### 3. Configure GitHub

1. Fork this repository
2. Go to Settings > Secrets and variables > Actions
3. Add two secrets:
   - `TELEGRAM_BOT_TOKEN` - Your bot token
   - `TELEGRAM_CHAT_ID` - Your chat ID

The bot will automatically send quotes at 6:00 AM Israel time.

### Manual Trigger

You can manually trigger the workflow:
1. Go to Actions > Daily Quotes
2. Click "Run workflow"
3. Optionally enable "Preview only" to see quotes without sending

## Project Structure

```
ashlag-yomi/
├── .github/workflows/
│   ├── ci.yml              # Code quality checks
│   └── daily_quotes.yml    # Scheduled sending
├── data/quotes/            # Quote JSON files
├── src/
│   ├── quote_manager.py    # Quote selection logic
│   └── telegram_bot.py     # Message sending
├── send_daily.py           # Entry point
└── requirements.txt
```

## Quote Format

Each quote includes:
- Hebrew text
- Source book/document
- Link to original source

Example message:
```
אשלג יומי
28/01/2026

השראה יומית מגדולי ישראל

---

✨ הבעל שם טוב

«שכחה היא גלות, וזיכרון הוא גאולה.»

📖 כתר שם טוב
🔗 מקור

---

יום מבורך
```

## Adding Quotes

Edit files in `data/quotes/`:

```json
{
  "id": "unique_id",
  "text": "Hebrew quote text",
  "source": "Source book name",
  "source_url": "https://link.to/source"
}
```

## License

MIT
