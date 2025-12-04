#!/usr/bin/env python3
"""
Quick Webhook Setup - Sets up Telegram webhook to receive bot updates
Run this after deploying to Render
"""

import requests
import sys
import os
from pathlib import Path

# Load environment
if Path('.env').exists():
    from dotenv import load_dotenv
    load_dotenv()

BOT_TOKEN = os.getenv('BOT_TOKEN')

if not BOT_TOKEN or BOT_TOKEN == 'your_bot_token_here':
    print("❌ BOT_TOKEN not configured in .env file")
    sys.exit(1)

TELEGRAM_API = f"https://api.telegram.org/bot{BOT_TOKEN}"

print("=" * 60)
print("🔗 Telegram Webhook Setup Helper")
print("=" * 60)
print()

# Get Render URL from user
print("📍 Enter your Render deployment URL:")
print("   (Find it in Render dashboard - should be like:")
print("    https://terabox-bot-xxxxx.onrender.com)")
print()

render_url = input("Render URL: ").strip()

if not render_url:
    print("❌ No URL provided")
    sys.exit(1)

# Ensure it has https
if not render_url.startswith('http'):
    render_url = 'https://' + render_url

# Remove trailing slash if present
render_url = render_url.rstrip('/')

webhook_url = f"{render_url}/webhook"

print()
print(f"📤 Setting webhook to: {webhook_url}")
print()

try:
    # Delete old webhook first
    requests.post(f"{TELEGRAM_API}/deleteWebhook")
    
    # Set new webhook
    response = requests.post(
        f"{TELEGRAM_API}/setWebhook",
        json={
            "url": webhook_url,
            "allowed_updates": ["message"],
            "drop_pending_updates": True
        },
        timeout=30
    )
    
    result = response.json()
    
    if result.get('ok'):
        print("✅ Webhook set successfully!")
        print()
        print("📋 Verifying webhook...")
        
        # Get webhook info
        info_response = requests.get(f"{TELEGRAM_API}/getWebhookInfo", timeout=10)
        info = info_response.json()
        
        if info.get('ok'):
            webhook_info = info.get('result', {})
            print()
            print("✓ Webhook URL:", webhook_info.get('url', 'Not set'))
            print("✓ Pending updates:", webhook_info.get('pending_update_count', 0))
            print("✓ Last error:", webhook_info.get('last_error_message', 'None'))
            print()
            print("✅ Webhook is ready!")
            print()
            print("Next steps:")
            print("1. Open your Telegram bot")
            print("2. Send /start")
            print("3. Send a TeraBox link")
            print("4. Bot should respond!")
        else:
            print(f"⚠️  Could not verify: {info.get('description')}")
    else:
        error = result.get('description', 'Unknown error')
        print(f"❌ Failed to set webhook: {error}")
        sys.exit(1)

except Exception as e:
    print(f"❌ Connection error: {e}")
    sys.exit(1)
