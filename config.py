"""
Configuration module for TeraBox Downloader Bot
Manages all environment variables and bot settings
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Bot Configuration
BOT_TOKEN = os.getenv("BOT_TOKEN", "your_bot_token_here")
API_ID = int(os.getenv("API_ID", "0"))
API_HASH = os.getenv("API_HASH", "your_api_hash_here")

# Database Configuration
MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
DATABASE_NAME = os.getenv("DATABASE_NAME", "terabox_bot")

# Channel Configuration
STORE_CHANNEL = int(os.getenv("STORE_CHANNEL", "0"))
ERROR_CHANNEL = int(os.getenv("ERROR_CHANNEL", "0"))
LOG_CHANNEL = int(os.getenv("LOG_CHANNEL", "0"))

# API Configuration
TERABOX_API = "https://my-noor-queen-api.woodmirror.workers.dev/api"
API_TIMEOUT = int(os.getenv("API_TIMEOUT", "30"))
MAX_RETRIES = int(os.getenv("MAX_RETRIES", "3"))

# Download Configuration
MAX_FILE_SIZE = int(os.getenv("MAX_FILE_SIZE", "10485760"))  # 10MB in bytes
DOWNLOAD_TIMEOUT = int(os.getenv("DOWNLOAD_TIMEOUT", "3600"))  # 1 hour
CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "1048576"))  # 1MB chunks

# Paths
BASE_DIR = Path(__file__).parent
DOWNLOAD_DIR = BASE_DIR / "downloads"
LOGS_DIR = BASE_DIR / "logs"
LOG_FILE = LOGS_DIR / "bot.log"

# Create necessary directories
DOWNLOAD_DIR.mkdir(exist_ok=True)
LOGS_DIR.mkdir(exist_ok=True)

# Logging Configuration
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

# Regex Patterns for TeraBox Links
TERABOX_DOMAINS = [
    r"https://(?:www\.)?terabox\.com/s/[\w-]+",
    r"https://(?:www\.)?1024terabox\.com/s/[\w-]+",
    r"https://(?:www\.)?freeterabox\.com/s/[\w-]+",
    r"https://(?:www\.)?teraboxapp\.com/s/[\w-]+",
    r"https://(?:www\.)?terashare\.co/s/[\w-]+",
    r"https://(?:www\.)?terabox\.net/s/[\w-]+",
]

# File size limits for different actions
SIZE_LIMIT_USER_MB = 10  # MB
SIZE_LIMIT_CHANNEL_MB = 2000  # MB (Telegram max is ~2GB)

# Thumbnail Configuration
THUMBNAIL_SIZE = (320, 180)
THUMBNAIL_QUALITY = 85

# Metadata Extraction
FFMPEG_TIMEOUT = int(os.getenv("FFMPEG_TIMEOUT", "30"))
EXTRACT_VIDEO_METADATA = os.getenv("EXTRACT_VIDEO_METADATA", "true").lower() == "true"

# Rate Limiting
RATE_LIMIT_ENABLED = os.getenv("RATE_LIMIT_ENABLED", "true").lower() == "true"
REQUESTS_PER_MINUTE = int(os.getenv("REQUESTS_PER_MINUTE", "20"))

# Cleanup Configuration
CLEANUP_DOWNLOADS = os.getenv("CLEANUP_DOWNLOADS", "true").lower() == "true"
KEEP_FAILED_DOWNLOADS = os.getenv("KEEP_FAILED_DOWNLOADS", "false").lower() == "true"

# Feature Flags
ENABLE_THUMBNAIL_GENERATION = os.getenv("ENABLE_THUMBNAIL_GENERATION", "true").lower() == "true"
ENABLE_METADATA_EXTRACTION = os.getenv("ENABLE_METADATA_EXTRACTION", "true").lower() == "true"
ENABLE_DATABASE_LOGGING = os.getenv("ENABLE_DATABASE_LOGGING", "true").lower() == "true"
