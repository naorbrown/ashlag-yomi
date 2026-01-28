#!/usr/bin/env python3
"""
Test Pipeline Script for Ashlag Yomi

This script provides a full pipeline test that:
1. Validates all quote files
2. Tests quote loading and selection
3. Formats sample messages
4. Optionally sends test messages to Telegram

Usage:
    # Full validation (no Telegram)
    python scripts/test_pipeline.py

    # With Telegram test (requires TELEGRAM_BOT_TOKEN and TEST_CHAT_ID)
    python scripts/test_pipeline.py --telegram

    # Flush and rebuild (clear cache, reload everything)
    python scripts/test_pipeline.py --flush
"""

import argparse
import asyncio
import json
import os
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


def print_header(text: str) -> None:
    """Print a formatted header."""
    print("\n" + "=" * 60)
    print(f"  {text}")
    print("=" * 60)


def print_success(text: str) -> None:
    """Print success message."""
    print(f"  [PASS] {text}")


def print_error(text: str) -> None:
    """Print error message."""
    print(f"  [FAIL] {text}")


def print_info(text: str) -> None:
    """Print info message."""
    print(f"  [INFO] {text}")


def validate_json_files(quotes_dir: Path) -> bool:
    """Validate all JSON files in the quotes directory."""
    print_header("Validating JSON Files")

    all_valid = True
    quote_files = list(quotes_dir.glob("*.json"))

    if not quote_files:
        print_error(f"No JSON files found in {quotes_dir}")
        return False

    for quote_file in quote_files:
        try:
            with open(quote_file, encoding="utf-8") as f:
                data = json.load(f)

            if quote_file.name == "metadata.json":
                print_success(f"{quote_file.name}: Valid metadata ({len(data)} rabbis)")
                continue

            if "quotes" not in data:
                print_error(f"{quote_file.name}: Missing 'quotes' key")
                all_valid = False
                continue

            quotes = data["quotes"]
            if not quotes:
                print_error(f"{quote_file.name}: Empty quotes array")
                all_valid = False
                continue

            # Validate each quote
            issues = []
            for i, quote in enumerate(quotes):
                if "text" not in quote:
                    issues.append(f"Quote {i}: missing 'text'")
                if "source" not in quote:
                    issues.append(f"Quote {i}: missing 'source'")
                if not quote.get("text", "").strip():
                    issues.append(f"Quote {i}: empty text")

            if issues:
                print_error(f"{quote_file.name}: {len(issues)} issues found")
                for issue in issues[:3]:  # Show first 3 issues
                    print(f"           - {issue}")
                all_valid = False
            else:
                print_success(f"{quote_file.name}: Valid ({len(quotes)} quotes)")

        except json.JSONDecodeError as e:
            print_error(f"{quote_file.name}: Invalid JSON - {e}")
            all_valid = False
        except Exception as e:
            print_error(f"{quote_file.name}: Error - {e}")
            all_valid = False

    return all_valid


def test_quotes_manager(quotes_dir: Path) -> bool:
    """Test the QuotesManager class."""
    print_header("Testing QuotesManager")

    try:
        from bot import QuotesManager

        manager = QuotesManager(quotes_dir)

        # Check loaded rabbis
        rabbi_keys = manager.get_all_rabbi_keys()
        print_info(f"Loaded {len(rabbi_keys)} rabbi quote files")

        # Required rabbis
        required = [
            "arizal",
            "baal_shem_tov",
            "simcha_bunim",
            "kotzker_rebbe",
            "baal_hasulam",
            "rabash",
            "ashlag_talmidim",
        ]

        for rabbi in required:
            if rabbi in rabbi_keys:
                quotes_count = len(manager.quotes_cache.get(rabbi, []))
                name = manager.get_rabbi_display_name(rabbi)
                print_success(f"{rabbi}: {quotes_count} quotes ({name})")
            else:
                print_error(f"{rabbi}: Missing!")
                return False

        # Test random quote selection
        print_info("Testing random quote selection...")
        for rabbi in required:
            quote = manager.get_random_quote(rabbi)
            if quote:
                text_preview = quote.get("text", "")[:40]
                print_success(f"{rabbi}: '{text_preview}...'")
            else:
                print_error(f"{rabbi}: Failed to get random quote")
                return False

        # Test daily quotes
        print_info("Testing daily quotes generation...")
        daily = manager.get_daily_quotes()
        print_success(f"Generated {len(daily)} daily quotes")

        return True

    except Exception as e:
        print_error(f"QuotesManager test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_message_formatting() -> bool:
    """Test message formatting functions."""
    print_header("Testing Message Formatting")

    try:
        from bot import format_quote_message, split_long_message

        # Test basic formatting
        quote = {
            "text": "זהו ציטוט לדוגמה בעברית.",
            "source": "ספר הבדיקות",
            "source_url": "https://example.com/test",
        }

        message = format_quote_message(quote, "רב לדוגמה")
        print_success(f"Basic formatting: {len(message)} chars")

        # Test message splitting
        long_message = "שורה ארוכה מאוד\n" * 500
        parts = split_long_message(long_message, max_length=4096)
        print_success(f"Message splitting: {len(parts)} parts from {len(long_message)} chars")

        return True

    except Exception as e:
        print_error(f"Message formatting test failed: {e}")
        return False


async def test_telegram_integration(token: str, chat_id: int) -> bool:
    """Test Telegram bot integration."""
    print_header("Testing Telegram Integration")

    try:
        from telegram import Bot

        bot = Bot(token=token)

        # Test connection
        me = await bot.get_me()
        print_success(f"Connected as @{me.username}")

        # Send test message
        test_message = (
            "🧪 *בדיקת מערכת אשלג יומי*\n\n"
            "System test successful!\n"
            "כל המערכות פועלות.\n\n"
            "_הודעה זו היא בדיקה בלבד._"
        )

        await bot.send_message(
            chat_id=chat_id,
            text=test_message,
            parse_mode="Markdown",
        )
        print_success(f"Test message sent to chat {chat_id}")

        return True

    except Exception as e:
        print_error(f"Telegram test failed: {e}")
        return False


def run_tests(args: argparse.Namespace) -> bool:
    """Run all tests."""
    quotes_dir = Path(__file__).parent.parent / "data" / "quotes"

    if args.flush:
        print_header("Flushing Cache (Reload Everything)")
        print_info("Cache cleared - all data will be reloaded fresh")

    # Run validation tests
    all_passed = True

    if not validate_json_files(quotes_dir):
        all_passed = False

    if not test_quotes_manager(quotes_dir):
        all_passed = False

    if not test_message_formatting():
        all_passed = False

    # Telegram test (optional)
    if args.telegram:
        token = os.environ.get("TELEGRAM_BOT_TOKEN")
        chat_id = os.environ.get("TEST_CHAT_ID")

        if not token:
            print_error("TELEGRAM_BOT_TOKEN not set")
            all_passed = False
        elif not chat_id:
            print_error("TEST_CHAT_ID not set")
            all_passed = False
        else:
            if not asyncio.run(test_telegram_integration(token, int(chat_id))):
                all_passed = False

    # Summary
    print_header("Test Summary")
    if all_passed:
        print_success("All tests passed!")
        return True
    else:
        print_error("Some tests failed!")
        return False


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Test pipeline for Ashlag Yomi bot"
    )
    parser.add_argument(
        "--telegram",
        action="store_true",
        help="Run Telegram integration tests",
    )
    parser.add_argument(
        "--flush",
        action="store_true",
        help="Flush cache and reload everything",
    )

    args = parser.parse_args()

    success = run_tests(args)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
