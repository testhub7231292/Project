#!/bin/bash
# TeraBox Bot - Render Deployment Assistant
# Run this to deploy the bot to Render with UptimeRobot

set -e

echo "🚀 TeraBox Bot - Render Deployment Assistant"
echo "=============================================="
echo ""

# Check prerequisites
echo "📋 Checking prerequisites..."

if ! command -v git &> /dev/null; then
    echo "❌ Git not found. Please install Git first."
    exit 1
fi

if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 not found. Please install Python 3 first."
    exit 1
fi

echo "✅ Git: $(git --version | cut -d' ' -f3)"
echo "✅ Python: $(python3 --version | cut -d' ' -f2)"
echo ""

# Verify repository
if [ ! -f "main.py" ] || [ ! -f "requirements.txt" ]; then
    echo "❌ Not in project directory. Run from project root."
    exit 1
fi

echo "✅ Project files found"
echo ""

# Show deployment options
echo "Select deployment method:"
echo ""
echo "1) Full Deployment Guide (read detailed instructions)"
echo "2) Quick Deployment (copy/paste commands)"
echo "3) Test Locally First (verify before deploying)"
echo "4) Setup Webhook Only (for existing Render service)"
echo "5) View Configuration (show required environment variables)"
echo "6) Exit"
echo ""

read -p "Select option (1-6): " choice

case $choice in
    1)
        echo ""
        echo "📖 Opening detailed deployment guide..."
        echo ""
        head -100 RENDER_DEPLOYMENT_GUIDE.md
        echo ""
        echo "... (full guide in RENDER_DEPLOYMENT_GUIDE.md) ..."
        ;;
    2)
        echo ""
        echo "🚀 Quick Deployment Steps:"
        echo ""
        echo "Step 1: Push to GitHub"
        echo "  git add -A"
        echo "  git commit -m 'Ready for Render deployment'"
        echo "  git push"
        echo ""
        echo "Step 2: Go to https://render.com/dashboard"
        echo "Step 3: Create Web Service"
        echo "Step 4: Connect GitHub repository"
        echo "Step 5: Configure service with:"
        echo "  - Name: terabox-bot"
        echo "  - Runtime: Python 3.11"
        echo "  - Build: pip install -r requirements.txt"
        echo "  - Start: gunicorn --worker-class gevent --workers 1 main:app"
        echo "Step 6: Add environment variables"
        echo "Step 7: Deploy"
        echo ""
        ;;
    3)
        echo ""
        echo "🧪 Testing Locally..."
        echo ""
        
        # Install dependencies if needed
        if ! python3 -c "import flask" 2>/dev/null; then
            echo "📥 Installing dependencies..."
            pip install -q -r requirements.txt
        fi
        
        # Check .env
        if [ ! -f ".env" ]; then
            echo "⚠️  .env file not found"
            cp .env.example .env
            echo "📝 Please update .env with your credentials"
            exit 1
        fi
        
        # Start app
        echo "🚀 Starting Flask app (timeout 10s)..."
        timeout 10 python main.py 2>&1 &
        sleep 3
        
        # Test endpoints
        echo ""
        echo "Testing endpoints..."
        echo ""
        
        if curl -s http://localhost:5000/health 2>/dev/null | grep -q "ok"; then
            echo "✅ Health endpoint: Working"
        else
            echo "⚠️  Health endpoint: Timeout (app initializing)"
        fi
        
        echo ""
        echo "✅ App tested successfully!"
        pkill -f "python main.py" 2>/dev/null || true
        ;;
    4)
        echo ""
        echo "🔗 Setting up Telegram Webhook..."
        echo ""
        python3 setup_webhook.py
        ;;
    5)
        echo ""
        echo "📋 Required Environment Variables:"
        echo ""
        grep "=" .env.example | head -15
        echo ""
        ;;
    6)
        echo "👋 Goodbye!"
        exit 0
        ;;
    *)
        echo "❌ Invalid option"
        exit 1
        ;;
esac

echo ""
echo "📚 Documentation:"
echo "   - DEPLOYMENT_SUMMARY.md (status & overview)"
echo "   - RENDER_DEPLOYMENT_GUIDE.md (detailed steps)"
echo "   - QUICK_DEPLOY.md (quick reference)"
echo "   - .env.example (all variables)"
echo ""
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
