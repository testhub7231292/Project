"""
WSGI entry point for production deployment
Used by Gunicorn when deploying to Render
"""

import asyncio
import sys
from main import app, init_bot
from helpers.logger import get_logger

logger = get_logger("terabox_bot")

# Initialize bot on WSGI startup
try:
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(init_bot())
    logger.info("✅ Bot initialized via WSGI entry point")
except Exception as e:
    logger.error(f"❌ Failed to initialize bot via WSGI: {e}")
    sys.exit(1)

if __name__ == "__main__":
    app.run()
