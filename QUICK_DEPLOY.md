# Render Deployment Quick Start

## Overview

The bot has been converted from **polling** (background worker) to **webhooks** (web service). This allows free deployment on Render.

### Why?
- **Polling** = Worker service = $0.50/month minimum
- **Webhooks** = Web service = FREE on Render + UptimeRobot

## 3-Step Deployment

### Step 1: Push Code to GitHub

```bash
git add -A
git commit -m "Convert to Flask web service for Render deployment"
git push
```

### Step 2: Deploy on Render

1. Go to [render.com](https://render.com)
2. Click **"New Web Service"**
3. Connect your GitHub repo
4. Enter these settings:

| Setting | Value |
|---------|-------|
| **Name** | `terabox-bot` |
| **Environment** | Python 3.11 |
| **Build Command** | `pip install -r requirements.txt` |
| **Start Command** | `gunicorn --worker-class gevent --workers 1 main:app` |
| **Plan** | Free |

5. **Add Environment Variables** - Click "Advanced" and add:
```
BOT_TOKEN=your_token_here
API_ID=your_api_id
API_HASH=your_api_hash
STORE_CHANNEL=your_channel_id
ERROR_CHANNEL=your_error_channel_id
LOG_CHANNEL=your_log_channel_id
MONGODB_URI=your_mongodb_uri
PORT=10000
HOST=0.0.0.0
```

6. Click **"Create Web Service"**
7. Wait for deployment (shows "Live" when ready)
8. Copy your URL like `https://terabox-bot.onrender.com`

### Step 3: Update Telegram Webhook

Once Render deployment is complete:

```bash
# Replace YOUR_TOKEN and YOUR_URL
curl -X POST "https://api.telegram.org/botYOUR_TOKEN/setWebhook" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://terabox-bot.onrender.com/webhook",
    "allowed_updates": ["message", "callback_query"]
  }'
```

**Verify it worked:**
```bash
curl "https://api.telegram.org/botYOUR_TOKEN/getWebhookInfo"
```

Should show:
```json
{
  "ok": true,
  "result": {
    "url": "https://terabox-bot.onrender.com/webhook",
    "pending_update_count": 0
  }
}
```

## Keep Bot Alive with UptimeRobot

Render free tier spins down after 15 minutes of inactivity. UptimeRobot keeps it alive.

### 1. Create UptimeRobot Monitor

1. Go to [uptimerobot.com](https://uptimerobot.com)
2. Click **"Add New Monitor"**
3. Settings:
   - **Monitor Type:** HTTP(s)
   - **URL:** `https://terabox-bot.onrender.com/health`
   - **Monitoring Interval:** 5 minutes
   - **Friendly Name:** TeraBox Bot

4. Click **"Create Monitor"**

That's it! UptimeRobot will ping every 5 minutes, keeping your bot alive 24/7.

## Test the Bot

### Test Health Endpoint
```bash
curl https://your-render-url.onrender.com/health
```

Response:
```json
{"status": "ok", "service": "terabox-bot"}
```

### Test Root Endpoint
```bash
curl https://your-render-url.onrender.com/
```

Response:
```json
{
  "name": "TeraBox Downloader Bot",
  "status": "running",
  "endpoints": {
    "webhook": "/webhook (POST)",
    "health": "/health (GET)"
  }
}
```

### Test Webhook (Manual)
```bash
curl -X POST "https://your-render-url.onrender.com/webhook" \
  -H "Content-Type: application/json" \
  -d '{
    "update_id": 1,
    "message": {
      "message_id": 1,
      "date": 1234567890,
      "chat": {"id": 123, "type": "private"},
      "from": {"id": 123, "first_name": "Test"},
      "text": "/help"
    }
  }'
```

## View Logs

### On Render Dashboard
1. Go to your service
2. Click **"Logs"** tab
3. Watch real-time logs

### CLI
```bash
# View recent logs
curl https://your-render-url.onrender.com/ -s | jq .
```

## Troubleshooting

### Bot Not Responding

**Check 1: Is webhook set?**
```bash
curl "https://api.telegram.org/botTOKEN/getWebhookInfo"
```

Should show your Render URL.

**Check 2: Check Render logs**
- Go to Render dashboard
- Click "Logs"
- Look for errors

**Check 3: Is service running?**
```bash
curl https://your-render-url.onrender.com/health
```

Should return 200 OK.

### Service Spins Down

**Make sure:**
1. UptimeRobot monitor is created
2. Monitor is set to every 5 minutes
3. Monitor shows "Up" status

**Manual wake-up:**
```bash
curl https://your-render-url.onrender.com/health
```

### Database Connection Error

**Check MONGODB_URI:**
1. Go to Render dashboard
2. Settings → Environment Variables
3. Verify MONGODB_URI is correct
4. Check MongoDB Atlas IP whitelist includes Render IPs

## Cost Breakdown

| Service | Free Tier | Cost |
|---------|-----------|------|
| Render Web Service | YES | $0 |
| UptimeRobot Monitor | YES | $0 |
| MongoDB Atlas | 512MB | $0 |
| **Total** | | **$0/month** |

**Limits:**
- Render: 750 hours/month (sufficient for 24/7 with monitoring)
- UptimeRobot: 1 monitor free
- MongoDB: 3 free clusters, 512MB each

## Advanced

### Enable Debug Mode (Not Recommended for Production)
```
FLASK_DEBUG=True
FLASK_ENV=development
```

### Use Custom Webhook Secret
```bash
curl -X POST "https://api.telegram.org/botTOKEN/setWebhook" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://your-render-url.onrender.com/webhook",
    "secret_token": "your-secret-here"
  }'
```

## Need Help?

📖 **Full Documentation:** See `RENDER_DEPLOYMENT.md`

For issues:
1. Check Render logs
2. Verify webhook is set
3. Confirm UptimeRobot monitor is running
4. Check MongoDB connection
