"""
TeraBox Downloader Bot - Flask Webhook Service
Telegram bot for downloading files from TeraBox
Uses Flask to receive webhook updates from Telegram
"""

import asyncio
import os
import sys
from pathlib import Path
from functools import wraps

from flask import Flask, request, jsonify
from telegram import Update
from telegram.ext import Application

from helpers.logger import get_logger
from helpers.db import db
from helpers.api_client import api_client
from helpers.downloader import downloader
from config import BOT_TOKEN, BASE_DIR, STORE_CHANNEL, ERROR_CHANNEL, LOG_CHANNEL
from plugins.start import setup_start_handlers
from plugins.handler import setup_message_handlers

logger = get_logger("terabox_bot")

# Flask app
app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False

# Global event loop for async handlers
loop = None


def async_route(f):
    """Decorator to handle async routes in Flask"""
    @wraps(f)
    def wrapped(*args, **kwargs):
        global loop
        if loop is None:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        return loop.run_until_complete(f(*args, **kwargs))
    return wrapped


class TeraBoxBot:
    """TeraBox bot with webhook support"""

    def __init__(self):
        self.tg_app = None
        self.running = False

    async def initialize(self):
        """Initialize bot components"""
        try:
            logger.info("=" * 50)
            logger.info("🚀 TeraBox Downloader Bot Starting...")
            logger.info("=" * 50)

            # Validate configuration
            if not BOT_TOKEN or BOT_TOKEN == "your_bot_token_here":
                logger.error("❌ BOT_TOKEN not configured!")
                sys.exit(1)

            # Connect to database
            logger.info("🔗 Connecting to MongoDB...")
            await db.connect()
            logger.info("✅ Connected to MongoDB")

            # Initialize API client
            logger.info("📡 Initializing API client...")
            await api_client.init_session()
            logger.info("✅ API client initialized")

            # Initialize downloader
            logger.info("⬇️ Initializing downloader...")
            await downloader.init_session()
            logger.info("✅ Downloader initialized")

            # Create telegram bot application
            logger.info("🤖 Creating Telegram bot...")
            self.tg_app = Application.builder().token(BOT_TOKEN).build()

            # Setup handlers
            logger.info("📝 Setting up handlers...")
            setup_start_handlers(self.tg_app)
            setup_message_handlers(self.tg_app)

            # Initialize application
            await self.tg_app.initialize()
            await self.tg_app.start()

            self.running = True

            logger.info("=" * 50)
            logger.info("🎉 Bot initialized successfully!")
            logger.info("=" * 50)

        except Exception as e:
            logger.error(f"❌ Failed to initialize bot: {e}", exc_info=True)
            raise

    async def process_update(self, update_data: dict) -> bool:
        """Process a Telegram update from webhook"""
        try:
            if not self.tg_app or not self.running:
                logger.warning("Bot not initialized")
                return False

            # Convert dict to Update object
            update = Update.de_json(update_data, self.tg_app.bot)
            if not update:
                logger.warning("Invalid update received")
                return False

            # Process the update
            await self.tg_app.process_update(update)
            return True

        except Exception as e:
            logger.error(f"Error processing update: {e}", exc_info=True)
            return False

    async def shutdown(self):
        """Shutdown bot gracefully"""
        logger.info("🛑 Shutting down bot...")
        self.running = False

        try:
            # Stop application
            if self.tg_app:
                await self.tg_app.stop()
                await self.tg_app.shutdown()
                logger.info("✅ Bot stopped")

            # Close API client
            await api_client.close_session()
            logger.info("✅ API client closed")

            # Close downloader
            await downloader.close_session()
            logger.info("✅ Downloader cleaned up")

            # Disconnect from database
            await db.disconnect()
            logger.info("✅ Database disconnected")

            logger.info("=" * 50)
            logger.info("✅ Bot shutdown successfully")
            logger.info("=" * 50)

        except Exception as e:
            logger.error(f"Error during shutdown: {e}", exc_info=True)


# Global bot instance
bot_instance = None


async def get_bot():
    """Get or create bot instance"""
    global bot_instance
    if bot_instance is None:
        bot_instance = TeraBoxBot()
        await bot_instance.initialize()
    return bot_instance


# ==================== Flask Routes ====================

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint for UptimeRobot"""
    try:
        if bot_instance is None or not bot_instance.running:
            return jsonify({"status": "initializing"}), 202
        return jsonify({"status": "ok", "service": "terabox-bot"}), 200
    except Exception as e:
        logger.error(f"Health check error: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route('/webhook', methods=['POST'])
@async_route
async def webhook():
    """Telegram webhook endpoint"""
    try:
        # Get the bot instance
        bot = await get_bot()

        # Get the update data
        update_data = request.get_json()
        if not update_data:
            logger.warning("Empty webhook payload")
            return jsonify({"ok": False, "error": "Empty payload"}), 400

        # Process the update
        success = await bot.process_update(update_data)

        if success:
            return jsonify({"ok": True}), 200
        else:
            return jsonify({"ok": False}), 400

    except Exception as e:
        logger.error(f"Webhook error: {e}", exc_info=True)
        return jsonify({"ok": False, "error": str(e)}), 500


@app.route('/', methods=['GET'])
def index():
    """Root endpoint"""
    return jsonify({
        "name": "TeraBox Downloader Bot",
        "status": "running" if bot_instance and bot_instance.running else "starting",
        "endpoints": {
            "webhook": "/webhook (POST)",
            "health": "/health (GET)"
        }
    }), 200


@app.errorhandler(404)
def not_found(e):
    """Handle 404 errors"""
    return jsonify({"error": "Not found"}), 404


@app.errorhandler(500)
def server_error(e):
    """Handle 500 errors"""
    logger.error(f"Server error: {e}")
    return jsonify({"error": "Internal server error"}), 500


async def init_bot():
    """Initialize bot on startup"""
    try:
        await get_bot()
    except Exception as e:
        logger.error(f"Failed to initialize bot on startup: {e}")
        raise


if __name__ == "__main__":
    try:
        # Get port from environment or default to 5000
        port = int(os.getenv("PORT", 5000))
        host = os.getenv("HOST", "0.0.0.0")
        debug = os.getenv("FLASK_DEBUG", "False").lower() == "true"

        # Initialize bot before starting Flask
        asyncio.run(init_bot())

        logger.info(f"🚀 Starting Flask server on {host}:{port}")
        app.run(host=host, port=port, debug=debug)

    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)
