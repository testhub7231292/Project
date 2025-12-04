# Render Deployment Guide - TeraBox Bot Web Service

This guide provides step-by-step instructions for deploying the TeraBox Downloader Bot as a web service on Render with UptimeRobot for uptime monitoring.

## Architecture Overview

```
Telegram User
    ↓
Telegram Server
    ↓
Webhook → Render Web Service (Flask)
    ↓
Bot Processing (async handlers)
    ↓
MongoDB Atlas (Database)
    ↓
TeraBox API
    ↓
File Download & Storage
```

## Prerequisites

1. **Render Account**: Sign up at https://render.com (free tier available)
2. **MongoDB Atlas Cluster**: Already configured at cluster0.gxhgvp4.mongodb.net
3. **Telegram Bot Token**: Already created and configured
4. **UptimeRobot Account** (optional): Sign up at https://uptimerobot.com for free uptime monitoring
5. **GitHub Account**: For deploying from repository

## Step 1: Prepare Environment Variables

Before deploying, gather all required environment variables:

```env
# Telegram Bot
BOT_TOKEN=<your_bot_token>
API_ID=<your_api_id>
API_HASH=<your_api_hash>

# Database
MONGODB_URI=mongodb+srv://username:password@cluster0.gxhgvp4.mongodb.net/?retryWrites=true&w=majority

# Channels
STORE_CHANNEL=-1003235502239
ERROR_CHANNEL=-1003332074919
LOG_CHANNEL=-1003393746281

# Deployment
PORT=10000
HOST=0.0.0.0
FLASK_DEBUG=False
```

## Step 2: Deploy on Render

### Option A: One-Click Deploy (Recommended)

1. Push your code to GitHub (main branch)
2. Go to https://render.com/dashboard
3. Click "Create +" → "Web Service"
4. Select "Build and deploy from a Git repository"
5. Connect your GitHub account and select the `Project` repository
6. Configure the service:
   - **Name**: `terabox-bot`
   - **Environment**: `Python 3.11`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn --worker-class gevent --workers 1 main:app`
   - **Plan**: Free (or higher if needed)

### Option B: Manual Configuration

1. Go to Render Dashboard
2. Click "New +" → "Web Service"
3. Fill in the form:
   - Name: `terabox-bot`
   - Runtime: `Python 3.11`
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `gunicorn --worker-class gevent --workers 1 main:app`
   - Plan: Free

## Step 3: Set Environment Variables on Render

1. In your Render service dashboard, click "Environment"
2. Add each variable from the prerequisites:

```
BOT_TOKEN = <your_token>
API_ID = <your_api_id>
API_HASH = <your_api_hash>
MONGODB_URI = <your_mongodb_uri>
STORE_CHANNEL = -1003235502239
ERROR_CHANNEL = -1003332074919
LOG_CHANNEL = -1003393746281
PORT = 10000
HOST = 0.0.0.0
FLASK_DEBUG = False
```

3. Click "Deploy" to apply changes

## Step 4: Get Your Webhook URL

Once deployed, Render will provide your service URL. Copy it:

```
https://terabox-bot-xxxxx.onrender.com
```

Your webhook URL will be:
```
https://terabox-bot-xxxxx.onrender.com/webhook
```

## Step 5: Set Telegram Webhook

Set up the Telegram webhook to point to your Render service:

```bash
curl -X POST https://api.telegram.org/bot<YOUR_BOT_TOKEN>/setWebhook \
  -H "Content-Type: application/json" \
  -d '{"url": "https://terabox-bot-xxxxx.onrender.com/webhook", "allowed_updates": ["message"]}'
```

Or use Python:

```python
import requests

bot_token = "YOUR_BOT_TOKEN"
webhook_url = "https://terabox-bot-xxxxx.onrender.com/webhook"

response = requests.post(
    f"https://api.telegram.org/bot{bot_token}/setWebhook",
    json={"url": webhook_url, "allowed_updates": ["message"]}
)
print(response.json())
```

Verify the webhook:

```bash
curl https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getWebhookInfo
```

## Step 6: Test the Service

1. **Health Check**:
   ```bash
   curl https://terabox-bot-xxxxx.onrender.com/health
   ```

2. **Root Endpoint**:
   ```bash
   curl https://terabox-bot-xxxxx.onrender.com/
   ```

3. **Send a Test Message**:
   - Open your Telegram bot
   - Send `/start`
   - Send a TeraBox link like `https://1024terabox.com/s/XXXXX`
   - Bot should process and download the file

## Step 7: Set Up UptimeRobot (Optional)

UptimeRobot ensures your bot stays awake on Render's free tier.

1. Go to https://uptimerobot.com
2. Sign up for free account
3. Click "Add Monitor"
4. Configure:
   - **Monitor Type**: HTTP(s)
   - **Friendly Name**: `TeraBox Bot`
   - **URL**: `https://terabox-bot-xxxxx.onrender.com/health`
   - **Monitoring Interval**: 5 minutes (default)
5. Click "Create Monitor"

This will ping your health endpoint every 5 minutes, keeping the service active.

## Endpoints

Your web service exposes these endpoints:

| Endpoint | Method | Purpose | Response |
|----------|--------|---------|----------|
| `/` | GET | Root/status | Service info |
| `/health` | GET | Health check (for UptimeRobot) | `{"status": "ok"}` |
| `/webhook` | POST | Telegram updates | Processes messages |

## Monitoring & Logs

1. **View Logs**: In Render dashboard → Logs tab
2. **Monitor Activity**: Check `/logs/bot.log` file
3. **Check Status**: UptimeRobot dashboard shows uptime %

## Troubleshooting

### "Service won't start"
- Check Build Logs for errors
- Verify all environment variables are set
- Ensure `requirements.txt` has all dependencies

### "Webhook not receiving updates"
- Verify webhook URL with `getWebhookInfo` API call
- Check Render logs for errors
- Ensure bot token is correct
- Test health endpoint: `curl https://terabox-bot-xxxxx.onrender.com/health`

### "MongoDB connection fails"
- Verify `MONGODB_URI` in environment variables
- Check MongoDB Atlas IP whitelist (should allow all: 0.0.0.0/0)
- Test connection from local machine first

### "Files not downloading"
- Check error logs in Render dashboard
- Verify TeraBox links are valid
- Check storage channel ID is correct

### "UptimeRobot not triggering"
- Verify webhook URL in UptimeRobot
- Check if health endpoint returns status 200
- Monitor response times in UptimeRobot dashboard

## Performance Tips

1. **Free Tier Limits**:
   - CPU: Shared
   - RAM: 512 MB
   - Idle timeout: Services spin down after 15 minutes of inactivity
   - UptimeRobot keeps it active with pings

2. **Optimization**:
   - Use async/await for all I/O operations
   - Limit concurrent downloads (already implemented)
   - Set reasonable file size limits
   - Clean up old logs periodically

3. **Scaling**:
   - If you hit limits, upgrade to Pro tier ($7/month)
   - Add more workers: `gunicorn --worker-class gevent --workers 2 main:app`
   - Consider using PostgreSQL instead of MongoDB for better performance

## Updating the Bot

To update the bot code:

1. Make changes locally
2. Commit and push to GitHub main branch
3. Render will auto-redeploy (if connected to GitHub)
4. Or manually trigger deploy in Render dashboard

## Migration from Polling to Webhook

**What changed**:
- ✅ **Before**: Bot ran 24/7 in polling mode, consumed resources
- ✅ **Now**: Web service receives webhook updates, minimal resource usage
- ✅ **Benefit**: Can run free on Render with UptimeRobot pings

**No client-side changes needed** - bot works the same way!

## Cost Analysis

| Component | Cost |
|-----------|------|
| Render Web Service | FREE (5000 hours/month free tier) |
| MongoDB Atlas | FREE (512MB free tier) |
| UptimeRobot | FREE (5 monitors free) |
| **Total** | **FREE** |

## Support

For issues:
1. Check Render logs
2. Check MongoDB Atlas metrics
3. Verify Telegram API with `getWebhookInfo`
4. Test health endpoint directly
5. Review code for exceptions in logs

---

**Last Updated**: December 4, 2025
**Service Type**: Flask Web Service (Webhook-based)
**Deployment Platform**: Render
**Monitoring**: UptimeRobot
