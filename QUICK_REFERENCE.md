# ⚡ Quick Reference Guide

## File Structure at a Glance

```
terabox-bot/
├── 📄 main.py                    ← Bot entry point
├── 📄 config.py                  ← All settings (environment variables)
├── 📄 requirements.txt           ← Python dependencies
├── 🐳 Dockerfile                 ← Container image
├── 📄 docker-compose.yml         ← Full stack (bot + MongoDB)
├── 📋 README.md                  ← User documentation
├── 🚀 DEPLOYMENT.md              ← How to deploy everywhere
├── 🎯 HANDLER_ARCHITECTURE.md    ← Handler design details
├── .env.example                  ← Config template
├── .gitignore                    ← Git ignore file
│
├── 📁 helpers/
│   ├── api_client.py            ← TeraBox API calls
│   ├── downloader.py            ← Async file downloads
│   ├── metadata.py              ← Video metadata & thumbnails
│   ├── db.py                    ← MongoDB operations (Motor)
│   └── logger.py                ← Logging system
│
├── 📁 plugins/
│   ├── __init__.py              ← Package marker
│   ├── start.py                 ← /start /help /stats commands
│   └── handler.py               ← 🔥 UNIFIED LINK HANDLER 🔥
│
├── 📁 downloads/                ← Temp downloaded files
└── 📁 logs/                     ← Log files (bot.log)
```

---

## Environment Variables Cheat Sheet

```env
# Required
BOT_TOKEN=                      # From @BotFather
API_ID=                         # From my.telegram.org
API_HASH=                       # From my.telegram.org

# Channels (at least STORE_CHANNEL)
STORE_CHANNEL=-1001234567890    # Files storage
ERROR_CHANNEL=-1001234567891    # Error notifications
LOG_CHANNEL=-1001234567892      # Bot logs

# Database
MONGODB_URI=mongodb://localhost:27017
DATABASE_NAME=terabox_bot

# Sizes
MAX_FILE_SIZE=10485760          # 10MB in bytes
SIZE_LIMIT_USER_MB=10           # Send to user if < 10MB
SIZE_LIMIT_CHANNEL_MB=2000      # Max for channel (2GB)

# Timeouts
API_TIMEOUT=30                  # API request timeout
DOWNLOAD_TIMEOUT=3600           # Download timeout (1 hour)
FFMPEG_TIMEOUT=30               # FFmpeg timeout

# Features (all optional, default to true)
ENABLE_THUMBNAIL_GENERATION=true
ENABLE_METADATA_EXTRACTION=true
ENABLE_DATABASE_LOGGING=true
CLEANUP_DOWNLOADS=true
```

---

## Key Files & Their Purpose

### main.py
```python
# Creates Pyrogram Client
# Connects to MongoDB
# Starts the bot
# Handles graceful shutdown
```

### config.py
```python
# Single source of truth for ALL settings
# Reads from environment variables
# Provides defaults
# Used by all other modules
```

### helpers/api_client.py
```python
# Call TeraBox API: resolve_link(url)
# Returns: file_name, file_size, download_link, thumbnail
# Handles retries and timeouts
```

### helpers/downloader.py
```python
# Download files with progress tracking
# Stream to disk in chunks
# Real-time progress callbacks
# Cleanup on failure
```

### helpers/metadata.py
```python
# Extract video metadata (duration, resolution, codec)
# Generate thumbnails from video
# Uses FFprobe/FFmpeg
# Fallback to basic info if unavailable
```

### helpers/db.py
```python
# MongoDB operations
# User tracking (stats, history)
# Logging (all actions)
# Uses Motor (async driver)
```

### helpers/logger.py
```python
# Centralized logging
# File + console output
# Database integration
# Async log operations
```

### plugins/start.py
```python
# /start command → Welcome message
# /help command → Instructions
# /stats command → User statistics
```

### plugins/handler.py
```python
# 🔥 THE MAGIC FILE 🔥
# Receives ALL user messages
# Extracts links from: text, caption, forward, reply, files
# Processes links sequentially
# Manages downloads, metadata, uploads
# Handles all errors
```

---

## Bot Commands

```
/start   → Welcome message + instructions
/help    → Detailed help
/stats   → Your download statistics
```

## How Users Interact

1. **Send Link:** `https://terabox.com/s/abc123`
   → Bot downloads and sends (if <10MB) or stores

2. **Send Multiple:** Two links in one message
   → Bot processes both sequentially

3. **Send File:** Text file with links (one per line)
   → Bot extracts all and processes

4. **Forward:** Forward a message/post with link in caption
   → Bot extracts from caption

5. **Reply:** Reply to message containing link
   → Bot extracts from reply message

---

## Development Commands

```bash
# Setup
git clone <repo>
cd terabox-bot
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env

# Configure .env with your tokens/IDs

# Run
python main.py

# Stop
Ctrl+C

# View logs
tail -f logs/bot.log

# Code quality
black .                    # Format
flake8 .                   # Lint
pylint plugins/ helpers/   # Analyze
```

---

## Docker Commands

```bash
# Build
docker build -t terabox-bot .

# Run standalone
docker run -d --env-file .env -v bot_downloads:/app/downloads terabox-bot

# With MongoDB (recommended)
docker-compose up -d
docker-compose logs -f bot
docker-compose down

# Clean up
docker system prune -a
```

---

## Deployment Checklist

- [ ] Get Telegram bot token from @BotFather
- [ ] Get API_ID and API_HASH from my.telegram.org
- [ ] Create 3 channels for STORE, ERROR, LOG
- [ ] Get MongoDB connection string
- [ ] Copy .env.example to .env
- [ ] Fill in all environment variables
- [ ] Test locally: `python main.py`
- [ ] Send bot a test link
- [ ] Check logs: `tail -f logs/bot.log`
- [ ] Check database: Links should be stored
- [ ] Deploy using Docker or systemd service
- [ ] Setup monitoring/alerts
- [ ] Done! 🎉

---

## Common Issues & Fixes

| Issue | Solution |
|-------|----------|
| Bot not responding | Check BOT_TOKEN, view logs |
| API errors | Verify TeraBox link is valid |
| File too large | Increase MAX_FILE_SIZE in config |
| Download timeout | Increase DOWNLOAD_TIMEOUT |
| No metadata | Install FFmpeg: `apt install ffmpeg` |
| MongoDB error | Check MONGODB_URI, ensure MongoDB running |
| High memory | Reduce CHUNK_SIZE, increase cleanup frequency |
| Permission denied | Check file permissions, Docker user settings |

---

## API Response Example

```json
{
  "file_name": "video.mp4",
  "file_size": "250.50 MB",
  "size_bytes": 262656000,
  "download_link": "https://d8.freeterabox.com/file/...",
  "thumbnail": "https://data.1024tera.com/thumbnail/...",
  "proxy_url": "https://my-noor-queen-api.woodmirror.workers.dev/proxy?url=...",
  "status": "Successfully"
}
```

---

## Database Queries

```javascript
// Find user
db.users.findOne({ user_id: 123456789 })

// Get user stats
db.users.findOne(
  { user_id: 123456789 },
  { total_requests: 1, links_processed: 1, downloaded_count: 1 }
)

// Get user's downloaded files
db.users.aggregate([
  { $match: { user_id: 123456789 } },
  { $unwind: "$downloaded_files" },
  { $sort: { "downloaded_files.timestamp": -1 } }
])

// Get recent logs
db.logs.find({ user_id: 123456789 }).sort({ timestamp: -1 }).limit(10)

// Get errors today
db.logs.find({
  level: "ERROR",
  timestamp: { $gte: new Date(new Date().toDateString()) }
})

// User count
db.users.countDocuments()

// Total files downloaded
db.users.aggregate([
  { $group: { _id: null, total: { $sum: { $size: "$downloaded_files" } } } }
])
```

---

## Supported TeraBox Domains

```
✓ https://terabox.com/s/xxxxx
✓ https://1024terabox.com/s/xxxxx
✓ https://freeterabox.com/s/xxxxx
✓ https://teraboxapp.com/s/xxxxx
✓ https://terashare.co/s/xxxxx
✓ https://terabox.net/s/xxxxx
```

---

## Performance Targets

- API response: <2 seconds (with retries)
- Download: ~10-50 Mbps (varies)
- Metadata: <5 seconds
- Thumbnail: <2 seconds
- Total per link: 5-30 seconds (file size dependent)

---

## File Size Reference

```
10 MB   = 10,485,760 bytes (default user limit)
100 MB  = 104,857,600 bytes
1 GB    = 1,073,741,824 bytes
2 GB    = 2,147,483,648 bytes (channel max)
```

---

## Getting Help

1. **Check logs:** `tail -f logs/bot.log`
2. **Read docs:** README.md, DEPLOYMENT.md, HANDLER_ARCHITECTURE.md
3. **Test locally:** Run `python main.py` and test with link
4. **Check MongoDB:** `mongosh` and verify data
5. **Review code:** handlers are well-commented

---

## Links & Resources

- Telegram Bot API: https://core.telegram.org/bots/api
- Pyrogram Docs: https://docs.pyrogram.org
- MongoDB: https://www.mongodb.com
- FFmpeg: https://ffmpeg.org
- Motor (Async MongoDB): https://motor.readthedocs.io

---

**Bot Status: ✅ Production Ready**

Last Updated: January 2024
