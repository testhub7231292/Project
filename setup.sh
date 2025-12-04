#!/bin/bash
# Quick setup script for local testing before deployment

set -e

echo "🚀 TeraBox Bot - Local Setup Script"
echo "===================================="
echo ""

# Check Python version
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "✓ Python version: $python_version"

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate || . venv/Scripts/activate

# Install dependencies
echo "📥 Installing dependencies..."
pip install -q -r requirements.txt

# Check for .env file
if [ ! -f ".env" ]; then
    echo "⚠️  .env file not found. Creating from template..."
    cat > .env << 'EOF'
# Telegram Bot Configuration
BOT_TOKEN=your_bot_token_here
API_ID=your_api_id_here
API_HASH=your_api_hash_here

# MongoDB Configuration
MONGODB_URI=mongodb+srv://username:password@cluster0.gxhgvp4.mongodb.net/?retryWrites=true&w=majority

# Channel IDs
STORE_CHANNEL=-1003235502239
ERROR_CHANNEL=-1003332074919
LOG_CHANNEL=-1003393746281

# Server Configuration
PORT=5000
HOST=0.0.0.0
FLASK_DEBUG=False
EOF
    echo "📝 Created .env file - please update with your credentials"
else
    echo "✓ .env file found"
fi

# Create logs directory
mkdir -p logs

echo ""
echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Update .env file with your credentials"
echo "2. Run: python main.py"
echo "3. Test health endpoint: curl http://localhost:5000/health"
echo ""
echo "For production deployment on Render:"
echo "- See RENDER_DEPLOYMENT_GUIDE.md"
echo "- Push to GitHub and connect to Render"
echo "- Set environment variables in Render dashboard"
echo ""
