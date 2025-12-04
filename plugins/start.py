"""
Start command plugin for TeraBox Downloader Bot
"""

from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

from helpers.logger import get_logger
from helpers.db import db

logger = get_logger("terabox_bot")


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command"""
    try:
        user_id = update.effective_user.id
        first_name = update.effective_user.first_name or "User"
        last_name = update.effective_user.last_name or ""

        # Get or create user
        user = await db.get_user(user_id)
        if not user:
            await db.create_user(user_id, first_name, last_name)
        else:
            await db.update_user(user_id, last_active_now=True)

        logger.info(f"User {user_id} executed /start command")

        welcome_text = f"""
🎉 **Welcome to TeraBox Downloader Bot!**

Hi {first_name}! 👋

I can help you download files from TeraBox links. Here's what I can do:

📥 **Features:**
• Download files from TeraBox links
• Extract multiple links from messages
• Process bulk links automatically
• Extract links from captions and forwarded messages
• Real-time download progress
• Auto-upload to storage channel

🔗 **Supported Link Formats:**
• https://terabox.com/s/xxxxx
• https://1024terabox.com/s/xxxxx
• https://freeterabox.com/s/xxxxx
• Other TeraBox mirrors

📝 **How to Use:**
1. Send a TeraBox link → Bot downloads it
2. Bot processes and uploads to storage
3. You get the file!

⚙️ **Available Commands:**
/start - Show this message
/help - Get detailed help
/stats - View your statistics

👤 **Privacy:**
• No data tracking
• Links processed locally
• Files temporarily stored

Made with ❤️ for TeraBox lovers!
"""
        await update.message.reply_text(welcome_text, parse_mode="Markdown")

    except Exception as e:
        logger.error(f"Error in start_command: {e}", exc_info=True)
        await update.message.reply_text("❌ An error occurred. Please try again.")


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /help command"""
    try:
        help_text = """
📚 **Help & Documentation**

**Basic Usage:**
1. Send any TeraBox link
2. Bot automatically downloads
3. Files are processed and uploaded

**Supported Commands:**
/start - Welcome message
/help - This help message
/stats - Your usage statistics

**Extracting Links:**
The bot can extract TeraBox links from:
• Plain text messages
• Captions on photos/videos
• Forwarded messages
• Reply messages

**Multiple Links:**
Send multiple links in one message, separated by spaces or newlines. The bot will process all of them!

**Tips:**
• Shorter links work better
• Check your link is valid
• Large files take time to process
• Downloads are kept for 24 hours

**Troubleshooting:**
• Link invalid? Check if it's correct
• Download failed? Try again in 5 minutes
• Need help? Contact support

**Storage:**
Files are stored temporarily in a private channel for security and easy access.

For more information or support, contact @your_support_handle
"""
        await update.message.reply_text(help_text, parse_mode="Markdown")

    except Exception as e:
        logger.error(f"Error in help_command: {e}", exc_info=True)
        await update.message.reply_text("❌ An error occurred. Please try again.")


async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /stats command"""
    try:
        user_id = update.effective_user.id
        user = await db.get_user(user_id)

        if not user:
            stats_text = "📊 **Your Statistics**\n\nNo downloads yet. Send a TeraBox link to get started!"
        else:
            downloads = user.get("downloads", 0)
            total_size = user.get("total_downloaded", 0)
            created_at = user.get("created_at", "Unknown")

            # Format size
            if total_size > 1024**3:
                size_str = f"{total_size / (1024**3):.2f} GB"
            elif total_size > 1024**2:
                size_str = f"{total_size / (1024**2):.2f} MB"
            else:
                size_str = f"{total_size / 1024:.2f} KB"

            stats_text = f"""
📊 **Your Statistics**

👤 User ID: `{user_id}`
📥 Total Downloads: {downloads}
💾 Total Size Downloaded: {size_str}
📅 Account Created: {created_at}
⏰ Last Active: {user.get('last_active', 'Unknown')}

Keep downloading! 🎉
"""

        await update.message.reply_text(stats_text, parse_mode="Markdown")

    except Exception as e:
        logger.error(f"Error in stats_command: {e}", exc_info=True)
        await update.message.reply_text("❌ An error occurred. Please try again.")


def setup_start_handlers(app: Application):
    """Setup start command handlers"""
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("stats", stats_command))
    logger.info("✅ Start handlers registered")
