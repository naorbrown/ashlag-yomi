"""
Message formatters for Telegram output.

Handles:
- Hebrew RTL text formatting
- Telegram HTML formatting (more reliable than Markdown for links)
- Quote presentation with proper attribution
- Daily bundle composition
- Channel vs Bot formatting differences
- Inline keyboards for clickable links (nachyomi-bot pattern)
"""

from datetime import date

from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from src.data.models import DailyBundle, Quote, QuoteCategory
from src.utils.logger import get_logger

logger = get_logger(__name__)

# Category emoji mapping for visual distinction
CATEGORY_EMOJI: dict[QuoteCategory, str] = {
    QuoteCategory.ARIZAL: "🕯️",
    QuoteCategory.BAAL_SHEM_TOV: "✨",
    QuoteCategory.POLISH_CHASSIDUT: "🔥",
    QuoteCategory.BAAL_HASULAM: "📖",
    QuoteCategory.RABASH: "💎",
    QuoteCategory.CHASDEI_ASHLAG: "🌱",
}


def build_source_keyboard(quote: Quote) -> InlineKeyboardMarkup | None:
    """
    Build inline keyboard with source link (nachyomi-bot pattern).

    Uses URL buttons instead of inline text links for reliable clickability.

    Args:
        quote: The quote to build a keyboard for

    Returns:
        InlineKeyboardMarkup with source button, or None if no source URL
    """
    if not quote.source_url:
        return None

    keyboard = [
        [InlineKeyboardButton(text="📖 מקור", url=quote.source_url)]
    ]
    return InlineKeyboardMarkup(keyboard)


def format_quote(quote: Quote) -> str:
    """
    Format a single quote for Telegram.

    Uses HTML formatting with Hebrew RTL support.
    Telegram automatically handles RTL for Hebrew text.

    Note: Source links are provided via inline keyboard (build_source_keyboard),
    not as inline text links. This follows the nachyomi-bot pattern for
    reliable clickable links.

    Args:
        quote: The quote to format

    Returns:
        Formatted HTML string
    """
    emoji = CATEGORY_EMOJI.get(quote.category, "📜")

    # For categories with multiple rabbis, show the specific rabbi name
    # Otherwise show the category name
    if quote.category in (QuoteCategory.POLISH_CHASSIDUT, QuoteCategory.CHASDEI_ASHLAG):
        rabbi_name = quote.source_rabbi
    else:
        rabbi_name = quote.source_rabbi or quote.category.display_name_hebrew

    # Build the message parts (HTML formatting)
    parts: list[str] = [
        f"{emoji} <b>{rabbi_name}</b>",
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

    # Source link is provided via inline keyboard (build_source_keyboard)
    # not as inline text link - this follows nachyomi-bot pattern

    return "\n".join(parts)


def format_channel_message(quote: Quote, target_date: date | None = None) -> str:
    """
    Format a quote for channel broadcast - single, elegant message.

    Different from bot format - designed for passive consumption.

    Note: Source links are provided via inline keyboard (build_source_keyboard),
    not as inline text links. This follows the nachyomi-bot pattern.

    Args:
        quote: The quote to send
        target_date: Date for header

    Returns:
        Formatted HTML string
    """
    if target_date is None:
        target_date = date.today()

    emoji = CATEGORY_EMOJI.get(quote.category, "📜")

    # For categories with multiple rabbis, show the specific rabbi name
    if quote.category in (QuoteCategory.POLISH_CHASSIDUT, QuoteCategory.CHASDEI_ASHLAG):
        rabbi_name = quote.source_rabbi
    else:
        rabbi_name = quote.source_rabbi or quote.category.display_name_hebrew

    # Hebrew date format
    date_str = target_date.strftime("%d.%m.%Y")

    parts: list[str] = [
        f"🌅 <b>אשלג יומי</b> | {date_str}",
        "",
        "═══════════════════",
        "",
        f"{emoji} <b>{rabbi_name}</b>",
        "",
        f"״{quote.text}״",
    ]

    # Add source attribution
    if quote.source_book:
        source_line = f"📚 <i>{quote.source_book}</i>"
        if quote.source_section:
            source_line += f", <i>{quote.source_section}</i>"
        parts.append("")
        parts.append(source_line)

    # Source link is provided via inline keyboard (build_source_keyboard)
    # not as inline text link - this follows nachyomi-bot pattern

    parts.extend([
        "",
        "═══════════════════",
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
        List of formatted HTML strings (one per quote)
    """
    if not bundle.quotes:
        return ["אין ציטוטים זמינים להיום 😔"]

    messages: list[str] = []

    # Header message
    date_str = bundle.date.strftime("%d.%m.%Y")

    header = f"🌅 <b>אשלג יומי - {date_str}</b>"
    header += "\n\n═══════════════════"
    messages.append(header)

    # Format each quote
    for quote in bundle.quotes:
        formatted = format_quote(quote)
        messages.append(formatted)

    # Footer message
    footer = "═══════════════════"
    messages.append(footer)

    return messages


def format_single_quote_message(quote: Quote) -> str:
    """
    Format a single quote as a standalone message.

    Useful for individual quote sharing or testing.

    Args:
        quote: The quote to format

    Returns:
        Formatted HTML string
    """
    formatted_quote = format_quote(quote)

    return f"""📜 <b>ציטוט יומי</b>

{formatted_quote}

═══════════════════
"""


def escape_html(text: str) -> str:
    """
    Escape special HTML characters in text.

    Use this for user-provided content that shouldn't be interpreted
    as HTML formatting.

    Args:
        text: Raw text to escape

    Returns:
        Text with HTML special characters escaped
    """
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )


# Keep for backwards compatibility
escape_markdown = escape_html
