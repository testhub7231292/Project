#!/bin/bash
# Quick deployment setup script for Render

set -e

echo "🚀 TeraBox Bot - Render Deployment Setup"
echo "=========================================="
echo ""

# Check if .env exists
if [ ! -f .env ]; then
    echo "❌ .env file not found!"
    echo "Please create .env file with required variables:"
    echo "  - BOT_TOKEN"
    echo "  - API_ID"
    echo "  - API_HASH"
    echo "  - STORE_CHANNEL"
    echo "  - ERROR_CHANNEL"
    echo "  - LOG_CHANNEL"
    echo "  - MONGODB_URI"
    echo ""
    exit 1
fi

# Test the bot locally first
echo "📝 Testing bot initialization locally..."
python3 -c "
import asyncio
from main import init_bot

try:
    asyncio.run(init_bot())
    print('✅ Bot initialized successfully!')
except Exception as e:
    print(f'❌ Bot initialization failed: {e}')
    exit(1)
"

if [ $? -ne 0 ]; then
    echo "❌ Local test failed. Fix errors before deploying."
    exit 1
fi

echo ""
echo "✅ Local test passed!"
echo ""
echo "📋 Next steps:"
echo "1. Commit and push to GitHub:"
echo "   git add -A"
echo "   git commit -m 'Convert to Flask web service for Render'"
echo "   git push"
echo ""
echo "2. Deploy to Render:"
echo "   - Go to https://dashboard.render.com"
echo "   - Create new Web Service"
echo "   - Connect your GitHub repo"
echo "   - Use these settings:"
echo "     - Build Command: pip install -r requirements.txt"
echo "     - Start Command: gunicorn --worker-class gevent --workers 1 main:app"
echo "     - Plan: Free"
echo ""
echo "3. Set environment variables in Render dashboard"
echo ""
echo "4. Update webhook after deployment:"
echo "   curl -X POST https://api.telegram.org/botBOT_TOKEN/setWebhook \\"
echo "     -H 'Content-Type: application/json' \\"
echo "     -d '{\"url\": \"https://YOUR_RENDER_URL/webhook\"}'"
echo ""
echo "5. Set up UptimeRobot monitor:"
echo "   - Monitor: https://YOUR_RENDER_URL/health"
echo "   - Interval: 5 minutes"
echo ""
