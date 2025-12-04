# Render Deployment Checklist

Complete this checklist before deploying to Render.

## Pre-Deployment (Local)

- [ ] Clone repository: `git clone <repo-url>`
- [ ] Run setup script: `bash setup.sh`
- [ ] Create .env file with all credentials
- [ ] Test locally: `python main.py`
- [ ] Verify health endpoint: `curl http://localhost:5000/health`
- [ ] Test with sample TeraBox link
- [ ] Commit and push to GitHub main branch

## Render Setup

- [ ] Create Render account at https://render.com
- [ ] Create new Web Service
- [ ] Connect GitHub repository
- [ ] Configure service:
  - [ ] Name: `terabox-bot`
  - [ ] Runtime: Python 3.11
  - [ ] Build Command: `pip install -r requirements.txt`
  - [ ] Start Command: `gunicorn --worker-class gevent --workers 1 main:app`
  - [ ] Plan: Free

## Environment Variables on Render

Add these to Environment section in Render dashboard:

- [ ] `BOT_TOKEN` = your_bot_token
- [ ] `API_ID` = your_api_id
- [ ] `API_HASH` = your_api_hash
- [ ] `MONGODB_URI` = your_mongodb_uri
- [ ] `STORE_CHANNEL` = -1003235502239
- [ ] `ERROR_CHANNEL` = -1003332074919
- [ ] `LOG_CHANNEL` = -1003393746281
- [ ] `PORT` = 10000
- [ ] `HOST` = 0.0.0.0
- [ ] `FLASK_DEBUG` = False

## Post-Deployment (Render)

- [ ] Wait for deployment to complete
- [ ] Get service URL from dashboard
- [ ] Test health endpoint: `curl https://your-service.onrender.com/health`
- [ ] Verify root endpoint: `curl https://your-service.onrender.com/`

## Telegram Webhook Setup

- [ ] Set webhook using script or curl:
  ```bash
  python setup_webhook.py
  # OR manually:
  curl -X POST https://api.telegram.org/bot<BOT_TOKEN>/setWebhook \
    -H "Content-Type: application/json" \
    -d '{"url": "https://your-service.onrender.com/webhook", "allowed_updates": ["message"]}'
  ```

- [ ] Verify webhook: `python setup_webhook.py` (option 1)
- [ ] Check webhook info includes your Render URL

## UptimeRobot Setup (Keep Service Awake)

- [ ] Create UptimeRobot account at https://uptimerobot.com
- [ ] Add new Monitor:
  - [ ] Type: HTTP(s)
  - [ ] URL: `https://your-service.onrender.com/health`
  - [ ] Interval: 5 minutes
  - [ ] Friendly name: `TeraBox Bot`

- [ ] Verify monitor is active (green check)
- [ ] Check response times in dashboard

## Testing

- [ ] Open Telegram and find your bot
- [ ] Send `/start` command
- [ ] Bot should respond with welcome message
- [ ] Send a valid TeraBox link
- [ ] Bot should start processing
- [ ] File should be downloaded and sent back
- [ ] Check Render logs for no errors
- [ ] Verify file appears in STORE_CHANNEL

## Optional Enhancements

- [ ] Set up GitHub Actions for auto-deployment
- [ ] Configure email alerts in UptimeRobot
- [ ] Monitor MongoDB Atlas metrics
- [ ] Set up custom domain (if needed)
- [ ] Enable SSL/TLS (automatic on Render)

## Troubleshooting Checklist

If something doesn't work:

- [ ] Check Render Build Logs for compilation errors
- [ ] Check Render Logs for runtime errors
- [ ] Verify all environment variables are set
- [ ] Test health endpoint is returning 200
- [ ] Verify webhook URL is correct: `curl https://api.telegram.org/bot<BOT_TOKEN>/getWebhookInfo`
- [ ] Check MongoDB connection is working
- [ ] Send test message and check logs
- [ ] Verify UptimeRobot is pinging the service

## Documentation

- [ ] Read RENDER_DEPLOYMENT_GUIDE.md
- [ ] Bookmark UptimeRobot dashboard
- [ ] Keep Render service URL noted
- [ ] Know how to check logs in Render
- [ ] Understand free tier limitations

## Maintenance

- [ ] Monitor uptime % in UptimeRobot
- [ ] Check Render logs weekly for errors
- [ ] Update code and push (auto-deploys)
- [ ] Monitor MongoDB usage
- [ ] Keep dependencies up to date
- [ ] Test bot functionality weekly

---

**Deployment Date**: _____________
**Service URL**: https://___________
**Status**: Production / Staging

**Notes**:
_________________________________
_________________________________
_________________________________
