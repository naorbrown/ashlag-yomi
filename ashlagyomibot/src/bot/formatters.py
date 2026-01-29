"""
Message formatters for Telegram output.

Handles:
- Hebrew RTL text formatting
- Telegram HTML formatting (more reliable than Markdown for links)
- Quote/Maamar presentation with proper attribution
- Daily bundle composition
- Channel vs Bot formatting differences
- Inline keyboards for clickable links (nachyomi-bot pattern)
- Long text splitting for Telegram's 4096 char limit
"""

from datetime import date

from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from src.data.models import (
    DailyBundle,
    Maamar,
    Quote,
    QuoteCategory,
    SourceCategory,
)
from src.utils.logger import get_logger

logger = get_logger(__name__)

# Telegram message character limit
TELEGRAM_MAX_LENGTH = 4096
# Safe limit accounting for HTML tags and buffer
TELEGRAM_SAFE_LENGTH = 3800

# Category emoji mapping for visual distinction (legacy quotes)
CATEGORY_EMOJI: dict[QuoteCategory, str] = {
    QuoteCategory.ARIZAL: "🕯️",
    QuoteCategory.BAAL_SHEM_TOV: "✨",
    QuoteCategory.POLISH_CHASSIDUT: "🔥",
    QuoteCategory.BAAL_HASULAM: "📖",
    QuoteCategory.RABASH: "💎",
    QuoteCategory.CHASDEI_ASHLAG: "🌱",
}

# Source category emoji mapping (new maamarim)
SOURCE_EMOJI: dict[SourceCategory, str] = {
    SourceCategory.BAAL_HASULAM: "📖",
    SourceCategory.RABASH: "💎",
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

    keyboard = [[InlineKeyboardButton(text="📖 מקור", url=quote.source_url)]]
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

    parts.extend(
        [
            "",
            "═══════════════════",
        ]
    )

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
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


# Keep for backwards compatibility
escape_markdown = escape_html


# =============================================================================
# MAAMAR FORMATTING FUNCTIONS (NEW)
# =============================================================================


def build_maamar_keyboard(maamar: Maamar) -> InlineKeyboardMarkup:
    """
    Build inline keyboard with source link for a maamar.

    Args:
        maamar: The maamar to build a keyboard for

    Returns:
        InlineKeyboardMarkup with source button
    """
    keyboard = [[InlineKeyboardButton(text="📖 מקור", url=maamar.source_url)]]
    return InlineKeyboardMarkup(keyboard)


def split_hebrew_text(
    text: str,
    max_length: int = TELEGRAM_SAFE_LENGTH,
) -> list[str]:
    """
    Split long Hebrew text into chunks suitable for Telegram.

    Tries to split at natural boundaries (paragraph, sentence, word)
    while respecting RTL text direction.

    Args:
        text: The text to split
        max_length: Maximum length per chunk

    Returns:
        List of text chunks
    """
    if len(text) <= max_length:
        return [text]

    chunks: list[str] = []
    remaining = text

    while remaining:
        if len(remaining) <= max_length:
            chunks.append(remaining)
            break

        # Find the best split point within the limit
        split_at = max_length

        # Try to split at paragraph boundary (double newline)
        para_pos = remaining.rfind("\n\n", 0, max_length)
        if para_pos > max_length // 2:
            split_at = para_pos + 2

        # Try to split at sentence boundary (Hebrew period or newline)
        elif (sent_pos := remaining.rfind(".", 0, max_length)) > max_length // 2 or (
            sent_pos := remaining.rfind("\n", 0, max_length)
        ) > max_length // 2:
            split_at = sent_pos + 1

        # Last resort: split at word boundary (space)
        elif (space_pos := remaining.rfind(" ", 0, max_length)) > max_length // 2:
            split_at = space_pos + 1

        # Add the chunk
        chunk = remaining[:split_at].strip()
        if chunk:
            chunks.append(chunk)

        remaining = remaining[split_at:].strip()

    return chunks


def format_maamar_header(maamar: Maamar) -> str:
    """
    Format the header for a single maamar message.

    Args:
        maamar: The maamar to format

    Returns:
        Formatted HTML header string
    """
    emoji = SOURCE_EMOJI.get(maamar.source, "📜")

    parts = [
        f"{emoji} <b>{maamar.source.display_name_hebrew}</b>",
        "",
        f"<b>{maamar.title}</b>",
    ]

    if maamar.subtitle:
        parts.append(f"<i>{maamar.subtitle}</i>")

    parts.extend(["", f"📚 {maamar.book}"])

    if maamar.page:
        parts[-1] += f" | עמ׳ {maamar.page}"

    parts.extend(["", "───────────────────", ""])

    return "\n".join(parts)


def format_maamar(maamar: Maamar) -> list[str]:
    """
    Format a maamar for Telegram, splitting into multiple messages if needed.

    Args:
        maamar: The maamar to format

    Returns:
        List of formatted HTML messages
    """
    header = format_maamar_header(maamar)
    header_len = len(header)

    # Check if it fits in one message
    full_message = header + maamar.text
    if len(full_message) <= TELEGRAM_SAFE_LENGTH:
        return [full_message]

    # Need to split - first chunk gets header
    first_chunk_max = TELEGRAM_SAFE_LENGTH - header_len - 10
    cont_overhead = 30  # "📜 חלק X/Y\n\n"

    text_chunks = split_hebrew_text(maamar.text, first_chunk_max)

    # Re-split if needed for subsequent chunks
    if len(text_chunks) > 1:
        subsequent_max = TELEGRAM_SAFE_LENGTH - cont_overhead
        all_chunks = [text_chunks[0]]
        remaining = maamar.text[len(text_chunks[0]) :].strip()
        all_chunks.extend(split_hebrew_text(remaining, subsequent_max))
        text_chunks = all_chunks

    total_parts = len(text_chunks)
    messages: list[str] = []

    for i, chunk in enumerate(text_chunks):
        if i == 0:
            messages.append(header + chunk + (" ..." if total_parts > 1 else ""))
        else:
            cont = f"📜 חלק {i + 1}/{total_parts}\n\n"
            messages.append(cont + chunk + (" ..." if i < total_parts - 1 else ""))

    return messages


def format_maamar_preview(maamar: Maamar, max_preview_length: int = 200) -> str:
    """
    Format a short preview of a maamar.

    Useful for listings or search results.

    Args:
        maamar: The maamar to preview
        max_preview_length: Maximum length of the preview text

    Returns:
        Formatted HTML preview string
    """
    emoji = SOURCE_EMOJI.get(maamar.source, "📜")

    # Truncate text for preview
    preview_text = maamar.text[:max_preview_length]
    if len(maamar.text) > max_preview_length:
        # Find last word boundary
        last_space = preview_text.rfind(" ")
        if last_space > max_preview_length // 2:
            preview_text = preview_text[:last_space]
        preview_text += "..."

    parts = [
        f"{emoji} <b>{maamar.title}</b>",
        f"📚 {maamar.book}",
        "",
        f"״{preview_text}״",
    ]

    return "\n".join(parts)
