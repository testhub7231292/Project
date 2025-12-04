"""
Logger module for TeraBox Downloader Bot
Handles logging to file and database
"""

import logging
from pathlib import Path
from datetime import datetime
import asyncio
from typing import Optional

from config import LOGS_DIR, LOG_FILE


def get_logger(name: str = "terabox_bot") -> logging.Logger:
    """Get or create a logger instance"""
    logger = logging.getLogger(name)
    
    if not logger.handlers:
        logger.setLevel(logging.DEBUG)

        # Create logs directory if it doesn't exist
        LOGS_DIR.mkdir(exist_ok=True)

        # File handler
        fh = logging.FileHandler(LOG_FILE)
        fh.setLevel(logging.DEBUG)

        # Console handler
        ch = logging.StreamHandler()
        ch.setLevel(logging.INFO)

        # Formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        fh.setFormatter(formatter)
        ch.setFormatter(formatter)

        # Add handlers
        logger.addHandler(fh)
        logger.addHandler(ch)
    
    return logger


class BotLogger:
    """Centralized logging handler for the bot"""

    def __init__(self):
        self.logger = logging.getLogger("terabox_bot")
        self.logger.setLevel(logging.DEBUG)

        # Create logs directory if it doesn't exist
        LOGS_DIR.mkdir(exist_ok=True)

        # File handler
        fh = logging.FileHandler(LOG_FILE)
        fh.setLevel(logging.DEBUG)

        # Console handler
        ch = logging.StreamHandler()
        ch.setLevel(logging.INFO)

        # Formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        fh.setFormatter(formatter)
        ch.setFormatter(formatter)

        self.logger.addHandler(fh)
        self.logger.addHandler(ch)

        self.db = None

    def set_db(self, db):
        """Set database connection for logging"""
        self.db = db

    def info(self, message: str, **kwargs):
        """Log info message"""
        self.logger.info(message, **kwargs)

    def error(self, message: str, exc_info: bool = False, **kwargs):
        """Log error message"""
        self.logger.error(message, exc_info=exc_info, **kwargs)

    def warning(self, message: str, **kwargs):
        """Log warning message"""
        self.logger.warning(message, **kwargs)

    def debug(self, message: str, **kwargs):
        """Log debug message"""
        self.logger.debug(message, **kwargs)

    async def log_to_db(self, level: str, message: str, user_id: Optional[int] = None, **extra):
        """Log message to database"""
        if not self.db:
            return

        try:
            log_entry = {
                "timestamp": datetime.utcnow(),
                "level": level,
                "message": message,
                "user_id": user_id,
                **extra,
            }
            await self.db.insert_log(log_entry)
        except Exception as e:
            self.error(f"Failed to log to database: {e}")

    async def log_user_action(self, user_id: int, action: str, details: dict):
        """Log user action to database"""
        await self.log_to_db(
            "INFO", f"User action: {action}", user_id=user_id, action=action, details=details
        )

    async def log_error(self, error: str, user_id: Optional[int] = None, link: Optional[str] = None):
        """Log error to database"""
        await self.log_to_db("ERROR", error, user_id=user_id, link=link)


# Global logger instance (for backward compatibility if needed)
# logger = BotLogger()
