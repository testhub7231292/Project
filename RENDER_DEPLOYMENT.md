# Render & UptimeRobot Deployment Guide

This guide explains how to deploy the TeraBox Downloader Bot as a web service on Render with UptimeRobot monitoring.

## Why Web Service Instead of Worker?

**Worker Pros & Cons:**
- ✅ Can run indefinitely
- ✅ Polling is automatic
- ❌ Costs money (minimum $0.50/month)
- ❌ Limited free tier options

**Web Service Pros & Cons:**
- ✅ **FREE tier available on Render**
- ✅ Can process webhooks from Telegram
- ✅ UptimeRobot keeps it alive (pings /health endpoint)
- ✅ Scales horizontally with requests
- ❌ Spins down after 15 min of inactivity (UptimeRobot solves this)

## Architecture

```
Telegram User → Telegram API → Webhook POST to /webhook
                                ↓
                        Flask Web Service (Render)
                        ↓
                    Process Update → Database
                    Download File
                    Send to User
```

UptimeRobot monitors `/health` endpoint every 5 minutes, keeping the service awake.

---

## Step 1: Prepare for Deployment

### Install Dependencies Locally (Optional Testing)
```bash
pip install -r requirements.txt
```

### Test Flask Server Locally
```bash
export PORT=5000
python main.py
```

Visit `http://localhost:5000` to verify it's running.

---

## Step 2: Deploy to Render

### Create a Render Account
1. Go to [render.com](https://render.com)
2. Sign up with GitHub (recommended)
3. Create a new Web Service

### Deploy from GitHub

1. **Connect Repository**
   - Select "New" → "Web Service"
   - Connect your GitHub repository
   - Select the repo branch (usually `main`)

2. **Configure Service**
   - **Name:** `terabox-bot` (or your preference)
   - **Environment:** `Python 3.11`
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn --worker-class gevent --workers 1 main:app`
   - **Plan:** Free (or paid if you want no inactivity spindown)

### Set Environment Variables

In Render Dashboard:

1. Go to your service's "Settings"
2. Add environment variables:
   ```
   BOT_TOKEN=your_bot_token_here
   API_ID=your_api_id
   API_HASH=your_api_hash
   STORE_CHANNEL=your_store_channel_id
   ERROR_CHANNEL=your_error_channel_id
   LOG_CHANNEL=your_log_channel_id
   MONGODB_URI=your_mongodb_connection_string
   PORT=10000
   HOST=0.0.0.0
   ```

### Deploy
- Click "Create Web Service"
- Render will automatically build and deploy
- Once deployed, you'll get a URL like: `https://terabox-bot.onrender.com`

---

## Step 3: Update Telegram Webhook

After deployment, set the webhook to point to your Render service.

### Option A: Using curl

```bash
curl -X POST \
  "https://api.telegram.org/botBOT_TOKEN/setWebhook" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://terabox-bot.onrender.com/webhook",
    "allowed_updates": ["message", "callback_query"]
  }'
```

### Option B: Using Python Script

```python
import requests

BOT_TOKEN = "your_bot_token"
WEBHOOK_URL = "https://terabox-bot.onrender.com/webhook"

response = requests.post(
    f"https://api.telegram.org/bot{BOT_TOKEN}/setWebhook",
    json={
        "url": WEBHOOK_URL,
        "allowed_updates": ["message", "callback_query"]
    }
)
print(response.json())
```

### Verify Webhook
```bash
curl "https://api.telegram.org/botBOT_TOKEN/getWebhookInfo"
```

Should return:
```json
{
  "ok": true,
  "result": {
    "url": "https://terabox-bot.onrender.com/webhook",
    "has_custom_certificate": false,
    "pending_update_count": 0
  }
}
```

---

## Step 4: Set Up UptimeRobot

### Create Account
1. Go to [uptimerobot.com](https://uptimerobot.com)
2. Sign up (free account available)

### Add Monitor

1. **Click "Add New Monitor"**
   - **Monitor Type:** HTTP(s)
   - **Friendly Name:** `TeraBox Bot`
   - **URL:** `https://terabox-bot.onrender.com/health`
   - **Monitoring Interval:** 5 minutes

2. **Alert Contacts** (Optional)
   - Add email/webhook to get alerts if bot goes down
   - For telegram notifications, add custom webhook

3. **Save**

### How It Works
- UptimeRobot pings `/health` endpoint every 5 minutes
- Render free tier only spins down after 15 minutes of inactivity
- UptimeRobot's ping keeps it active
- Your bot stays alive 24/7 for free!

---

## Step 5: Monitoring & Logs

### View Logs on Render
1. Go to your service in Render dashboard
2. Click "Logs" tab
3. View real-time logs

### Manual Health Check
```bash
curl https://terabox-bot.onrender.com/health
```

Response when healthy:
```json
{
  "status": "ok",
  "service": "terabox-bot"
}
```

### Check Webhook Status
```bash
curl https://terabox-bot.onrender.com/
```

---

## Troubleshooting

### Bot Not Responding to Messages

1. **Verify Webhook is Set**
   ```bash
   curl "https://api.telegram.org/botBOT_TOKEN/getWebhookInfo"
   ```

2. **Check Logs**
   - View Render dashboard logs
   - Look for errors in `/webhook` endpoint

3. **Test Webhook Manually**
   ```bash
   curl -X POST "https://terabox-bot.onrender.com/webhook" \
     -H "Content-Type: application/json" \
     -d '{"update_id": 1, "message": {"text": "/help"}}'
   ```

### Service Spins Down

If UptimeRobot monitor is not running:
1. Verify UptimeRobot monitor is active (green checkmark)
2. Check monitoring interval (should be 5 minutes)
3. Manually ping to wake up: `curl https://terabox-bot.onrender.com/health`

### Database Connection Issues

1. Check MONGODB_URI in environment variables
2. Verify MongoDB Atlas IP whitelist includes Render IPs
3. Test connection: Check logs for "Connected to MongoDB" message

---

## Cost Analysis

| Component | Free Tier | Notes |
|-----------|-----------|-------|
| **Render Web Service** | YES | Spins down after 15min inactivity |
| **UptimeRobot** | YES | Pings every 5min (keeps alive) |
| **MongoDB Atlas** | YES | 512MB storage, up to 3 free clusters |
| **Total Cost** | $0/month | Completely free! |

**Limitations:**
- Render free tier has 750 hours/month (shared across services)
- If you run 24/7, you need paid tier ($7/month minimum)
- For free, use UptimeRobot to keep service alive within 750 hour limit

---

## API Endpoints

### GET `/`
Root endpoint - service info
```
Response: {
  "name": "TeraBox Downloader Bot",
  "status": "running|starting",
  "endpoints": {...}
}
```

### GET `/health`
Health check for UptimeRobot
```
Response: {"status": "ok", "service": "terabox-bot"}
Status: 200 OK (when healthy)
```

### POST `/webhook`
Telegram webhook receiver
```
Request: Telegram Update JSON
Response: {"ok": true} or {"ok": false}
```

---

## Migration from Polling to Webhooks

The bot automatically:
1. Initializes on first request
2. Keeps connections alive between requests
3. Processes updates via webhook
4. No polling loops - more efficient

All existing handlers and logic remain unchanged.

---

## Advanced Configuration

### Custom Webhook Secret (Optional)
```bash
# Set webhook with secret token for security
curl -X POST \
  "https://api.telegram.org/botBOT_TOKEN/setWebhook" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://terabox-bot.onrender.com/webhook",
    "secret_token": "your_secret_token_here"
  }'
```

Then validate in Flask:
```python
@app.route('/webhook', methods=['POST'])
async def webhook():
    secret = request.headers.get('X-Telegram-Bot-Api-Secret-Token')
    if secret != os.getenv('WEBHOOK_SECRET'):
        return jsonify({"ok": False}), 403
    # ... process update
```

---

## Summary

✅ **Free Deployment:**
- Render free tier web service
- UptimeRobot free monitoring
- MongoDB Atlas free tier

✅ **24/7 Uptime:**
- UptimeRobot pings /health every 5 minutes
- Keeps service alive within 750 hour/month limit

✅ **Easy Updates:**
- Push to GitHub → Auto-deploys on Render
- No downtime during updates

✅ **Cost Savings:**
- Worker: $0.50+/month minimum
- Web Service + UptimeRobot: **$0/month**
