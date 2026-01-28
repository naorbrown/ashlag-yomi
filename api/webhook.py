"""
Vercel Serverless Function for Telegram Webhook
Handles incoming Telegram updates and responds to commands.
"""

import os
import json
import logging
from http.server import BaseHTTPRequestHandler
from datetime import date
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.quote_manager import QuoteManager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize quote manager once (reused across requests)
quote_manager = QuoteManager()


def send_telegram_message(chat_id: int, text: str, parse_mode: str = "Markdown") -> bool:
    """Send a message via Telegram API."""
    import urllib.request
    import urllib.parse
    
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    if not token:
        logger.error("TELEGRAM_BOT_TOKEN not set")
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
        logger.error(f"Failed to send message: {e}")
        return False


def handle_command(command: str, chat_id: int) -> None:
    """Handle a bot command."""
    rtl = "\u200F"
    
    if command == "/start":
        message = f"""
{rtl}🌟 *ברוכים הבאים לאשלג יומי!*

{rtl}בוט זה שולח ציטוטים יומיים מגדולי ישראל:
• האר״י הקדוש
• הבעל שם טוב
• רבי שמחה בונים מפשיסחא
• הרבי מקוצק
• בעל הסולם
• הרב״ש
• תלמידי קו אשלג

{rtl}*פקודות זמינות:*
/today - הציטוטים של היום
/quote - ציטוט אקראי
/stats - סטטיסטיקות
/about - אודות הבוט
/help - עזרה

{rtl}💫 יום מבורך!
"""
        send_telegram_message(chat_id, message)
    
    elif command in ["/today", "/daily"]:
        quotes = quote_manager.get_daily_quotes()
        today = date.today()
        
        # Send header
        header = f"🌅 *{rtl}ציטוט יומי - {today.strftime('%d/%m/%Y')}*\n"
        header += f"{rtl}השראה מגדולי ישראל"
        send_telegram_message(chat_id, header)
        
        # Send each quote
        for quote in quotes:
            msg = quote_manager.format_quote_message(quote)
            send_telegram_message(chat_id, msg)
        
        # Send footer
        footer = f"{rtl}━━━━━━━━━━━━━━━━━━━━\n{rtl}💫 יום מבורך!"
        send_telegram_message(chat_id, footer)
    
    elif command == "/quote":
        quote = quote_manager.get_random_quote()
        if quote:
            msg = quote_manager.format_quote_message(quote)
            send_telegram_message(chat_id, msg)
        else:
            send_telegram_message(chat_id, f"{rtl}❌ לא נמצאו ציטוטים.")
    
    elif command == "/stats":
        stats = quote_manager.get_stats()
        source_names = {
            "arizal": "האר״י הקדוש",
            "baal_shem_tov": "הבעל שם טוב",
            "simcha_bunim": "רבי שמחה בונים",
            "kotzker": "הרבי מקוצק",
            "baal_hasulam": "בעל הסולם",
            "rabash": "הרב״ש",
            "ashlag_talmidim": "תלמידי קו אשלג"
        }
        
        msg = f"{rtl}📊 *סטטיסטיקות ציטוטים*\n\n"
        for source, count in stats["by_source"].items():
            display_name = source_names.get(source, source)
            msg += f"• {rtl}{display_name}: {count} ציטוטים\n"
        msg += f"\n{rtl}*סה״כ: {stats['total']} ציטוטים*"
        send_telegram_message(chat_id, msg)
    
    elif command == "/about":
        stats = quote_manager.get_stats()
        msg = f"""
{rtl}📖 *אודות אשלג יומי*

{rtl}בוט זה מביא ציטוטים יומיים מגדולי הקבלה והחסידות.

{rtl}*המקורות:*
• האר״י הקדוש (המאה ה-16)
• הבעל שם טוב (1698-1760)
• רבי שמחה בונים מפשיסחא (1765-1827)
• הרבי מקוצק (1787-1859)
• בעל הסולם (1885-1954)
• הרב״ש (1907-1991)
• תלמידי קו אשלג

{rtl}*מאגר:* {stats['total']} ציטוטים מאומתים

{rtl}🙏 לתיקון עולם
"""
        send_telegram_message(chat_id, msg)
    
    elif command == "/help":
        msg = f"""
{rtl}📚 *עזרה - אשלג יומי*

{rtl}*פקודות:*
/start - התחלה והסבר על הבוט
/today - הציטוטים של היום ⭐
/quote - ציטוט אקראי
/stats - סטטיסטיקות
/about - אודות הבוט
/help - הצג הודעה זו

{rtl}*אודות:*
{rtl}הציטוטים נשלחים אוטומטית כל יום בשעה 6:00 בבוקר (שעון ישראל).

{rtl}🙏 לתיקון עולם
"""
        send_telegram_message(chat_id, msg)
    
    elif command == "/quality":
        msg = quote_manager.get_selection_explanation()
        send_telegram_message(chat_id, msg)
    
    else:
        send_telegram_message(chat_id, f"{rtl}❓ פקודה לא מוכרת. השתמש ב-/help")


class handler(BaseHTTPRequestHandler):
    """Vercel serverless handler for Telegram webhook."""
    
    def do_POST(self):
        """Handle POST request from Telegram."""
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length)
            update = json.loads(body.decode('utf-8'))
            
            logger.info(f"Received update: {update.get('update_id')}")
            
            # Extract message info
            message = update.get("message", {})
            chat_id = message.get("chat", {}).get("id")
            text = message.get("text", "")
            
            if chat_id and text.startswith("/"):
                command = text.split()[0].split("@")[0]  # Handle /command@botname
                handle_command(command, chat_id)
            
            # Respond OK
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"ok": True}).encode())
            
        except Exception as e:
            logger.exception(f"Error handling webhook: {e}")
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"error": str(e)}).encode())
    
    def do_GET(self):
        """Health check endpoint."""
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        
        stats = quote_manager.get_stats()
        response = {
            "status": "ok",
            "bot": "AshlagYomiBot",
            "quotes": stats["total"]
        }
        self.wfile.write(json.dumps(response).encode())
