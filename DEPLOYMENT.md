# 🚀 Deployment Guide

Complete instructions for deploying TeraBox Downloader Bot to various platforms.

## Table of Contents
1. [Local Development](#local-development)
2. [Docker](#docker)
3. [VPS (Ubuntu/Debian)](#vps-ubuntudebian)
4. [Replit](#replit)
5. [Render](#render)
6. [Railway](#railway)

---

## Local Development

### Prerequisites
- Python 3.9 or higher
- MongoDB running locally
- FFmpeg installed

### Setup Steps

```bash
# 1. Clone repository
git clone <repo>
cd terabox-bot

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Copy and configure .env
cp .env.example .env
# Edit .env with your values

# 5. Start MongoDB (if not running)
mongod

# 6. Run the bot
python main.py
```

### Development Commands

```bash
# Format code
black .

# Lint code
flake8 .
pylint plugins/ helpers/

# Run tests
pytest tests/

# Check logs
tail -f logs/bot.log
```

---

## Docker

### Using Docker Directly

```bash
# 1. Build image
docker build -t terabox-bot .

# 2. Run with external MongoDB
docker run -d \
  --env-file .env \
  -v bot_downloads:/app/downloads \
  -v bot_logs:/app/logs \
  --name terabox-bot \
  --restart unless-stopped \
  terabox-bot

# 3. View logs
docker logs -f terabox-bot

# 4. Stop bot
docker stop terabox-bot
docker rm terabox-bot
```

### Using Docker Compose (Recommended)

```bash
# 1. Start services
docker-compose up -d

# 2. View logs
docker-compose logs -f bot

# 3. Check status
docker-compose ps

# 4. Stop services
docker-compose down

# 5. Clean up (remove volumes)
docker-compose down -v
```

### Docker Registry Deployment

```bash
# 1. Build and tag
docker build -t yourusername/terabox-bot:latest .

# 2. Push to registry
docker login
docker push yourusername/terabox-bot:latest

# 3. On server
docker pull yourusername/terabox-bot:latest
docker run -d --env-file .env yourusername/terabox-bot:latest
```

---

## VPS (Ubuntu/Debian)

### Complete Setup Guide

```bash
# 1. Update system
sudo apt update && sudo apt upgrade -y

# 2. Install dependencies
sudo apt install -y \
  python3.11 \
  python3-pip \
  mongodb \
  ffmpeg \
  git \
  curl \
  wget

# 3. Create bot user (optional but recommended)
sudo useradd -m -s /bin/bash botuser

# 4. Clone repository
cd /home/botuser
sudo git clone <repo> terabox-bot
sudo chown -R botuser:botuser terabox-bot

# 5. Setup Python environment
cd terabox-bot
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 6. Configure environment
cp .env.example .env
# Edit with your values using nano or vim
nano .env

# 7. Test the bot
python main.py
# Press Ctrl+C to stop
```

### Systemd Service Setup

Create `/etc/systemd/system/terabox-bot.service`:

```bash
sudo nano /etc/systemd/system/terabox-bot.service
```

Paste this content:

```ini
[Unit]
Description=TeraBox Downloader Bot
After=network.target mongodb.service

[Service]
Type=simple
User=botuser
WorkingDirectory=/home/botuser/terabox-bot
Environment="PATH=/home/botuser/terabox-bot/venv/bin"
EnvironmentFile=/home/botuser/terabox-bot/.env
ExecStart=/home/botuser/terabox-bot/venv/bin/python main.py
Restart=on-failure
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
```

Enable and start the service:

```bash
sudo systemctl daemon-reload
sudo systemctl enable terabox-bot
sudo systemctl start terabox-bot

# Check status
sudo systemctl status terabox-bot

# View logs
sudo journalctl -u terabox-bot -f
```

### Nginx Reverse Proxy (Optional for monitoring)

```nginx
server {
    listen 80;
    server_name bot.example.com;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

---

## Replit

### Step-by-Step

1. **Create New Replit Project**
   - Language: Python
   - Import from GitHub: `<repo>`

2. **Install Dependencies**
   - Open Shell (bottom right)
   - Run: `pip install -r requirements.txt`

3. **Configure Environment**
   - Click "Secrets" (padlock icon) in left sidebar
   - Add each variable from `.env.example`
   - Example:
     ```
     BOT_TOKEN = your_token_here
     API_ID = your_api_id
     API_HASH = your_api_hash
     ```

4. **Setup MongoDB**
   - Use MongoDB Atlas (free tier)
   - Create cluster: https://www.mongodb.com/cloud/atlas
   - Get connection URI
   - Add to secrets: `MONGODB_URI = mongodb+srv://user:pass@cluster.mongodb.net/terabox_bot`

5. **Run Bot**
   - Click "Run" button at top
   - Or in shell: `python main.py`

6. **Keep Running (Optional)**
   - Use Replit "Always On" feature (requires Replit Pro)
   - Or use uptime monitoring service

---

## Render

### Deployment Steps

1. **Create Account**
   - Sign up at https://render.com

2. **Create Web Service**
   - Click "New" → "Web Service"
   - Connect GitHub repo
   - Choose Python as runtime

3. **Configure**
   - **Name:** terabox-bot
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `python main.py`
   - **Plan:** Free tier or Paid

4. **Environment Variables**
   - Click "Environment"
   - Add all variables from `.env.example`

5. **Add-ons**
   - Click "Add" → MongoDB Atlas
   - Copy connection string to `MONGODB_URI`
   - Or use external MongoDB

6. **Deploy**
   - Click "Create Web Service"
   - Wait for build and deployment
   - Check logs at bottom

### Important Notes
- Free tier may have limitations
- Keep bot responsive by using pings
- Monitor resource usage

---

## Railway

### Deployment Steps

1. **Create Account**
   - Sign up at https://railway.app

2. **Create Project**
   - "New Project" → "GitHub Repo"
   - Select your repository
   - Authorize Railway

3. **Add Services**
   - Add MongoDB:
     - Click "Add"
     - Select "MongoDB"
     - Create service

4. **Configure Bot Service**
   - Go to Repository
   - Settings → Environment
   - Add all variables from `.env.example`
   - Set `MONGODB_URI` to Railway MongoDB connection string

5. **Deploy**
   - Push to GitHub
   - Railway auto-deploys
   - Check logs in dashboard

---

## Performance Tuning

### Database Optimization

```bash
# Create MongoDB indexes
mongo
> db.users.createIndex({ "user_id": 1 }, { "unique": true })
> db.logs.createIndex({ "timestamp": -1 })
> db.logs.createIndex({ "user_id": 1 })
```

### Memory Management

Edit `main.py` for resource limits:

```python
# Limit concurrent downloads
MAX_CONCURRENT_DOWNLOADS = 5

# Cleanup interval
CLEANUP_INTERVAL = 3600  # 1 hour
```

### Auto-Restart on Crash

Using `systemd` (already configured above):

```bash
sudo systemctl restart terabox-bot
```

Or using `supervisor`:

```ini
[program:terabox-bot]
command=/path/to/venv/bin/python /path/to/main.py
autostart=true
autorestart=true
stderr_logfile=/var/log/terabox.err.log
stdout_logfile=/var/log/terabox.out.log
```

---

## Monitoring & Logs

### View Logs

**Local:**
```bash
tail -f logs/bot.log
```

**Systemd:**
```bash
sudo journalctl -u terabox-bot -f --lines 50
```

**Docker:**
```bash
docker logs -f terabox-bot
```

### Health Check

```bash
# Check if MongoDB is running
mongosh "mongodb://localhost:27017"

# Check bot status
curl http://localhost:8000/health  # If you add health endpoint

# Check system resources
top
df -h
```

---

## Troubleshooting

### Port Already in Use

```bash
# Find process using port
lsof -i :8000

# Kill process
kill -9 PID
```

### MongoDB Connection Failed

```bash
# Test connection
mongosh "mongodb://your_connection_string"

# Check MongoDB logs
sudo systemctl status mongodb
sudo journalctl -u mongodb -f
```

### High Memory Usage

```bash
# Check memory
free -h

# Reduce download chunk size in config.py
CHUNK_SIZE = 524288  # 512KB instead of 1MB
```

### Bot Crashes on Start

```bash
# Check Python version
python --version  # Must be 3.9+

# Check dependencies
pip list

# Reinstall dependencies
pip install -r requirements.txt --upgrade
```

---

## Backup & Recovery

### Backup MongoDB

```bash
# Backup entire database
mongodump --uri="mongodb://localhost:27017" --out ./backup

# Backup specific collection
mongodump --uri="mongodb://localhost:27017" --collection users --out ./backup
```

### Restore MongoDB

```bash
# Restore from backup
mongorestore --uri="mongodb://localhost:27017" ./backup
```

### Backup Application Files

```bash
# Create tarball
tar -czf terabox-bot-backup.tar.gz /home/botuser/terabox-bot/

# Upload to cloud storage
scp terabox-bot-backup.tar.gz user@backup-server:/backups/
```

---

## Next Steps

- [ ] Configure all environment variables
- [ ] Test with sample TeraBox link
- [ ] Set up monitoring alerts
- [ ] Configure backup strategy
- [ ] Document your setup
- [ ] Test recovery procedures

---

**Questions?** Check logs or open an issue on GitHub.

**Last Updated:** January 2024
