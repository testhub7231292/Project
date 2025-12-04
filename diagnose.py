#!/usr/bin/env python3
"""
Bot Deployment Diagnostic Tool
Checks if bot is properly configured and ready to receive messages
"""

import requests
import os
import sys
from pathlib import Path

# Load environment
if Path('.env').exists():
    from dotenv import load_dotenv
    load_dotenv()

BOT_TOKEN = os.getenv('BOT_TOKEN')

if not BOT_TOKEN or BOT_TOKEN == 'your_bot_token_here':
    print("❌ BOT_TOKEN not configured")
    sys.exit(1)

TELEGRAM_API = f"https://api.telegram.org/bot{BOT_TOKEN}"

print("=" * 70)
print("🔍 TeraBox Bot Deployment Diagnostic")
print("=" * 70)
print()

# 1. Check bot token
print("1️⃣  Checking bot token...")
try:
    response = requests.get(f"{TELEGRAM_API}/getMe", timeout=10)
    if response.json().get('ok'):
        bot_info = response.json().get('result', {})
        print(f"   ✅ Bot token valid")
        print(f"   Bot: @{bot_info.get('username')}")
        print(f"   ID: {bot_info.get('id')}")
    else:
        print(f"   ❌ Invalid bot token")
        sys.exit(1)
except Exception as e:
    print(f"   ❌ Error: {e}")
    sys.exit(1)

print()

# 2. Check webhook status
print("2️⃣  Checking webhook status...")
try:
    response = requests.get(f"{TELEGRAM_API}/getWebhookInfo", timeout=10)
    if response.json().get('ok'):
        webhook_info = response.json().get('result', {})
        webhook_url = webhook_info.get('url', '')
        pending = webhook_info.get('pending_update_count', 0)
        last_error = webhook_info.get('last_error_message', '')
        
        if webhook_url:
            print(f"   ✅ Webhook configured")
            print(f"   URL: {webhook_url}")
            print(f"   Pending updates: {pending}")
            if last_error:
                print(f"   ⚠️  Last error: {last_error}")
        else:
            print(f"   ❌ No webhook URL configured!")
            print()
            print("   How to fix:")
            print("   1. Get your Render URL from dashboard")
            print("   2. Run: python quick_webhook_setup.py")
            print("   3. Enter your Render URL when prompted")
            sys.exit(1)
    else:
        print(f"   ❌ Could not get webhook info")
        sys.exit(1)
except Exception as e:
    print(f"   ❌ Error: {e}")
    sys.exit(1)

print()

# 3. Check if webhook URL is accessible
if webhook_url:
    print("3️⃣  Testing webhook URL accessibility...")
    try:
        # Remove /webhook to test base URL
        base_url = webhook_url.rsplit('/webhook', 1)[0]
        response = requests.get(f"{base_url}/health", timeout=10)
        if response.status_code == 200:
            health = response.json()
            print(f"   ✅ Service is running")
            print(f"   Status: {health.get('status')}")
        else:
            print(f"   ⚠️  Service returned status {response.status_code}")
            if response.status_code == 502:
                print("   (This can happen if service is still starting)")
    except requests.exceptions.ConnectionError:
        print(f"   ⚠️  Cannot reach service (may be initializing or Render URL wrong)")
    except Exception as e:
        print(f"   ⚠️  Error: {e}")

print()

# 4. Summary
print("=" * 70)
print("📋 Summary")
print("=" * 70)
print()

if webhook_url:
    print("✅ Bot is configured and ready!")
    print()
    print("Next steps:")
    print("1. Open Telegram")
    print("2. Find your bot")
    print("3. Send /start")
    print("4. Send a TeraBox link")
    print()
    print("If still not working:")
    print("• Check Render logs for errors")
    print("• Verify MONGODB_URI is correct")
    print("• Try sending /help command")
    print("• Check if there are any Telegram API errors")
else:
    print("❌ Webhook is NOT configured")
    print()
    print("To fix:")
    print("1. Make sure you deployed to Render")
    print("2. Get your Render service URL (e.g., https://terabox-bot-xxxxx.onrender.com)")
    print("3. Run: python quick_webhook_setup.py")
    print("4. Enter your Render URL when prompted")

print()
