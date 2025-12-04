#!/usr/bin/env python3
"""
Telegram Webhook Configuration Helper
Sets up and verifies webhook configuration for the bot
"""

import requests
import json
import sys
from pathlib import Path

# Load environment
env_file = Path('.env')
if env_file.exists():
    from dotenv import load_dotenv
    load_dotenv()

import os

BOT_TOKEN = os.getenv('BOT_TOKEN')
WEBHOOK_URL = os.getenv('WEBHOOK_URL', '')

TELEGRAM_API = f"https://api.telegram.org/bot{BOT_TOKEN}"


def set_webhook(webhook_url: str, allowed_updates: list = None):
    """Set the webhook URL for Telegram bot"""
    if not webhook_url:
        print("❌ Error: No webhook URL provided")
        sys.exit(1)

    if allowed_updates is None:
        allowed_updates = ["message"]

    print(f"🔗 Setting webhook to: {webhook_url}")

    data = {
        "url": webhook_url,
        "allowed_updates": allowed_updates,
        "drop_pending_updates": False
    }

    try:
        response = requests.post(f"{TELEGRAM_API}/setWebhook", json=data, timeout=10)
        result = response.json()

        if result.get("ok"):
            print("✅ Webhook set successfully!")
            return True
        else:
            print(f"❌ Error: {result.get('description', 'Unknown error')}")
            return False

    except Exception as e:
        print(f"❌ Connection error: {e}")
        return False


def get_webhook_info():
    """Get current webhook information"""
    print("📋 Fetching webhook info...")

    try:
        response = requests.get(f"{TELEGRAM_API}/getWebhookInfo", timeout=10)
        info = response.json()

        if info.get("ok"):
            webhook_info = info.get("result", {})
            print("\n📊 Webhook Information:")
            print(f"  URL: {webhook_info.get('url', 'Not set')}")
            print(f"  IP Address: {webhook_info.get('ip_address', 'N/A')}")
            print(f"  Has Custom Certificate: {webhook_info.get('has_custom_certificate', False)}")
            print(f"  Pending Update Count: {webhook_info.get('pending_update_count', 0)}")
            print(f"  Last Error Date: {webhook_info.get('last_error_date', 'None')}")
            if webhook_info.get('last_error_message'):
                print(f"  Last Error: {webhook_info.get('last_error_message')}")
            print()
            return webhook_info
        else:
            print(f"❌ Error: {info.get('description', 'Unknown error')}")
            return None

    except Exception as e:
        print(f"❌ Connection error: {e}")
        return None


def delete_webhook():
    """Delete the webhook (switch back to polling)"""
    print("🗑️  Deleting webhook...")

    data = {"drop_pending_updates": False}

    try:
        response = requests.post(f"{TELEGRAM_API}/deleteWebhook", json=data, timeout=10)
        result = response.json()

        if result.get("ok"):
            print("✅ Webhook deleted successfully")
            return True
        else:
            print(f"❌ Error: {result.get('description', 'Unknown error')}")
            return False

    except Exception as e:
        print(f"❌ Connection error: {e}")
        return False


def test_webhook():
    """Test the webhook by sending a test update"""
    print("🧪 Testing webhook...")
    print("Send a message to your bot and check the logs.")
    print("If you see the message processed, webhook is working!")


def main():
    """Main function"""
    if not BOT_TOKEN or BOT_TOKEN == "your_bot_token_here":
        print("❌ Error: BOT_TOKEN not configured in .env")
        sys.exit(1)

    print("=" * 50)
    print("🤖 Telegram Webhook Configuration Helper")
    print("=" * 50)
    print()

    # Show menu
    print("Options:")
    print("1. Get webhook info")
    print("2. Set webhook URL")
    print("3. Delete webhook (switch to polling)")
    print("4. Exit")
    print()

    choice = input("Select option (1-4): ").strip()

    if choice == "1":
        get_webhook_info()

    elif choice == "2":
        webhook = input("Enter webhook URL (e.g., https://your-domain.com/webhook): ").strip()
        if webhook:
            if set_webhook(webhook):
                print()
                get_webhook_info()
        else:
            print("❌ No URL provided")

    elif choice == "3":
        confirm = input("Are you sure? (yes/no): ").strip().lower()
        if confirm in ["yes", "y"]:
            delete_webhook()

    elif choice == "4":
        print("👋 Goodbye!")
        sys.exit(0)

    else:
        print("❌ Invalid option")
        sys.exit(1)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n⚠️  Cancelled by user")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)
