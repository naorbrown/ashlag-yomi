"""
Message formatters for Telegram output.

Handles:
- Hebrew RTL text formatting
- Telegram MarkdownV2 syntax
- Quote presentation with proper attribution
- Daily bundle composition
- Channel vs Bot formatting differences
"""

import random
from datetime import date

from src.data.models import DailyBundle, Quote, QuoteCategory
from src.utils.logger import get_logger

logger = get_logger(__name__)

# Category emoji mapping for visual distinction
CATEGORY_EMOJI: dict[QuoteCategory, str] = {
    QuoteCategory.ARIZAL: "🕯️",
    QuoteCategory.BAAL_SHEM_TOV: "✨",
    QuoteCategory.SIMCHA_BUNIM: "🌟",
    QuoteCategory.KOTZKER: "🔥",
    QuoteCategory.BAAL_HASULAM: "📖",
    QuoteCategory.RABASH: "💎",
    QuoteCategory.TALMIDIM: "🌱",
}

# Daily greetings for variety - rotate based on day
DAILY_GREETINGS: list[str] = [
    "בוקר אור ✨",
    "יום טוב ומבורך 🌅",
    "שבוע טוב 🌟",
    "שלום וברכה 🕊️",
    "יום מאיר 🌞",
    "בהצלחה ביומכם 💪",
    "חזקו ואמצו 🌿",
]

# Inspirational footers - rotate for variety
DAILY_FOOTERS: list[str] = [
    "״הסתכלות בתכלית מביאה את האדם לשלמות״",
    "״אין אור גדול יותר מהאור היוצא מתוך החושך״",
    "״כל ישראל ערבים זה לזה״",
    "״ואהבת לרעך כמוך - זהו כלל גדול בתורה״",
    "״תכלית הבריאה היא להיטיב לנבראיו״",
    "״החירות האמיתית היא חירות מהרצון לקבל לעצמו״",
    "״אהבת חברים היא הסולם לעלות לאהבת הבורא״",
]


def _get_daily_greeting(target_date: date | None = None) -> str:
    """Get a greeting based on the day of year for consistent daily rotation."""
    if target_date is None:
        target_date = date.today()
    day_of_year = target_date.timetuple().tm_yday
    return DAILY_GREETINGS[day_of_year % len(DAILY_GREETINGS)]


def _get_daily_footer(target_date: date | None = None) -> str:
    """Get a footer based on the day of year for consistent daily rotation."""
    if target_date is None:
        target_date = date.today()
    day_of_year = target_date.timetuple().tm_yday
    return DAILY_FOOTERS[day_of_year % len(DAILY_FOOTERS)]


def format_quote(quote: Quote, *, include_source_link: bool = True) -> str:
    """
    Format a single quote for Telegram.

    Uses Markdown formatting with Hebrew RTL support.
    Telegram automatically handles RTL for Hebrew text.

    Args:
        quote: The quote to format
        include_source_link: Whether to include the source URL

    Returns:
        Formatted Markdown string
    """
    emoji = CATEGORY_EMOJI.get(quote.category, "📜")
    rabbi_name = quote.category.display_name_hebrew

    # Build the message parts
    parts: list[str] = [
        f"{emoji} *{rabbi_name}*",
        "",  # Blank line
        f"״{quote.text}״",
    ]

    # Add source attribution if available
    if quote.source_book:
        source_line = f"📚 {quote.source_book}"
        if quote.source_section:
            source_line += f", {quote.source_section}"
        parts.append("")
        parts.append(source_line)

    # Add source link
    if include_source_link and quote.source_url:
        parts.append(f"[📎 מקור]({quote.source_url})")

    return "\n".join(parts)


def format_channel_message(quote: Quote, target_date: date | None = None) -> str:
    """
    Format a quote for channel broadcast - single, elegant message.

    Different from bot format - designed for passive consumption.

    Args:
        quote: The quote to send
        target_date: Date for greeting/footer rotation

    Returns:
        Formatted Markdown string
    """
    if target_date is None:
        target_date = date.today()

    emoji = CATEGORY_EMOJI.get(quote.category, "📜")
    rabbi_name = quote.category.display_name_hebrew
    greeting = _get_daily_greeting(target_date)
    footer = _get_daily_footer(target_date)

    # Hebrew date format
    date_str = target_date.strftime("%d.%m.%Y")

    parts: list[str] = [
        f"🌅 *אשלג יומי* | {date_str}",
        f"{greeting}",
        "",
        "═══════════════════",
        "",
        f"{emoji} *{rabbi_name}*",
        "",
        f"״{quote.text}״",
    ]

    # Add source attribution
    if quote.source_book:
        source_line = f"📚 _{quote.source_book}_"
        if quote.source_section:
            source_line += f", _{quote.source_section}_"
        parts.append("")
        parts.append(source_line)

    # Add source link
    if quote.source_url:
        parts.append(f"[📎 מקור]({quote.source_url})")

    parts.extend([
        "",
        "═══════════════════",
        "",
        f"_{footer}_",
        "",
        "🤖 @AshlagYomiBot | 📢 @AshlagYomi",
    ])

    return "\n".join(parts)


def format_daily_bundle(bundle: DailyBundle) -> list[str]:
    """
    Format a daily bundle as a list of messages.

    Each quote gets its own message for better readability.
    The first message includes a header, and the last includes a footer.

    Args:
        bundle: The daily bundle to format

    Returns:
        List of formatted Markdown strings (one per quote)
    """
    if not bundle.quotes:
        return ["אין ציטוטים זמינים להיום 😔"]

    messages: list[str] = []

    # Header message
    date_str = bundle.date.strftime("%d.%m.%Y")
    greeting = _get_daily_greeting(bundle.date)

    header = f"🌅 *אשלג יומי - {date_str}*\n"
    header += f"{greeting}\n\n"
    header += f"_זמן קריאה משוער: {bundle.total_reading_time_minutes} דקות_"
    header += "\n\n═══════════════════"
    messages.append(header)

    # Format each quote
    for quote in bundle.quotes:
        formatted = format_quote(quote)
        messages.append(formatted)

    # Footer message
    footer_quote = _get_daily_footer(bundle.date)
    footer = "═══════════════════\n\n"
    footer += f"_{footer_quote}_\n\n"
    footer += "📲 /today לציטוט נוסף | /about על הפרויקט"
    messages.append(footer)

    return messages


def format_single_quote_message(quote: Quote) -> str:
    """
    Format a single quote as a standalone message.

    Useful for individual quote sharing or testing.

    Args:
        quote: The quote to format

    Returns:
        Formatted Markdown string
    """
    formatted_quote = format_quote(quote)

    return f"""📜 *ציטוט יומי*

{formatted_quote}

═══════════════════
📲 /today | /about
"""


def escape_markdown(text: str) -> str:
    """
    Escape special Markdown characters in text.

    Use this for user-provided content that shouldn't be interpreted
    as Markdown formatting.

    Args:
        text: Raw text to escape

    Returns:
        Text with Markdown special characters escaped
    """
    special_chars = ["_", "*", "[", "]", "(", ")", "~", "`", ">", "#", "+", "-", "=", "|", "{", "}", ".", "!"]
    for char in special_chars:
        text = text.replace(char, f"\\{char}")
    return text
