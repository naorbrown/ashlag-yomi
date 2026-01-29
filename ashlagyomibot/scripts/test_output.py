#!/usr/bin/env python3
"""
Test script to preview today's quotes output.

Run this to see exactly what will be sent to Telegram.
Outputs formatted quotes to console for verification.
"""

import sys
from datetime import date
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.data.models import Quote
from src.data.quote_repository import get_quote_repository


def format_quote_for_console(quote: Quote) -> str:
    """Format a quote for console display."""
    # Build title from source book and section
    title_parts = []
    if quote.source_book:
        title_parts.append(quote.source_book)
    if quote.source_section:
        title_parts.append(quote.source_section)

    title = ", ".join(title_parts) if title_parts else quote.source_rabbi

    output = []
    output.append("=" * 60)
    output.append(f"📖 {title}")
    output.append("")
    output.append(quote.text)
    output.append("")
    output.append(f"— {quote.source_rabbi}")
    output.append("")
    output.append(f"🔗 Source: {quote.source_url}")
    output.append("=" * 60)

    return "\n".join(output)


def main():
    """Preview today's quotes."""
    print("\n" + "=" * 60)
    print("🌅 אשלג יומי - Quote Preview")
    print("=" * 60)

    repository = get_quote_repository()

    # Show stats
    stats = repository.get_stats()
    print("\n📊 Loaded quotes:")
    print(f"   • Baal Hasulam: {stats.get('baal_hasulam', 0)}")
    print(f"   • Rabash: {stats.get('rabash', 0)}")
    print(f"   • Total: {stats.get('total', 0)}")

    # Get today's quotes
    target_date = date.today()
    quotes = repository.get_daily_quotes(target_date)

    print(f"\n📅 Today's quotes ({target_date.strftime('%d.%m.%Y')}):")
    print(f"   Will send {len(quotes)} quotes\n")

    for i, quote in enumerate(quotes, 1):
        print(f"\n--- Quote {i} ---\n")
        print(format_quote_for_console(quote))
        print()

    # Show what Telegram will display
    print("\n" + "=" * 60)
    print("📱 Telegram Output Preview (HTML removed):")
    print("=" * 60)

    header = f"🌅 אשלג יומי - {target_date.strftime('%d.%m.%Y')}"
    print(f"\n{header}")
    print("═══════════════════\n")

    for quote in quotes:
        title_parts = []
        if quote.source_book:
            title_parts.append(quote.source_book)
        if quote.source_section:
            title_parts.append(quote.source_section)
        title = ", ".join(title_parts) if title_parts else quote.source_rabbi

        print(f"📖 {title}")
        print()
        print(quote.text)
        print()
        print(f"— {quote.source_rabbi}")
        print(f"[📖 מקור מלא] -> {quote.source_url}")
        print()
        print("---")
        print()

    print("═══════════════════")
    print("\n✅ Preview complete!\n")


if __name__ == "__main__":
    main()
