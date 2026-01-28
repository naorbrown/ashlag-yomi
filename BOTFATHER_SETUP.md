# BotFather Setup Guide for AshlagYomiBot

This document contains all the text needed to configure your bot via [@BotFather](https://t.me/botfather).

## Bot Name
```
AshlagYomiBot
```

## Bot Username
```
@AshlagYomiBot
```

## Bot Description (shown in bot info)
```
📖 Daily Kabbalah wisdom from Baal HaSulam, Rabash, and the Ashlag lineage.

Receive inspirational quotes every morning at 6:00 AM Israel time from the greatest Kabbalistic masters:
• האר״י הקדוש (The Arizal)
• הבעל שם טוב (Baal Shem Tov)
• רבי שמחה בונים (Simcha Bunim)
• הרבי מקוצק (Kotzker Rebbe)
• בעל הסולם (Baal HaSulam)
• הרב״ש (Rabash)
• תלמידי קו אשלג (Ashlag Students)

All quotes include links to authentic sources.
Free • No ads • Open source
```

## Bot About (shown when user clicks bot name)
```
אשלג יומי - Daily Kabbalah Wisdom

A Telegram bot delivering daily inspirational quotes from the masters of Kabbalah and Chassidut, following the Ashlag lineage.

📚 126 curated quotes from 7 sources
🔗 Every quote links to its original source
⏰ Automatic delivery at 6:00 AM Israel time
🆓 Completely free, no ads

Commands:
/today - Today's quotes
/quote - Random quote
/about - About this bot

GitHub: github.com/naorbrown/ashlag-yomi

לתיקון עולם 💫
```

## Bot Commands (set via /setcommands)
```
today - הציטוטים של היום
quote - ציטוט אקראי
stats - סטטיסטיקות
about - אודות הבוט
quality - איך נבחרים הציטוטים
help - עזרה
```

## Bot Profile Picture
Use the logo from `assets/logo.svg` (convert to PNG first):
- Dark blue circular background (#1a237e to #0d1333)
- Golden ladder (סולם) symbol - representing "The Sulam" commentary
- Hebrew text "אשלג יומי" in gold
- Light rays emanating from above
- Matches the brand style of DafHistoryBot, NachYomiBot, DailyLikuteiHalachotBot

## Inline Mode Placeholder (optional)
```
Search quotes by topic...
```

## Setup Steps

1. Open [@BotFather](https://t.me/botfather) on Telegram

2. Create or select your bot:
   - New bot: `/newbot` → follow prompts
   - Existing: `/mybots` → select bot

3. Set description: `/setdescription`
   - Paste the "Bot Description" text above

4. Set about: `/setabouttext`
   - Paste the "Bot About" text above

5. Set commands: `/setcommands`
   - Paste the "Bot Commands" text above

6. Set profile picture: `/setuserpic`
   - Upload the converted PNG logo

7. Get your token: `/token`
   - Save this as `TELEGRAM_BOT_TOKEN` in GitHub Secrets

## Recommended Privacy Settings

Via `/mybots` → Bot Settings:
- **Group Privacy**: Enabled (bot only sees commands)
- **Allow Groups**: Yes (users can add to groups)
- **Inline Mode**: Disabled (not implemented)

---

*Part of the Daily Torah Bots family:*
- [@DafHistoryBot](https://t.me/DafHistoryBot) - Daf Yomi History
- [@NachYomiBot](https://t.me/NachYomiBot) - Nach Yomi
- [@DailyLikuteiHalachotBot](https://t.me/DailyLikuteiHalachotBot) - Likutei Halachot
- [@AshlagYomiBot](https://t.me/AshlagYomiBot) - Ashlag Yomi
