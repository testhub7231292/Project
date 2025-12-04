# 🚀 Bot Not Responding - Fix Guide

## Problem
Your bot is deployed successfully on Render, but it's not responding to messages because **the webhook URL is not configured**.

## Why This Happens
- The bot code is running on Render ✅
- MongoDB is connected ✅
- But Telegram doesn't know where to send messages ❌

## Quick Fix (2 Steps)

### Step 1: Find Your Render Service URL

1. Go to https://dashboard.render.com
2. Find your service **"terabox-bot"**
3. Click on it
4. Look at the top - you'll see a URL like:

```
https://terabox-bot-xxxxx.onrender.com
```

**Copy this URL** (without /webhook at the end)

### Step 2: Set the Webhook

Run this command in terminal:

```bash
python quick_webhook_setup.py
```

It will ask for your Render URL. Paste the URL from Step 1.

Example:
```
Render URL: https://terabox-bot-xxxxx.onrender.com
```

The script will automatically:
- ✅ Set your webhook
- ✅ Configure Telegram to send messages to your bot
- ✅ Verify everything is working

### That's It!

Once done, your bot will:
1. 🟢 Be live (green status on Render)
2. 📨 Receive messages from Telegram
3. 🤖 Process TeraBox links
4. 📤 Send files back to users

## Test It

In Telegram:
1. Find your bot
2. Send `/start` 
3. Send a TeraBox link like: `https://1024terabox.com/s/XXXXX`
4. Bot should download and send the file

## Troubleshooting

### "Still not working?"

Run the diagnostic:
```bash
python diagnose.py
```

It will tell you exactly what's wrong.

### Common Issues

| Error | Fix |
|-------|-----|
| "Service is initializing" | Wait 5 minutes for Render deployment |
| "Cannot reach service" | Check your Render URL is correct |
| "Webhook update failed" | Make sure BOT_TOKEN in .env is correct |
| "Service returned 502" | Check Render logs for errors |

### Check Render Logs

1. Go to https://dashboard.render.com
2. Click your "terabox-bot" service
3. Click "Logs" tab
4. Look for errors or "🎉 Bot started successfully!"

If you see errors, let me know what they are!

## Alternative: Manual Webhook Setup

If the script doesn't work, you can set it manually:

```bash
# Replace URL with your actual Render URL
curl -X POST https://api.telegram.org/bot$(grep BOT_TOKEN .env | cut -d= -f2)/setWebhook \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://terabox-bot-xxxxx.onrender.com/webhook",
    "allowed_updates": ["message"]
  }'
```

## Need Help?

1. Run: `python diagnose.py` - shows exact status
2. Check your Render URL - make sure it's https://
3. Verify BOT_TOKEN in .env is correct
4. Wait 5 minutes after first Render deployment

---

**Key Point**: Without the webhook, Telegram has no way to tell your bot about incoming messages. That's why it's not responding.

Once you set it, everything works! 🎉
