#!/usr/bin/env python3
"""
Setup Bot Commands for Telegram

This script configures the bot's command menu that appears when users
tap the "/" button or the menu button in Telegram.

Usage:
    python scripts/setup_bot_commands.py

Requires TELEGRAM_BOT_TOKEN environment variable or pass as argument.
"""

import json
import os
import sys
import urllib.request
import urllib.error


def setup_commands(token: str) -> bool:
    """Set up bot commands via Telegram API."""

    # Commands optimized for UX - bilingual with clear descriptions
    commands = [
        {
            "command": "start",
            "description": "הרשמה לציטוטים יומיים / Subscribe"
        },
        {
            "command": "today",
            "description": "ציטוטים של היום / Today's quotes"
        },
        {
            "command": "quote",
            "description": "ציטוט אקראי / Random quote"
        },
        {
            "command": "help",
            "description": "עזרה / Help"
        },
        {
            "command": "about",
            "description": "אודות הבוט / About"
        },
        {
            "command": "stop",
            "description": "ביטול מנוי / Unsubscribe"
        }
    ]

    url = f"https://api.telegram.org/bot{token}/setMyCommands"

    data = json.dumps({"commands": commands}).encode('utf-8')

    req = urllib.request.Request(
        url,
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST"
    )

    try:
        with urllib.request.urlopen(req, timeout=30) as response:
            result = json.loads(response.read().decode())
            if result.get("ok"):
                print("✅ Bot commands configured successfully!")
                print("\nCommands set:")
                for cmd in commands:
                    print(f"  /{cmd['command']} - {cmd['description']}")
                return True
            else:
                print(f"❌ Error: {result}")
                return False
    except urllib.error.URLError as e:
        print(f"❌ Network error: {e}")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def get_bot_info(token: str) -> dict:
    """Get bot information."""
    url = f"https://api.telegram.org/bot{token}/getMe"

    try:
        with urllib.request.urlopen(url, timeout=30) as response:
            result = json.loads(response.read().decode())
            if result.get("ok"):
                return result.get("result", {})
    except Exception as e:
        print(f"❌ Error getting bot info: {e}")
    return {}


def delete_webhook(token: str) -> bool:
    """Delete any existing webhook to enable polling mode."""
    url = f"https://api.telegram.org/bot{token}/deleteWebhook"

    try:
        with urllib.request.urlopen(url, timeout=30) as response:
            result = json.loads(response.read().decode())
            if result.get("ok"):
                print("✅ Webhook deleted (polling mode enabled)")
                return True
    except Exception as e:
        print(f"⚠️ Could not delete webhook: {e}")
    return False


def main():
    # Get token from env or argument
    token = os.environ.get("TELEGRAM_BOT_TOKEN")

    if len(sys.argv) > 1:
        token = sys.argv[1]

    if not token:
        print("❌ Please set TELEGRAM_BOT_TOKEN or pass token as argument")
        print("Usage: python setup_bot_commands.py <token>")
        sys.exit(1)

    print("🤖 Ashlag Yomi Bot Setup")
    print("=" * 40)

    # Get bot info
    bot_info = get_bot_info(token)
    if bot_info:
        print(f"✅ Connected to @{bot_info.get('username')}")
        print(f"   Name: {bot_info.get('first_name')}")

    # Delete webhook for polling
    delete_webhook(token)

    # Set up commands
    print("\n📋 Setting up commands...")
    if setup_commands(token):
        print("\n🎉 Setup complete!")
        print(f"\n👉 Open https://t.me/{bot_info.get('username', 'AshlagYomiBot')} to test")
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()
