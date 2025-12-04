# 🎯 Bot Handler Architecture

## The Unified Handler Concept

The **entire link processing logic** is contained in a single file: `plugins/handler.py`

This single handler automatically:
- ✅ Extracts links from messages, captions, forwarded posts, replies, and text files
- ✅ Deduplicates links
- ✅ Processes them sequentially with real-time progress
- ✅ Handles all error cases gracefully

### No Circular Imports Pattern

```
main.py
├── creates Pyrogram Client
└── imports plugins/ (AFTER client creation)
    ├── plugins/start.py
    │   └── imports from helpers/ (safe)
    │       ├── helpers/logger.py
    │       └── helpers/db.py
    │
    └── plugins/handler.py
        └── imports from helpers/ (safe)
            ├── helpers/api_client.py
            ├── helpers/downloader.py
            ├── helpers/metadata.py
            ├── helpers/db.py
            └── helpers/logger.py

KEY RULE: helpers/* do NOT import from plugins/*
```

---

## Unified Handler Flow

### Input Processing
```python
# Handler receives ANY message type:
@Client.on_message(filters.private & ~filters.command(...))
async def unified_handler(client: Client, message: Message):
    
    # Collect links from all possible sources
    all_links = set()
    
    # 1. Direct message text
    if message.text:
        all_links.update(extract_terabox_links(message.text))
    
    # 2. Caption (forwarded posts, photos, etc.)
    if message.caption:
        all_links.update(extract_terabox_links(message.caption))
    
    # 3. Forwarded message content
    if message.forward_from_chat:
        all_links.update(extract_terabox_links(message.text))
    
    # 4. Reply message
    if message.reply_to_message:
        all_links.update(extract_terabox_links(message.reply_to_message.text))
        all_links.update(extract_terabox_links(message.reply_to_message.caption))
    
    # 5. Attached text file
    if message.document and message.document.file_name.endswith('.txt'):
        file_content = await client.download_media(message)
        all_links.update(extract_terabox_links(file_content))
    
    # Deduplicate
    all_links = set(filter(None, all_links))
```

### Sequential Processing
```python
# Process each link one by one with progress
for index, link in enumerate(all_links, 1):
    success = await process_single_link(
        client, message, link,
        status_msg,
        link_index=index,
        total_links=len(all_links)
    )
```

### Per-Link Processing
```python
async def process_single_link(...):
    # 1. Update status: "Resolving..."
    await status_msg.edit_text(f"[{index}/{total}] 🔍 Resolving link...")
    
    # 2. Call TeraBox API
    file_info = await api_client.resolve_link(link)
    
    # 3. Validate file info
    if not file_info:
        # Log to ERROR_CHANNEL
        # Log to database
        # Update status: "❌ Failed"
        return False
    
    # 4. Download with progress callback
    file_path = await downloader.download(
        url=file_info['download_link'],
        file_name=file_info['file_name'],
        progress_callback=progress_callback  # Real-time updates
    )
    
    # 5. Extract metadata
    metadata = await metadata_extractor.extract_metadata(file_path)
    
    # 6. Generate thumbnail
    thumbnail = await metadata_extractor.generate_thumbnail(file_path)
    
    # 7. Upload to STORE_CHANNEL
    await client.send_document(
        STORE_CHANNEL,
        file_path,
        thumb=thumbnail,
        caption=format_caption(metadata, link)
    )
    
    # 8. If file < 10MB, also send to user
    if file_size_mb < 10:
        await message.reply_document(file_path)
    
    # 9. Log to database
    await db.add_downloaded_file(user_id, file_info)
    
    # 10. Cleanup
    file_path.unlink()
    
    return True
```

---

## Handler Features Matrix

| Feature | Implementation | Location |
|---------|-----------------|----------|
| **Link Extraction** | Regex matching 6 TBox domains | `extract_terabox_links()` |
| **Multiple Formats** | Text, caption, forward, reply, file | Covered in input processing |
| **Deduplication** | `set()` data structure | Input collection phase |
| **Sequential Processing** | `for` loop with `index` | Main handler loop |
| **Progress Updates** | Async status message edits | `process_single_link()` callback |
| **Real-time Download %** | Progress callback every 2s | Download streaming |
| **Size Validation** | Check file_size vs limits | Before download |
| **API Resolution** | HTTP GET to TBox resolver | `api_client.resolve_link()` |
| **Metadata Extraction** | FFprobe parsing | `metadata_extractor.extract_metadata()` |
| **Thumbnail Generation** | FFmpeg frame extraction | `metadata_extractor.generate_thumbnail()` |
| **Storage Upload** | Send to STORE_CHANNEL | `client.send_document()` |
| **User Delivery** | Conditional (size < 10MB) | Check `user_size_mb < 10` |
| **Error Logging** | To ERROR_CHANNEL + MongoDB | `logger.log_error()` |
| **User Tracking** | Stats in MongoDB | `db.add_downloaded_file()` |
| **Cleanup** | Delete temp files | File cleanup section |

---

## Configuration Examples

### Process Single Link
```
User: https://terabox.com/s/abc123
Bot:
[1/1] 🔍 Resolving link...
[1/1] ⬇️ Downloading: video.mp4
[1/1] 100% (100MB / 100MB)
[1/1] 📊 Extracting metadata...
[1/1] ✅ Complete: video.mp4
→ File uploaded to STORE_CHANNEL (too large for user)
```

### Process Multiple Links
```
User: 
link1: https://terabox.com/s/abc
link2: https://1024terabox.com/s/xyz
link3: https://freeterabox.com/s/def

Bot:
[1/3] 🔍 Resolving...
[1/3] ✅ Complete: file1.pdf (8MB)
→ Sent to user (under 10MB limit)

[2/3] 🔍 Resolving...
[2/3] ✅ Complete: file2.mp4 (500MB)
→ Uploaded to STORE_CHANNEL only (over limit)

[3/3] 🔍 Resolving...
[3/3] ✅ Complete: file3.zip (100MB)
→ Uploaded to STORE_CHANNEL only (over limit)

✅ Complete | 3/3 successful
```

### Extract from Text File
```
User: [sends document.txt]
Content of file:
https://terabox.com/s/link1
https://terabox.com/s/link2
https://terabox.com/s/link3

Bot:
✅ Extracted 3 links from file
[1/3] Processing...
[2/3] Processing...
[3/3] Processing...
✅ Complete | 3/3 successful
```

### Extract from Caption
```
User: [forwards message with caption]
Caption: "Check this video: https://terabox.com/s/movie123"

Bot:
✅ Extracted 1 link from caption
[1/1] 🔍 Resolving...
[1/1] ✅ Complete: movie.mp4

✅ Complete | 1/1 successful
```

---

## Error Handling

### If API Resolution Fails
```
→ Log error to ERROR_CHANNEL
→ Log to MongoDB
→ Update user: "❌ Failed to resolve"
→ Skip to next link
```

### If Download Fails
```
→ Log error to ERROR_CHANNEL with file details
→ Clean up partial file
→ Log to MongoDB
→ Update user: "❌ Download failed"
→ Skip to next link
```

### If Upload to Channel Fails
```
→ Log error to ERROR_CHANNEL
→ Clean up local file
→ Still try to send to user if eligible
→ Update user: "⚠️ Storage failed but sending to you"
```

### If File Too Large
```
→ Log warning to ERROR_CHANNEL
→ Notify user: "❌ File too large (5GB)"
→ Skip to next link
```

---

## Database Operations

Every action logs to MongoDB:

### Users Collection
```javascript
{
  user_id: 123456,
  total_requests: 42,
  links_processed: 128,
  downloaded_files: [
    { file_name: "video.mp4", size_bytes: 100000000, timestamp: ... },
    { file_name: "doc.pdf", size_bytes: 5000000, timestamp: ... }
  ]
}
```

### Logs Collection
```javascript
{
  timestamp: ISODate(),
  level: "INFO",
  message: "User action: process_links",
  user_id: 123456,
  action: "process_links",
  details: {
    link_count: 2,
    links: ["https://terabox.com/s/abc", "https://1024terabox.com/s/xyz"],
    successful: 1,
    failed: 1
  }
}
```

---

## Key Design Principles

1. **Single Responsibility** - Handler only handles user messages
2. **Clean Separation** - Helpers are independent modules
3. **No Circular Dependencies** - Plugins → Helpers (one direction)
4. **Graceful Degradation** - Missing ffmpeg? Still downloads (no thumbnails)
5. **Atomic Operations** - Each link processed independently
6. **User Feedback** - Real-time status updates
7. **Complete Logging** - Every action tracked for debugging

---

## Performance Characteristics

- **Link Extraction**: <100ms for 100 links
- **API Resolution**: 1-3 seconds per link (with retries)
- **Download**: Depends on file size and speed
- **Metadata Extraction**: <5 seconds per file
- **Thumbnail Generation**: <2 seconds per video
- **Total Time for 1 link**: ~5-30 seconds (varies by file size)

---

## Testing the Handler

```bash
# 1. Start bot
python main.py

# 2. Send bot a message with link
# 3. Watch real-time status updates
# 4. Check logs
tail -f logs/bot.log

# 5. Check database
mongosh
> db.users.findOne({user_id: YOUR_USER_ID})
> db.logs.find({user_id: YOUR_USER_ID}).sort({timestamp: -1}).limit(5)
```

---

**This architecture ensures:**
- ✅ Clean, maintainable code
- ✅ No code duplication
- ✅ Easy to extend with new features
- ✅ Robust error handling
- ✅ Complete audit trail
- ✅ Production-ready reliability

