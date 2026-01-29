#!/usr/bin/env python3
"""
Diagnostic script for Ashlag Yomi Telegram bot.

Run this script to verify all components are working correctly:
- Quote data loading
- Formatting
- Settings configuration

Usage:
    python scripts/diagnose.py
"""

import sys
from datetime import date
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def check_environment():
    """Check environment variables."""
    print("\n📋 Checking environment...")

    import os

    required_vars = ["TELEGRAM_BOT_TOKEN", "TELEGRAM_CHAT_ID"]
    optional_vars = ["ENVIRONMENT", "DRY_RUN", "LOG_LEVEL"]

    all_ok = True
    for var in required_vars:
        value = os.environ.get(var)
        if value:
            # Mask token for security
            display = value[:10] + "..." if len(value) > 10 else value
            print(f"  ✅ {var}: {display}")
        else:
            print(f"  ❌ {var}: NOT SET (required)")
            all_ok = False

    for var in optional_vars:
        value = os.environ.get(var, "(default)")
        print(f"  ℹ️  {var}: {value}")

    return all_ok


def check_settings():
    """Check settings can be loaded."""
    print("\n⚙️  Checking settings...")

    try:
        from src.utils.config import get_settings

        settings = get_settings()
        print(f"  ✅ Environment: {settings.environment}")
        print(f"  ✅ Dry run: {settings.dry_run}")
        print(f"  ✅ Log level: {settings.log_level}")
        return True
    except Exception as e:
        print(f"  ❌ Failed to load settings: {e}")
        return False


def check_quote_repository():
    """Check quote repository works."""
    print("\n📚 Checking quote repository...")

    try:
        from src.data.repository import QuoteRepository
        from src.data.models import QuoteCategory

        repo = QuoteRepository()

        # Check quotes directory
        print(f"  ℹ️  Quotes dir: {repo._quotes_dir}")
        print(f"  ℹ️  Quotes dir exists: {repo._quotes_dir.exists()}")

        # Load and validate quotes
        stats = repo.validate_all()
        print(f"  ✅ Total quotes: {stats['total']}")

        for category in QuoteCategory:
            count = stats.get(category.value, 0)
            status = "✅" if count > 0 else "⚠️"
            print(f"  {status} {category.value}: {count} quotes")

        return stats["total"] > 0
    except Exception as e:
        print(f"  ❌ Failed to load quotes: {e}")
        import traceback

        traceback.print_exc()
        return False


def check_daily_bundle():
    """Check daily bundle generation."""
    print("\n📅 Checking daily bundle...")

    try:
        from src.data.repository import QuoteRepository

        repo = QuoteRepository()
        bundle = repo.get_daily_bundle(date.today())

        print(f"  ✅ Bundle date: {bundle.date}")
        print(f"  ✅ Quotes in bundle: {len(bundle.quotes)}")

        for quote in bundle.quotes:
            print(f"    - {quote.category.value}: {quote.id[:30]}...")

        return len(bundle.quotes) == 6
    except Exception as e:
        print(f"  ❌ Failed to generate bundle: {e}")
        import traceback

        traceback.print_exc()
        return False


def check_formatting():
    """Check quote formatting works."""
    print("\n🎨 Checking formatting...")

    try:
        from src.data.repository import QuoteRepository
        from src.bot.formatters import format_quote, build_source_keyboard

        repo = QuoteRepository()
        bundle = repo.get_daily_bundle(date.today())

        for quote in bundle.quotes:
            formatted = format_quote(quote)
            keyboard = build_source_keyboard(quote)

            if not formatted:
                print(f"  ❌ {quote.category.value}: Empty formatted message")
                return False

            if "<b>" not in formatted:
                print(f"  ❌ {quote.category.value}: Missing HTML formatting")
                return False

            print(f"  ✅ {quote.category.value}: {len(formatted)} chars, keyboard={'yes' if keyboard else 'no'}")

        return True
    except Exception as e:
        print(f"  ❌ Failed to format quotes: {e}")
        import traceback

        traceback.print_exc()
        return False


def check_telegram_connection():
    """Check Telegram API connection."""
    print("\n📡 Checking Telegram connection...")

    try:
        import asyncio
        from telegram import Bot
        from src.utils.config import get_settings

        settings = get_settings()

        async def test_connection():
            bot = Bot(token=settings.telegram_bot_token.get_secret_value())
            me = await bot.get_me()
            return me

        me = asyncio.run(test_connection())
        print(f"  ✅ Bot username: @{me.username}")
        print(f"  ✅ Bot ID: {me.id}")
        return True
    except Exception as e:
        print(f"  ❌ Failed to connect: {e}")
        return False


def main():
    """Run all diagnostics."""
    print("=" * 60)
    print("🔍 Ashlag Yomi Bot Diagnostics")
    print("=" * 60)

    results = []

    # Run checks
    results.append(("Environment", check_environment()))
    results.append(("Settings", check_settings()))
    results.append(("Quote Repository", check_quote_repository()))
    results.append(("Daily Bundle", check_daily_bundle()))
    results.append(("Formatting", check_formatting()))
    results.append(("Telegram Connection", check_telegram_connection()))

    # Summary
    print("\n" + "=" * 60)
    print("📊 Summary")
    print("=" * 60)

    all_passed = True
    for name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"  {status}: {name}")
        if not passed:
            all_passed = False

    print()
    if all_passed:
        print("🎉 All checks passed! Bot should work correctly.")
        return 0
    else:
        print("⚠️  Some checks failed. Review the errors above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
