"""
Unified handler plugin for TeraBox Downloader Bot
Handles single/multiple links, captions, forwarded messages, and text files
"""

import re
from pathlib import Path
from typing import Set
from datetime import datetime

from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes

from helpers.logger import get_logger
from helpers.db import db

logger = get_logger("terabox_bot")

# TeraBox link patterns - matches word chars, hyphens, and underscores in share IDs
TERABOX_PATTERNS = [
    r"https?://(?:www\.)?terabox\.com/s/[\w\-_]+",
    r"https?://(?:www\.)?1024terabox\.com/s/[\w\-_]+",
    r"https?://(?:www\.)?freeterabox\.com/s/[\w\-_]+",
    r"https?://(?:www\.)?teraboxapp\.com/s/[\w\-_]+",
    r"https?://(?:www\.)?terashare\.co/s/[\w\-_]+",
]


async def extract_terabox_links(text: str) -> Set[str]:
    """
    Extract TeraBox links from text

    Args:
        text: Text to extract links from

    Returns:
        Set of unique TeraBox links
    """
    if not text:
        return set()

    links = set()
    for pattern in TERABOX_PATTERNS:
        matches = re.findall(pattern, text, re.IGNORECASE)
        links.update(matches)

    return links



async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle incoming messages with TeraBox links"""
    from helpers.api_client import api_client
    from helpers.downloader import downloader
    
    try:
        user_id = update.effective_user.id
        
        # Ensure user exists
        user = await db.get_user(user_id)
        if not user:
            await db.create_user(
                user_id,
                update.effective_user.first_name or "User",
                update.effective_user.last_name or ""
            )
        
        # Update activity
        await db.update_user(user_id, last_active_now=True)
        
        # Extract links from message
        text = update.message.text or update.message.caption or ""
        links = await extract_terabox_links(text)
        
        if not links:
            await update.message.reply_text(
                "❌ **No TeraBox links found**\n\n"
                "Send me TeraBox links to download files.\n"
                "Use /help for more information.",
                parse_mode="Markdown"
            )
            return
        
        # Send processing message
        status_msg = await update.message.reply_text(
            f"🔄 Processing {len(links)} link(s)...",
            parse_mode="Markdown"
        )
        
        # Log action
        logger.info(f"User {user_id} processing {len(links)} links: {links}")
        
        # Process each link
        successful = 0
        for idx, link in enumerate(links, 1):
            try:
                await status_msg.edit_text(
                    f"🔍 Step {idx}/{len(links)}: Resolving...\n`{link}`",
                    parse_mode="Markdown"
                )
                
                logger.info(f"Resolving link: {link}")
                
                # Resolve link
                file_info = await api_client.resolve_link(link)
                
                if not file_info:
                    logger.error(f"Failed to resolve: {link}")
                    
                    # Send failed link to ERROR_CHANNEL
                    from config import ERROR_CHANNEL
                    if ERROR_CHANNEL and ERROR_CHANNEL != 0:
                        try:
                            await context.bot.send_message(
                                chat_id=ERROR_CHANNEL,
                                text=f"❌ **Failed to Resolve Link**\n\n"
                                     f"Link: `{link}`\n"
                                     f"User: {update.effective_user.first_name}\n"
                                     f"Status: Resolution Failed",
                                parse_mode="Markdown"
                            )
                        except Exception as e:
                            logger.error(f"Failed to send error to channel: {e}")
                    
                    await status_msg.edit_text(
                        f"❌ Link {idx}/{len(links)}: Failed to resolve",
                        parse_mode="Markdown"
                    )
                    continue
                
                file_name = file_info.get("file_name", "file")
                file_size = file_info.get("file_size", "Unknown")
                download_url = file_info.get("download_link", "")
                
                logger.info(f"File info: {file_name} ({file_size}), URL: {download_url}")
                
                if not download_url:
                    logger.error(f"No download URL in response: {file_info}")
                    
                    # Send error to ERROR_CHANNEL
                    from config import ERROR_CHANNEL
                    if ERROR_CHANNEL and ERROR_CHANNEL != 0:
                        try:
                            await context.bot.send_message(
                                chat_id=ERROR_CHANNEL,
                                text=f"❌ **No Download URL**\n\n"
                                     f"Link: `{link}`\n"
                                     f"User: {update.effective_user.first_name}\n"
                                     f"Error: API returned no download link",
                                parse_mode="Markdown"
                            )
                        except Exception as e:
                            logger.error(f"Failed to send error to channel: {e}")
                    
                    await status_msg.edit_text(
                        f"❌ Link {idx}/{len(links)}: No download URL",
                        parse_mode="Markdown"
                    )
                    continue
                
                # Update status: Downloading
                await status_msg.edit_text(
                    f"⬇️ Link {idx}/{len(links)}: Downloading {file_name}...",
                    parse_mode="Markdown"
                )
                
                logger.info(f"Starting download from: {download_url}")
                
                # Download file
                file_path = await downloader.download(download_url, file_name)
                
                if not file_path:
                    logger.error(f"Download failed: {file_name}")
                    
                    # Send error to ERROR_CHANNEL
                    from config import ERROR_CHANNEL
                    if ERROR_CHANNEL and ERROR_CHANNEL != 0:
                        try:
                            await context.bot.send_message(
                                chat_id=ERROR_CHANNEL,
                                text=f"❌ **Download Failed**\n\n"
                                     f"File: {file_name}\n"
                                     f"Link: `{link}`\n"
                                     f"User: {update.effective_user.first_name}",
                                parse_mode="Markdown"
                            )
                        except Exception as e:
                            logger.error(f"Failed to send error to channel: {e}")
                    
                    await status_msg.edit_text(
                        f"❌ Link {idx}/{len(links)}: Download failed",
                        parse_mode="Markdown"
                    )
                    continue
                
                logger.info(f"Downloaded successfully: {file_path}")
                
                # Send file to user as video
                try:
                    await update.message.reply_video(
                        video=open(file_path, "rb"),
                        caption=f"📥 **{file_name}**\n💾 Size: {file_size}",
                        parse_mode="Markdown",
                        supports_streaming=True
                    )
                except Exception as e:
                    logger.warning(f"Failed to send as video, trying as document: {e}")
                    # Fallback to document if video fails
                    await update.message.reply_document(
                        document=open(file_path, "rb"),
                        caption=f"📥 **{file_name}**\n💾 Size: {file_size}",
                        parse_mode="Markdown"
                    )
                
                # Send to storage channel
                from config import STORE_CHANNEL
                if STORE_CHANNEL and STORE_CHANNEL != 0:
                    try:
                        with open(file_path, "rb") as video_file:
                            await context.bot.send_video(
                                chat_id=STORE_CHANNEL,
                                video=video_file,
                                caption=f"📥 **{file_name}**\n💾 Size: {file_size}\n👤 User: {update.effective_user.first_name}",
                                parse_mode="Markdown",
                                supports_streaming=True
                            )
                        logger.info(f"Sent to storage channel: {file_name}")
                    except Exception as e:
                        logger.error(f"Failed to send to storage channel: {e}")
                
                # Update status
                await status_msg.edit_text(
                    f"✅ Link {idx}/{len(links)}: {file_name} sent!",
                    parse_mode="Markdown"
                )
                
                successful += 1
                logger.info(f"Successfully processed: {file_name}")
                
            except Exception as e:
                logger.error(f"Error processing link {idx}: {e}", exc_info=True)
                await status_msg.edit_text(
                    f"❌ Link {idx}/{len(links)}: Error - {str(e)[:50]}",
                    parse_mode="Markdown"
                )
                continue
        
        # Final summary
        await status_msg.edit_text(
            f"✅ Complete: {successful}/{len(links)} successful",
            parse_mode="Markdown"
        )
        
    except Exception as e:
        logger.error(f"Error in message handler: {e}", exc_info=True)
        await update.message.reply_text(f"❌ Error: {str(e)[:100]}")


def setup_message_handlers(app: Application):
    """Setup message handlers"""
    handler = MessageHandler(
        filters.TEXT | filters.CAPTION,
        handle_message
    )
    app.add_handler(handler)
    logger.info("✅ Message handlers registered")
