"""
Vercel Serverless Function for Telegram Webhook
"""

import os
import json
import logging
from datetime import date
from http.server import BaseHTTPRequestHandler
import urllib.request
import urllib.parse

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Inline quote data to avoid import issues in serverless
QUOTES_DATA = {
    "arizal": {
        "source_name": "האר״י הקדוש",
        "quotes": [
            {"text": "דע, כי טרם שנאצלו הנאצלים ונבראו הנבראים, היה אור עליון פשוט ממלא כל המציאות.", "source": "עץ חיים, שער א׳", "source_url": "https://www.sefaria.org/Etz_Chaim"},
            {"text": "אין לך עשב למטה שאין לו מזל למעלה שמכה בו ואומר לו גדל.", "source": "שער המצוות", "source_url": "https://www.sefaria.org/Shaar_HaMitzvot"},
            {"text": "התפילה היא בחינת סולם מוצב ארצה וראשו מגיע השמימה.", "source": "שער הכוונות", "source_url": "https://www.sefaria.org/Shaar_HaKavanot"},
            {"text": "העיקר הוא הכוונה, כי המעשה בלי כוונה הוא כגוף בלי נשמה.", "source": "שער הכוונות", "source_url": "https://www.sefaria.org/Shaar_HaKavanot"},
            {"text": "אהבת ישראל היא השער הגדול לכניסה לקדושה.", "source": "שער רוח הקודש", "source_url": "https://www.sefaria.org/Shaar_Ruach_HaKodesh"},
        ]
    },
    "baal_shem_tov": {
        "source_name": "הבעל שם טוב",
        "quotes": [
            {"text": "במקום שמחשבתו של אדם, שם הוא נמצא כולו.", "source": "כתר שם טוב", "source_url": "https://www.sefaria.org/Keter_Shem_Tov"},
            {"text": "שכחה היא גלות, וזיכרון הוא גאולה.", "source": "כתר שם טוב", "source_url": "https://www.sefaria.org/Keter_Shem_Tov"},
            {"text": "השמחה היא המפתח לכל השערים.", "source": "צוואת הריב״ש", "source_url": "https://www.sefaria.org/Tzavaat_HaRivash"},
            {"text": "כל ירידה היא לצורך עלייה.", "source": "כתר שם טוב", "source_url": "https://www.sefaria.org/Keter_Shem_Tov"},
            {"text": "אהבת ישראל היא אהבת הקב״ה.", "source": "כתר שם טוב", "source_url": "https://www.sefaria.org/Keter_Shem_Tov"},
        ]
    },
    "simcha_bunim": {
        "source_name": "רבי שמחה בונים מפשיסחא",
        "quotes": [
            {"text": "כל אדם צריך שיהיו לו שני כיסים: בכיס אחד פתק שכתוב בו 'בשבילי נברא העולם', ובכיס השני פתק שכתוב בו 'אנכי עפר ואפר'.", "source": "שיח שרפי קודש", "source_url": "https://www.sefaria.org/"},
            {"text": "הגאווה היא שורש כל הרע.", "source": "קול שמחה", "source_url": "https://www.sefaria.org/"},
            {"text": "האמת היא היסוד של הכל.", "source": "קול שמחה", "source_url": "https://www.sefaria.org/"},
            {"text": "עבודת ה׳ צריכה להיות בשמחה.", "source": "קול שמחה", "source_url": "https://www.sefaria.org/"},
            {"text": "התפילה היא עבודת הלב.", "source": "קול שמחה", "source_url": "https://www.sefaria.org/"},
        ]
    },
    "kotzker": {
        "source_name": "הרבי מקוצק",
        "quotes": [
            {"text": "איפה נמצא אלוקים? במקום שנותנים לו להיכנס.", "source": "אמת ואמונה", "source_url": "https://www.chabad.org/library/article_cdo/aid/4287676"},
            {"text": "אין דבר שלם יותר מלב שבור.", "source": "אמת ואמונה", "source_url": "https://www.chabad.org/library/article_cdo/aid/4287676"},
            {"text": "אל תסתפק בדיבורי פיך ובמחשבות ליבך, קום ועשה!", "source": "אמת ואמונה", "source_url": "https://www.chabad.org/library/article_cdo/aid/4287676"},
            {"text": "צריך להיות קדוש בדרך אנושית, לקב״ה יש מספיק מלאכים.", "source": "אמת ואמונה", "source_url": "https://www.chabad.org/library/article_cdo/aid/4287676"},
            {"text": "מי שאינו משתפר, מתקלקל.", "source": "אמת ואמונה", "source_url": "https://www.chabad.org/library/article_cdo/aid/4287676"},
        ]
    },
    "baal_hasulam": {
        "source_name": "בעל הסולם",
        "quotes": [
            {"text": "כל העולם כולו הוא לא יותר מאשר השתקפות של הפנימיות שלנו.", "source": "מאמרי הסולם", "source_url": "https://www.kabbalah.info/"},
            {"text": "אין אור בלי כלי.", "source": "תלמוד עשר הספירות", "source_url": "https://www.sefaria.org/"},
            {"text": "האהבה היא הכלי לגילוי הבורא.", "source": "מאמרי הסולם", "source_url": "https://www.kabbalah.info/"},
            {"text": "כל המציאות היא רק רצון לקבל.", "source": "תלמוד עשר הספירות", "source_url": "https://www.sefaria.org/"},
            {"text": "התיקון הוא להפוך את הרצון לקבל לרצון להשפיע.", "source": "מאמרי הסולם", "source_url": "https://www.kabbalah.info/"},
        ]
    },
    "rabash": {
        "source_name": "הרב״ש",
        "quotes": [
            {"text": "ואהבת לרעך כמוך - רבי עקיבא אומר זה כלל גדול בתורה.", "source": "כתבי רב״ש", "source_url": "https://www.kabbalah.info/eng/content/view/full/115977"},
            {"text": "צריכים לחדש את העבודה בכל יום, כלומר לשכוח את העבר.", "source": "שלבי הסולם", "source_url": "https://www.kabbalah.info/eng/content/view/full/31839"},
            {"text": "אהבת החברים היא הסולם לאהבת הבורא.", "source": "כתבי רב״ש", "source_url": "https://www.kabbalah.info/eng/content/view/full/115977"},
            {"text": "אין להתייאש אף פעם, כי כל נפילה היא הכנה לעלייה.", "source": "שלבי הסולם", "source_url": "https://www.kabbalah.info/eng/content/view/full/31839"},
            {"text": "הלימוד בקבוצה נותן כוח שאין ביחיד.", "source": "כתבי רב״ש", "source_url": "https://www.kabbalah.info/eng/content/view/full/115977"},
        ]
    },
    "ashlag_talmidim": {
        "source_name": "תלמידי קו אשלג",
        "quotes": [
            {"text": "הלימוד צריך להיות בהתמדה ובקביעות, כי רק כך נבנה הכלי לקבלת האור.", "source": "מפי השמועה", "source_url": "https://www.kabbalah.info/"},
            {"text": "החברותא היא הכלי החשוב ביותר בעבודה הרוחנית.", "source": "מפי השמועה", "source_url": "https://www.kabbalah.info/"},
            {"text": "אין להתייאש לעולם, כי כל נפילה היא הכנה לעלייה גדולה יותר.", "source": "מפי השמועה", "source_url": "https://www.kabbalah.info/"},
            {"text": "האמונה היא למעלה מהשכל, וצריך לעבוד עליה כל יום.", "source": "מפי השמועה", "source_url": "https://www.kabbalah.info/"},
            {"text": "כשאדם לומד בקבוצה, הוא מקבל כוח שאין לו לבד.", "source": "מפי השמועה", "source_url": "https://www.kabbalah.info/"},
        ]
    }
}


def get_daily_seed():
    """Generate consistent seed for today."""
    import hashlib
    today = date.today().isoformat()
    hash_bytes = hashlib.md5(today.encode()).digest()
    return int.from_bytes(hash_bytes[:4], byteorder='big')


def get_daily_quotes():
    """Get today's quotes - one from each source."""
    import random
    seed = get_daily_seed()
    quotes = []
    
    for i, (source_key, source_data) in enumerate(QUOTES_DATA.items()):
        random.seed(seed + i)
        quote = random.choice(source_data["quotes"])
        quote["source_name"] = source_data["source_name"]
        quotes.append(quote)
    
    return quotes


def get_random_quote():
    """Get a random quote from any source."""
    import random
    source_key = random.choice(list(QUOTES_DATA.keys()))
    source_data = QUOTES_DATA[source_key]
    quote = random.choice(source_data["quotes"])
    quote["source_name"] = source_data["source_name"]
    return quote


def format_quote(quote):
    """Format a quote for Telegram."""
    rtl = "\u200F"
    return f"""✨ *{rtl}{quote['source_name']}*

{rtl}«{quote['text']}»

📖 _{rtl}{quote['source']}_
🔗 [מקור]({quote['source_url']})"""


def send_message(chat_id, text, parse_mode="Markdown"):
    """Send message via Telegram API."""
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    if not token:
        logger.error("No token!")
        return False
    
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    data = urllib.parse.urlencode({
        "chat_id": chat_id,
        "text": text,
        "parse_mode": parse_mode,
        "disable_web_page_preview": "true"
    }).encode()
    
    try:
        req = urllib.request.Request(url, data=data)
        urllib.request.urlopen(req, timeout=10)
        return True
    except Exception as e:
        logger.error(f"Send failed: {e}")
        return False


def handle_command(command, chat_id):
    """Handle bot commands."""
    rtl = "\u200F"
    
    if command == "/start":
        msg = f"""{rtl}🌟 *ברוכים הבאים לאשלג יומי!*

{rtl}ציטוטים יומיים מגדולי הקבלה והחסידות.

{rtl}*פקודות:*
/today - הציטוטים של היום
/quote - ציטוט אקראי
/help - עזרה

{rtl}💫 יום מבורך!"""
        send_message(chat_id, msg)
    
    elif command in ["/today", "/daily"]:
        today = date.today()
        header = f"🌅 *{rtl}אשלג יומי - {today.strftime('%d/%m/%Y')}*"
        send_message(chat_id, header)
        
        for quote in get_daily_quotes():
            send_message(chat_id, format_quote(quote))
        
        send_message(chat_id, f"{rtl}💫 יום מבורך!")
    
    elif command == "/quote":
        quote = get_random_quote()
        send_message(chat_id, format_quote(quote))
    
    elif command in ["/help", "/about", "/stats"]:
        total = sum(len(s["quotes"]) for s in QUOTES_DATA.values())
        msg = f"""{rtl}📚 *אשלג יומי*

{rtl}ציטוטים מ-7 מקורות ({total} ציטוטים)

{rtl}*פקודות:*
/today - ציטוטים יומיים
/quote - ציטוט אקראי
/help - עזרה

{rtl}🙏 לתיקון עולם"""
        send_message(chat_id, msg)
    
    else:
        send_message(chat_id, f"{rtl}❓ פקודה לא מוכרת. נסה /help")


class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        try:
            length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(length)
            update = json.loads(body.decode('utf-8'))
            
            message = update.get("message", {})
            chat_id = message.get("chat", {}).get("id")
            text = message.get("text", "")
            
            if chat_id and text.startswith("/"):
                cmd = text.split()[0].split("@")[0]
                handle_command(cmd, chat_id)
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(b'{"ok":true}')
        except Exception as e:
            logger.exception(f"Error: {e}")
            self.send_response(200)  # Still return 200 to avoid Telegram retries
            self.end_headers()
            self.wfile.write(b'{"ok":false}')
    
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(b'{"status":"ok","bot":"AshlagYomiBot"}')
