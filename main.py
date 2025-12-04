"""
TeraBox Downloader Bot - Main Entry Point
Telegram bot for downloading files from TeraBox
"""

import asyncio
import signal
import sys
from pathlib import Path

from telegram import Update
from telegram.ext import Application, CallbackContext

from helpers.logger import get_logger
from helpers.db import db
from helpers.api_client import api_client
from helpers.downloader import downloader
from config import BOT_TOKEN, BASE_DIR, STORE_CHANNEL, ERROR_CHANNEL, LOG_CHANNEL
from plugins.start import setup_start_handlers
from plugins.handler import setup_message_handlers

logger = get_logger("terabox_bot")


class TeraBoxBot:
    """Main bot class"""

    def __init__(self):
        self.app = None
        self.running = False

    async def start(self):
        """Start the bot"""
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
            self.app = Application.builder().token(BOT_TOKEN).build()

            # Setup handlers
            logger.info("📝 Setting up handlers...")
            setup_start_handlers(self.app)
            setup_message_handlers(self.app)

            self.running = True

            # Initialize and start the application
            logger.info("✅ Starting bot polling...")
            await self.app.initialize()
            await self.app.start()
            await self.app.updater.start_polling(allowed_updates=Update.ALL_TYPES)

            logger.info("=" * 50)
            logger.info("🎉 Bot started successfully!")
            logger.info("=" * 50)

            # Keep running
            await asyncio.Event().wait()

        except Exception as e:
            logger.error(f"❌ Failed to start bot: {e}", exc_info=True)
            await self.stop()
            sys.exit(1)

    async def stop(self):
        """Stop the bot gracefully"""
        logger.info("🛑 Shutting down bot...")
        self.running = False

        try:
            # Stop application
            if self.app:
                await self.app.stop()
                await self.app.shutdown()
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
            logger.info("✅ Bot stopped successfully")
            logger.info("=" * 50)

        except Exception as e:
            logger.error(f"Error during shutdown: {e}", exc_info=True)

    async def _idle(self):
        """Keep bot running until interrupted"""
        try:
            await asyncio.Event().wait()
        except KeyboardInterrupt:
            logger.info("Received interrupt signal")
        except Exception as e:
            logger.error(f"Unexpected error in idle loop: {e}")


def signal_handler(signum, frame):
    """Handle system signals"""
    logger.info(f"Received signal {signum}")


async def main():
    """Main entry point"""
    bot = TeraBoxBot()

    # Setup signal handlers
    signal.signal(signal.SIGINT, lambda s, f: None)
    signal.signal(signal.SIGTERM, lambda s, f: None)

    try:
        await bot.start()
    except KeyboardInterrupt:
        logger.info("Keyboard interrupt received")
        await bot.stop()
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        await bot.stop()
        sys.exit(1)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Fatal error in main: {e}", exc_info=True)
        sys.exit(1)
